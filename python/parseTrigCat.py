#!/usr/bin/env python
import os,sys,glob,math
#from config import *
#import ROOT
import utils
import pyfits
from GTGRB import genutils
import LLEutils 
#ftp_base_path='ftp://legacy.gsfc.nasa.gov/fermi/data/gbm/triggers'
import makeLLE

########################################################
# Classes Definition
########################################################

class GRB:
    def __init__(self,x):
        if isinstance(x,str):
            self.fromFileName(x)
        elif isinstance(x,float) or isinstance(x,int):
            self.fromMET(x)
        elif isinstance(x,list):
            self.fromTupla(x)
        else:
            print('type not recognised:',x)
    
    def fromMET(self,MET): 
        self.fileName=None        
        self.CLASS='GRB'
        self.TriggerName = genutils.met2date(MET,opt="grbname")
        self.OBJECT=self.CLASS+self.TriggerName
        self.RA_OBJ=0
        self.DEC_OBJ=0
        self.ERR_RAD=0
        self.TRIGTIME=float(MET)
        self.LOC_SRC=''
        self.simple_filename=None
        self.FT2=None
        self.theta=None
        pass    
    
    def fromFileName(self,fileName):
        self.fileName=fileName
        self.CLASS,self.OBJECT,self.RA_OBJ,self.DEC_OBJ,self.ERR_RAD,self.TRIGTIME,self.LOC_SRC=makeLLE.ParseTrigCatFile(fileName)
        self.TriggerName = fileName.split('glg_tcat_all_')[1].split('_')[0].replace('*.fit','').replace('bn','')
        self.simple_filename=fileName[fileName.rfind('/')+1:]
        self.FT2=None
        self.theta=None
        pass

    def fromTupla(self,myObject):
        self.fileName=None
        self.RA_OBJ      = myObject[1] 
        self.DEC_OBJ     = myObject[2] 
        self.ERR_RAD     = myObject[3] 
        self.TRIGTIME    = myObject[0]
        self.LOC_SRC     = 'XXX'
        self.CLASS       = myObject[6]
        self.TriggerName = genutils.met2date(self.TRIGTIME,opt="grbname")
        self.OBJECT=self.CLASS+self.TriggerName
        self.simple_filename=None
        self.FT2=None                                                                                                                                                                                                                     
        self.theta=None 

    def getTupla(self):
        return self.TriggerName,self.CLASS,self.OBJECT,self.RA_OBJ,self.DEC_OBJ,self.ERR_RAD,self.TRIGTIME,self.LOC_SRC

    def getFT2(self):
        if self.FT2 is None: self.FT2=makeLLE.GetFT2(self.TRIGTIME)
        return self.FT2

    def getTheta(self):
        if self.theta is None:  self.theta=makeLLE.GetTheta(self.getFT2(),self.TRIGTIME,self.RA_OBJ,self.DEC_OBJ)
        return self.theta
    
    def getDate(self):
        dt=utils.computeDate(self.TRIGTIME)
        return dt.isoformat()
    
    pass
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
    try:    print "GPL_DEBUG = ",os.environ['GPL_DEBUG']
    except: pass    
    execfile(GPL2+'/python/GPLinit.py')
    from GPL import *
    
    # This configure the variables:
    GPL_GBMTRIGCATDIR = os.getenv('GPL_GBMTRIGCATDIR','/afs/slac/g/glast/groups/grb/GBM_TriggerCatalog')
    OUTPUT_NAME       = os.getenv('OUTPUT_NAME','GRBYYMMDDFFF')
    VERSION           = int(os.getenv('VERSION','0'))
    GPL2_MESSAGELVL   = os.getenv('GPL2_MESSAGELVL','DEBUG')
    GPL_DATADIR       = os.getenv('GPL_DATADIR','TEST_%(VERSION)02d' % locals())
        
    # #################################################
    TRIGTIME       = float(os.getenv('TRIGTIME','0.0'))
    # #################################################    
    # THIS GENERATE THE MC TO BE-RE-GENERATE
    GENERATE_MC       = int(os.getenv('GENERATE_MC','0'))
    # THIS FORCE THE MC TO BE-RE-GENERATE
    FORCE_MC          = int(os.getenv('FORCE_MC','0'))    
    # You can update the location...
    RA             = float(os.getenv('RA','0.0'))
    DEC            = float(os.getenv('DEC','0.0'))
    UPDATE_POSITION=   int(os.getenv('UPDATE_POSITION','0'))
    # ... and the time interval
    OFFSET            = float(os.getenv('OFFSET','0'))
    DURATION          = float(os.getenv('DURATION','0'))

    # These are instead variables that needs to be defined. Default values are provided, but they can be changed by the pipeline.    
    DT                = float(os.getenv('DT','1.0'))
    BEFORE            = float(os.getenv('BEFORE','1000.0'))
    AFTER             = float(os.getenv('AFTER','1000.0'))
    RADIUS            = float(os.getenv('RADIUS','-1'))    
    ZENITHMAX         = float(os.getenv('ZENITHMAX','90.0'))
    THETAMAX          = float(os.getenv('THETAMAX','90.0'))
    
    ###############################
    # NFS_OUT:    
    ###############################
    # DEFINING THE STAGING DIRECTORY:
    
    STAGEDIR   = '/scratch/makeLLE_%s' %(OUTPUT_NAME)
    stageSet = stageFiles.StageSet(STAGEDIR)    
    log.debug('Calling getStageDir()...')    
    stageDir = stageSet.getStageDir()
    log.info("Staging to "+stageDir)
    if GPL2_MESSAGELVL=='DEBUG':        
        for x in sorted(os.environ.keys()): print '%s=%s' %(x,os.environ[x])
        pass
    print '-----------------------------------'
    print 'GPL_GBMTRIGCATDIR...........',GPL_GBMTRIGCATDIR
    print 'OUTPUT_NAME.................',OUTPUT_NAME
    print 'VERSION.....................',VERSION
    print 'GPL_DATADIR.................',GPL_DATADIR
    print 'GENERATE_MC.................',GENERATE_MC
    print 'FORCE_MC....................',FORCE_MC
    print '-----------------------------------'
    print 'RA.........',RA
    print 'DEC........',DEC
    print 'TRIGTIME...',TRIGTIME
    print 'OFFSET.....',OFFSET
    print 'DURATION...',DURATION
    print 'DT.........',DT
    print 'BEFORE.....',BEFORE
    print 'AFTER......',AFTER
    print 'RADIUS.....',RADIUS
    print 'ZENITHMAX..',ZENITHMAX
    print 'THETAMAX ..',THETAMAX
    print '-----------------------------------'

    TRIGGER_NAME = OUTPUT_NAME[-9:] #genutils.met2date(TRIGTIME,opt="grbname")
    CLASS        = OUTPUT_NAME[:-9]

    results={}    
    OUTPUT_DIR  = '%s/%s/v%02d' %(GPL_DATADIR,OUTPUT_NAME,VERSION)
    LLE_RESULTS = '%(OUTPUT_DIR)s/gll_results_bn%(TRIGGER_NAME)s_v%(VERSION)02d.txt' % locals()
    
    ##################################################
    # OUTFILES:
    FT2_FILE     = '%s/gll_pt_bn%s_v%02d.fit' %(OUTPUT_DIR,TRIGGER_NAME,VERSION)
    FT2_FILE_NAME= 'gll_pt_bn%s_v%02d.fit' %(TRIGGER_NAME,VERSION)
    ##################################################
    
    log.debug("Calling stageOut for "+LLE_RESULTS)        
    LLE_RESULTS_staged = stageSet.stageOut(LLE_RESULTS)
    log.debug("Calling stageOut for "+FT2_FILE)                
    FT2_FILE_staged    = stageSet.stageOut(FT2_FILE)
    
    ft2_1 = makeLLE.GetFT2(TRIGTIME)
    THETA = makeLLE.GetTheta(ft2_1,TRIGTIME,RA,DEC)
    
    os.system('cp %s %s' %(ft2_1,FT2_FILE_staged))

    ft2filefits = pyfits.open(FT2_FILE_staged,mode="update")
    my_header   = ft2filefits[0].header
    my_header.set('FILENAME',FT2_FILE_NAME,comment='Name of the file')
    my_header.set('VERSION', VERSION,comment="Version of the file")
    my_header.set('CREATOR','GLAST Data Portal',comment="Creator")
    my_header.set('SOFTWARE','2.6.0',comment="Version of software")

    ft2filefits.writeto(FT2_FILE_staged,output_verify='fix',clobber=1)    

    os.system('fchecksum %s update=yes' % FT2_FILE_staged)
    
    # WRITE THE RESULT FILE:

    # DIRECTORY DEFINITION:
    results['LLE_RESULTS'] = LLE_RESULTS    
    results['OUTPUT_DIR']  = OUTPUT_DIR
    results['OUTPUT_NAME'] = OUTPUT_NAME
    results['VERSION']     = VERSION
    results['FT2']         = FT2_FILE
    
    # RELATED TO THE TRIGGER_NAME:
    results['TRIGGER_NAME'] = TRIGGER_NAME #YYMMDDFFF
    results['CLASS']        = CLASS
    results['OBJECT']       = OUTPUT_NAME
    results['RA']           = RA
    results['DEC']          = DEC
    results['UPDATE_POSITION'] = UPDATE_POSITION
    results['THETA']        = THETA
    results['TRIGTIME']     = TRIGTIME

    # INITIAL CONFIGURATION
    results['DURATION']     = DURATION
    results['OFFSET']       = OFFSET
    results['DT']           = DT
    results['BEFORE']       = BEFORE
    results['AFTER ']       = AFTER
    results['RADIUS ']      = RADIUS
    results['ZENITHMAX']    = ZENITHMAX
    results['THETAMAX']     = THETAMAX
    # #################################################
    
    res_dic = LLEutils.ResultFile(LLE_RESULTS_staged)
    res_dic.set(results)
    
    if GPL2_MESSAGELVL=='DEBUG': res_dic.Print()
    res_dic.save()

    log.debug('About to list stageDir...')
    stageSet.listStageDir()
    
    log.debug('Calling stageSet.finish(alldone)...')
    stagerc = stageSet.finish("alldone")
    log.info('Return from stageSet.finish = '+str(stagerc))
    
    pass

