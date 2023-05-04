#!/usr/bin/env python
import os,sys,glob,math
import utils
import pyfits
import config
import LLEutils 
import makeLLE
import ROOT

########################################################
# Classes Definition
########################################################

def CreateXMLSource(name,ra,dec,idx,flux):
    _xml  = os.getenv('GPL_MCTASKROOT','/nfs/farm/g/glast/u26/MC-tasks/makeLLE-P8/PointSourceSimulator-P8')+'/config/xml'
    txt='''<!-- ************************************************************************** -->
    <source_library title="GRBSimulator Library">    
    <!-- E^-%s spectrum from 10 MeV to 100 GeV from a point source (%s)-->
    <source name="GRBSOURCE" flux="%.3e">
        <spectrum escale="GeV">
            <particle name="gamma">
                <power_law emin="0.01" emax="10.0" gamma="%s"/>
            </particle>
            <celestial_dir ra="%s" dec="%s"/>
        </spectrum>
     </source>
     </source_library>
     ''' %(idx,name,flux, idx, ra,dec)
    fileName = '%s/%s.xml' % (_xml,name)
    fout     = file(fileName,'w')
    fout.write(txt)
    fout.close()
    return fileName
########################################################
if __name__=='__main__':
    ###############################
    # SETUP THE GPLTools:
    mode='forReal'
    try:     GPL = os.environ['GPL_SCRIPTS']
    except:  GPL = "/afs/slac.stanford.edu/g/glast/ground/PipelineConfig/GPL/python"        
    print "GPL = ",GPL
    sys.path.insert(0, GPL)
    from floop import *    
    # All-important check that we are running an adequate version of python
    print "Check we're running adequate version of python...\n"
    floop()    
    # Second, is the location of GPLtools package
    ## See if GPLtools location defined by taskConfig.xml
    try:    GPL2 = os.environ['GPL2']
    except: GPL2 = "/afs/slac.stanford.edu/g/glast/ground/PipelineConfig/GPLtools/prod/"
    os.environ['GPL2']=GPL2    
    print "GPL2 = ",GPL2
    execfile(GPL2+'/python/GPLinit.py')
    from GPL import *
        
    ###############################
    # DEFINING THE STAGING DIRECTORY:
    OUTPUT_NAME       = os.getenv('OUTPUT_NAME','GRBYYMMDDFFF')
    VERSION           = int(os.getenv('VERSION','0'))
    GPL_DATADIR       = os.getenv('GPL_DATADIR','TEST_%(VERSION)02d' % locals())    
    
    OUTPUT_DIR  = '%s/%s/v%02d' %(GPL_DATADIR,OUTPUT_NAME,VERSION)
    TRIGGER_NAME=OUTPUT_NAME[-9:]
    LLE_RESULTS = '%(OUTPUT_DIR)s/gll_results_bn%(TRIGGER_NAME)s_v%(VERSION)02d.txt' % locals()
    print 'LLE_RESULTS = ',LLE_RESULTS


    GPL2_MESSAGELVL   = os.getenv('GPL2_MESSAGELVL','DEBUG')
    
    if GPL2_MESSAGELVL=='DEBUG':
        for x in sorted(os.environ.keys()): print '%s=%s' %(x,os.environ[x])        
        pass
    
    ###############################
    # READ THE RESULT FILE:
    res = LLEutils.ResultFile(LLE_RESULTS)
    
    print 'LLE_RESULTS file: %s' % LLE_RESULTS
    if GPL2_MESSAGELVL=='DEBUG': res.Print()
    resd = res.get()
    
    OUTPUT_DIR   = resd['OUTPUT_DIR']    
    version      = int(resd['VERSION'])
    OBJECT       = resd['OBJECT']
    TRIGGER_NAME = resd['TRIGGER_NAME']    
    TRIGTIME     = float(resd['TRIGTIME'])
    RA           = float(resd['RA'])
    DEC          = float(resd['DEC'])
    DURATION     = float(resd['DURATION'])
    OFFSET       = float(resd['OFFSET'])
    DT           = float(resd['DT'])
    BEFORE       = float(resd['BEFORE'])
    AFTER        = float(resd['AFTER'])
    RADIUS       = float(resd['RADIUS'])
    ZENITHMAX    = float(resd['ZENITHMAX'])
    THETAMAX     = float(resd['THETAMAX'])
    FT2          = resd['FT2']

    DETECTED      = int(resd['DETECTED'])
    DETECT_TFIRST = float(resd['DETECT_TFIRST'])
    DETECT_TLAST  = float(resd['DETECT_TLAST'])

    # THIS IS AN OVERWRITE
    if DURATION>0:
        DETECT_TFIRST=OFFSET
        DETECT_TLAST =DURATION+OFFSET
        DETECTED=1
        pass

    MC_GENERATE = int(os.getenv('MC_GENERATE','1'))
    LLEVERSION  = os.getenv('LLEVERSION','v00')
    
    MCINPUTFILE = '%(OUTPUT_DIR)s/MCConfig_bn%(TRIGGER_NAME)s_v%(version)02d.txt'% locals()
    MCCONFIGFILE= MCINPUTFILE.replace('.txt','_runConfig.txt')
    for x in (MCINPUTFILE,MCCONFIGFILE):
        if os.path.exists(x): os.system('rm %s' % x)
        pass

    if MC_GENERATE and DETECTED:        
        print 'configureMC.py :  MC WILL BE CREATED WITH THIS VERSION...: %s' % LLEVERSION
        if not os.path.exists(FT2):
            print 'FT2 Does not exist!'
            exit()
            pass
        GRBNAME     = OBJECT
        MC_MET      = TRIGTIME+DETECT_TFIRST
        MC_DURATION = (DETECT_TLAST-DETECT_TFIRST)
        NGEN = 10000
        IDX  = 1
        FLUX = NGEN/6.0/MC_DURATION
        print ' NGEN = %s, DURATION = %s, FLUX = %.3e ' %(NGEN,MC_DURATION,FLUX)        
        print '--------------------------------------------------: Generation of the TEXT file to be used in the generation of LLE Montecarlo DATA'
        txt = "# Configuration file for %s\n" % GRBNAME
        txt+="NAME                      = '%s'\n" % GRBNAME
        txt+="DURATION                  = %.2f\n" % (MC_DURATION)
        txt+="MET                       = %.4f\n" % (MC_MET)
        txt+="RA                        = %.4f\n" % RA
        txt+="DEC                       = %.4f\n" % DEC
        fout=file(MCINPUTFILE,'w')
        fout.write(txt)
        fout.close()
        print '==> MC INPUT FILE SAVED IN: %s' % MCINPUTFILE
        print txt
        res.setv('MCINPUTFILE',MCINPUTFILE)
        # 3 THESE VARIABLES ARE USED IN THE TASK:
        # THEY ARE SAVED INTO A FILE AND THEN READ
        fout = file(MCCONFIGFILE,'w' )
        fout.write('OUTPUT_NAME = %s\n' % GRBNAME)
        fout.write('POINTING_HISTORY_FILE = %s\n' % FT2)
        fout.write('LLEVERSION = %s\n' % LLEVERSION)
        fout.write('startTime = %s,%s\n' % (MC_MET,MC_DURATION))
        fout.write('XML_SRC_LIBRARY = %s\n' % CreateXMLSource(GRBNAME,RA,DEC,IDX,FLUX))
        fout.close()
        print '==> MC CONFIG FILE SAVED IN: %s' % MCCONFIGFILE
        res.setv('MCCONFIGFILE',MCCONFIGFILE)
        res.save()
        res.Print()
        pass
    print '--------------------------------------------------'
    print ' CONFIGURE MC ENDED'
    print '--------------------------------------------------'
    pass
