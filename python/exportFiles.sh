#!/bin/bash 
echo running the wrapper $GPL_CONFIGDIR
source ${GPL_TASKROOT}/config/setup_gtgrb.sh
#OVERWRITE PYTHION PATH:
export PYTHONPATH=/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/python:/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/python/app:/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/python/GtBurst:/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/python/GtBurst/scripts:/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/lib/redhat6-x86_64-64bit-gcc44-Optimized

$GPL_CONFIGDIR/exportFiles.py
