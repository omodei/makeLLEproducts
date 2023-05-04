#!/usr/bin/env python
import pyfits
import os,sys
from array import array

def getArrays(f1n):
    f1=pyfits.open(f1n)
    f1.info()
    d1=f1['SPECTRUM'].data
    h1=f1['SPECTRUM'].header
    return h1,d1

def AveragePHA2(f1n,f2n,f3n):
    f4n=f3n.replace('.pha','.bak')
    print '-------------------------------------------------------------'
    print 'Background 1...........:',f1n
    print 'Background 2...........:',f2n
    print 'Source Template........:',f3n
    print 'Background output in...:',f4n
    print '-------------------------------------------------------------'
    h1,d1=getArrays(f1n)
    h2,d2=getArrays(f2n)

    n1=d1.names
    
    a1=d1.field('COUNTS')
    a2=d2.field('COUNTS')
    average = (a1+a2)/2.
    print 'Number of Time interval in the 1st background file:',len(a1)
    print 'Number of Time interval in the 2nd background file:',len(a2)
    print 'Number of Time interval in the average file:',len(average)
    #print 'a1=',a1
    #print 'a2=',a2
    #print '(a1+a2)/2=',average
    
    os.system('cp %s %s' % (f3n,f4n))
    f1=pyfits.open(f4n)
        
    tbdata   = f1['SPECTRUM'].data
    tbheader = f1['SPECTRUM'].header

    counts = tbdata.field('COUNTS')
    tstart = tbdata.field('TIME')
    tend   = tbdata.field('ENDTIME')
    
    EnergyBins=len(counts[0])
    TimeBins=len(counts)
    print '...reading the template file:',f4n 
    print 'Number of TimeBins...%d from %s to %s' %(TimeBins,tstart[0],tend[-1])
    print 'Number of EnergyBins.:',EnergyBins

    counts_f = array('f',[0.0])
    countarray=[]
    #tbdata.formats[3]=tbdata.formats[3].replace('J','D')    
    #print tbdata.formats
    timeBins=()
    TZERO4 = tbheader['TZERO4']
    TZERO5 = tbheader['TZERO5']
    for t in range(TimeBins):
        fcounts=[]
        tstart[t] = tstart[t] - TZERO4
        tend[t]   = tend[t] - TZERO5
        #print tstart[t],tend[t]
        for en in range(EnergyBins): fcounts.append(average[t,en])
        countarray.append(fcounts)
        pass
    
    newCounts=pyfits.Column(name="COUNTS", format="%iD" %EnergyBins, unit = 'Counts', array=countarray)
    newTime=pyfits.Column(name="TIME", format="D" , unit = 's', array=tstart)
    newEndTime=pyfits.Column(name="ENDTIME", format="D" , unit = 's', array=tend)
    
    old_Cols=f1['SPECTRUM'].get_coldefs()
    
    new_cols_array=[]
    print '--------------------------------------------------'
    print newCounts
    print '=================================================='
    for c in old_Cols:
        if c.name == 'COUNTS':
            new_cols_array.append(newCounts)
            print 'adding new colum name:',newCounts.name                    
        elif c.name == 'TIME':
            new_cols_array.append(newTime)
            print 'adding new colum name:',newTime.name
        elif c.name == 'ENDTIME':
            new_cols_array.append(newEndTime)
            print 'adding new colum name:',newEndTime.name
        else:
            new_cols_array.append(c)
            print 'adding old colum name:',c.name
            pass
        
        print new_cols_array[-1]
        print '--------------------------------------------------'
        pass
    print '**************************************************'
    print new_cols_array
    
    #tbdata['SPECTRUM']=
    
    tb=pyfits.new_table(new_cols_array)
    tb.name='SPECTRUM'
    print '--------------------------------------------------'
    print tb.header
    print '--------------------------------------------------'
    print tbheader
    print '--------------------------------------------------'
    print tbheader.items()
    print tb.header.items()
    oldNames=[]
    for n in tb.header.items():
        oldNames.append(n[0])
        pass
    for n in tbheader.items():        
        if n[0] not in oldNames:
            print 'update'
            tb.header.update(n[0],n[1])
            pass
        pass
    print '--------------------------------------------------'    
    print tb.header
    #print dir(tb)

    f1['SPECTRUM']=tb
    
    #f1['SPECTRUM'].header=tbheader
    #f1.append(tb)
    f1.writeto(f4n,clobber=True)
    
    #pyfits.update('avg.fits', tb,'SPECTRUM') 

    #h,d=getArrays('avg.fits')
    #print d.field('COUNTS')
    #print d.field('TIME')
    
    pass


def AveragePHA1(f1n,f2n,f3n):
    f4n=f3n.replace('.fit','.bak')
    print '-------------------------------------------------------------'
    print 'Background 1...........:',f1n
    print 'Background 2...........:',f2n
    print 'Source Template........:',f3n
    print 'Background output in...:',f4n
    print '-------------------------------------------------------------'
    h1,d1=getArrays(f1n)
    h2,d2=getArrays(f2n)

    n1=d1.names
    
    a1=d1.field('COUNTS')
    a2=d2.field('COUNTS')
    average = (a1+a2)/2.

    print 'Number of Time interval in the 1st background file:',len(a1)
    print 'Number of Time interval in the 2nd background file:',len(a2)
    print 'Number of Time interval in the average file:',len(average)
    print 'a1=',a1
    print 'a2=',a2
    print '(a1+a2)/2=',average
    
    os.system('cp %s %s' % (f3n,f4n))
    f1=pyfits.open(f4n)
        
    tbdata   = f1['SPECTRUM'].data
    tbheader = f1['SPECTRUM'].header

    counts = tbdata.field('COUNTS')    
    EnergyBins=len(counts)
    print '...reading the template file:',f4n 
    print 'Number of EnergyBins.:',EnergyBins

    #counts_f = array('f',[0.0])
    #countarray=[]
    #tbdata.formats[3]=tbdata.formats[3].replace('J','D')    
    #print tbdata.formats
    #for en in range(EnergyBins): fcounts.append(average[en])
    
    newCounts=pyfits.Column(name="COUNTS", format="D" , unit = 'Counts', array=average)
    
    old_Cols=f1['SPECTRUM'].get_coldefs()
    
    new_cols_array=[]
    print '--------------------------------------------------'
    print newCounts
    print '=================================================='
    for c in old_Cols:
        if c.name == 'COUNTS':
            new_cols_array.append(newCounts)
            print 'adding new colum name:',newCounts.name                    
        else:
            new_cols_array.append(c)
            print 'adding old colum name:',c.name
            pass
        
        print new_cols_array[-1]
        print '--------------------------------------------------'
        pass
    print '**************************************************'
    print new_cols_array
    
    #tbdata['SPECTRUM']=
    
    tb=pyfits.new_table(new_cols_array)
    tb.name='SPECTRUM'
    print '--------------------------------------------------'
    print tb.header
    print '--------------------------------------------------'
    print tbheader
    print '--------------------------------------------------'
    print tbheader.items()
    print tb.header.items()
    oldNames=[]
    for n in tb.header.items():
        oldNames.append(n[0])
        pass
    for n in tbheader.items():        
        if n[0] not in oldNames:
            print 'update'
            tb.header.update(n[0],n[1])
            pass
        pass
    print '--------------------------------------------------'    
    print tb.header
    #print dir(tb)

    f1['SPECTRUM']=tb
    
    #f1['SPECTRUM'].header=tbheader
    #f1.append(tb)
    f1.writeto(f4n,clobber=True)
    
    #pyfits.update('avg.fits', tb,'SPECTRUM') 

    #h,d=getArrays('avg.fits')
    #print d.field('COUNTS')
    #print d.field('TIME')
    
    pass





if __name__=='__main__':
    f1n=sys.argv[1]
    f2n=sys.argv[2]
    f3n=sys.argv[3]
    opt=None
    try:     opt=sys.argv[4]
    except:  pass
    if opt=='pha1': AveragePHA1(f1n,f2n,f3n)
    else: AveragePHA2(f1n,f2n,f3n)
    
