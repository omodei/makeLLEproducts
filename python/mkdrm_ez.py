#!/usr/bin/env python
from ROOT import *
from makeFits import *
import makeLLEcut
import astropy.io.fits as pyfits
from pyfits import Column, HDUList, PrimaryHDU
#import pyfits
import sys,os
import numpy as num
import math
import utils
import datetime
from GtApp import *

##################################################
# THIS IS SOME STYLE STUFFS:
gStyle.SetOptTitle(1)
gStyle.SetOptStat(0)
gStyle.SetCanvasColor(10)
gStyle.SetPadColor(10)
gStyle.SetPadTickX(True)
gStyle.SetPadTickY(True)
gStyle.SetFrameFillColor(10)
gStyle.SetPalette(1)
##################################################
_directory='OUTPUT'
_MCBASENAME='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass7'

if __name__=='__main__':

    fin_name=RA=DEC=basename=TRIGTIME=mode=FT=None
    OFFSET     = 0
    RADIUS_ROI = 12
    ZENITHTHETA= 100.0
    THETAMAX      = 90
    BEFORE     = 300
    AFTER      = 300
    DT         = 1
    SSD        = 0
    NOTRANS    = 0
    FT2        = None
    mc_version     = None
    lle_version    = 0
    DATAFILE = None
    for i,a in enumerate(sys.argv):
        # needed
        if a=='-i'  : fin_name        = sys.argv[i+1] # needed        
        if a=='-ra' : RA              = float(sys.argv[i+1])
        if a=='-dec': DEC             = float(sys.argv[i+1])        
        if a=='-n'  : basename        = sys.argv[i+1]
        if a=='-t'  : TRIGTIME        = float(sys.argv[i+1])
        if a=='-d'  : DURATION        = float(sys.argv[i+1])
        
        # optional
        if a=='-b'  : BEFORE          = float(sys.argv[i+1])
        if a=='-a'  : AFTER           = float(sys.argv[i+1])

        if a=='-off': OFFSET          = float(sys.argv[i+1])
        if a=='-m'  : mode            = sys.argv[i+1]
        if a=='-dt' : DT              = float(sys.argv[i+1])
        if a=='-r': RADIUS_ROI        = float(sys.argv[i+1])
        if a=='-zenith': ZENITHTHETA  = float(sys.argv[i+1])
        if a=='-theta': THETAMAX         = float(sys.argv[i+1])
        if a=='-ssd':   SSD           = 1
        if a=='-notransient': NOTRANS = 1
        #########
        if a=='-outdir': _directory  = sys.argv[i+1]
        if a=='-mcbase': _MCBASENAME = sys.argv[i+1]
        if a=='-ft2':    FT2         = sys.argv[i+1]
        if a=='-v'  : lle_version    = sys.argv[i+1]
        if a=='-mcv': mc_versionn    = sys.argv[i+1]
        if a=='-datafile' : DATAFILE = sys.argv[i+1]
        #########
        if a=='-h': printHelp(); exit()
        pass
    
    def printHelp():
        txt='''
        usage:
        ./mkdrm_ez.py -i <config fileName (config/DefaultLLE.txt]>  -ra <RA> -dec <DEC> -n <Basename [GRB080916C]> -t <TRIGTIME, MET> -d <DURATION> -off <OFFSET(optional)> -m <mode: drm|pha> -dt <DT> -r <RADIUS_ROI (if negative: abs number of PSF> -zenith <Max ZENITH ange> -theta <Max Theta> -notransient
        '''
        print txt
        pass
    
    
    try:
        fin = file(fin_name,'r')
    except:
        print 'Configuration file Not found!'
        printHelp()
        exit()
        pass
    
    
    # READ THE PARAMETERS FILE:
    
    #fin_name_only = fin_name.replace('config/','output/')
    if(_directory=='OUTPUT'):
        _directory = 'output_ez/%s' % basename #fin_name_only.replace('.txt','')
        pass
    
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
    print ' mkdrm.py - written by nicola.omodei@stanford.edu'
    print '  CONFIGURATION FILE    ......: %s ' % fin
    print ' **************************************************'
    print ' #                  CONFIGURATION                 # '
    INDEX = par['INDEX']
    EMAX = par['EMAX']
    
    useAllGamma = 0
    DATAFILESBASE = '*'
    NDATAFILES    = 1 
    
    EMIN = par['EMIN']
    FLUX = 0
    NREC = int(par['NREC'])
    NGEN = int(par['NGEN'])
    MYCUT  = par['MYCUT']
    DETNAM = par['DETNAM']
    NMC = int(par['NMC'])
    
    #DETNAM='%s_%.2f_%.2f' %(DETNAM,OFFSET,DURATION)
    
    if RADIUS_ROI<0:   DETNAM='%s_ROIE%d' %(DETNAM,-RADIUS_ROI)
    else:              DETNAM='%s_ROI%.0f' %(DETNAM,RADIUS_ROI)
    
    DETNAM='%s_Z%.0f' %(DETNAM,ZENITHTHETA)
    DETNAM='%s_TH%.0f' %(DETNAM,THETAMAX)
    BASE='LLE'
    if SSD:
        MYCUT='(%s) && (Tkr1SSDVeto>0)' %(MYCUT)
        DETNAM+='_SSD'
        BASE='SSD'
        pass
    
    #If the user requested to remove Transient event from the LLE sample, do that
    if(NOTRANS):
        print("\n\n EXCLUDING TRANSIENT EVENTS FROM THE SAMPLE \n\n")
        MYCUT = "(%s) && !(CTBParticleType==0 && CTBClassLevel >= 1)" % (MYCUT)
        DETNAM +="_NOTRANS" 
        pass
    
    try:     ROOT.gROOT.SetBatch(int(par['SETBATCH']))
    except:  print "Can not set ROOT BATCH mode, using default..."
    
    try:
        DATAENERGYVAR = par['ENERGYVAR']
    except:
        DATAENERGYVAR = 'EvtEnergyCorr'
        print 'Can not set data energy variable, using default: %s' %\
              DATAENERGYVAR
        pass
    
    for k in par.keys():  print '%20s:\t%s'%(k,par[k])

    print '################################################## '
    print ' CONFIGURATION SUCCESSFULLY READ '
    print '##################################################'    
  
    from findMerit import find_merit_files
    #BEFORE  = max(BEFORE,-OFFSET)
    #AFTER   = max(AFTER,DURATION)
    METMIN  = TRIGTIME - BEFORE
    METMAX  = TRIGTIME + AFTER
    NMET    =int((METMAX-METMIN)/DT)
    
    print ('Tstart = %s, Tstop=%s, Nbin=%s' %(METMIN,METMAX,NMET))
    if(FT2==None):
        print ('getting FT2 fle...')
        FT2 = utils.getFT2('FT2',METMIN-3600,METMAX+3600)
    else:
        print("\nUsing the FT2 file %s\n" %(FT2))
        pass  
    #################################################################################
    MAKEPHA2 = 1
    MAKEDRM  = 1
    MAKEPHA1 = 1

    if mode=='pha2' or mode=='pha':
        MAKEPHA1 = 1            
        MAKEPHA2 = 1
        MAKEDRM  = 0
        pass
    elif mode=='pha1':
        MAKEPHA1 = 1            
        MAKEPHA2 = 0
        MAKEDRM  = 0
        
    elif mode=='drm':
        MAKEPHA1 = 0            
        MAKEPHA2 = 0
        MAKEDRM  = 1
        pass
    
    #################################################################
    # Calculate the angle between the GRB and the LAT z axis (GRB_THETA)
    theta_idx = 0
    GRB_THETA,theta_idx =utils.getTheta(FT2,TRIGTIME,RA,DEC,theta_idx)    
    print ('theta= (GRB) %s' % GRB_THETA)
    if GRB_THETA>90:
        MAKEDRM=0
        MAKEPHA2=1
        pass
    #################################################################

    # HERE WE DEFINE THE CUT ONCE FOR ALL
    MYCUT=makeLLEcut.Do(RA          = RA,
                        DEC         = DEC,
                        ZENITHTHETA = ZENITHTHETA,
                        THETAMAX    = THETAMAX,
                        RADIUS      = RADIUS_ROI,
                        myCut       = MYCUT,
                        verbose     = 1,
                        ENERGYVAR   = DATAENERGYVAR)
    #################################################################
    #PASS_VER = _MCBASENAME.split('GRBSimulator-')[-1].strip()

    
# _DCBASENAME='/Data/Flight/Level1/LPA/'


    if 'Pass6v3' in _MCBASENAME: 
        _DCBASENAME='/Data/Flight/Level1/LPA/'        
        PASS_VER = 'P6V3'        
        PROC_VER = '001'
        if METMIN>333880535: 
            print '$$$$$ FAILED!!!: NO PASS6 DATA AVAILABLE!'
            exit()
            pass        
    elif 'Pass7' in _MCBASENAME:        
        PASS_VER = 'P7REP'
        PROC_VER = '001'
        if METMIN>333880535:  _DCBASENAME='/Data/Flight/Level1/LPA/'
        else:                 _DCBASENAME='/Data/Flight/Reprocess/P202/'
    elif 'Pass8' in _MCBASENAME: 
        PASS_VER = 'P8V2'
        PROC_VER = '301'
        if METMIN > 456829490:_DCBASENAME='/Data/Flight/Level1/LPA/'
        else: _DCBASENAME='/Data/Flight/Reprocess/P301/'        
        pass
    else: 
        print '$$$$$ FAILED!!!: MCBASENAME: %s not VALID!!!!' % _MCBASENAME
        exit()
        
    MC_VER   = None

    KEYWORDS={'OBJECT':basename,
              'EMIN':EMIN,
              'EMAX':EMAX,
              'RA_OBJ':RA,
              'DEC_OBJ':DEC,
              'ZMAX':ZENITHTHETA,
              'THMAX':THETAMAX,
              'ROI':RADIUS_ROI,
              'DT': DT,
              'BASE':BASE,
              'MY_CUT':MYCUT,
              'PROC_VER':PROC_VER,
              'PASS_VER':PASS_VER,
              'MC_VER':MC_VER,              
              'VERSION':lle_version,
              'RSPTMIN':OFFSET,
              'RSPTMAX':OFFSET+DURATION,
              'MAKEPHA1':MAKEPHA1,
              'BEFORE':BEFORE,
              'AFTER':AFTER,
              'TRIGTIME':TRIGTIME,
              'OFFSET':OFFSET,
              'DURATION':DURATION,              
              'TTEFILE':None,
              'TTESELECTED':None,
              'PHA2FILE':None,
              'PHA1FILE':None,
              'RSPFILE':None,              
              'CSPEC_PNG':None,
              'QUICK_PNG':None,
              'EDISP_PNG':None,
              'EFFAREA_PNG':None,
              'MCVAR_PNG':None,
              'FT21SEC':None
              }
    
    KEYWORDS['FT21SEC']=FT2
    if MAKEDRM:
        ROOTfiles=[]
        from findMerit import find_MC_files,getVersion
        
        try: ROOTfiles = find_MC_files(name=basename,base=_MCBASENAME,version=mc_version,maximum=1000)
        except: ROOTfiles=[]

        if(len(ROOTfiles)>0):
            MC_VER = getVersion(_MCBASENAME,ROOTfiles[0])        
            #print 'TRY with PASS 6 MC'
            #ROOTfiles = find_MC_files(name=basename,base='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass6v3')
            #if(len(ROOTfiles)==0): raise RuntimeError("No MC found for this GRB! Impossible to produce LLE products.")
            #
            print 'Added %s valid MC files...: ' % len(ROOTfiles)
            print 'selected MC version.......: %d' % MC_VER
            KEYWORDS['MC_VER']=MC_VER
            
            from makeRootDRM import *
            filename = makeRootDRM(ROOTfiles,
                                   NMC,NREC,NGEN,FLUX,
                                   DETNAM,_directory,
                                   DATAENERGYVAR,EMIN,EMAX,
                                   METMIN,METMAX,basename,
                                   INDEX,
                                   TRIGTIME,
                                   MYCUT, 
                                   OFFSET, DURATION,KEYWORDS)
            KEYWORDS['RSPFILE']=filename
        else:
            print "No MC found for this GRB! Impossible to produce LLE DRM products."
            pass
        pass
    
    if MAKEPHA2:
        from makePHA2 import *
        GRBFILES=[]
        
        print 'USING  mccbase=',_MCBASENAME
        print 'USING  dcbase=',_DCBASENAME
        
        if DATAFILE is None:
            GRBFILES = find_merit_files(TRIGTIME, _DCBASENAME, dt=(-BEFORE,AFTER))        
        else:
            GRBFILES=[DATAFILE]
            print '** USING GRBFILES...',GRBFILES
            pass
        filename = makePHA2(GRBFILES, FT2,
                            NREC,EMIN,EMAX,
                            NMET,METMIN,METMAX,
                            TRIGTIME,
                            MYCUT,
                            DETNAM,_directory,basename,
                            DATAENERGYVAR,
                            OFFSET,DURATION,KEYWORDS)        

        KEYWORDS['PHA2FILE']=filename
        
        #Now produce the FT1 file using makeLLE
        print("\n\nNow producing FT1 file with LLE data...:")        
        from makeLLE_FT1 import makeLLE_FT1
        FT1outfile=makeLLE_FT1(GRBFILES, FT2, 
                               TRIGTIME, METMIN,METMAX,
                               MYCUT, 
                               DETNAM,_directory,basename,
                               DATAENERGYVAR,KEYWORDS)
        KEYWORDS['TTEFILE']=FT1outfile
        update_keywords = True

        '''
        #First we need to produce a text file with the list of merit files
        dumbFilename         = os.path.join(_directory,"meritList.txt")
        dumbFile             = open(dumbFilename,'w')
        for meritFile in GRBFILES:    dumbFile.write("%s\n" % meritFile)
        dumbFile.close()

        try: version    = int(KEYWORDS['VERSION'])
        except: version = 0                
        FT1outfile           = os.path.join(_directory,"gll_lle_bn%s_v%02d.fit" %(basename[-9:],version))
        
        makeLLE              = GtApp('makeLLE')
        makeLLE['infile']    = "@"+dumbFilename
        makeLLE['outfile']   = FT1outfile
        makeLLE['scfile']    = FT2
        makeLLE['t0']        = TRIGTIME
        makeLLE['ra']        = RA
        makeLLE['dec']       = DEC
        makeLLE['dtstart']   = float(BEFORE)*(-1)
        makeLLE['dtstop']    = float(AFTER)
        makeLLE['dict_file'] = os.path.join(os.environ['INST_DIR'],'fitsGen','data','FT1variables')
        makeLLE['clobber']   = 'yes'
        makeLLE['apply_psf'] = 'no'
        makeLLE['zmax']      = 180.0
        makeLLE['TCuts']     = MYCUT
        try: makeLLE.run()
        except: pass
        #Now update some keywords
        update_keywords = True
        
        if update_keywords:
            print 'UPDATING KEYWORDS on %s file' % FT1outfile
            ##################################################        
            LLEft1               = pyfits.open(FT1outfile,mode="update")
            # Get the selection
            # splitted       = DETNAM.split('_')
            # thisSelection  = "_".join(splitted[1:])
            # detnam         = splitted[0]

            ##################################################
            # UPDATE KEYWORDS TO EACH HEADER 
            ##################################################
            for i in (0,1,2):
                my_header             = LLEft1[i].header
                
                # primary_hdr.header.set("DETNAM",detnam)
                # primary_hdr.header.set("FILTER","None")

                
                # VERSION KEYWORDS
                my_header.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
                my_header.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")            
                if i==0: my_header.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
                
                # DATATYPE & FILETYPE (ONLY IN THE PRIMARY HEADER)
                if i==0:
                    my_header.set('DATATYPE','LLE',comment="LAT datatype used for this file")            
                    my_header.set('FILETYPE','LAT PHOTON LIST',comment="Name for this type of FITS file")    
                    pass
                # OBJECT INFO
                my_header.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
                my_header.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
                my_header.set("OBJECT",basename,comment="Object name in standard format, yymmddfff")                        
                my_header.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")
                
                # STRING USED IN THE LLE SELECTION
                my_header.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
                my_header.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
                
                # THESE ARE COMMENTS:
                my_header.add_comment('TRIGTIME=%s' %(TRIGTIME))
                pass
            ####################################################                        
            # UPDATE THE FILE AND FIX CHECKSUM
            ####################################################                                    
            LLEft1.writeto(FT1outfile,output_verify='fix',clobber=1)
            #os.system('fchecksum %s update=yes' % FT1outfile)

            pass
            '''    

        ##################################################
        # Running gtselect
        ##################################################
        pass
    
    if MAKEPHA1:
        TMIN_SELECT           = TRIGTIME + OFFSET
        TMAX_SELECT           = TMIN_SELECT + DURATION
        start_date            = utils.datetime2string(utils.computeDate(TMIN_SELECT),0)#METMIN-int(METMIN))
        end_date              = utils.datetime2string(utils.computeDate(TMAX_SELECT),0)#METMAX-int(METMAX))
        # trig_date             = utils.datetime2string(utils.computeDate(TRIGTIME),0)#TRIGTIME-int(TRIGTIME))
        
        selected_file         = FT1outfile.replace('lle','selected')        
        gtselect              = GtApp('gtselect')
        gtselect['infile']    = FT1outfile
        gtselect['outfile']   = selected_file
        gtselect['ra']        = RA
        gtselect['dec']       = DEC
        gtselect['rad']       = 180
        gtselect['tmin']      = TMIN_SELECT
        gtselect['tmax']      = TMAX_SELECT
        gtselect['emin']      = 0
        gtselect['emax']      = 1e9
        gtselect['zmax']      = 180
        print '--------------------------------------------------'
        print 'Selecting events from %.2f to %.2f (with respect the trigger time)' % (OFFSET, OFFSET+DURATION)
        gtselect.run()
        KEYWORDS['TTESELECTED']=selected_file
        # #################################################
        # RUNNING GTBIN and produce a PHA1 file
        # #################################################
        print '--------------------------------------------------'                
        print ' Binning the selected events into a PHA1 file in %d log bins in [%.1e,%.1e] MeV ' %(NREC,EMIN,EMAX)
        pha_file         = FT1outfile.replace('lle','pha')        
        gtbin              = GtApp('gtbin')
        gtbin['evfile']    = selected_file
        gtbin['scfile']    = FT2
        gtbin['outfile']   = pha_file
        gtbin['algorithm'] = 'PHA1'
        gtbin['ebinalg']   = 'LOG'
        gtbin['emin']      = EMIN
        gtbin['emax']      = EMAX 
        gtbin['enumbins']  = NREC
        gtbin.run()
        print '--------------------------------------------------'
        KEYWORDS['PHA1FILE']=pha_file
        # #################################################
        # ADDING MISSING KEYWORDS
        # #################################################
        
        if update_keywords:
            # #################################################        
            PHA1file               = pyfits.open(pha_file,mode="update")
            # Get the selection
            # splitted       = DETNAM.split('_')
            # thisSelection  = "_".join(splitted[1:])
            # detnam         = splitted[0]
            
            # #################################################
            # UPDATE KEYWORDS TO EACH HEADER 
            # #################################################
            
            for i in (0,1,2,3):
                my_header             = PHA1file[i].header
                if PHA1file[i].name=='EBOUNDS':
                    my_header.set('TLMIN1',1,comment='Channel numbers are positive')
                    my_header.set('TLMAX1',NREC,comment='Greater than the number of channels')
                    my_header.set('TLMIN2',EMIN*1000.,comment='Lowest channel energy')
                    my_header.set('TLMAX2',EMAX*1000.,comment='Highest channel energy')
                    my_header.set('TUNIT2','keV',comment='physical unit of field')
                    my_header.set('TLMIN3',EMIN*1000.,comment='Lowest channel energy')
                    my_header.set('TLMAX3',EMAX*1000.,comment='Highest channel energy')
                    my_header.set('TUNIT3','keV',comment='physical unit of field')
                    pass
                if PHA1file[i].name=='SPECTRUM':
                    my_header.set('POISSERR',False,comment="Wether the poissonian errors are appropriate")
                    my_header.set('HDUCLAS4','PHA:I',comment="Single PHA dataset")                    
                    my_header.set('STAT_ERR',0,comment="Statistical error")
                    pass
                # primary_hdr.header.set("DETNAM",detnam)
                # primary_hdr.header.set("FILTER","None")                                
                # VERSION KEYWORDS
                my_header.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
                my_header.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")            
                if i==0: my_header.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
                my_header.set('CREATOR','mkdrm_ez',comment="Software and version creating file")
                my_header.set('ORIGIN','LISOC',comment="Name of organization making file")
                
                # DATATYPE & FILETYPE (ONLY IN THE PRIMARY HEADER)
                if i==0:
                    my_header.set('DATATYPE','LLE',comment="LAT datatype used for this file")            
                    my_header.set('FILETYPE','SPECTRUM',comment="Name for this type of FITS file")    
                    pass
                # OBJECT INFO
                my_header.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
                my_header.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
                my_header.set('RADECSYS','FK5',comment='Stellar reference frame')
                my_header.set('EQUINOX',2000.0,comment='Equinox for RA and Dec')
                
                my_header.set("OBJECT",basename,comment="Object name in standard format, yymmddfff")
                
                my_header.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")
                my_header.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
                my_header.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
                
                my_header.set('TSTART',TMIN_SELECT,comment="Start Time of the selected interval relative to MJDREF, double precision")
                my_header.set('TSTOP',TMAX_SELECT,comment="End Time of the selected interval relative to MJDREF, double precision")                
                my_header.set('DATE-OBS',start_date,comment="[UTC] start date of the selected time interval")
                my_header.set('DATE-END',end_date,comment="[UTC] end date of the selected time interval")
                
                # STRING USED IN THE LLE SELECTION
                my_header.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
                my_header.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
                
                # THESE ARE COMMENTS:
                my_header.add_comment('TRIGTIME=%s' %(TRIGTIME))
                # I REMOVE THE EMPY KEYWORDS...
                try: del my_header['']
                except: pass
                pass
            
            # ###################################################
            # UPDATE THE FILE AND FIX CHECKSUM
            # ###################################################
            PHA1file.writeto(pha_file,output_verify='fix',clobber=1)
            os.system('fchecksum %s update=yes' % pha_file)
            pass
        pass        
    
    ReadmeFilename       = os.path.join(_directory,"README.txt")            
    from Readme import ReadmeFile
    readme=ReadmeFile(ReadmeFilename)
    readme.WriteReadme()
    print '----All succesfully Done----'
