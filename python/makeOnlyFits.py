#!/usr/bin/env python
from ROOT import *
from pyfits import Column, HDUList, PrimaryHDU, new_table

import numpy as num
import math
import utils
import datetime
from makeFits import *
import glob,sys,os

if __name__=='__main__':
    
    filename      = sys.argv[1]
    lines         = file(filename,'r').readlines()
    DETNAM       = None
    for line in lines:
        if '#' in line:
            continue
        if 'DETNAM' in line:
            fava=line.split(':=')
            DETNAM        = fava[1].strip()
            pass
        pass
    if DETNAM==None:
        sys.exit()
    print 'DETNAM = ',DETNAM
    
    DIRECTORY      = filename.replace('.txt','')
    os.system('mkdir -p %s' % DIRECTORY)
    ##################################################
    # PHA2
    ##################################################
    
    DIRECTORY_PHA2  = '%s_0*_pha2' % DIRECTORY    
    DIRECTORY_PHA2_LIST  = glob.glob(DIRECTORY_PHA2)
    
    print DIRECTORY_PHA2_LIST
    
    nPHA2                = len(DIRECTORY_PHA2_LIST)
    
    FT2        = ''
    TRIGTIME   = 0.0
    METMIN     = 0.0
    METMAX     = 0.0
    CORRECTION = 0.0    
    Tmin       = 1e12
    Tmax       = 0.0
    
    output_histo    = filename.replace('.txt','_pha2_sum.root')
    input_histo_list=[]
    
    pars = {}
    filelist = ''
    for i in range(nPHA2):
        iDIRECTORY = '%s_%04d_pha2' % (DIRECTORY,i)
        iParFile   = '%s_%04d_pha2/PHA2_PARAMETERS_%s.txt' % (DIRECTORY,i,DETNAM)
        iHistoFile = '%s_%04d_pha2/PHA2_HISTOGRAMS_%s.root' % (DIRECTORY,i,DETNAM)
        input_histo_list.append(iHistoFile)
        filelist +=iHistoFile
        filelist +=' '
        
        fcorr = file(iParFile,'r')
        lines=fcorr.readlines()
        for l in lines:
            pars[l.split('=')[0].strip()] = l.split('=')[1].strip()
            pass
        FT2        = pars['FT2']
        TRIGTIME   = float(pars['TRIGTIME'])
        METMIN     = float(pars['METMIN'])
        METMAX     = float(pars['METMAX'])
        
        Tmin       = min(Tmin,float(pars['TSTART']))
        Tmax       = max(Tmax,float(pars['TEND']))

        #CORRECTION += float(pars['CORRECTION'])
        
        print FT2
        print TRIGTIME
        print METMIN,METMAX
        print Tmin,Tmax
        print float(pars['CORRECTION'])        
        pass
    ft2=pyfits.open(FT2)    
    ft2.info()
    LTF =  utils.GetLiveTimeFraction(ft2,Tmin,Tmax,0)
    # THIS IS THE LIVE TIME FRACTION "PER PHASE"
    CORRECTION =  (Tmax-Tmin)/(METMAX-METMIN) * LTF
    print 'TMIN = %s,  TMAX =%s ' % (Tmin,Tmax)
    print 'CORRECTION (LIVETIME):.........................: ',CORRECTION    
    print 'TOTAL ELAPSED TIME.............................: ',(Tmax-Tmin)
    print 'LIVETIME FRACTION..............................: ',CORRECTION/(Tmax-Tmin)
    
    #for f in input_histo_list:
    #    filelist+=f+' '
    #    pass
    #print filelist
    hadd='hadd -f %s %s' %(output_histo,filelist)
    print hadd
    os.system(hadd)

    PHA2_File = TFile(output_histo,'OPEN')

    PHA2=PHA2_File.Get('PHA2')
    fitsPHA2(PHA2,FT2,DETNAM,DIRECTORY,TRIGTIME,METMIN,METMAX,CORRECTION)
    PHA2_File.Close()
    
    ##################################################
    # DRM
    
    DIRECTORY_DRM  = '%s_0*_drm' % DIRECTORY    
    DIRECTORY_DRM_LIST  = glob.glob(DIRECTORY_DRM)
    
    print DIRECTORY_DRM_LIST
    
    nDRM                = len(DIRECTORY_DRM_LIST)
    
    FT2        = ''
    TRIGTIME   = 0.0
    METMIN     = 0.0
    METMAX     = 0.0
    CORRECTION = 0.0    
    
    output_histo     =  filename.replace('.txt','_drm_sum.root')
    input_histo_list = []
    
    pars = {}
    filelist = ''
    if nDRM>1:
        for i in range(nDRM):
            iDIRECTORY = '%s_%04d_drm' % (DIRECTORY,i)
            # iParFile   = '%s_%04d_drm/DRM_PARAMETERS_%s.txt' % (DIRECTORY,i,DETNAM)
            iHistoFile = '%s_%04d_drm/DRM_HISTOGRAMS_%s.root' % (DIRECTORY,i,DETNAM)
            input_histo_list.append(iHistoFile)
            filelist+=iHistoFile
            filelist+=' '
            # fcorr = file(iParFile,'r')
            # fcorr.readlines()
            # for l in lines:
            #    pars[l.split('=')[0].strip()] = l.split('=')[1].strip()
            #    pass
            # FT2        = pars['FT2']
            # TRIGTIME   = float(pars['TRIGTIME'])
            # METMIN     = float(pars['METMIN'])
            # METMAX     = float(pars['METMAX'])
            # CORRECTION += float(pars['CORRECTION'])
            # print FT2
            # print TRIGTIME
            # print METMIN
            # print METMAX
            # print float(pars['CORRECTION'])        
            pass
        
        # filelist = ''
        # for f in input_histo_list:
        #     filelist+=f+' '
        
        hadd='hadd -f %s %s' %(output_histo,filelist)
        print hadd
        os.system(hadd)
        # fitsDRM(DRM,FT2,DETNAM,DIRECTORY,TRIGTIME,METMIN,METMAX,CORRECTION)
    ##################################################
        DRM_File = TFile(output_histo,'OPEN')
        DRM      = DRM_File.Get('DRM')
        filename = fitsDRM(DRM,DETNAM,DIRECTORY,TRIGTIME, METMIN, METMAX)
        DRM_File.Close()
        pass
    
    ##################################################
    pass
