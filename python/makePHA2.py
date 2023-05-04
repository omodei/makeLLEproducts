#!/usr/bin/env python

from ROOT import *
#from pyfits import Column, HDUList, PrimaryHDU, new_table

import numpy as num
import math
import utils
import datetime
from makeFits import *

def makePHA2(GRBFILES,
             FT2,
             NREC,EMIN,EMAX,
             NMET,METMIN,METMAX,
             TRIGTIME,
             MYCUT,
             DETNAM,
             DIRECTORY,
             GRBNAME,
             DATAENERGYVAR='EvtEnergyCorr',
             OFFSET=0,
             DURATION=0,
             KEYWORDS=None):
    
    EvtElapsedTime = 'EvtElapsedTime'
    FT1ZenithTheta = 'FT1ZenithTheta'
    FT1Theta       = 'FT1Theta'
    FT1Dec         = 'FT1Dec'
    FT1Ra          = 'FT1Ra'
    FT1Dec         = 'FT1Dec'
    time           = 'EvtElapsedTime'
    TREE           = 'MeritTuple'
    
    print '##################################################'
    print '           MAKING THE PHA2 FILE for %s (%s/%s)' % (GRBNAME,DIRECTORY,DETNAM)
    print '##################################################'
    print 'Number of GRB files...: %s' %len(GRBFILES)
    print 'FT2 file:.............: ',FT2,
    print 'Number of energy bins.: %s, from %s to %s MeV' % (NREC,EMIN,EMAX)
    print 'Number of time bins...: %s, from %s to %s s  ' %(NMET,METMIN,METMAX)
    print 'Trigger Time..........: %s ' % TRIGTIME
    print ' + OFFSET   ..........: %s ' % OFFSET
    print ' + DURATION ..........: %s ' % DURATION
    print 'Energy Variable.......: %s ' % DATAENERGYVAR
    print '--------------------------------------------------'
    print ' Selection:...........: %s ' % MYCUT    
    print '--------------------------------------------------'
    try: version=int(KEYWORDS['VERSION'])
    except: version=0   
    source_filename='%s/gll_quick_bn%s_v%02d.png' % (DIRECTORY,GRBNAME[-9:],version)
    cspec_filename='%s/gll_cspec_bn%s_v%02d.png' % (DIRECTORY,GRBNAME[-9:],version)
    cspec_parameters='%s/gll_cspec_bn%s_v%02d.txt' % (DIRECTORY,GRBNAME[-9:],version)
    cspec_root='%s/gll_cspec_bn%s_v%02d.root' % (DIRECTORY,GRBNAME[-9:],version)

    try:
        KEYWORDS['CSPEC_PNG'] = cspec_filename
        KEYWORDS['QUICK_PNG'] = source_filename
    except:
        pass
    

    
    LEMIN=log10(EMIN)
    LEMAX=log10(EMAX)
    CHAINGRB=TChain(TREE)
    for GRBFILE in GRBFILES:
        CHAINGRB.Add(GRBFILE.strip())
        pass

    # ##################################################
    TimeCut='%(EvtElapsedTime)s > %(METMIN)s && %(EvtElapsedTime)s < %(METMAX)s' % locals()
    myCut='(%s) && (%s)' %(MYCUT, TimeCut)
    NumberOfTotalEvents    = CHAINGRB.GetEntries()
    NumberOfSelectedEvents = CHAINGRB.GetEntries(myCut)
    print '--------------------------------------------------'
    print ' Final Selection......: %s ' % myCut
    print ' Selected %d over %d events (%.3f)' % (NumberOfSelectedEvents,NumberOfTotalEvents, (1.0*NumberOfSelectedEvents)/(1.0*NumberOfTotalEvents))
    print '--------------------------------------------------'
    PHA2  = TH2D("PHA2","PHA2",NMET,METMIN,METMAX,NREC,LEMIN,LEMAX)    
    PHA1  = TH1D("PHA1","Count Spectrum",NREC,LEMIN,LEMAX)
    LC    = TH1D("LC","LIGHT CURVE",NMET,METMIN-TRIGTIME,METMAX-TRIGTIME)
    LT    = TH1D("LT","LIVE TIME",NMET,METMIN-TRIGTIME,METMAX-TRIGTIME)
    radec = TH2D("RD","Sky Map J2000",360,0,360,180,-90,90)
    hTHETA = TH1D('h_THETA','Angle with the LAT Boresight',100,0,100)
    
    PHA2.GetXaxis().SetTitle('MET')
    PHA2.GetYaxis().SetTitle('log10(%s)' % DATAENERGYVAR)
    PHA1.GetXaxis().SetTitle('log10(%s)' % DATAENERGYVAR)
    radec.GetXaxis().SetTitle('R.A. (deg)')
    radec.GetYaxis().SetTitle('Dec. (deg)')
    radec.GetXaxis().CenterTitle()
    radec.GetYaxis().CenterTitle()
    
    
    C=TCanvas("SRC_CANVAS",DETNAM)
    C.Divide(2,2)
    C.cd(1)
    print '... drawing the LC...'
    CHAINGRB.Draw('%(EvtElapsedTime)s-%(TRIGTIME)s>>LC' % locals(),myCut,"E0")
    LC.Sumw2()
    LC.GetXaxis().SetTitle('Time since Trigger(%s)' % TRIGTIME)
    LC.SetLineColor(kBlue)
    LC.SetFillColor(kGray)
    
    ##################################################
    # Compute livetime fraction:
    
    print '... opening the FT2 file ...'
    ft2=pyfits.open(FT2)    
    ft2.info()
    
    CORRECTION = 0
    Tmin       = METMIN
    Tmax       = METMAX
    
    index1=0
    EXPOSURE=0.0
    
    for t in range(NMET):
        BinWidth    = LC.GetXaxis().GetBinWidth(t+1)
        BinLowEdge  = LC.GetXaxis().GetBinLowEdge(t+1)
        
        aTIME    = 1.0*BinLowEdge
        aENDTIME = aTIME + 1.0*BinWidth
        #This Compute the expsure:
        if CORRECTION:
            LTF = CORRECTION /(METMAX-METMIN)#* utils.GetLiveTimeFraction(ft2,aTIME+TRIGTIME,aENDTIME+TRIGTIME,index1)
        else:
            LTF = utils.GetLiveTimeFraction(ft2,aTIME+TRIGTIME,aENDTIME+TRIGTIME,index1)
            pass
        # This is the LIVETIME per bin.                    
        aLiveTime  = BinWidth * LTF
        LT.SetBinContent(t+1,aLiveTime)
        #  LC.SetBinContent(t+1,BinContent/aLiveTime)
        pass
    
    # #################################################
    lineStart = TLine(OFFSET,0,OFFSET,LC.GetMaximum())
    lineStart.SetLineStyle(3)
    lineStart.Draw()
    
    if DURATION>0:
        lineEnd = TLine(OFFSET+DURATION,0,OFFSET+DURATION,LC.GetMaximum())
        lineEnd.SetLineStyle(3)
        lineEnd.Draw()
        pass
    gPad.Update()

    C.cd(2)
    print '... drawing the theta histogram ...'
    CHAINGRB.Draw('%(FT1Theta)s>>h_THETA' % locals(),myCut,'E0')
    hTHETA.SetFillColor(kYellow)
    hTHETA.SetLineColor(kBlue)
    hTHETA.GetXaxis().SetTitle('Angle from LAT boresight (degrees)')
    gPad.Update()
    
    C.cd(3)
    print '... drawing the pha2 histogram ...'
    CHAINGRB.Draw('log10(%s)>>PHA1' %(DATAENERGYVAR),myCut,'E1')
    PHA1.SetLineColor(kBlue)
    PHA1.SetMarkerStyle(23)
    gPad.SetLogy()
    gPad.Update()
    
    C.cd(4)
    print '... drawing the ra-dec histogram ...'
    CHAINGRB.Draw('%(FT1Dec)s:%(FT1Ra)s>>RD' % locals(),myCut,'colz')
    gPad.SetLogz()
    gPad.Update()
    
    C.Update()
    C.Print(source_filename)
    #for i in range(NREC):
    #    low_energy =pow(10.,PHA1.GetBinLowEdge(i+1))
    #    high_energy=pow(10.,PHA1.GetBinLowEdge(i+1)+PHA1.GetBinWidth(i+1))
    #    W=high_energy-low_energy
        #PHA1.SetBinContent(i+1,C/W)
        
        
    C2=TCanvas("PHA2_CANVAS",DETNAM)
    print '... drawing the pha2 histogram ...'
    CHAINGRB.Draw('log10(%(DATAENERGYVAR)s):%(EvtElapsedTime)s>>PHA2' % locals(),myCut,'colz')    
    C2.SetLogz()    
    C2.Update()
    C2.Print(cspec_filename)

    print '...Now Saving the fits file...'
    
    # print FT2,DETNAM,TRIGTIME,TRIGTIME,METMIN,METMAX
    filename = fitsPHA2(PHA2,FT2,DETNAM,DIRECTORY,TRIGTIME,METMIN,METMAX,GRBNAME,CORRECTION,KEYWORDS)
    print 'Done!'
    print '...Now Saving the ROOT file...',cspec_root
    ftemp = TFile(cspec_root,'RECREATE')
    LC.Write()
    LT.Write()
    PHA2.Write()
    PHA1.Write()
    hTHETA.Write()    
    ftemp.Close()
    fcorr = file(cspec_parameters,'w')    
    fcorr.writelines('FT2=%s\n' % FT2)
    fcorr.writelines('DETNAM=%s\n' % DETNAM)
    fcorr.writelines('DIRECTORY=%s\n' % DIRECTORY)
    fcorr.writelines('TRIGTIME=%s\n' % TRIGTIME)
    fcorr.writelines('METMIN=%s\n' % METMIN)
    fcorr.writelines('METMAX=%s\n' % METMAX)
    fcorr.writelines('CORRECTION=%s\n' % CORRECTION)
    fcorr.writelines('TSTART    =%s\n' % Tmin)
    fcorr.writelines('TEND      =%s\n' % Tmax)
    fcorr.close()
    print 'Done!'
    return filename
