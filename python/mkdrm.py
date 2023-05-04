#!/usr/bin/env python

from ROOT import *
from makeFits import *
from pyfits import Column, HDUList, PrimaryHDU, new_table
import sys,os
import numpy as num
import math
import utils
import datetime
##################################################
# THIS IS SOME STYLE STUFFS:
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetCanvasColor(10)
gStyle.SetPadColor(10)
gStyle.SetPadTickX(True)
gStyle.SetPadTickY(True)
gStyle.SetFrameFillColor(10)
gStyle.SetPalette(1)
##################################################
_directory='OUTPUT'

def getLiveTimeCubes(LTCFILE,RA,DEC):
    import pyfits
    lc_file=pyfits.open(LTCFILE)
    table2 = lc_file[2].data
    ra =table2.field('RA')
    dec=table2.field('DEC')
    cos=table2.field('COSBINS')
    h0=lc_file[2].header
    tstart=h0['TSTART']
    tstop =h0['TSTOP']
    print 'ltcubeFile: %s tstart: %s tstop: %s duration: %s '%(LTCFILE,tstart,tstop,tstop-tstart)
    #dist=sqrt((ra[i]-RA)*(ra[i]-RA)+(dec[i]-DEC)*(dec[i]-DEC))
    nbins=len(ra)
    distMin=180.0
    iMin=0
    for i in xrange(nbins):
        dist=sqrt((ra[i]-RA)*(ra[i]-RA)+(dec[i]-DEC)*(dec[i]-DEC))
        if dist<distMin:
            distMin=dist
            iMin=i
            pass
        pass
    print iMin,ra[iMin],dec[iMin],distMin
    print cos[iMin]
    pass

if __name__=='__main__':
    # READ THE PARAMETERS FILE:
    
    try:
        fin_name = sys.argv[1]
        fin = file(sys.argv[1],'r')
    except:
        print 'Usage: mkdrm.py <parfile> [drm|pha2]'
        exit()
        pass
    try:
        mode=sys.argv[2]
        print mode
    except:
        mode=''
        pass

    fin_name_only = fin_name.replace('config/','output/')
    _directory = fin_name_only.replace('.txt','')
    os.system('mkdir -p %s .' % _directory)
    
    lines = fin.readlines()
    par={}
    for l in lines:
        if '#' not in l:            
            try:
                name=l.split(':=')[0].strip()
                try:
                    value = float(l.split(':=')[1].strip())
                    pass
                except:
                    value = l.split(':=')[1].strip()
                    pass            
                par[name]=value
                print name, value
            except:
                pass
            pass
        pass
    ##################################################
    print ' ################################################## '
    print ' mkdrm.py - written by nicola.omodei@gmail.com'
    print '  CONFIGURATION FILE    ......: %s ' % fin
    print ' **************************************************'
    print ' #                  CONFIGURATION                 # '
    INDEX = par['INDEX']
    MAKEPHA2 = par['MAKEPHA2']
    EMAX = par['EMAX']
    basename = par['basename'].replace('"','')

    DEC = par['DEC']
    TRIGTIME = par['TRIGTIME']
    BINFILE=None
    try:
        BINFILE = par['BINFILE']
        print 'Bins definition readed from %s ' % BINFILE
    except:
        BEFORE = par['BEFORE']
        AFTER  = par['AFTER']
        DT     = par['DT']
        pass
    try:
        DURATION=par['DURATION']
    except:
        DURATION=0
        pass

    try:
        OFFSET=par['OFFSET']
    except:
        OFFSET=0
        pass

    useAllGamma = par['useAllGamma']
    MAKEDRM = par['MAKEDRM']
    DATAFILESBASE = par['DATAFILESBASE'].replace('"','')
    NDATAFILES = int(par['NDATAFILES'])
    try:
        NDATAFILES = int(os.environ['NDATAFILES'])
    except:
        pass
    
    try:
        NDATAFIRST=int(par['NDATAFIRST'])
    except:
        NDATAFIRST=0
        pass
    
    try:
        NDATAFIRST = NDATAFIRST + int(os.environ['NDATAFIRST'])
    except:
        pass
    
    EMIN = par['EMIN']
    FLUX = par['FLUX']
    RA = par['RA']
    NREC = int(par['NREC'])
    NGEN = int(par['NGEN'])
    try:
        NGEN = int(os.environ['NGEN'])
    except:
        pass
    
    NAllGammaFiles = int(par['NAllGammaFiles'])
    
    try:
        NAllGammaFiles = int(os.environ['NAllGammaFiles'])
    except:
        pass
    
    try:
        FirstFile      = int(par['FirstFile'])
    except:
        FirstFile      = 0
        pass
    
    try:
        FirstFile      = FirstFile + int(os.environ['FirstFile'])
    except:        
        pass
    

    

    
    ZENITHTHETA = par['ZENITHTHETA']
    RADIUS_ROI = par['RADIUS_ROI']
    useNgen = par['useNgen']
    if not useNgen:
        NGEN = 0
        pass
    MYCUT = par['MYCUT']
    DETNAM = par['DETNAM']
    NMC = int(par['NMC'])
    
    try:
        ROOT.gROOT.SetBatch(int(par['SETBATCH']))
    except:
        print "Can not set ROOT BATCH mode, using default..."
        
    try:
        DATAENERGYVAR = par['ENERGYVAR']
    except:
        DATAENERGYVAR = 'EvtEnergyCorr'
        print 'Can not set data energy variable, using default: %s' %\
              DATAENERGYVAR
        pass
    try:
        SOURCE = par['SOURCE']
    except:
        SOURCE='MERIT'
        print 'Can not set source tree. Using default: %s' %\
              SOURCE
        pass
    
    
    for k in par.keys():
        print '%20s:\t%s'%(k,par[k])
        #print "%s = par['%s']" % (k,k)
        pass
    print ' ################################################## '
    
    GRBFILES=[]
    if '.txt' in DATAFILESBASE:
        print '===>',DATAFILESBASE
        lines = file(DATAFILESBASE,'r').readlines()
        #print lines
        GRBFILES=lines[NDATAFIRST:NDATAFILES+NDATAFIRST]
        
    elif '%' in DATAFILESBASE:
        for i in range(NDATAFILES):
            rootFilename     = DATAFILESBASE % (i+NDATAFIRST)
            # Try to take into account missing files or keys:
            f=TFile.Open(rootFilename)
            try:
                if f.GetListOfKeys().GetSize() > 0:
                    GRBFILES.append(rootFilename)
                    pass
                pass
            except:
                pass
            pass
        pass
    elif DATAFILESBASE=='*':
        from findMerit import find_merit_files
        #datacatalogFiles = find_merit_files(TRIGTIME, dt=(BEFORE,AFTER))
        GRBFILES = find_merit_files(TRIGTIME, dt=(BEFORE,AFTER))        
        #for rootFilename in datacatalogFiles:
        #    #f=TFile.Open(rootFilename)
        #    GRBFILES.append(rootFilename)            
    else:
        GRBFILES=[DATAFILESBASE]
        pass    
    print '##################################################'
    print ' CONFIGURATION SUCCESSFULLY READ '
    print '##################################################'
    print 'Building the time array...'
    BINS=[]
    if BINFILE is not None:
        BINS = ReadTimeBins(BINFILE)        
        BEFORE = fabs(BINS[0])
        AFTER  = fabs(BINS[-1])
        NMET   = len(BINS)
        for i in len(BINS):
            BINS[i]=BINS[i] + TRIGTIME
            pass
        pass
    else:
        METMIN  = TRIGTIME - BEFORE
        METMAX  = TRIGTIME + AFTER
        NMET    =int((METMAX-METMIN)/DT)
        pass
        #BINS    =range(NMET)
        #for i in len(BINS):
        #    BINS[i] = METMIN + 1.0*i*(DT)
        #    pass
        pass
    
    
    
    
    print 'Tstart = %s, Tstop=%s, Nbin=%s' %(METMIN,METMAX,NMET)
    print 'getting FT2 fle...'    
    FT2 = utils.getFT2('FT2',METMIN-3600,METMAX+3600)
    #################################################################################
    if mode=='pha2':
        MAKEPHA2 = 1
        MAKEDRM  = 0
        pass
    
    elif mode=='drm':
        MAKEPHA2 = 0
        MAKEDRM  = 1
        pass
    
    if MAKEDRM:
        ROOTfiles=[]
        offset=FirstFile
        if NAllGammaFiles==0:
            from findMerit import find_MC_files
            ROOTfiles = find_MC_files(name=basename)
        else:
            for i in range(NAllGammaFiles):
                filename     = basename % (i+offset)
                rootFileName = filename.replace("'",'').replace('"','')
                # Try to take into account missing files or keys:
                f=TFile.Open(rootFileName)
                try:
                    if f.GetListOfKeys().GetSize()>0:
                        ROOTfiles.append(rootFileName)
                        pass
                    pass
                except:
                    pass
                pass
            pass
        
        print 'Added %s valid MC files ' % len(ROOTfiles)
        theta_idx = 0
        try:
            THETA=float(par['THETA'])
            print '===== Unsing theta from configuration file !!!!'
        except:
            THETA,theta_idx =utils.getTheta(FT2,TRIGTIME,RA,DEC,theta_idx)        
            pass        
        print 'theta= (GRB) %s' % THETA
        
        from makeRootDRM import *
        filename = makeRootDRM(ROOTfiles,NMC,NREC,NGEN,FLUX,
                               useAllGamma,DETNAM,_directory,
                               DATAENERGYVAR,EMIN,EMAX,
                               METMIN,METMAX,
                               INDEX, RA, DEC, 
                               ZENITHTHETA, THETA,
                               RADIUS_ROI, TRIGTIME, MYCUT, 
                               OFFSET, DURATION)
        
        pass
    
    
    if MAKEPHA2:
        from makePHA2 import *
        filename = makePHA2(GRBFILES, FT2,
                            NREC,EMIN,EMAX,
                            NMET,METMIN,METMAX,
                            RA,DEC,ZENITHTHETA,RADIUS_ROI,
                            TRIGTIME,MYCUT,
                            DETNAM,_directory,
                            DATAENERGYVAR,SOURCE,
                            OFFSET,DURATION)        
        pass
