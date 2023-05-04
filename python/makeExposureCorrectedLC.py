#!/usr/bin/env python
from ROOT import *
import sys,os

##################################################
# THIS IS SOME STYLE STUFFS:
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetCanvasColor(10)
gStyle.SetPadColor(10)
gStyle.SetPadTickX(True)
gStyle.SetPadTickY(True)
gStyle.SetFrameFillColor(10)
gStyle.SetPalette(1)
##################################################

def makeLC(lcfile,exposure):
    lightCurveCanvas    = TCanvas('lightCurveCanvas','Background Subtracetd Light Cuve')
    lightCurveCanvas.Divide(1,3)
    lc           = lcfile.Get('LC')
    lt           = lcfile.Get('LT')    
    lc_norm      = lc.Clone('NormalizedLC')
    lc.Sumw2()
    lc_norm.Sumw2()
    
    lc.GetYaxis().SetTitle('Counts/s')
    lc_norm.GetYaxis().SetTitle('Counts/cm^{2}/s')
    
    bkg          = exposure.Get('hTime_mc').ShowBackground()
    bkg.GetYaxis().SetTitle('cm^{2}')

    tMin0     = lc.GetXaxis().GetXmin()
    tMax0     = lc.GetXaxis().GetXmax()

    tMin1      = bkg.GetXaxis().GetXmin()
    tMax1      = bkg.GetXaxis().GetXmax()

    tMin=max(tMin0,tMin1)
    tMax=min(tMax0,tMax1)
    
    print tMin,tMax
    Nbin = lc_norm.GetNbinsX()
    ascii = file('lc_exposure_corrected.txt','w')
    
    for x in range(Nbin):
        binW = lc.GetBinWidth(x+1)
        t    = lc.GetBinCenter(x+1)
        ltf  = lt.GetBinContent(x+1)
        #bin  = lc_norm.FindBin(t)
        yexp = bkg.Interpolate(t)
        y    = lc.GetBinContent(x+1)/yexp/ltf
        ey   = lc.GetBinError(x+1)/yexp/ltf
        
        lc_norm.SetBinContent(x+1,y)
        lc_norm.SetBinError(x+1,ey)
        
        ascii.write('%s\t %s\t %s\n' % (lc.GetBinLowEdge(x+1),y,yexp))
        #print x,t,y,yexp
        pass
    ascii.close()
    lc.GetXaxis().SetRangeUser(tMin,tMax)
    lc_norm.GetXaxis().SetRangeUser(tMin,tMax)
    bkg.GetXaxis().SetRangeUser(tMin,tMax)
    
    lightCurveCanvas.cd(1)
    lc.Draw('e0')
    lightCurveCanvas.cd(2)
    bkg.SetMinimum(0)
    bkg.Draw()
    lightCurveCanvas.cd(3)
    lc_norm.Draw('e0')
    lightCurveCanvas.cd()
    lightCurveCanvas.Update()
    a=raw_input('press eneter to exit.')
    pass

if __name__=='__main__':
    if len(sys.argv)<2:
        print './makeExposureCorrectedLC.py lcfile.root exposure.root'
    else:
        base = sys.argv[1][:sys.argv[1].rfind('/')]
        
        lcfile   = TFile(sys.argv[1],'OPEN')
        exposure = TFile(sys.argv[2],'OPEN')    
        makeLC(lcfile,exposure)
        cmd = 'mv lc_exposure_corrected.txt %s/.' % base
        os.system(cmd)
        pass
    
    
    
