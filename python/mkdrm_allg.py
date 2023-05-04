#!/usr/bin/env python

import ROOT
from pyfits import Column, HDUList, PrimaryHDU, new_table

import numpy as num
from math import *
import datetime,calendar

myCut0='ObfGamState==0 && CTBBestEnergyProb>0 && CTBCORE>0 && CTBBestEnergy>10 && CTBBestEnergyRatio<5 && CTBClassLevel>0'
#myCut0='ObfGamState==0 && TkrNumTracks>0' #&& McZDir>%s && McZDir<%s' %(ZDIR,ZDIR+DZ)    
#myCut0='ObfGamState==0 && CalEnergyRaw<5 && TkrNumHits<=20' #&& McZDir>%s && McZDir<%s' %(ZDIR,ZDIR+DZ)    
#myCut0='1==1'

def computeDate(MET):    
    if MET>252460801: MET=MET-1 # 2008 leap second
    if MET>157766400: MET=MET-1 # 2005 leap second
    metdate  = datetime.datetime(2001, 1, 1,0,0,0)
    dt=datetime.timedelta(seconds=MET)
    grb_date=metdate + dt
    return grb_date

def datetime2string(adate, fff=0.0):
    yy=adate.year
    mm=adate.month
    dd=adate.day
    hr=adate.hour
    mi=adate.minute
    ss=adate.second
    #fff=float(ss+60.*mi+3600.*hr)/86.4        
    string='%i-%02i-%02iT%02i:%02i:%.4f' % (yy,mm,dd,hr,mi,ss+fff)
    return string


def makeRootDRMAllG(ROOTfiles,THETA,NMC,NREC,EMIN,EMAX,RADIUS):
    Ngenerated=10000.*len(ROOTfiles)
    Ageo     = 60000. # cm^2   
    LEMIN=log10(EMIN)
    LEMAX=log10(EMAX)
    
    Z1=cos(radians(THETA+RADIUS))
    Z2=cos(radians(THETA-RADIUS))
    ZDIR=(Z1+Z2)/2
    DZ=fabs(Z2-Z1)
    print Z1,Z2,ZDIR,DZ
    print LEMIN,LEMAX

    CHAIN=ROOT.TChain("MeritTuple")
    for ROOTfile in ROOTfiles:
        CHAIN.Add(ROOTfile)
        pass
    
    tmin=CHAIN.GetMinimum("EvtElapsedTime")
    tmax=CHAIN.GetMaximum("EvtElapsedTime")
    
    # Only Theta:
    myCut=' %s && -McZDir>%s && -McZDir<%s ' % (myCut0, Z1,Z2)
    ##################################################
    test=ROOT.TCanvas("test",myCut)
    test.Divide(2,3)
    test.cd(1)
    CHAIN.Draw('EvtElapsedTime-%s' % tmin,myCut0)
    CHAIN.Draw('EvtElapsedTime-%s' % tmin,myCut,'hsame')
    thetaLine1 = ROOT.TLine(0, THETA-RADIUS, 360, THETA-RADIUS)
    thetaLine2 = ROOT.TLine(0, THETA+RADIUS, 360, THETA+RADIUS)
    thetaLine1.SetLineColor(ROOT.kRed)
    thetaLine2.SetLineColor(ROOT.kRed)
    thetaLine1.SetLineStyle(3)
    thetaLine2.SetLineStyle(3)

    test.cd(2)
    CHAIN.Draw('FT1Theta',myCut0)
    CHAIN.Draw('FT1Theta',myCut,'hsame')
    
    thetaLine1v = ROOT.TLine(THETA-RADIUS, 0,THETA-RADIUS,500)
    thetaLine2v = ROOT.TLine(THETA+RADIUS, 0,THETA+RADIUS,500)
    thetaLine1v.SetLineColor(ROOT.kRed)
    thetaLine2v.SetLineColor(ROOT.kRed)
    thetaLine1v.SetLineStyle(3)
    thetaLine2v.SetLineStyle(3)
    thetaLine1v.Draw()
    thetaLine2v.Draw()

    test.cd(3)
    CHAIN.Draw('FT1Theta:FT1Phi',myCut0, 'colz')
    thetaLine1.Draw()
    thetaLine2.Draw()

    test.cd(5)
    CHAIN.Draw('FT1Theta:FT1Phi',myCut,'colz')
    thetaLine1.Draw()
    thetaLine2.Draw()

    test.cd(4)
    CHAIN.Draw('FT1Dec:FT1Ra',myCut0,'colz')
    test.cd(6)
    CHAIN.Draw('FT1Dec:FT1Ra',myCut,'colz')
    

    h_1=ROOT.TH1D("h_1"," McEnergy>%s && McEnergy< %s " % (20,40), 50,-1,1) 
    h_2=ROOT.TH1D("h_2"," McEnergy>%s && McEnergy< %s " % (100,200), 50,-1,1)
    h_3=ROOT.TH1D("h_3"," McEnergy>%s && McEnergy< %s " % (350,700), 50,-1,1)
    h_4=ROOT.TH1D("h_4"," McEnergy>%s && McEnergy< %s " % (1000,2000), 50,-1,1)

    h_1.GetXaxis().SetTitle("(EvtEnergyCorr-McEnergy)/McEnergy")    
    h_2.GetXaxis().SetTitle("(EvtEnergyCorr-McEnergy)/McEnergy")    
    h_3.GetXaxis().SetTitle("(EvtEnergyCorr-McEnergy)/McEnergy")    
    h_4.GetXaxis().SetTitle("(EvtEnergyCorr-McEnergy)/McEnergy")    
    h_1.GetXaxis().CenterTitle()
    h_2.GetXaxis().CenterTitle()
    h_3.GetXaxis().CenterTitle()
    h_4.GetXaxis().CenterTitle()

    test2=ROOT.TCanvas("EnergyValidation",myCut)
    test2.Divide(2,2)
    test2.cd(1)
    CHAIN.Draw('(EvtEnergyCorr-McEnergy)/McEnergy>>h_1','%s && McEnergy>%s && McEnergy< %s'%(myCut,20,40))
    test2.cd(2)
    CHAIN.Draw('(EvtEnergyCorr-McEnergy)/McEnergy>>h_2','%s && McEnergy>%s && McEnergy< %s'%(myCut,100,200))
    test2.cd(3)
    CHAIN.Draw('(EvtEnergyCorr-McEnergy)/McEnergy>>h_3','%s && McEnergy>%s && McEnergy< %s'%(myCut,350,700))
    test2.cd(4)
    CHAIN.Draw('(EvtEnergyCorr-McEnergy)/McEnergy>>h_4','%s && McEnergy>%s && McEnergy< %s'%(myCut,1000,2000))
    
    ##################################################    
    duration = (tmax-tmin)*len(ROOTfiles)
    print 'tmin: %f, tmax: %.1f, duration: %.3f' %(tmin,tmax,duration)
    #print 'Ngenerated/Ageo= ',Ngenerated/Ageo,'F*duration= ',100.0*(duration)*1.0e-4
    
    DRM=ROOT.TH2D("DRM","DRM",NMC,LEMIN,LEMAX,NREC,LEMIN,LEMAX)    
    AEFF=ROOT.TH1D("AEFF","AEFF",NMC,LEMIN,LEMAX)
    DRM.GetXaxis().SetTitle('McLogEnergy')
    DRM.GetYaxis().SetTitle('log10(EvtEnergyCorr)')
    C=ROOT.TCanvas("DRM_CANVAS")
    C.Divide(1,2)
    C.cd(1)
    CHAIN.Draw('log10(EvtEnergyCorr):McLogEnergy>>DRM',myCut,'colz')
    C.cd(2)
    CHAIN.Draw('McLogEnergy>>AEFF',myCut)
    
    # i == x
    # j == y
    for i in range(NMC):
        LE1=AEFF.GetBinLowEdge(i+1)
        LE2=LE1+AEFF.GetBinWidth(i+1)
        Ni = AEFF.GetBinContent(i+1)
        
        emin=pow(10.0,LE1)
        emax=pow(10.0,LE2)
        
        DE=(1./emin - 1./emax)/(1./EMIN-1./EMAX) # < 1
        
        # OnlyTheta e^-1
        #Neff=Ngenerated*DZ*(LE2-LE1)/(LEMAX-LEMIN)
        # Theta and phi, e^-1
        #Neff=Ngenerated*DZ**(LE2-LE1)/(LEMAX-LEMIN)
        # OnlyTheta e^-2
        Neff=Ngenerated* DE * DZ
        # Theta and phi, e^-2
        #Neff=Ngenerated*DZ*DE

        Ai = Ni *Ageo/Neff # cm^2

        AEFF.SetBinContent(i+1,Ai)
        
        for j in range(NREC):
            Mij  = DRM.GetBinContent(i+1,j+1)     
            Aij  = Ageo * Mij / Neff
            DRM.SetBinContent(i+1,j+1,Aij)
            pass
        pass
    C.cd(1)
    DRM.Draw('colz')
    C.cd(2)
    AEFF.Draw()
    C.Update()
    a=raw_input('')
    fitsDRM(DRM)
    pass

    

def makeRootDRM(ROOTfiles,NMC,NREC,EMIN,EMAX):
    Ngenerated=10000.*len(ROOTfiles)
    Ageo     = 60000. # cm^2   
    flux_int = 100.0 # ph/cm^2/s
    method=1 # (Use the Ageo and the gen)
    LEMIN=log10(EMIN)
    LEMAX=log10(EMAX)
    
    print LEMIN,LEMAX
    CHAIN=ROOT.TChain("MeritTuple")
    for ROOTfile in ROOTfiles:
        CHAIN.Add(ROOTfile)
        pass
    
    print len(ROOTfiles)
    tmin=CHAIN.GetMinimum("EvtElapsedTime")
    tmax=CHAIN.GetMaximum("EvtElapsedTime")
    ##################################################
    
    ##################################################
    test=ROOT.TCanvas("test",myCut0)
    test.Divide(2,2)
    test.cd(1)
    CHAIN.Draw('EvtElapsedTime-%s>>(%s)' % (tmin,int(tmax-tmin)),myCut0)
    test.cd(2)
    CHAIN.Draw('FT1Theta',myCut0)
    test.cd(3)
    CHAIN.Draw('FT1Theta:FT1Phi',myCut0)
    test.cd(4)
    CHAIN.Draw('FT1Ra:FT1Dec',myCut0)

    test2=ROOT.TCanvas("EnergyValidation",myCut0)
    test2.Divide(2,2)
    test2.cd(1)
    CHAIN.Draw('EvtEnergyCorr','%s && McEnergy>%s && McEnergy< %s'%(myCut0,10,15))
    test2.cd(2)
    CHAIN.Draw('EvtEnergyCorr','%s && McEnergy>%s && McEnergy< %s'%(myCut0,100,150))
    test2.cd(3)
    CHAIN.Draw('EvtEnergyCorr','%s && McEnergy>%s && McEnergy< %s'%(myCut0,350,385))
    test2.cd(4)
    CHAIN.Draw('EvtEnergyCorr','%s && McEnergy>%s && McEnergy< %s'%(myCut0,1000,1500))
    ##################################################    
    duration = (tmax-tmin)*len(ROOTfiles)
    print 'tmin: %f, tmax: %.1f, duration: %.3f' %(tmin,tmax,duration)
    print 'Ngenerated/Ageo= ',Ngenerated/Ageo,'F*duration= ',10.0*(duration)*1.0e-4
    #print 'Nselected events: %.0f' % NEVENTS

    DRM=ROOT.TH2D("DRM","DRM",NMC,LEMIN,LEMAX,NREC,LEMIN,LEMAX)    
    AEFF=ROOT.TH1D("AEFF","AEFF",NMC,LEMIN,LEMAX)
    DRM.GetXaxis().SetTitle('McLogEnergy')
    DRM.GetYaxis().SetTitle('log10(EvtEnergyCorr)')

    C=ROOT.TCanvas("DRM_CANVAS")
    C.Divide(1,2)
    C.cd(1)
    CHAIN.Draw('log10(EvtEnergyCorr):McLogEnergy>>DRM',myCut0,'colz')
    C.cd(2)
    CHAIN.Draw('McLogEnergy>>AEFF',myCut0)
    
    # i == x
    # j == y


    for i in range(NMC):
        LE1=AEFF.GetBinLowEdge(i+1)
        LE2=LE1+AEFF.GetBinWidth(i+1)


        Ni = AEFF.GetBinContent(i+1)
        
        emin=pow(10.0,LE1)
        emax=pow(10.0,LE2)

        DE=(1./emin - 1./emax)/(1./EMIN-1./EMAX) # < 1

        flux = flux_int*1.e-04 * DE # /cm2/s in the considered energy bin
        Neff = Ngenerated      * DE

        #        print Ni *Ageo/Neff , Ni/(flux*duration)
        if method==1:
            Ai = Ni *Ageo/Neff # cm^2
        else:
            Ai = Ni/(flux*duration) # cm^2
            pass
        AEFF.SetBinContent(i+1,Ai)

        for j in range(NREC):
            Mij  = DRM.GetBinContent(i+1,j+1)     
            if method==1:
                Aij  = Mij * Ageo/Neff # cm^2
            else:
                Aij = Mij/(flux*duration) # cm^2
                pass
            DRM.SetBinContent(i+1,j+1,Aij)
            pass
        pass
    
    C.cd(1)
    DRM.Draw('colz')
    C.cd(2)
    AEFF.Draw()
    C.Update()
    a=raw_input('')
    fitsDRM(DRM)
    pass

def makePHA2(GRBFILES,FT2, NREC,EMIN,EMAX,NMET,METMIN,METMAX,RA,DEC,THETA,RADIUS,TRIGTIME):
    LEMIN=log10(EMIN)
    LEMAX=log10(EMAX)
    CHAIN=ROOT.TChain("MeritTuple")
    for GRBFILE in GRBFILES:
        CHAIN.Add(GRBFILE)
        pass

    #myCut1=' %s && -cos(FT1Theta*1.74e-2)>%s && -cos(FT1Theta*1.74e-2)<%s' %(myCut0,ZDIR,ZDIR+DZ)
    TimeCut='EvtElapsedTime > %s && EvtElapsedTime < %s' %(METMIN,METMAX)
    ZenithCut='FT1ZenithTheta<%s' % THETA

    if(RADIUS==0):
        ROICut ="1==1"
    elif(RADIUS<0):
        ROICut ="((cos(FT1Dec*0.0174533)*(FT1Ra - (%s)))^2+(FT1Dec- (%s))^2)< (%s*EvtPSFModel*57.3)^2 " %(RA,DEC,RADIUS)
    else:
        ROICut ="((cos(FT1Dec*0.0174533)*(FT1Ra - (%s)))^2+(FT1Dec- (%s))^2)< (%s)^2 " %(RA,DEC,RADIUS)
        pass
    myCut='(%s) && (%s) && (%s) && (%s)' %(myCut0,TimeCut,ZenithCut,ROICut)
    print myCut
    PHA2=ROOT.TH2D("PHA2","PHA2",NMET,METMIN,METMAX,NREC,LEMIN,LEMAX)    
    PHA1=ROOT.TH1D("PHA1","PHA1",NREC,LEMIN,LEMAX)
    LC  =ROOT.TH1D("LC","LIGHT CURVE",NMET,METMIN-TRIGTIME,METMAX-TRIGTIME)

    PHA2.GetXaxis().SetTitle('MET')
    PHA2.GetYaxis().SetTitle('log10(EvtEnergyCorr)')
    PHA1.GetXaxis().SetTitle('log10(EvtEnergyCorr)')
    LC.GetXaxis().SetTitle('Time since Trigger(%s)' % TRIGTIME)
    LC.SetLineColor(ROOT.kBlue)

    C=ROOT.TCanvas("GRB_CANVAS")
    C.Divide(1,2)
    C.cd(1)
    CHAIN.Draw('EvtElapsedTime-%s>>LC' % TRIGTIME,myCut)
    C.cd(2)
    CHAIN.Draw('log10(EvtEnergyCorr)>>PHA1',myCut,'E1')
    C.Update()
    #for i in range(NREC):
    #    low_energy =pow(10.,PHA1.GetBinLowEdge(i+1))
    #    high_energy=pow(10.,PHA1.GetBinLowEdge(i+1)+PHA1.GetBinWidth(i+1))
    #    W=high_energy-low_energy
        #PHA1.SetBinContent(i+1,C/W)
        
        
    C2=ROOT.TCanvas("PHA2_CANVAS")
    CHAIN.Draw('log10(EvtEnergyCorr):EvtElapsedTime>>PHA2',myCut,'lego2z')
    C2.Update()

    a=raw_input('')
    fitsPHA2(PHA2,FT2)
    pass

def fitsPHA2(TH2D,FT2):   
    filename='pha2.pha'
    import pyfits
    ft2=pyfits.open(FT2)    
    ft2.info()
    data=ft2[1].data
    cols=ft2[1].columns
    cols.info()
    SC_TSTART=data.field('START')
    SC_TSTOP=data.field('STOP')    
    SC_LIVETIME=data.field('LIVETIME')    
    

    import numpy as num
    print 'imported numpy'
    nt=TH2D.GetNbinsX()
    ne=TH2D.GetNbinsY()
    aTIME=num.arange(float(nt))
    aENDTIME=num.arange(float(nt))
    aBOUNDS=num.arange(float(ne))
    aSPEC_NUM=num.arange(float(nt))
    aCHANNEL=num.zeros((float(nt),float(ne)))
    aCOUNTS =num.zeros((float(nt),float(ne)))
    aEXPOSURE=num.zeros(float(nt))
    aROWID=[]
    ##########
    aE_MIN=num.zeros(float(ne))
    aE_MAX=num.zeros(float(ne))

    index1=0
    index2=0
    EXPOSURE=0.0
    for t in range(nt):
        BinWidth=TH2D.GetXaxis().GetBinWidth(t+1)
        BinLowEdge=TH2D.GetXaxis().GetBinLowEdge(t+1)

        aTIME[t]=1.0*BinLowEdge-TRIGTIME
        aENDTIME[t]=aTIME[t]+1.0*BinWidth
        aSPEC_NUM[t]=t+1

        #print aTIME[t],aENDTIME[t]

        aROWID.append('') #t+1

        while (SC_TSTART[index1]-TRIGTIME<aTIME[t]):
            #print SC_TSTART[index1]-TRIGTIME-aTIME[t],SC_TSTART[index1]-TRIGTIME,aTIME[t]
            index1=index1+1
            pass
        
        index2=index1
        while (SC_TSTOP[index2]-TRIGTIME<aENDTIME[t]):
            index2=index2+1
            pass
        #print SC_TSTART[index1]-TRIGTIME, aTIME[t], SC_TSTOP[index1]-TRIGTIME, SC_TSTART[index1]-TRIGTIME<aTIME[t]
        #print SC_TSTOP[index2]-TRIGTIME, aENDTIME[t], SC_TSTOP[index2]-TRIGTIME, SC_TSTOP[index2]-TRIGTIME>aTIME[t]
        x1=0
        x2=0
        #print index1-1,index2
        for i in range(index1,index2+1):
            x1=x1+SC_LIVETIME[i]
            x2=x2+(SC_TSTOP[i]-SC_TSTART[i])
            pass
        LTF=x1/x2
        
        #print index1, index2, SC_TSTART[index1-1], SC_TSTART[index2], SC_LIVETIME[index2],SC_LIVETIME[index1-1], SC_LIVETIME[index2]-SC_LIVETIME[index1-1], (SC_TSTART[index2]-SC_TSTART[index1-1]), aTIME[t], aENDTIME[t],LTF

        aEXPOSURE[t] = BinWidth * LTF
        EXPOSURE     = EXPOSURE + aEXPOSURE[t]
        #print aEXPOSURE[t],EXPOSURE

        for en in range(ne):
            aCHANNEL[t,en]=en+1
            aCOUNTS[t,en]=TH2D.GetBinContent(t+1,en+1)
            pass
        pass
    
    for en in range(ne):
        EBinLowEdge = TH2D.GetYaxis().GetBinLowEdge(en+1)
        EBinWidth   = TH2D.GetYaxis().GetBinWidth(en+1)
        
        aE_MIN[en]=pow(10.0,EBinLowEdge)*1e3
        aE_MAX[en]=pow(10.0,EBinLowEdge+EBinWidth)*1e3
        pass
    

    #TMIN=aTIME[0]
    #TMAX=aENDTIME[nt]
    print 'nt=%s,ne=%s' %(nt,ne)
    # HDU:
    
    # header
    prim=PrimaryHDU() 
    primary_hdr=prim.header

    now=datetime2string(datetime.datetime.today())
    
    start_date=datetime2string(computeDate(METMIN),METMIN-int(METMIN))
    end_date=datetime2string(computeDate(METMAX),METMAX-int(METMAX))
    trig_date=datetime2string(computeDate(TRIGTIME),TRIGTIME-int(TRIGTIME))
    print 'Now: ',now
    print 'MET MIN:   ',METMIN,' => ',start_date
    print 'MET MAX:   ',METMAX,' => ',end_date
    print 'TRIG TIME: ',TRIGTIME,' => ',trig_date
    primary_hdr.update('DATE',now)
    primary_hdr.update('TELESCOP','GLAST')
    primary_hdr.update('INSTRUME','LAT')
    primary_hdr.update('DETNAM','LAT')

    primary_hdr.update('DATE-OBS',start_date)
    primary_hdr.update('DATE-END',end_date)
    primary_hdr.update('FILETYPE','PHAII')
    primary_hdr.update('TRIGTIME',TRIGTIME)


    #prim.name = 'Primary'
    output = HDUList()
    output.append(prim)
    
    # SPECTRUM    
    S1=Column(name='TIME', format='D', array=aTIME,unit='s')
    S2=Column(name='ENDTIME', format='D', array=aENDTIME,unit='s')
    S3=Column(name='SPEC_NUM', format='I', array=aSPEC_NUM)
    S4=Column(name='CHANNEL', format='%iI'%NREC, array=aCHANNEL,unit='')
    S5=Column(name='COUNTS', format='%iJ'%NREC, array=num.array(aCOUNTS),unit='Counts')
    S6=Column(name='ROWID', format='A',array=num.array(aROWID))#num.arange(1,nt+1),unit='')
    S7=Column(name='EXPOSURE', format='D', array=num.array(aEXPOSURE),unit='s')
    
    columns1=[S1,S2,S3,S4,S5,S6,S7]
    output.append(new_table(columns1))
    ext1hdr=output[1]        
    spectrum_hdr = ext1hdr.header
    ext1hdr.name = 'SPECTRUM'

    #spectrum_hdr.update('TTYPE1','TIME',after)
    #spectrum_hdr.update('TUNIT1','s')
    #spectrum_hdr.update('TTYPE2','ENDTIME')
    #spectrum_hdr.update('TUNIT2','s')
    spectrum_hdr.update('TZERO1',TRIGTIME,after='TFORM1')
    spectrum_hdr.update('TZERO2',TRIGTIME,after='TFORM2')
    spectrum_hdr.update('TELESCOP','GLAST')
    spectrum_hdr.update('INSTRUME','LAT')
    spectrum_hdr.update('DETNAM','LAT')
    spectrum_hdr.update('HDUCLASS','OGIP')
    spectrum_hdr.update('HDUCLAS1','SPECTRUM')
    spectrum_hdr.update('HDUCLAS2','TOTAL')
    spectrum_hdr.update('HDUCLAS3','COUNT')
    spectrum_hdr.update('HDUCLAS4','PHA:II')
    spectrum_hdr.update('HDUVERS','1.2.0')
    spectrum_hdr.update('DETCHANS',NREC)
    spectrum_hdr.update('POISSERR','T')
    spectrum_hdr.update('BACKFILE','none')
    spectrum_hdr.update('CORRFILE','none')
    spectrum_hdr.update('CORRSCAL',1)
    spectrum_hdr.update('RESPFILE','none')
    spectrum_hdr.update('ANCRFILE','none')
    spectrum_hdr.update('SYS_ERR',0.)
    spectrum_hdr.update('QUALITY',0)
    spectrum_hdr.update('GROUPING',0)
    spectrum_hdr.update('AREASCAL',1.)
    spectrum_hdr.update('BACKSCAL',1.)
    spectrum_hdr.update('CHANTYPE','PI')
    spectrum_hdr.update('FILTER','')
    spectrum_hdr.update('OBJECT','')
    spectrum_hdr.update('EQUINOX',2000.)
    spectrum_hdr.update('RADECSYS','FK5')
    spectrum_hdr.update('DATE-OBS',start_date)
    spectrum_hdr.update('DATE-END',end_date)
    spectrum_hdr.update('TSTART',TRIGTIME)#,after='DATE-END')
    spectrum_hdr.update('NDSKEYS',4)
    spectrum_hdr.update('CREATOR','mkdrm')

    # EBOUNDS
    E1=Column(name='CHANNEL', format='I', array=num.arange(1,en+2))
    E2=Column(name='E_MIN', format='1E', array=aE_MIN,unit='keV')
    E3=Column(name='E_MAX', format='1E', array=aE_MAX,unit='keV')
    columns2=[E1,E2,E3]
    output.append(new_table(columns2))
    ext2hdr=output[2]        
    ext2hdr.name = 'EBOUNDS'
    ebounds_hdr = ext2hdr.header
    ebounds_hdr.update('TELESCOP','GLAST')
    ebounds_hdr.update('INSTRUME','LAT')
    ebounds_hdr.update('DETNAM','LAT')
    ebounds_hdr.update('FILTER','')
    ebounds_hdr.update('CHANTYPE','PI')
    ebounds_hdr.update('DETCHANS',NREC)
    ebounds_hdr.update('HDUCLASS','OGIP')
    ebounds_hdr.update('HDUCLAS1','RESPONSE')
    ebounds_hdr.update('HDUCLAS3','EBOUNDS')
    ebounds_hdr.update('HDUVERS','1.0.0')
    ebounds_hdr.update('DATE-OBS',start_date)
    ebounds_hdr.update('DATE-END',end_date)
    ebounds_hdr.update('CREATOR','mkdrm')

    # GTI
    G1=Column(name='START', format='D', array=num.array([METMIN]))
    G2=Column(name='STOP', format='D', array=num.array([METMAX]))
    columns3=[G1,G2]
    output.append(new_table(columns3))
    ext3hdr=output[3]        
    ext3hdr.name = 'GTI'
    gti_hdr = ext3hdr.header
    gti_hdr.update
    gti_hdr.update('TELESCOP','GLAST')
    gti_hdr.update('INSTRUME','LAT')
    gti_hdr.update('DETNAM','LAT')    
    gti_hdr.update('HDUCLASS','OGIP')
    gti_hdr.update('HDUCLAS1','GTI')
    gti_hdr.update('HDUVERS','1.0.0')
    gti_hdr.update('CREATOR','mkdrm')
    gti_hdr.update('ONTIME',METMAX-METMIN)
    gti_hdr.update('MJDREF','')
    gti_hdr.update('TSTART',METMIN)
    gti_hdr.update('TSTOP',METMAX)
    gti_hdr.update('EXPOSURE',EXPOSURE)
    gti_hdr.update('TIMESYS','TT')
    gti_hdr.update('TIMEUNIT','s')
    gti_hdr.update('DATE-OBS',start_date)
    gti_hdr.update('DATE-END',end_date)
    gti_hdr.update('CREATOR','mkdrm')
    ##########
    output.info()    
    output.verify()
    output.writeto(filename, clobber=True)
    pass

def fitsDRM(DRM):
    filename='LATDRM.rsp'
    NMC=DRM.GetNbinsX()
    NREC=DRM.GetNbinsY()
    aENERG_LO=num.zeros(NMC)
    aENERG_HI=num.zeros(NMC)
    aN_GRP=num.zeros(NMC)+1
    aF_CHAN=num.zeros((NMC,1))+1
    aN_CHAN=num.zeros((NMC,1))+NREC
    aMATRIX=num.zeros((NMC,NREC))
    aE_MIN=num.zeros(NREC)
    aE_MAX=num.zeros(NREC)

    now=datetime2string(datetime.datetime.today())
    start_date=datetime2string(computeDate(METMIN),METMIN-int(METMIN))
    end_date=datetime2string(computeDate(METMAX),METMAX-int(METMAX))
    trig_date=datetime2string(computeDate(TRIGTIME),TRIGTIME-int(TRIGTIME))
    ##################################################
    for en in range(NMC):
        aENERG_LO[en]=pow(10,DRM.GetXaxis().GetBinLowEdge(en+1))*1e3
        aENERG_HI[en]=pow(10,DRM.GetXaxis().GetBinLowEdge(en+2))*1e3
        for ren in range(NREC):
            aMATRIX[en,ren]=DRM.GetBinContent(en+1,ren+1)
            pass
        pass
    for ren in range(NREC):
        aE_MIN[ren]=pow(10,DRM.GetYaxis().GetBinLowEdge(ren+1))*1e3
        aE_MAX[ren]=pow(10,DRM.GetYaxis().GetBinLowEdge(ren+2))*1e3
    ##################################################
    prim=PrimaryHDU() 
    primary_hdr=prim.header
    primary_hdr.update('DATE',now)
    primary_hdr.update('FILENAME',filename)
    primary_hdr.update('TELESCOP','GLAST')
    primary_hdr.update('INSTRUME','LAT')
    primary_hdr.update('DETNAM','LAT')
    primary_hdr.update('DATE-OBS',start_date)
    primary_hdr.update('DATE-END',end_date)
    primary_hdr.update('DRM_NUM',1)
    #primary_hdr.update('FILETYPE','PHAII')
    primary_hdr.update('CREATOR','mkdrm')
    # primary_hdr.update('TRIGTIME',TRIGTIME)
    # prim.name = 'Primary'

    output = HDUList()
    output.append(prim)
    
    # MATRIX 

    M1=Column(name='ENERG_LO',format='E',unit='keV',array=aENERG_LO)
    M2=Column(name='ENERG_HI',format='E',unit='keV',array=aENERG_HI)
    M3=Column(name='N_GRP',format='I',array=aN_GRP)
    M4=Column(name='F_CHAN',format='PI(1)',array=aF_CHAN)
    M5=Column(name='N_CHAN',format='PI(1)',array=aN_CHAN)
    M6=Column(name='MATRIX',format='PE(%i)'% NREC, unit='cm**2',array=aMATRIX)
    columns1=[M1,M2,M3,M4,M5,M6]
    output.append(new_table(columns1))
    ext1hdr=output[1]        
    matrix_hdr = ext1hdr.header
    ext1hdr.name = 'MATRIX'
    matrix_hdr.update('TELESCOP','GLAST')
    matrix_hdr.update('INSTRUME','LAT')
    matrix_hdr.update('DETNAM','LAT')
    matrix_hdr.update('FILTER','')
    matrix_hdr.update('CHANTYPE','PI')
    matrix_hdr.update('DETCHANS',NREC)
    matrix_hdr.update('HDUCLASS','OGIP')
    matrix_hdr.update('HDUCLAS1','RESPONSE')
    matrix_hdr.update('HDUCLAS2','RSP_MATRIX')
    matrix_hdr.update('HDUVERS','1.0.0')
    matrix_hdr.update('DATE-OBS',start_date)
    matrix_hdr.update('DATE-END',end_date)
    matrix_hdr.update('NDSKEYS',0)
    matrix_hdr.update('CREATOR','mkdrm')
    # EBOUNDS
    ##########
    E1=Column(name='CHANNEL',format='I',array=num.arange(1,NREC+1))
    E2=Column(name='E_MIN',format='1E',unit='keV',array=aE_MIN)
    E3=Column(name='E_MAX',format='1E',unit='keV',array=aE_MAX)
    columns2=[E1,E2,E3]
    output.append(new_table(columns2))
    ext2hdr=output[2]        
    ebounds_hdr = ext2hdr.header
    ext2hdr.name = 'EBOUNDS'
    ebounds_hdr.update('TELESCOP','GLAST')
    ebounds_hdr.update('INSTRUME','LAT')
    ebounds_hdr.update('DETNAM','LAT')
    ebounds_hdr.update('FILTER','none')
    ebounds_hdr.update('CHANTYPE','PI')
    ebounds_hdr.update('DETCHANS',NREC)
    ebounds_hdr.update('HDUCLASS','OGIP')
    ebounds_hdr.update('HDUCLAS1','RESPONSE')
    ebounds_hdr.update('HDUCLAS2','EBOUNDS')
    ebounds_hdr.update('HDUVERS','1.0.0')
    ebounds_hdr.update('DATE-OBS',start_date)
    ebounds_hdr.update('DATE-END',end_date)
    ebounds_hdr.update('CREATOR','mkdrm')
    
    output.info()    
    output.verify()
    output.writeto(filename, clobber=True)
    pass


if __name__=='__main__':
    # This parameters define 
    NMC=100 #MC
    NREC=80 #RECON
    # Standard All Gamma
    #EMIN=18
    #EMAX=562000
    # Standard All Gamma Law Energy
    #EMIN=18
    #EMAX=562
    # New All Gamma withn E^-2
    EMIN=5
    EMAX=100000
    
    # SLAC
    #    basename='root://glast-rdr//glast/mc/ServiceChallenge/allGamma-GR-v17r7-allE-OVRLY/merit/allGamma-GR-v17r7-allE-OVRLY-%06i-merit.root'
    # LOCAL
    basename='/Volumes/Lacie/DATA/MERIT/AllGamma_v17r7-Nicola/%06i_merit.root' # this is the e-2 all gamma 

    basename='/Users/omodei/Documents/DATA/GRB081024_theta/%06d_merit.root'

    #basename='AllGamma_v17r7_LowEnergy/%06i_merit.root'
    allGamma=False
    #basename='/Users/omodei/Documents/DATA/MERIT/grb080916C_v17r7/allGamma-GR-v17r7-Nicola-%06i-merit.root'
    
    

    NAllGammaFiles = 100#*200
        
    # GRB080825C
    #METMIN=241366229.105 
    #METMAX=241367029.105 
    #TRIGTIME=241366429.105
    #GRBFILES=['GRB080825593.root']
    #FT2='r0241365685_ft2.fit'
    #THETA=21.3 #60.0
    #PHI=0.0
    #    RADIUS=1.0
    
    # GRB080916C
    #basename='/Users/omodei/Documents/DATA/MERIT/grb080916C_v15r39/allGamma-GR-v15r39-Nicola-%06i-merit.root'
    #basename='/Users/omodei/Documents/DATA/MERIT/grb080916C_v17r7/allGamma-GR-v17r7-Nicola-%06i-merit.root'


    TRIGTIME=243216766.6135420
    METMIN=TRIGTIME-100
    METMAX=TRIGTIME+200
    #GRBFILES=['r0243215785_v000_merit.root']
    GRBFILES=['080916009.root'] #r0243215785_v000_merit.root']
    #GRBFILES=[]
    #for i in range(10):
    #    GRBFILES.append(basename % i)
    
    FT2='r0243215785_ft2.fit'
    RA     = 119.88
    DEC    = -65.59
    THETA  = 48.5

    # #################################################
    # GRB081024B

    TRIGTIME=246576161.864192
    METMIN=TRIGTIME-10
    METMAX=TRIGTIME+10
    #GRBFILES=['r0243215785_v000_merit.root']
    GRBFILES=['081024891_LAT.root'] #r0243215785_v000_merit.root']
    #GRBFILES=[]
    #for i in range(10):
    #    GRBFILES.append(basename % i)
    
    FT2='GRB081024B_FT2.fit'
    RA     = 322.9 
    DEC    = 21.204
    THETA  = 21.3


    # #################################################
    DT=0.1    
    
    RADIUS_ROI =  0.0
    RADIUS_DRM =  5.0
    ZENITHTHETA=180.0
    NMET=int((METMAX-METMIN)/DT)
    print 'Tstart = %s, Tstop=%s, Nbin=%s' %(METMIN,METMAX,NMET)    

    #ZDIR=-cos(radians(THETA))
    #print 'THETA: %s, ZDIR: %s' % (THETA,ZDIR)

    

    ROOTfiles=[]
    offset=0
    for i in range(NAllGammaFiles):
        ROOTfiles.append(basename % (i+offset))
        print 'Adding response file: ',basename % (i+offset)
        pass
    
    makeRootDRM(ROOTfiles,NMC,NREC,EMIN,EMAX)

    '''
    if NAllGammaFiles>0:
    if(allGamma):
    makeRootDRMAllG(ROOTfiles,THETA,NMC,NREC,EMIN,EMAX, RADIUS_DRM)
    else:
    makeRootDRM(ROOTfiles,NMC,NREC,EMIN,EMAX)
    pass
    '''
    makePHA2(GRBFILES,FT2, NREC,EMIN,EMAX,NMET,METMIN,METMAX,RA,DEC,ZENITHTHETA,RADIUS_ROI,TRIGTIME)
        
