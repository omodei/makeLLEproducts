
#!/usr/bin/env python

from ROOT import *
import math
from makeFits import *
import sys,os

def makeRootDRM(ROOTfiles,
                NMC,NREC,NGEN,FLUX,
                DETNAM,DIRECTORY,
                DATAENERGYVAR,EMIN,EMAX,
                METMIN,METMAX,GRBNAME,
                INDEX,
                TRIGGER=0,
                MYCUT='1==1',
                OFFSET=0,   DURATION=0,KEYWORDS=None):
    # #################################################
    try: version=int(KEYWORDS['VERSION'])
    except: version=0
    distributions_filename='%s/gll_mcvar_bn%s_v%02d.png' % (DIRECTORY,GRBNAME[-9:],version)
    EnergyDispersion_filename='%s/gll_edisp_bn%s_v%02d.png' % (DIRECTORY,GRBNAME[-9:],version)
    PointSpreadFunction_filename='%s/gll_psf_bn%s_v%02d.png' % (DIRECTORY,GRBNAME[-9:],version)
    EffectiveArea_filename='%s/gll_effarea_bn%s_v%02d.png' % (DIRECTORY,GRBNAME[-9:],version)    
    DRM_RootFilename='%s/gll_DRM_bn%s_v%02d.root' % (DIRECTORY,GRBNAME[-9:],version)
    try:
        KEYWORDS['EDISP_PNG']   = EnergyDispersion_filename
        KEYWORDS['EFFAREA_PNG'] = EffectiveArea_filename
        KEYWORDS['MCVAR_PNG']   = distributions_filename
    except:
        pass
    
            
    
    
    myCut = MYCUT.replace('FswGamState','ObfGamState')
    DZ = 1
    LEMIN = log10(EMIN)
    LEMAX = log10(EMAX)
    print 'Energy interval (log10) : %s, %s' %(LEMIN,LEMAX)
    print '----------------------------------------------------------------------------'
    print ' Final Selection......: %s ' % myCut
    print '----------------------------------------------------------------------------'
    # ##################################################
    # LOADING FILES:
    # ##################################################
    
    CHAIN   = TChain('MeritTuple')
    JobInfo = TChain('jobinfo')
   
    for ROOTfile in ROOTfiles:
        print '----> %s ' % ROOTfile
        CHAIN.Add(ROOTfile)
        JobInfo.Add(ROOTfile)        
        pass
    
    
    BranchToActivate=['McEnergy','McLogEnergy','McZDir',
                      'ObfGamState','FswGamState',
                      'TkrNumTracks','Tkr1SSDVeto',
                      'GltEngine','GltGemEngine',
                      'CalEnergyRaw','VtxAngle','Tkr1FirstLayer',
                      'Acd2TriggerVeto','Acd2Tkr1VetoSigmaHit',
                      'Acd2VetoCount','Acd2VetoFaces','Acd2Tkr1TriggerEnergy45',
                      'CalNewCfpEnergy','CalCsIRLn']
    
    listOfBranches=CHAIN.GetListOfBranches()

    CHAIN.SetBranchStatus('*',0)
    CHAIN.SetBranchStatus('Evt*',1)
    CHAIN.SetBranchStatus('FT1*',1)
    CHAIN.SetBranchStatus('CTB*',1)
    CHAIN.SetBranchStatus('Pt*',1)
    for x in BranchToActivate:
        if x in listOfBranches: 
            CHAIN.SetBranchStatus(x,1)
            pass
        pass
    #CHAIN.SetBranchStatus('McEnergy',1)
    #CHAIN.SetBranchStatus('McLogEnergy',1)
    #CHAIN.SetBranchStatus('McZDir',1)
    #CHAIN.SetBranchStatus('ObfGamState',1)
    #CHAIN.SetBranchStatus('FswGamState',1)
    #CHAIN.SetBranchStatus('TkrNumTracks',1)
    #CHAIN.SetBranchStatus('Tkr1SSDVeto',1)
    #CHAIN.SetBranchStatus('GltEngine',1)
    #CHAIN.SetBranchStatus('GltGemEngine',1)
    #CHAIN.SetBranchStatus('CalEnergyRaw',1)
    #CHAIN.SetBranchStatus('VtxAngle',1)
    #CHAIN.SetBranchStatus('Tkr1FirstLayer',1)
    
    # ##################################################
    tmin=CHAIN.GetMinimum("EvtElapsedTime")
    tmax=CHAIN.GetMaximum("EvtElapsedTime")
    duration = (tmax-tmin)
    # ##################################################
    Ngenerated = NGEN*len(ROOTfiles)
    Ageo       = 60000. # cm^2
    NGEN_fromJobInfo = 0
    for i in range(len(ROOTfiles)):
        JobInfo.GetEntry(i)
        NGEN_fromJobInfo += JobInfo.generated
        pass
    print '***********************************************'
    print 'Number of generated events per file: %d' % NGEN
    print 'Number of generated events in the jobinfo: %d' % (NGEN_fromJobInfo/len(ROOTfiles))
    print '***********************************************'
    # I take the number of generated events from the MC file. 
    # Ngenerated = NGEN_fromJobInfo
    # ##################################################
    
    if TRIGGER==0: TRIGGER = tmin
    
    TMIN   = TRIGGER + OFFSET
    TMAX   = TMIN + DURATION
    
    if DURATION==0: TMAX   = tmax   
    
    if(tmin > TMIN or tmax < TMAX):
      print("\n\nWARNING: the requested tmin and tmax for the response are outside")
      print("         the time span covered by the MC. Cutting to that time span")
      TMIN   = max(tmin,TMIN)
      TMAX   = min(tmax,TMIN + DURATION)
      print("---> New TMIN = %s" %(TMIN-TRIGGER))
      print("---> New TMAX = %s" %(TMAX-TRIGGER))      
    pass

    DURATION = TMAX-TMIN
    NSCALE = DURATION/(tmax-tmin)

    TimeCut = 'EvtElapsedTime > %s && EvtElapsedTime < %s' % (TMIN,TMAX)
    # ##################################################        
    
    nMCFiles = len(ROOTfiles)
    print 'MC File : Tmin: %.3f, Tmax: %.3f, duration: %.3f x(%d)' %(tmin-TRIGGER,tmax-TRIGGER,tmax-tmin, nMCFiles)
    print 'DRM TIME: TMIN: %.3f, TMAX: %.3f, DURATION: %.3f x(%d), NSCALE=%.3f' %(TMIN-TRIGGER,TMAX-TRIGGER,DURATION, nMCFiles,NSCALE)
    

    
    ##################################################
    # PLOTS SOME DISTRIBUTIONS, mainly for tests
    ##################################################
    distributions=TCanvas("Distribution",DETNAM)
    
    NTimeBins = int(tmax-tmin)
    
    if int(tmax-tmin) > 864000:  NTimeBins = int((tmax-tmin)/86400.)        
    elif int(tmax-tmin) > 36000: NTimeBins = int((tmax-tmin)/3600.)      
    
    print '...defining the histograms...'    
    hTime_mc = TH1D('hTime_mc','Light Curve',NTimeBins,TMIN-TRIGGER,TMAX-TRIGGER)
    hTime_mc.SetFillColor(kGray)
    hTime_mc.SetLineColor(kRed)
    hTime_mc.GetXaxis().SetTitle('MC EvtElapsedTime')
    hTime_mc.GetYaxis().SetTitle('Exposure (cm^{2})')
    hTime_mc.GetXaxis().CenterTitle()
    hTime_mc.GetYaxis().CenterTitle()
    
    hTheta_mc= TH1D('hTheta_mc','Boresight angle',100,0,100)
    hTheta_mc.SetFillColor(kYellow)
    hTheta_mc.SetLineColor(kRed)
    hTheta_mc.GetXaxis().SetTitle('MC Angle from LAT boresight (degrees)')
    hTheta_mc.GetXaxis().CenterTitle()
    
    thetaphi_mc = TH2D('thetaphi_mc','Instrument Coordinates',360,0,360,90,0,90)
    thetaphi_mc.GetXaxis().SetTitle('Phi angle (degrees)')
    thetaphi_mc.GetYaxis().SetTitle('Theta angle (degrees)')
    thetaphi_mc.GetXaxis().CenterTitle()
    thetaphi_mc.GetYaxis().CenterTitle()
    
    #try: RA_OBJ    = float(KEYWORDS['RA_OBJ'])
    #except: RA_OBJ = 0
    
    #try: DEC_OBJ    = float(KEYWORDS['DEC_OBJ'])
    #except: DEC_OBJ = 0
    
    radec_mc = TH2D('radec_mc','Sky Map J2000',360,0,360,180,-90,90)
    radec_mc.GetXaxis().SetTitle('R.A. (deg)')
    radec_mc.GetYaxis().SetTitle('Dec. (deg)')
    radec_mc.GetXaxis().CenterTitle()
    radec_mc.GetYaxis().CenterTitle()
    
    distributions.Divide(2,2)

    distributions.cd(1)
    hTime_mc.Sumw2()
    CHAIN.Draw('EvtElapsedTime-%s>>hTime_mc' % TRIGGER,myCut,"E0")
    
    hTime_mc.Scale(Ageo/(Ngenerated)) # *int(tmax-tmin)) # This is cm^2
    
    lStart = TLine(TMIN-TRIGGER,0,TMIN-TRIGGER,hTime_mc.GetMaximum())
    lEnd   = TLine(TMAX-TRIGGER,0,TMAX-TRIGGER,hTime_mc.GetMaximum())
    
    lStart.SetLineStyle(2)
    lEnd.SetLineStyle(2)
    lStart.Draw()
    lEnd.Draw()
    gPad.Update()

    distributions.cd(2)
    CHAIN.Draw('FT1Theta>>hTheta_mc','(%s) && (%s)' %(myCut,TimeCut),'E0')
    
    distributions.cd(3)
    CHAIN.Draw('FT1Theta:FT1Phi>>thetaphi_mc','(%s) && (%s)' %(myCut,TimeCut),'colz')
    gPad.SetLogz()
    
    distributions.cd(4)
    CHAIN.Draw('FT1Dec:FT1Ra>>radec_mc','(%s) && (%s)' %(myCut,TimeCut),'colz')
    gPad.SetLogz()
    
    distributions.Update()
    distributions.Print(distributions_filename)
    
    
    ##################################################
    # PLOT ENERGY VALIDATION
    ##################################################
    emin = 10
    emax = 10000
    Nbin = 9
    h_de=[]
    EnergyDispersion=TCanvas("EnergyValidation",DETNAM,800,800)
    EnergyDispersion.Divide(3,3)
    for i in range(Nbin):
        e1   = emin *pow(emax/emin,1.0*(i)/(Nbin))
        e2   = emin *pow(emax/emin,1.0*(i+1)/(Nbin))
        h_de.append(TH1D("h_%i" % i,"McEnergy>%.1f && McEnergy<%.1f " % (e1,e2), 50,-1,1))
        EnergyDispersion.cd(i+1)
        CHAIN.Draw('(%s-McEnergy)/McEnergy>>h_%i' %(DATAENERGYVAR,i) ,'(%s) && (%s) && McEnergy>%s && McEnergy< %s'%(myCut,TimeCut,e1,e2),"E1")
        h_de[-1].SetMarkerStyle(20)
        h_de[-1].SetMarkerColor(kRed)
        h_de[-1].GetXaxis().SetTitle("(%s-McEnergy)/McEnergy" % (DATAENERGYVAR))
        #label=TLatex(0.6,0.7,'[%i - %i] MeV' % (e1,e2))
        #label.Draw()                     
        pass
    
    
    EnergyDispersion.Print(EnergyDispersion_filename)

    # #################################################    
    #print 'Ngenerated/Ageo= ',Ngenerated/Ageo,'F*duration*nMCFiles= ',10.0*(duration*nMCFiles)*1.0e-4
    #print 'Nselected events: %.0f' % NEVENTS

    # #################################################    
    #       PSF ANALYSIS
    # #################################################
    '''
    PointSpreadFunction=TCanvas("PointSpreadFunction",DETNAM,1200,800)
    
    PointSpreadFunction.Divide(2,2)

    nTheta=90

    mcTheta=TH1D('mcTheta','',nTheta,0,90)
    reTheta=TH1D('reTheta','',nTheta,0,90)
    diTheta=TH1D('diTheta','',nTheta,0,90)
    InTheta=TH1D('InTheta','',nTheta,0,90)

    mcTheta1=TH1D('mcTheta1','',nTheta,0,90)
    reTheta1=TH1D('reTheta1','',nTheta,0,90)
    diTheta1=TH1D('diTheta1','',nTheta,0,90)
    InTheta1=TH1D('InTheta1','',nTheta,0,90)

    mcTheta1.SetLineColor(2)
    reTheta1.SetLineColor(2)
    diTheta1.SetLineColor(2)
    InTheta1.SetLineColor(2)

    InTheta.SetLineStyle(2)
    InTheta1.SetLineStyle(2)
    
    cutMc='(57.295*acos(-McZDir))>>mcTheta'
    cutRe='FT1Theta>>reTheta'
    cutDi='abs((57.295*acos(-McZDir)) - FT1Theta)>>diTheta'

    cutMc1='(57.295*acos(-McZDir))>>mcTheta1'
    cutRe1='FT1Theta>>reTheta1'
    cutDi1='abs((57.295*acos(-McZDir)) - FT1Theta)>>diTheta1'

        
    PointSpreadFunction.cd(1)
    CHAIN.Draw(cutMc)
    CHAIN.Draw(cutMc1,'(%s) && (%s)' %(myCut,TimeCut),'same')
    PointSpreadFunction.cd(2)
    CHAIN.Draw(cutRe)
    CHAIN.Draw(cutRe1,'(%s) && (%s)' %(myCut,TimeCut),'same')
    PointSpreadFunction.cd(3)
    CHAIN.Draw(cutDi)
    CHAIN.Draw(cutDi1,'(%s) && (%s)' %(myCut,TimeCut),'same')

    Ntot = 0
    Ntot1 = 0
    for i in range(nTheta):
        Ntot=Ntot+diTheta.GetBinContent(i+1)
        Ntot1=Ntot1+diTheta1.GetBinContent(i+1)
        
    print Ntot,Ntot1
    
    InTheta.SetBinContent(1,diTheta.GetBinContent(1)/Ntot)    
    InTheta1.SetBinContent(1,diTheta1.GetBinContent(1)/Ntot1)    
    
    for i in range(nTheta-1):
        temp=InTheta.GetBinContent(i+1)
        InTheta.SetBinContent(i+2,temp+diTheta.GetBinContent(i+2)/Ntot)

        temp=InTheta1.GetBinContent(i+1)
        InTheta1.SetBinContent(i+2,temp+diTheta1.GetBinContent(i+2)/Ntot1)
        pass
    


    PointSpreadFunction.cd(4)
    InTheta.SetMaximum(1.0)
    InTheta1.SetMaximum(1.0)
    InTheta.Draw()
    InTheta1.Draw('same')
    PointSpreadFunction.Update()
    PointSpreadFunction.Print(PointSpreadFunction_filename)
    '''
    
    # ##################################################
    print '''
    ##################################################    
    #      MAKE THE DETECTOR RESPONSE MATRIX
    ##################################################    
    '''
    print 'INDEX = ', INDEX
    if NGEN>0: print 'WILL USE THE NUMBER OF GENERATED EVENTS (%s)'% (Ngenerated/len(ROOTfiles))
    else:      print 'WILL USE THE GENERATED FLUX (%s) ph/m^2/s'   % FLUX
    print ' NUMBER OF MC ENERGY BINS: %s FROM %s TO %s MEV' %(NMC,EMIN,EMAX)
    print ' NUMBER OF RECONSTRUCTED ENERGY BINS: %s FROM %s TO %s MEV' %(NREC,EMIN,EMAX)
    
    DRM  = TH2D("DRM","Detector Response Matrix",NMC,LEMIN,LEMAX,NREC,LEMIN,LEMAX)    
    AEFF = TH1D("AEFF","Effective Area",NMC,LEMIN,LEMAX)
    
    AEFF.SetLineColor(kGreen)
    AEFF.SetMarkerStyle(20)
    
    DRM.GetXaxis().SetTitle('McLogEnergy [MeV]')    
    DRM.GetYaxis().SetTitle('log10(%s)' % DATAENERGYVAR)
    DRM.GetXaxis().CenterTitle()
    DRM.GetYaxis().CenterTitle()
    
    AEFF.GetXaxis().SetTitle('McLogEnergy')
    AEFF.GetYaxis().SetTitle('Effective Area [cm^2]')
    AEFF.GetXaxis().CenterTitle()
    AEFF.GetYaxis().CenterTitle()
    
    C=TCanvas("DRM_CANVAS",DETNAM)
    C.Divide(1,2)
    C.cd(1)
    gPad.SetLogz()
    CHAIN.Draw('log10(%s):McLogEnergy>>DRM' % DATAENERGYVAR, '(%s) && (%s)' %(myCut,TimeCut),'colz')
    C.cd(2)
    CHAIN.Draw('McLogEnergy>>AEFF','(%s) && (%s)' %(myCut,TimeCut))
    AEFF.SetMinimum(0)
    AEFF.SetMaximum(1e4)
    # i == x
    # j == y
    

    for i in range(NMC):
        LE1=AEFF.GetBinLowEdge(i+1)
        LE2=LE1+AEFF.GetBinWidth(i+1)
        
        Ni = AEFF.GetBinContent(i+1)
        
        emin=pow(10.0,LE1)
        emax=pow(10.0,LE2)
        
        DE=0.0
        
        if INDEX ==  -1:
            DE=(LE2-LE1)/(LEMAX-LEMIN)
        else:
            DE=(pow(emin,INDEX+1)-pow(emax,INDEX+1))/(pow(EMIN,INDEX+1)-pow(EMAX,INDEX+1)) # < 1            
            # (1./emin - 1./emax)/(1./EMIN-1./EMAX) # < 1
            pass
        
        flux = FLUX * 1.e-04 * DE  * DZ * NSCALE # /cm2/s in the considered energy bin        
        Neff = Ngenerated      * DE  * DZ * NSCALE
        
        if NGEN>0:
            Ai = Ni *Ageo/Neff # cm^2
        else:
            Ai = Ni/(flux*duration*nMCFiles) # cm^2
            pass
        #if Ai<0:
        #    print '##################################################'
        #    print '#           ERROR AEFF<0 !!!!!!!!                #'
        #    print '##################################################'
        AEFF.SetBinContent(i+1,Ai)

        for j in range(NREC):
            Mij  = DRM.GetBinContent(i+1,j+1)     
            if NGEN>0:
                Aij  = Mij * Ageo/Neff # cm^2
            else:
                Aij = Mij/(flux*duration*nMCFiles) # cm^2
                pass
            DRM.SetBinContent(i+1,j+1,Aij)
            pass
        if (i % (NMC/10))==0:
            sys.stdout.write('*')
            sys.stdout.flush()
            pass
        pass

    C.cd(1)
    DRM.Draw('colz')
    C.cd(2)
    AEFF.Draw('e0')
    C.Update()
    C.Print(EffectiveArea_filename)

    #a=raw_input('')
    print 'NOW GENERATING FITS FILE...'
    filename = fitsDRM(DRM,DETNAM,DIRECTORY,TRIGGER, METMIN,METMAX, TMIN, TMAX, GRBNAME, KEYWORDS)
    print 'Done!'
    ##################################################
    # OPEN AN OUTPUT FILE
    ##################################################
    print 'saving the histograms in the file: %s' %(DRM_RootFilename)    
    ftemp = TFile('%s' %(DRM_RootFilename),'RECREATE')
    
    hTime_mc.Write()
    thetaphi_mc.Write()
    #radec_mc.Write()    
    for i in range(Nbin):
        h_de[i].Write()
        pass
    DRM.Write()
    AEFF.Write()
    
    ftemp.Close()
    return filename
