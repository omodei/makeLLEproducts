#! /usr/bin/env python
import os,pyfits

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


def GetTimeMinMax(fitsFile):
    if not os.path.exists(fitsFile): return 0,0
    fin  = pyfits.open(fitsFile)
    hd   = fin['EVENTS']
    data = hd.data
    head = hd.header
    time = data.field('TIME')
    #t0   = head['TRIGTIME']
    #time = time-t0
    tmin = min(time)
    tmax = max(time)
    return tmin,tmax
