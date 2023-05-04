#!/usr/bin/env python
from glob import glob
import sys,os

def parseFile(filename):
    vars={}
    f=file(filename,'r')
    lines=f.readlines()
    for l in lines:
        if '#' in l: continue
        try:
            name = l.split('=')[0].strip()
            var  = l.split('=')[1].strip()
            vars[name]=var
        except:
            pass
        pass
    
    return vars
        
cmd0 = './mkdrm_ez.py -i %s -ra %s -dec %s -n %s -t %s -d %s -off %s -dt %s -r %s -zenith %s -theta %s'
configFile = 'config/DefaultLLE.txt'

if __name__=='__main__':
    print ''
    pipe    = 0
    execute = 1
    fileList = glob(sys.argv[1])    
    queue = 'medium'
    try:        
        queue = sys.argv[2]
        if queue in ['short','medium','long','xlong','xxl']: pipe=1
    except:
        execute=0
        print 'USAGE:'
        print './parseConfigFiles.py \'config/GRB*\' <short|medium|long|xlong|xxl|x>'
        
        pass
    

    
    
    for f in fileList:
        vars=parseFile(f)
        #print "%s:[%s, %s, %s, %s, 0.0, 1.0, -1.0, 100, 80]," %(vars)
        name = vars['NAME']
        duration = vars['DURATION']
        trigger  = vars['MET']
        ra       = vars['RA']
        dec      = vars['DEC']
        offset   = 0.0
        dt       = 1.0
        if float(duration)<10: dt = 0.1
        
        roi      = -1.0
        zenith   = 105
        theta    = 90
        cmd = cmd0 % (configFile,ra,dec,name,trigger,duration,offset,dt,roi,zenith,theta)
        if pipe:
            name1 = name.replace("'","")
            os.system('mkdir -p logfiles_ez')
            logfile = 'logfiles_ez/log_ez_%s_.log' % name1
            if os.path.exists(logfile): os.system('rm %s' % logfile)
            cmd_pipe = 'bsub -q %s -o %s %s' % (queue,logfile,cmd)
            print cmd_pipe
            if execute:  os.system(cmd_pipe)
            pass
        else:
            print cmd
            if execute: os.system(cmd)
            pass
        pass
    print 'DONE!!!'
    
