#!/bin/bash -e
echo setting up the environment... GPL_TASKROOT=$GPL_TASKROOT
source ${GPL_TASKROOT}/config/setup_gtgrb.sh
echo running the wrapper $GPL_CONFIGDIR
#set -e
$GPL_CONFIGDIR/generateLLE.py
