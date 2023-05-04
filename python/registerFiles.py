import os

##################################################
#               CLASS DEFINITION                 #
##################################################

class ResultFile:

    def __init__(self,fileName):
        self.fn=fileName
        self.d=self.get()
        pass
    
    def get(self):
        self.d={}
        if not os.path.exists(self.fn): return self.d
        lines=file(self.fn,'r').readlines()
        for l in lines:
            if '#' in l: continue
            nv=l.split(':=')
            n=nv[0].strip()
            #try: v=float(nv[1].strip())
            v=nv[1].strip()
            self.d[n]=v
            pass        
        return self.d
    
    def setv(self,n,v):
        self.d[n]=v
        pass
    
    def set(self,d):
        for x in d.keys(): self.d[x]=d[x]
        pass
    
    def save(self):
        fo=file(self.fn,'w')
        for k in self.d.keys(): fo.write('%s:=%s\n' %(k,self.d[k]))
        fo.close()
        pass

    def Print(self):
        print 100*'-'
        for k in self.d.keys(): print '%s:=%s' %(k,self.d[k])
        print 100*'-'
        pass
    pass
##################################################

print '--- Registering datafiles into the datacatalog ---'

OUTPUT_DIR  = '%s/%s/v%02d' %(GPL_DATADIR,OUTPUT_NAME,VERSION)
TRIGGER_NAME=OUTPUT_NAME[-9:]
LLE_RESULTS = '%(OUTPUT_DIR)s/gll_results_bn%(TRIGGER_NAME)s_v%(VERSION)02d.txt' % locals()
print 'LLE_RESULTS = ',LLE_RESULTS


###############################
# READ THE RESULT FILE:
res = ResultFile(LLE_RESULTS)

print 'LLE_RESULTS file: %s' % LLE_RESULTS   
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

attributes = ':'.join([
    "sOBJECT=%s"    % OBJECT,
    "nMetTrigger=%.4f"% TRIGTIME,
    "nOFFSET=%.3f"    % OFFSET,
    "nDURATION=%.3f"  % DURATION,
    "nRA=%.3f"      % RA,
    "nDEC=%.3f"     % DEC,
    "nDetected=%d"  % DETECTED,
    "nVersion=%02d" % version
    ])


#from java.util import HashMap
attributes = {"sOBJECT":"%s"    % OBJECT,
              "nMetTrigger":"%.4f"% TRIGTIME,
              "nOFFSET":"%.3f"    % OFFSET,
              "nDURATION":"%.3f"  % DURATION,
              "nRA":"%.3f"      % RA,
              "nDEC":"%.3f"     % DEC,
              "nDetected":"%d"  % DETECTED,
              "nVersion":"%02d" % version
              }

FILE_TO_REGISTER={'%(OUTPUT_DIR)s/README.txt' % locals():['LLE_README','txt'],
                  LLE_RESULTS:['LLE_RESULTS','txt'],
                  '%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.pha'% locals():['LLE_CSPECPHA','fits'],
                  '%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals() :['LLE_CSPECPNG','png'],
                  '%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.root'% locals() :['LLE_CSPECROOT','root'],
                  '%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.txt'% locals() :['LLE_CSPECTXT','txt'],
                  '%(OUTPUT_DIR)s/gll_lle_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals() :['LLE_EVENTS','fits'],
                  '%(OUTPUT_DIR)s/gll_pha_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals() :['LLE_PHA','fits'],
                  '%(OUTPUT_DIR)s/gll_quick_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals() :['LLE_QUICK','png'],
                  '%(OUTPUT_DIR)s/gll_detect_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals() :['LLE_DETECT','png'],
                  '%(OUTPUT_DIR)s/gll_selected_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals() :['LLE_EVENTSSEL','fits'],
                  '%(OUTPUT_DIR)s/meritList.txt'% locals() :['LLE_MERITLIST','txt'],
                  '%(OUTPUT_DIR)s/MCConfig_bn%(TRIGGER_NAME)s_v%(version)02d.txt'% locals() :['LLE_MCCONFIG','txt'],
                  '%(OUTPUT_DIR)s/gll_cspec_bn%(TRIGGER_NAME)s_v%(version)02d.rsp'% locals()  :['LLE_CSPECRSP','fits'], # DRM
                  '%(OUTPUT_DIR)s/gll_DRM_bn%(TRIGGER_NAME)s_v%(version)02d.root'% locals()   :['LLE_DRMROOT','root'], # DRM
                  '%(OUTPUT_DIR)s/gll_edisp_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals()  :['LLE_EDISP','png'], # DRM
                  '%(OUTPUT_DIR)s/gll_effarea_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals():['LLE_EFFAREA','png'], # DRM
                  '%(OUTPUT_DIR)s/gll_mcvar_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals()  :['LLE_MCVAR','png'],
                  '%(OUTPUT_DIR)s/gll_pt_bn%(TRIGGER_NAME)s_v%(version)02d.fit' % locals():['FT2SECONDS','fits'],
                  '%(OUTPUT_DIR)s/gll_bn%(TRIGGER_NAME)s_v%(version)02d.tgz' % locals():['LLE_TGZ','tgz']
                  } # DRM


DATACATALOG_DIRECTORY = '/LLE'

print 'OUTPUT_DIR..............:',OUTPUT_DIR
print 'LLE_RESULTS.............:',LLE_RESULTS
print 'DATACATALOG_DIRECTORY...:',DATACATALOG_DIRECTORY
print 'ATTRIBUTES..............:',attributes

fileName=OBJECT

for SOURCE in FILE_TO_REGISTER.keys():
    if os.path.exists(SOURCE):
        FILE_TYPE  = FILE_TO_REGISTER[SOURCE][0]
        #fileName  = SOURCE.replace('%s/' % OUTPUT_DIR,'').split('.')[0]
        DCLOCATION = DATACATALOG_DIRECTORY + '/' + FILE_TO_REGISTER[SOURCE][0] + ':' + fileName

        print '('+fileName+'):'+SOURCE+' => '+DCLOCATION        
        dsNew = datacatalog.newDataset(fileName, FILE_TO_REGISTER[SOURCE][1], FILE_TYPE, DATACATALOG_DIRECTORY, FILE_TO_REGISTER[SOURCE][0], 'SLAC', SOURCE)        
        NewVersion = version #datacatalog.getDatasetLatestVersion(fileName, DATACATALOG_DIRECTORY, FILE_TO_REGISTER[SOURCE][0])+1
        dsNew.setVersionID(NewVersion)
        try:
            ds = datacatalog.registerDataset(dsNew, attributes);
            print '*** Registration SUCEESS ***'
        except:
            print '*** Registration FAILED ***'
        #ds = datacatalog.registerDataset(FILE_TYPE,DCLOCATION,SOURCE,attributes)
        pass
    else:        print '%s Does NOT exist!' %(SOURCE)
    pass
pass




