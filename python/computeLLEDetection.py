#!/usr/bin/env python
import os,sys,glob,math
import utils
import pyfits
import config
import LLEutils 
#ftp_base_path='ftp://legacy.gsfc.nasa.gov/fermi/data/gbm/triggers'
import makeLLE
import ROOT

########################################################
# Classes Definition
########################################################

########################################################
if __name__=='__main__':
    ###############################
    # SETUP THE GPLTools:    
    try:     GPL = os.environ['GPL_SCRIPTS']
    except:  GPL = "/afs/slac.stanford.edu/g/glast/ground/PipelineConfig/GPL/python"        
    print "GPL = ",GPL
    sys.path.insert(0, GPL)
    from floop import *    
    # All-important check that we are running an adequate version of python
    print "Check we're running adequate version of python...\n"
    floop()    
    # Second, is the location of GPLtools package
    ## See if GPLtools location defined by taskConfig.xml
    try:    GPL2 = os.environ['GPL2']
    except: GPL2 = "/afs/slac.stanford.edu/g/glast/ground/PipelineConfig/GPLtools/prod/"
    os.environ['GPL2']=GPL2    
    print "GPL2 = ",GPL2
    execfile(GPL2+'/python/GPLinit.py')
    from GPL import *
    
    
    ###############################
    # DEFINING THE STAGING DIRECTORY:
    OUTPUT_NAME       = os.getenv('OUTPUT_NAME','GRBYYMMDDFFF')
    VERSION           = int(os.getenv('VERSION','0'))
    GPL_DATADIR       = os.getenv('GPL_DATADIR','TEST_%(VERSION)02d' % locals())    
    
    OUTPUT_DIR  = '%s/%s/v%02d' %(GPL_DATADIR,OUTPUT_NAME,VERSION)
    TRIGGER_NAME=OUTPUT_NAME[-9:]
    LLE_RESULTS = '%(OUTPUT_DIR)s/gll_results_bn%(TRIGGER_NAME)s_v%(VERSION)02d.txt' % locals()
    print 'LLE_RESULTS = ',LLE_RESULTS

    GPL2_MESSAGELVL   = os.getenv('GPL2_MESSAGELVL','DEBUG')
    
    if GPL2_MESSAGELVL=='DEBUG':
        for x in sorted(os.environ.keys()): print '%s=%s' %(x,os.environ[x])        
        pass
    
    ###############################
    # READ THE RESULT FILE:
    res = LLEutils.ResultFile(LLE_RESULTS)
    
    print 'LLE_RESULTS file: %s' % LLE_RESULTS
    if GPL2_MESSAGELVL=='DEBUG': res.Print()
    resd = res.get()
    
    OUTPUT_DIR   = resd['OUTPUT_DIR']    
    version      = int(resd['VERSION'])
    OBJECT       = resd['OBJECT']
    TRIGGER_NAME = resd['TRIGGER_NAME']
    TRIGTIME     = float(resd['TRIGTIME'])
    RA           = float(resd['RA'])
    DEC          = float(resd['DEC'])
    DURATION     = float(resd['DURATION'])
    OFFSET       = float(resd['OFFSET'])
    DT           = float(resd['DT'])
    BEFORE       = float(resd['BEFORE'])
    AFTER        = float(resd['AFTER'])
    RADIUS       = float(resd['RADIUS'])
    ZENITHMAX    = float(resd['ZENITHMAX'])
    THETAMAX     = float(resd['THETAMAX'])
    FT2          = resd['FT2']
    #myMode       = 'pha'
    
    # ##################################################
    # DEFINING THE STAGING DIRECTORY:
    # ##################################################

    STAGEDIR   = '/scratch/computeLLEDetection_%s' %(OBJECT)
    #  STAGING THE FILES...
    stageSet = stageFiles.StageSet(STAGEDIR)    
    log.debug('Calling getStageDir()...')
    stageDir = stageSet.getStageDir()
    log.info("Staging to "+stageDir)

    #STAGE IN:        
    log.debug("STAGE IN...")
    FT2_s = stageSet.stageIn(FT2)
    lle_file='%(OUTPUT_DIR)s/gll_lle_bn%(TRIGGER_NAME)s_v%(version)02d.fit'% locals()

    detected   = 0
    significance = 0
    t_first    = -666
    t_last     = -666

    if os.path.exists(lle_file):        
        fitsFile = stageSet.stageIn(lle_file)
        
        # STAGE OUT:
        log.debug("STAGE OUT...")
        canvasName='%(OUTPUT_DIR)s/gll_detect_bn%(TRIGGER_NAME)s_v%(version)02d.png'% locals()
        canvasName_s = stageSet.stageOut(canvasName)
        # COMPUTE THE DETECTION:
        import computeSimpleDetection
        
        XMIN_SIG=-10
        XMAX_SIG=300
        NSIGMA=4.0
        
        if 'SFL' in OBJECT:
            XMIN_SIG=-10
            XMAX_SIG=200
            pass
        
        ThetaGraph=computeSimpleDetection.GetThetaGraph(FT2_s,-BEFORE,AFTER,RA,DEC,TRIGTIME)
        ThetaGraph.SetLineColor(ROOT.kBlue)
        ThetaGraph.SetLineWidth(2)
        ThetaGraph.SetMinimum(0)
        ThetaGraph.SetMaximum(90)
    
        dts = [0.1,1.0,3.0,10.0]
        histos=[]
        graphs=[]    
        
        for i,dt in enumerate(dts): histos.append(computeSimpleDetection.makeLC(fitsFile,'histo_%d' % i,t0=TRIGTIME, dt=dt))
        XMIN,XMAX = LLEutils.GetTimeMinMax(fitsFile)    
        XMIN = XMIN - TRIGTIME
        XMAX = XMAX - TRIGTIME
    
        histo_bkg        = None
        histo_prob       = None
        #histo_prob_poiss = None
        for i,histo in enumerate(histos):
            histo_bkg_i, histo_prob_i, histo_prob_poiss_i, significance_i, significance_poiss_i, t_first_i, t_last_i = computeSimpleDetection.detectExcess2(histo,ThetaGraph,
                                                                                                                                                            XMIN_SIG=XMIN_SIG,
                                                                                                                                                            XMAX_SIG=XMAX_SIG,
                                                                                                                                                            NSIGMA=NSIGMA)
            duration=t_last_i-t_first_i
            print '* DT=%10.2f *** SIG: %5.1f FROM %5.1f TO %5.1f ***' %(dts[i],significance_i,t_first_i, t_last_i)
            # 2nd iteration:
            if t_last_i>t_first_i:
                FUN='pol9'
                histo_bkg_i, histo_prob_i, histo_prob_poiss_i, significance_i, significance_poiss_i, t_first_i, t_last_i = computeSimpleDetection.detectExcess2(histo,ThetaGraph,
                                                                                                                                                                XMIN_SIG=t_first_i,
                                                                                                                                                                XMAX_SIG=t_last_i,
                                                                                                                                                                NSIGMA=NSIGMA,FUN=FUN)
                
                print '* REITERATION: %s DT=%10.2f *** SIG: %5.1f FROM %5.1f TO %5.1f ***' %(FUN,dts[i],significance_i,t_first_i, t_last_i)
                pass
            
            if significance_i > significance:
                histo_bkg     = histo_bkg_i
                histo_prob    = histo_prob_i
                #histo_prob_poiss = histo_prob_poiss_i
                significance  = significance_i
                t_first       = t_first_i
                t_last        = t_last_i
                pass
            pass
        
        
        lines=[]
        if significance > NSIGMA:
            detected=1        
            print '* DETECTED!!! SIG: %5.1f FROM %5.1f TO %5.f ***' %(significance,t_first, t_last)                
            pass
        if significance>0:
            C=ROOT.TCanvas(OBJECT,OBJECT,1000,1200)
            C.Divide(1,4)
            C.cd(1)
            
            for i,histo in enumerate(histos):
                histo.Scale(1./dts[i])
                histo.SetLineColor(i+1)                                                            
                if i==0: histo.Draw('E0')
                else:    histo.Draw('E0same')
                if detected:
                    l=ROOT.TLine(t_first,0,t_first,histo.GetMaximum())
                    l.SetLineStyle(2)
                    lines.append(l)
                    l.Draw()
                    
                    l=ROOT.TLine(t_last,0,t_last,histo.GetMaximum())
                    l.SetLineStyle(2)
                    lines.append(l)
                    l.Draw()
                    pass
                pass
            C.cd(2)
            # ROOT.gPad.SetLogy()
            histo_bkg.Draw()
            if detected:
                l=ROOT.TLine(t_first,0,t_first,histo_bkg.GetMaximum())
                l.SetLineStyle(2)
                lines.append(l)
                l.Draw()
                
                l=ROOT.TLine(t_last,0,t_last,histo_bkg.GetMaximum())
                l.SetLineStyle(2)
                lines.append(l)
                l.Draw()
                pass
            C.cd(3)
            histo_prob.Draw()
            if detected:
                l=ROOT.TLine(t_first,0,t_first,histo_prob.GetMaximum())
                l.SetLineStyle(2)
                lines.append(l)
                l.Draw()
                
                l=ROOT.TLine(t_last,0,t_last,histo_prob.GetMaximum())
                l.SetLineStyle(2)
                lines.append(l)
                l.Draw()                
                pass
            C.cd(4)
            Frame=ROOT.TGraph()
            Frame.SetPoint(0,XMIN,0)
            Frame.SetPoint(1,XMAX,90)
            if detected:
                l=ROOT.TLine(t_first,0,t_first,90)
                l.SetLineStyle(2)
                lines.append(l)
                l.Draw()
                
                l=ROOT.TLine(t_last,0,t_last,90)
                l.SetLineStyle(2)
                lines.append(l)
                l.Draw()
                pass
            Frame.Draw('ap')
            ThetaGraph.Draw('l')
            C.cd()
            ROOT.gPad.Update()
            C.Print(canvasName_s)
            pass
        pass
    res.setv('DETECTED',detected)
    res.setv('DETECT_SIGNIFICANCE',significance)
    res.setv('DETECT_TFIRST',t_first)
    res.setv('DETECT_TLAST',t_last)
    res.save()
    res.Print()
    #output_report_file = file(detection_results_s,'w')
    #output_report_file.write('SIGNIFICANCE=%s\n' % significance)
    #output_report_file.write('TSTART=%s\n' % t_first)
    #output_report_file.write('TEND=%s\n' % t_last)
    #output_report_file.close()
    log.info('SIGNIFICANCE=%s\n' % significance)
    log.info('TSTART=%s\n' % t_first)
    log.info('TEND=%s\n' % t_last)
    log.debug('About to list stageDir...')
    stageSet.listStageDir()
    stagerc = stageSet.finish("alldone")      
    log.info('Return from stageSet.finish = '+str(stagerc))        
    pass
