#!/bin/bash 
echo running the wrapper $GPL_CONFIGDIR
source ${GPL_TASKROOT}/config/setup_gtgrb.sh
$GPL_CONFIGDIR/configureMC.py
