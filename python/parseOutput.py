#!/usr/bin/env python
import glob,os,sys
def Go(oneFile):
    fin=file(oneFile,'r')
    txt=fin.readlines()
    dic={}
    for l in txt:
        p0=l.split('=')[0].strip()
        p1=l.split('=')[1].strip()
        try:    p1=float(p1)
        except: pass
        dic[p0]=p1
        pass
    return dic

if __name__=='__main__':
    list=sorted(glob.glob('output_ez/*/results*'))
    filter = sys.argv[1]
    for f in list:
        if filter in f:
            sig=Go(f)['SIGNIFICANCE']
            if sig>4: print f,sig
