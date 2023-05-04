#! /usr/bin/env python
import sys,os
if __name__=='__main__':
    
    filename = sys.argv[1]
    
    # Vela new MC 2820 files. Old: 1000 files
    nDRMjobs    = 1#60
    DRM_files   = 1000#47
    
    # Vela LLE data: 5480 files
    nPHA2jobs    = 137
    PHA2_files   = 40
    
    _queue='long'
    ##################################################
    # GENERATION OF THE DRM
    ##################################################
    log_drm2 = filename.replace('.txt','_drm.log')
    os.environ['NAllGammaFiles'] = '%d' % DRM_files
    os.environ['NGEN']           = '%i' % (10000*nDRMjobs)

    for i in range(nDRMjobs):        
        inFile = filename.replace('.txt','_%04d_drm.txt' % i)
        os.system('cp %s %s' %(filename,inFile))
        os.environ['FirstFile']  = '%d' % (DRM_files * i)
        cmd = 'bsub -q %s -o %s ./mkdrm.py %s  drm  ' %(_queue,inFile.replace('.txt','.log'),inFile)
        os.system(cmd)
        pass
    
    ##################################################
    # GENERATION OF THE PHA2
    ##################################################
    log_pha2 = filename.replace('.txt','_pha2.log')
    
    os.environ['NDATAFILES'] = '%d' % PHA2_files
    
    for i in range(nPHA2jobs):        
        inFile = filename.replace('.txt','_%04d_pha2.txt' % i)
        os.system('cp %s %s' %(filename,inFile))
        os.environ['NDATAFIRST'] = '%d' % (PHA2_files * i)
        cmd = 'bsub -q %s -o %s ./mkdrm.py %s  pha2 ' %(_queue,inFile.replace('.txt','.log'),inFile)
        os.system(cmd)
        pass

    print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
    print 'WHEN JOBS ARE DONE, EXECUTE THE FOLLOWING COMMAND:'
    print './makeOnlyFits.py %s LLE_z105 <name_selection>' % filename
    print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'    
    pass
