#!/usr/bin/env python

import os,sys


def LLE_Post (GRBname):
    #print sys.argv
    #filename= sys.argv[1]
    filename = GRBname
    fileIn = file(filename,'r')
    lines = fileIn.readlines()
    #print lines
    parameters={}
    for l in lines:
        if '#' not in l:            
            try:
                name=l.split(':=')[0].strip()
                try:
                    value = float(l.split(':=')[1].strip())
                    pass
                except:
                    value = l.split(':=')[1].strip()
                    pass            
                parameters[name]=value
               # print name, value
            except:
                pass
            pass
        pass
    
    NAllGammaFiles = int(parameters['NAllGammaFiles'])
    basename = parameters['basename']
    FirstFile = int(parameters['FirstFile'])
    MYCUT = parameters['MYCUT']
    DATAFILESBASE = parameters['DATAFILESBASE']
    RADIUS_ROI = parameters['RADIUS_ROI']
    DETNAM = parameters['DETNAM']
    
    Post = open ("ConfluencePost_%s" % filename , "w")
   
    print >> Post, ' '
    print >> Post, 'The data are in:'
    print >> Post, '{code}'
    print >> Post, ' %s ' % DATAFILESBASE
    print >> Post, '{code}'
    print >> Post, ' '
    print >> Post, ' '
    print >> Post, ' '
    print >> Post, 'The Monte Carlo used is:'
    print >> Post, '{code}'
    print >> Post, ' %s'% basename
    print >> Post, '{code}'
    print >> Post, ' '
    print >> Post, '%s files are used, and the first file is the number %s (so the first value that the number in the line written above should assume is %s)' % (NAllGammaFiles, FirstFile, FirstFile)
    print >> Post, ' '
    print >> Post, ' '
    print >> Post, ' '
    print >> Post, 'pha2 file and DRM are computed.'
    print >> Post, ' '
    print >> Post, 'The LLE cut used is:'
    print >> Post, '%s' % MYCUT
    print >> Post, ' '
    
    if RADIUS_ROI<0.:
        print >> Post, 'The cut on the Region-Of-Interest used here is an ROI(E) depending on the energy of the events, according to the PSF.'
    else:
        print >> Post, 'The cut on the Region-Of-Intrest used here is ROI = %s' %RADIUS_ROI
        pass

    
    print >> Post, ' '
    print >> Post, 'pha2 file: [^pha2_%s.fit]' % DETNAM

    print >> Post, ' '
    print >> Post, 'DRM :[^LATDRM_%s.rsp]' % DETNAM

    print >> Post, ' '
    print >> Post, ' '
    print >> Post, ' '
    
    print >> Post, 'You can find the trigger time and the RA and DEC coordinates of the burst in the following .txt file:'
    print >> Post, '[%s]' % filename
    print >> Post, ' '
    
    Post.close()


if __name__=='__main__':

    LLE_Post (sys.argv[1])

    print 'All Done!'
