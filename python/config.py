#!/usr/bin/env python
import os

try:                        ## See if GPLtools location defined by taskConfig.xml
    GPL2 = os.environ['GPL2']
except:
    GPL2 = "/afs/slac.stanford.edu/g/glast/ground/PipelineConfig/GPLtools/prod/"
    os.environ['GPL2']=GPL2
    pass

print "GPL2 = ",GPL2
try:
    print "GPL_DEBUG = ",os.environ['GPL_DEBUG']
except:
    pass

execfile(GPL2+'/python/GPLinit.py')
from GPL import *
setup_gtgrb_rc = 0
GPL_CONFIGDIR = os.environ['GPL_CONFIGDIR']
setup_gtgrb = "%s/setup_gtgrb.sh" % GPL_CONFIGDIR
setup_gtgrb_rc = runner.run(setup_gtgrb)
log.info("Return from wrapper script, rc = "+str(setup_gtgrb_rc))
INST_DIR= os.environ['INST_DIR']
log.info("INST_DIR=%s" % INST_DIR)


#pars={'OFFSET'   : 0.0,
#      'DT'       : 1.0,
#      'ZENITHMAX': 90,
#      'THETAMAX' : 90,
#      'BEFORE'   : 300,
#      'AFTER'    : 600,
#      'NSIGMA'   : 4.0,
#      'THETA_MIN': 89
#      }

# DIRECTORIES:
#outputDir            = 'GBM_TriggerCatalog'
#dirMCGenerated       = 'Generated'
#dirMCToGenerateFiles = 'ToGenerate'

