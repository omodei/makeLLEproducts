#!/usr/bin/env python
import os,sys,glob,math
import LLEutils

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
    
    log.info('LLE_RESULTS file: %s' % LLE_RESULTS)    
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
    
    DETECTED      = int(resd['DETECTED'])
    DETECT_TFIRST = float(resd['DETECT_TFIRST'])
    DETECT_TLAST  = float(resd['DETECT_TLAST'])
    
    if DETECTED:
        DURATION      = DETECT_TLAST-DETECT_TFIRST
        OFFSET        = DETECT_TFIRST
        pass

       
    FILE_TO_ZIP=['README.txt' % locals(),
                 #'gll_results_bn%(TRIGGER_NAME)s_v%(version)02d.txt' % locals(),
                 'gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.pha'% locals(),
                 'gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals() ,
                 #'gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.root'% locals() ,
                 #'gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.txt'% locals() ,
                 'gll_lle_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals() ,
                 'gll_pha_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals() ,
                 'gll_quick_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals() ,
                 'gll_selected_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals() ,
                 'gll_pt_bn%(TRIGGER_NAME)s_v%(version)02d.fit' % locals(),                 
                 #'meritList.txt'% locals() ,
                 'gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.rsp'% locals() , # DRM
                 #'gll_DRM_bn%(TRIGGER_NAME)s_v%(version)02d.root'% locals() , # DRM
                 'gll_edisp_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals() , # DRM
                 'gll_effarea_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals() , # DRM
                 'gll_mcvar_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals()] # DRM
    
    archived = 'gll_bn%(TRIGGER_NAME)s_v%(version)02d.tgz' % locals()
    os.chdir('%(OUTPUT_DIR)s' % locals())
    
    cmd='tar zcvf %s ' % archived    
    for x in FILE_TO_ZIP:
        if os.path.exists(x): cmd+='%s '% x
        pass
    print cmd
    os.system(cmd)
    pass
##################################################

