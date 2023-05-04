#! /usr/bin/env python

import subprocess
from ROOT import std

def find_merit_files(trigger, base='/Data/Flight/Level1/LPA/',dt=(-100, 1000)):
    print '--------------------------------------------------'
    print 'looking for merit from %i to %i (t0=%i)' % (dt[0],dt[1],trigger)
    tmin = trigger + dt[0]
    tmax = trigger + dt[1]
    opt1 = '(%(tmin)i <= nMetStart && nMetStop <= %(tmax)i)' % locals()
    opt2 = '(nMetStart <= %(tmin)i && %(tmin)i <= nMetStop)' % locals()
    opt3 = '(nMetStart <= %(tmax)i && %(tmax)i <= nMetStop)' % locals()
    
    command_tpl = " ".join(("/afs/slac/g/glast/ground/bin/datacat find",
                            "\--filter '%s || %s || %s'",
                            "\--sort nMetStart \--group MERIT",
                            "\--site SLAC_XROOT %s"))
    
    command = command_tpl % (opt1, opt2, opt3, base)
    print command
    pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = pipe.stdout
    files = []
    for item in output: files.append(item.strip())
    if len(files)<10: print files
    print '==> %i files found' % len(files)
    return sorted(files)

def getVersion(base,filename):
    subdir=base.split('/')[-1]
    #version=filename.split(subdir)[1].split('merit')[0].replace('/','').replace('v','')
    try:    version=int(filename.split('-merit_v')[-1].replace('.root',''))        
    except: version=-1
    return version
    
def find_MC_files(name,base='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass7',version=None,maximum=10000):
    command_tpl = " ".join(("/afs/slac/g/glast/ground/bin/datacat find",
                            "\--group merit",
                            "\--site SLAC_XROOT %s/%s"))
    command = command_tpl % (base,name)
    if 'Pass6v3' in base: command+='/runs'
    print command
    pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = pipe.stdout    
    files0    = []
    versions = {}
    subdir=base.split('/')[-1]
    #1 get everything
    for item in sorted(output):
        oneFile = item.strip()
        vers    = getVersion(base,oneFile) #.split(subdir)[1].split('merit')[0].replace('/','')        
        if vers>=-1:
            files0.append(oneFile)
            versions[vers]=1
            pass
        pass
    # Did you find any files?
    if len(files0)==0: return files0    
    
    # look for the versions
    if version is None: version=sorted(versions.keys())[-1] # that's the latest
    print '-------------------------------------------------'
    print ' I have found the following versions: '
    print versions
    print ' Selected version: ', version
    files=[]
    # select only the selected...
    n=0
    for oneFile in sorted(files0):
        if n>=maximum: break
        if ('v%02d' % version) in oneFile or version==-1:
            files.append(oneFile)
            n+=1
            pass
        pass
    print ' Selected %d files' % len(files)
    print '-------------------------------------------------'        
    return sorted(files)





if __name__=='__main__':
    import sys
    arg = None
    find_mc=0
    time=1000
    base='Pass7'
    version=None
    for i,a in enumerate(sys.argv):
        if a =='-g':
            arg=sys.argv[i+1]
            find_mc=1
            pass
        if a=='-t': arg=float(sys.argv[i+1])
        if a=='-i': time=float(sys.argv[i+1])
        if a=='-b': base=sys.argv[i+1]
        if a=='-v': version=sys.argv[i+1]        
        pass
    
    if base=='Pass6v3': dcbase='/Data/Flight/Level1/LPA/'
    elif base=='Pass7': dcbase='/Data/Flight/Reprocess/P202/'

    mcbase='/MC-Tasks/ServiceChallenge/GRBSimulator-%s' % base
    
    meritfiles=[]
    
    if find_mc==0:
        meritfiles = find_merit_files(arg,dcbase,(-time,time))
    else:        
        print 'Looking for MC file in %s' %mcbase
        meritfiles = find_MC_files(arg,mcbase)
        pass
    
    if len(meritfiles)>0:  print 'found %d files:\n[%s...%s]' %(len(meritfiles),meritfiles[0],meritfiles[-1])
    else: print 'No file found!'
    pass
