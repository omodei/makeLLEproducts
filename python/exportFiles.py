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
    TRIGGER_NAME = resd['TRIGGER_NAME']
    DETECTED     = int(resd['DETECTED'])
    DURATION     = float(resd['DURATION'])
    
    if DURATION>0: DETECTED=1
    
    FILE_TO_EXPORT=['%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.pha'% locals(),
                    '%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals(),
                    '%(OUTPUT_DIR)s/gll_lle_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals(),
                    '%(OUTPUT_DIR)s/gll_pha_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals(),
                    '%(OUTPUT_DIR)s/gll_quick_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals(),
                    '%(OUTPUT_DIR)s/gll_selected_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals(),
                    '%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.rsp'% locals(),   # DRM
                    '%(OUTPUT_DIR)s/gll_edisp_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals(),   # DRM
                    '%(OUTPUT_DIR)s/gll_effarea_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals(), # DRM
                    '%(OUTPUT_DIR)s/gll_mcvar_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals(),   # DRM
                    '%(OUTPUT_DIR)s/gll_pt_bn%(TRIGGER_NAME)s_v%(version)02d.fit' % locals()      # FT2 1 second
                    ]
    
    EXPORT_TRUE = int(os.getenv('GPL_EXPORTFILE','0'))
    EXPORT_TRUE = 0 # 0 OR 1
    if not EXPORT_TRUE:  log.info('EXPORT_TRUE IS SET TO FALSE!')
    
    if DETECTED:
        ISOC_ENV = "eval `/afs/slac/g/glast/isoc/flightOps/rhel6_gcc44/ISOC_PROD/bin/isoc env --add-env=flightops`; "
        FC_COMMAND = ISOC_ENV + "cd /scratch/; FASTCopy.py --send GSSC" #LISOC " #GSSC
        for FILE in FILE_TO_EXPORT:
            print 'FILE %s added to the export package' % FILE
            FC_COMMAND = FC_COMMAND + " " + FILE
            pass
        print 'NOW EXECUTE : %s' % FC_COMMAND 
        if EXPORT_TRUE: os.system(FC_COMMAND)
        pass
    else:
        log.info('NO FILE TO EXPORT')
        pass
    print 'DONE'
    pass
##################################################

