# -*- python -*-
# $Id: SConscript,v 1.17 2014/08/27 18:23:20 omodei Exp $
# Authors: Giacomo Vianello <giacomov@slac.stanford.edu>,Nicola Omodei <omodei@slac.stanford.edu>
# Version: makeLLEproducts-01-06-03

Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()
##libEnv  = baseEnv.Clone()

# Uncomment to install python files.  Replace
# listFiles(['.. with an actual list to only install
# some of the files
progEnv.Tool('registerTargets', package = 'makeLLEproducts',
             python = listFiles(['python/*.py',\
                                 'python/config_LLE_DRM/DefaultLLE.txt']))

