#!/usr/bin/env python
import os,sys,glob,math
import utils
import pyfits
import config
import LLEutils 
#ftp_base_path='ftp://legacy.gsfc.nasa.gov/fermi/data/gbm/triggers'
import makeLLE

########################################################
# Classes Definition
########################################################

########################################################
if __name__=='__main__':
    ###############################
    # SETUP THE GPLTools:    
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
    
    LLEIFILE          = os.getenv('LLEIFILE','/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-10-00-02/makeLLEproducts/python/config_LLE_DRM/Pass7.txt')
    MCBASEDIR         = os.getenv('MCBASEDIR','/MC-Tasks/ServiceChallenge/GRBSimulator-Pass7')

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
    myMode       = 'pha'

    if DURATION==0: DURATION=100
    
    # ##################################################
    # DEFINING THE STAGING DIRECTORY:
    # ##################################################
    
    STAGEDIR   = '/scratch/generateLLE_%s' %(OBJECT)
    #  STAGING THE FILES...
    stageSet = stageFiles.StageSet(STAGEDIR)    
    log.debug('Calling getStageDir()...')
    stageDir = stageSet.getStageDir()
    log.info("Staging to "+stageDir)

    #STAGE IN:        
    log.debug("STAGE IN...")
    FT2_s = stageSet.stageIn(FT2)

    # STAGE OUT:
    log.debug("STAGE OUT...")
    stageSet.stageOut('%(OUTPUT_DIR)s/README.txt'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.pha'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.root'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.txt'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_lle_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_pha_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_quick_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/gll_selected_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/meritList.txt'% locals())
    stageSet.stageOut('%(OUTPUT_DIR)s/meritList3.txt'% locals()) # this is a fake!
    
    cmd='python -m mkdrm_ez -i %(LLEIFILE)s -ft2 %(FT2_s)s -outdir %(STAGEDIR)s/ -v %(VERSION)d ' %locals()
    cmd+='-mcbase %(MCBASEDIR)s ' % locals()
    cmd+='-ra %(RA).4f -dec %(DEC).4f -n %(OBJECT)s -t %(TRIGTIME).4f -d %(DURATION).1f -off %(OFFSET)s -dt %(DT)s -b %(BEFORE)s -a %(AFTER)s -r %(RADIUS)s -zenith %(ZENITHMAX)s -theta %(THETAMAX)d -m %(myMode)s' % locals()    
    log.info('Now calling:'+cmd)
    os.system(cmd)    
    os.system('pwd')
    
    log.debug('About to list stageDir...')
    stageSet.listStageDir()
    stagerc = stageSet.finish("alldone")      
    log.info('Return from stageSet.finish = '+str(stagerc))        
    pass
