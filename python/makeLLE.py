#!/usr/bin/env python
import os,sys,glob,ROOT,math
import utils
import pyfits

#ftp_base_path='ftp://legacy.gsfc.nasa.gov/fermi/data/gbm/triggers'

_OFFSET      = 0.0
_DT          = 1.0
_ZENITHMAX   = 90
_THETAMAX    = 90
_BEFORE      = 1000
_AFTER       = 1000
_NSIGMA      = 4.0
_interactive = 0
_pipeline    = 0
_THETA_MIN   = 89
_RADIUS      = -1

# DIRECTORIES:
outputDir            = 'GBM_TriggerCatalog'
dirMCGenerated       = 'Generated'
dirMCToGenerateFiles = 'ToGenerate'

LLE_TIMEWINDOWS_DEF={'160625945':(-16.549,183.451, 183.451, 243.451, 243.451, 324.325),
                     '130828306':(-269.588, 3.312, -1.688,  150 ,159.762, 842.012),
                     '150416773':(-200,-50,-50,100,100,200),
                     '160509374':(-100,0,0,40,40,100),
                     '101014175':(0,200,205,215,215,300),
                     '170409112':(-750,100,100,350,350,500),
                     '110903111':(-1000,0,0,300,300,1000),
                     '120526303':(0,600,600,800,800,1000),
                     '120624933':(-200,0,0,50,50,250),
                     '100116897':(-250,50,50,120,200,300),
                     '160101215':(-100,-10,-10,100,100,200)
                     }


def GetThetaMin():
    return _THETA_MIN

def UpdateArchive():
    print '################### UPDATE ARCHIVE ################### '
    #_fsscbase='wger
    cmd='wget -rc "ftp://legacy.gsfc.nasa.gov/fermi/data/gbm/triggers/" -A"*tcat*" --no-remove-listing -N -P %s' % outputDir
    print cmd
    os.system(cmd)
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

def GenerateMC(output_ez, version, GRBNAME,MET, RA,DEC,DURATION,mode):
    print '--------------------------------------------------: Generation of the TEXT file to be used in the generation of LLE Montecarlo DATA'
    MCToGenerateFile = '%s/%s/v%02d/%s/%s.txt' % (output_ez,GRBNAME,version,dirMCToGenerateFiles,GRBNAME)
    os.system('mkdir -pv %s/%s/v%02d/%s' % (output_ez,GRBNAME,version,dirMCToGenerateFiles))
    #fileOutput='%s/%s.txt' % (dirMCToGenerateFiles,GRBNAME)

    txt = "# Configuration file for %s\n" % GRBNAME
    txt+="NAME                      = '%s'\n" % GRBNAME
    txt+="DURATION                  = %.2f\n" % DURATION
    txt+="MET                       = %.4f\n" % MET
    txt+="RA                        = %.4f\n" % RA
    txt+="DEC                       = %.4f\n" % DEC
    if 'forReal' in mode:
        fout=file(MCToGenerateFile,'w')
        fout.write(txt)
        print 'file saved in %s' % MCToGenerateFile
    else:
        print txt
        pass
    return 1


def GenerateLLE(output_ez,version,GRBNAME,MET, RA,DEC,DURATION,
                OFFSET=_OFFSET, DT=_DT ,
                BEFORE=_BEFORE, AFTER=_AFTER,
                ZENITHMAX=_ZENITHMAX,
                THETAMAX=_THETAMAX,RADIUS=_RADIUS,mode=['pha']):
    mymode=[]
    for x in mode: mymode.append(x)
    
    print '###################  GenerateLLE: ',GRBNAME,MET, RA,DEC,DURATION,OFFSET,DT,BEFORE,AFTER,ZENITHMAX,THETAMAX,mymode,output_ez,RADIUS
    print 'pha: ',glob.glob('%s/%s/v%02d/gll_cspec*pha' % (output_ez,GRBNAME,version))
    print 'ft1: ',glob.glob('%s/%s/v%02d/gll_lle*fit' % (output_ez,GRBNAME,version))
    print 'rsp: ',glob.glob('%s/%s/v%02d/gll_cspec*rsp' % (output_ez,GRBNAME,version))
    
    if not 'regenerate' in mymode:
        if 'pha' in mymode and len(glob.glob('%s/%s/v%02d/gll_cspec*pha' % (output_ez,GRBNAME,version)))>0 and len(glob.glob('%s/%s/v%02d/gll_lle*fit' % (output_ez,GRBNAME,version)))>0:
            print 'PHA File and FT1 file already generated:'
            mymode.remove('pha')
            pass
        if 'drm' in mymode and len(glob.glob('%s/%s/v%02d/*rsp' % (output_ez,GRBNAME,version))):
            print 'DRM File already generated:'
            mymode.remove('drm')
            pass
        pass
    myMode=0
    if 'drm' in mymode and 'pha' in mymode: myMode='lle' 
    elif 'drm' in mymode: myMode='drm'
    elif 'pha' in mymode: myMode='pha'
    #print 'computig...',myMode
    LLEIFILE  = os.getenv('LLEIFILE','/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/makeLLEproducts/python/config_LLE_DRM/Pass8.txt')
    MCBASEDIR = os.getenv('MCBASEDIR','/MC-Tasks/ServiceChallenge/GRBSimulator-Pass8')
    print 'LLEIFILE.....: %s ' % LLEIFILE
    print 'MCBASEDIR....: %s ' % MCBASEDIR
    if myMode:
        cmd='python -m mkdrm_ez -i %(LLEIFILE)s -outdir %(output_ez)s/%(GRBNAME)s/v%(version)02d/ -v %(version)d ' %locals()
        cmd+='-mcbase %(MCBASEDIR)s '% locals()
        cmd+='-ra %(RA).4f -dec %(DEC).4f -n %(GRBNAME)s -t %(MET).4f -d %(DURATION).1f -off %(OFFSET)s -dt %(DT)s -b %(BEFORE)s -a %(AFTER)s -r %(RADIUS)s -zenith %(ZENITHMAX)s -theta %(THETAMAX)d -m %(myMode)s' % locals()
        print '----------------------------------------------------------------------------------------------------'
        print cmd
        print '----------------------------------------------------------------------------------------------------'
        if _pipeline:
            os.system('rm logfiles/%s.log' % GRBNAME)
            cmd=('bsub -J GEN_LLE_%s -o logfiles/%s.log -q long %s ' % (GRBNAME,GRBNAME,cmd))
            pass
        if 'forReal' in mymode: os.system(cmd)
        else: print cmd
    else:
        print 'Nothing to do :-('
        pass
    return 1


def ComputeBBBDetection(output_ez,version,OBJECT,FT2,search_window='-20 200',theta_max=88,zenith_max=105,off_pulse_intervals='-50 -5 150 500'):
    lle_file = glob.glob('%s/%s/v%02d/gll_lle*fit' % (output_ez,OBJECT,version))[0]
    OUTFILE  = lle_file.replace('_lle','_bbbd').replace('.fit','.py')
    # default -400 - 20 and 150 - 500 
    cmd_detection='bbbd_lle.py --lle %(lle_file)s --pt %(FT2)s --p0 1e-3 --outfile %(OUTFILE)s --search_window %(search_window)s --theta_max %(theta_max)s --zenith_max %(zenith_max)s --off_pulse_intervals %(off_pulse_intervals)s' % locals()
    #[--search_window SEARCH_WINDOW [SEARCH_WINDOW ...]]
    #               [--binsize BINSIZE] [--cut CUT] [--theta_max THETA_MAX]
    #               [--poly_degree POLY_DEGREE] [--nbkgsim NBKGSIM]
    #               [--off_pulse_intervals OFF_PULSE_INTERVALS [OFF_PULSE_INTERVALS ...]]'
    print cmd_detection
    os.system(cmd_detection)
    file_to_move=['gll_lle_bn%s_v%02d_mkt.fit' % (OBJECT,version),
                  'optimal_lc_%s.png' %(OBJECT),
                  'bkgfit_%s.png' %(OBJECT),
                  'bb_res_%s.png' %(OBJECT)]
    for x in file_to_move: os.system('mv %s %s/%s/v%02d/.' % (x,output_ez,OBJECT,version))
    import json
    data = json.load(open(OUTFILE))
    lle_t0=0
    lle_t1=0
    success=(data['final status'] == 'success')
    if data['detected']:
        bloks= data['blocks'].split(',')
        lle_t0=float(bloks[1])
        lle_t1=float(bloks[-2])
        pass
    if success: detected=int(data['detected'])
    else: detected=-1

    return detected, data['highest net rate significance'],data['highest net rate tstart'],data['highest net rate tstop'],data['highest net rate background error'],lle_t0,lle_t1



def ComputeLLEDetection(output_ez,version,OBJECT,FT2,RA_OBJ,DEC_OBJ,TRIGTIME,NSIGMA,DTS = [0.1,0.3,1.0,3.0,10.0],DSS=[0.0],XMIN_SIG=-5,XMAX_SIG=150):
    use_gauss=0
    print '###################  ComputeLLEDetection: ',output_ez,OBJECT,FT2,RA_OBJ,DEC_OBJ,TRIGTIME,NSIGMA
    import computeSimpleDetection
    detected     = 0
    SIGNIFICANCE = 0
    t_first      = -666
    t_last       = -666
    
    list = glob.glob('%s/%s/v%02d/gll_lle*fit' % (output_ez,OBJECT,version))
    if len(list)==0:
        print 'No FT1 file found !!!!'
        return SIGNIFICANCE,t_first,t_last
    output_report_file_name   = '%s/%s/v%02d/results.txt' %(output_ez,OBJECT,version)
    if os.path.exists(output_report_file_name):
        try:
            output_report_file = file(output_report_file_name,'r')
            lines = output_report_file.readlines()
            SIGNIFICANCE=float(lines[0].split('=')[1].strip())            
            t_first = float(lines[1].split('=')[1].strip())
            t_last  = float(lines[2].split('=')[1].strip())        
            if SIGNIFICANCE>NSIGMA: detected=1
            print 'LLE DETECTION ALREADY COMPUTED. SAVED RESULTS READ FROM FILE: %s' % output_report_file
            print ' .....SIGNIFICANCE... %.2f' % SIGNIFICANCE
            print ' .....T START........ %.2f' % t_first
            print ' .....T END.......... %.2f' % t_last
            return SIGNIFICANCE,t_first,t_last
        except:
            print 'FILE %s FOUND BUT SIGNIFICANCE NOT FOUND. RECOMPUTING...' % output_report_file_name
            pass
        pass
    
    ThetaGraph=computeSimpleDetection.GetThetaGraph(FT2,-_BEFORE,_AFTER,RA_OBJ,DEC_OBJ,TRIGTIME)
    ThetaGraph.SetLineColor(ROOT.kBlue)
    ThetaGraph.SetLineWidth(2)
    ThetaGraph.SetMinimum(0)
    ThetaGraph.SetMaximum(90)

    
    
    histos=[]
    graphs=[]    
    fitsFile = list[0]
    
    dt_ds=[(dt, ds) for dt in DTS for ds in DSS]
    XMIN,XMAX = GetTimeMinMax(fitsFile)    
    XMIN = XMIN - TRIGTIME
    XMAX = XMAX - TRIGTIME
    histo_bkg    = None
    histo_prob   = None
    histo_prob2   = None
    significance = 0
    
    for i,(dt,ds) in enumerate(dt_ds): 
        _histo=computeSimpleDetection.makeLC(fitsFile,'histo_%d' % i,t0=TRIGTIME, dt=dt,ds=ds)
        histos.append(_histo)        
        histo_bkg_i, histo_prob_i, histo_prob2_i, sign_gauss_i, sign_poiss_i, t_first_i, t_last_i = computeSimpleDetection.detectExcess2(_histo,ThetaGraph,
                                                                                                                                         XMIN_SIG=XMIN_SIG,
                                                                                                                                         XMAX_SIG=XMAX_SIG,
                                                                                                                                         NSIGMA=NSIGMA,gauss=use_gauss)
        duration=t_last_i-t_first_i
        print '* DT=%10.2f DS=%10.2f *** SIG [G]: %5.1f [P]: %5.1f FROM %5.1f TO %5.1f ***' %(dt,ds,sign_gauss_i, sign_poiss_i,t_first_i, t_last_i)
        # 2nd iteration:
        if t_last_i>t_first_i:
            FUN='pol3'
            histo_bkg_i, histo_prob_i, histo_prob2_i, sign_gauss_i, sign_poiss_i, t_first_i, t_last_i = computeSimpleDetection.detectExcess2(_histo,ThetaGraph,
                                                                                                                                             XMIN_SIG=t_first_i,
                                                                                                                                             XMAX_SIG=t_last_i,
                                                                                                                                             NSIGMA=NSIGMA,FUN=FUN,gauss=use_gauss)
            
            print '* REITERATION %s DT=%10.2f DS=%10.2f *** SIG [G]: %5.1f [P]: %5.1f FROM %5.1f TO %5.1f ***' %(FUN, dt,ds,sign_gauss_i, sign_poiss_i,t_first_i, t_last_i)
            pass
        if use_gauss: significance_i=sign_gauss_i
        else:         significance_i=sign_poiss_i

        if significance_i > significance:
            histo_bkg     = histo_bkg_i
            histo_prob    = histo_prob_i
            histo_prob2   = histo_prob2_i
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
        _xmin=t_first-10*histo_prob.GetBinWidth(1)
        _xmax=t_first+10*histo_prob.GetBinWidth(1)
        for i,histo in enumerate(histos):
            (dt,ds)=dt_ds[i]
            histo.Scale(1./dt)
            histo.SetLineColor(i+1)                                                            
            if i==0: histo.Draw('E0')
            else:    histo.Draw('E0same')
            if detected:
                duration = (t_last-t_first)
                histo.GetXaxis().SetRangeUser(_xmin,_xmax)
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
            duration = (t_last-t_first)
            histo_bkg.GetXaxis().SetRangeUser(_xmin,_xmax)

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
        histo_prob2.Draw("same")
        if detected:
            duration = (t_last-t_first)
            histo_prob.GetXaxis().SetRangeUser(_xmin,_xmax)
            histo_prob2.GetXaxis().SetRangeUser(_xmin,_xmax)

            l=ROOT.TLine(t_first,0,t_first,histo_prob.GetMaximum())
            l.SetLineStyle(2)
            if use_gauss: l.SetLineColor(ROOT.kRed)
            else:         l.SetLineColor(ROOT.kGreen)
            lines.append(l)
            l.Draw()
            
            l=ROOT.TLine(t_last,0,t_last,histo_prob.GetMaximum())
            if use_gauss: l.SetLineColor(ROOT.kRed)
            else:         l.SetLineColor(ROOT.kGreen)
            l.SetLineStyle(2)
            lines.append(l)
            l.Draw()
            
            pass
        C.cd(4)
        Frame=ROOT.TGraph()
        if detected:
            duration = (t_last-t_first)
            Frame.SetPoint(0,t_first-2*duration,0)
            Frame.SetPoint(1,t_last+3*duration,90)

            l=ROOT.TLine(t_first,0,t_first,90)
            l.SetLineStyle(2)
            lines.append(l)
            l.Draw()
            
            l=ROOT.TLine(t_last,0,t_last,90)
            l.SetLineStyle(2)
            lines.append(l)
            l.Draw()

        else:
            Frame.SetPoint(0,XMIN,0)
            Frame.SetPoint(1,XMAX,90)
            pass
        Frame.Draw('ap')
        ThetaGraph.Draw('l')
        
        C.cd()
        ROOT.gPad.Update()
        if _interactive:   a=raw_input('Continue')
        stringName=OBJECT[-9:]
        C.Print('%s/%s/v%02d/gll_detec_bn%s_v%02d.png' %(output_ez,OBJECT,version,stringName,version))
        pass
    
    output_report_file = file(output_report_file_name,'w')
    output_report_file.write('SIGNIFICANCE=%s\n' % significance)
    output_report_file.write('TSTART=%s\n' % t_first)
    output_report_file.write('TEND=%s\n' % t_last)
    output_report_file.close()

    #output_report_file_name_2 = '%s/%s/v%02d/%s_%.3f_%.3f_res.txt' %(output_ez,OBJECT,version,OBJECT,RA_OBJ,DEC_OBJ)
    #output_report_file_2=file(output_report_file_name_2,'w')
    #output_report_file_2.write('#name ra dec tstart tstop TS photonIndex photonIndexError flux fluxError photonFlux photonFluxError roi irf zmax thetamax strategy\n')
    #output_report_file_2.write('%s %.3f %.3f %.3f %.3f %.1f 0 0 <1e-9 n.a. <1e-9 n.a. 0 LLE 0 0 0 \n' %(OBJECT,
    #                                                                                                    RA_OBJ,DEC_OBJ,
    #                                                                                                    t_first, t_last,
    #                                                                                                    significance
    #                                                                                                    ))
    #output_report_file_2.close()    
    return significance,t_first, t_last

def ComputeDetection(GRBNAME, mode, opt={}):
    print '--------------------------------------------------: ComputeDetection:',GRBNAME, mode
    ##################################################
    GeneralOptions={ "IGNORE_THETA":1,
                     "TSTART":-20, 
                     "TSTOP":300,
                     "BEFORE":600,
                     "AFTER":3600,
                     "EMIN":100,
                     "EMAX":100000,
                     "TSMIN":20,
                     "TSMIN_EXT":10,
                     "UPDATE_POS_TSMAP":1,
                     "ULINDEX":-2.00,
                     "ZMAX":105,
                     "ROI":12,
                     "DT":1.0,
                     "IRFS":None,
                     "like_model":'GRB+TEM+GAL0+2FGL',
                     "like_timeBins":'LOG',
                     "NLIKEBINS":48,
                     "EXTENDED_TSTART":0.01,
                     "EXTENDED_TSTOP":10000,
                     "MAKE_LIKE":1,
                     "MAKE_LLE":1,
                     "MAKE_TSMAP":1,
                     "LLEDT":"0.1,10",
                     "N":10,
                     "LLEDS":0,
                     "GRBTRIGGERDATE":0,
                     "GRBT05":0,
                     "GRBT90":60,
                     "RA":0,
                     "DEC":0,
                     "ERR":0}
    for k in opt.keys():
        try: GeneralOptions[k]=opt[k]
        except: print ' *** Option %s not available!' % k
        pass
    ##################################################
    def convertToString(D):
        txt=''
        for k in D.keys():
            if isinstance(D[k],str): txt+="%s=\'%s\' " %(k,D[k])
            else: txt+='%s=%s '%(k,D[k])
            pass
        return txt
    ##################################################
    if GeneralOptions['GRBTRIGGERDATE']==0 or GeneralOptions['IRFS']==None: 
        print 'You have to pass a dictionary containing GRBTRIGGERDATE,RA,and DEC, and the IRFS at least. Otgher possible variables are:'
        for k in GeneralOptions.keys(): print k, GeneralOptions[k]
        return 0
    stringName=GRBNAME[-9:]
    OUTDIR   = os.environ['OUTDIR']
    try:     SCRIPT   = os.environ['SCRIPTS']
    except:  SCRIPT='computeDetection'
    General = convertToString(GeneralOptions)
    print ' *** Running %s ON : %s' %(SCRIPT, stringName)
    subJob0  = 'submitJob.py -q xxl -exe %s %s' %(SCRIPT,General)
    test     = 'gtgrb.py -nox -go -exe %s %s' % (SCRIPT,General)
    if 'pipe' in mode: cmd=subJob0
    else: cmd=test
    
    if 'forReal' in mode: os.system(cmd)        
    else: print cmd
    return 1

def CreateDictionaryFromTree(rootFile):
    if not os.path.exists(rootFile): return None
    print '########################### CreateDictionaryFromTree:',rootFile
    tfile=ROOT.TFile(rootFile,'OPEN')
    tree=tfile.Get("GRBCatalog")
    
    #except: return none
    grbs={}
    for i in range(tree.GetEntries()):
        vars={}
        tree.GetEntry(i)
        vars['LLENSIG']=tree.LLENSIG
        vars['LLEDURATION']=tree.LLET90+tree.LLET90hierr+tree.LLEt05+tree.LLEt05loerr
        #print tree.GRBNAME.strip(),tree.LLET90,tree.LLET90hierr,tree.LLEt05,tree.LLEt05loerr,vars['LLENSIG'],vars['LLEDURATION']
        # ...
        grbs[tree.GRBNAME.strip()]=vars
        pass
    
    return grbs

def ParseTrigCatFile(fileName):    
    fin = pyfits.open(fileName)
    h   = fin[0].header
    RA_OBJ   = float(h['RA_OBJ'])
    DEC_OBJ  = float(h['DEC_OBJ'])
    ERR_RAD  = float(h['ERR_RAD'])
    TRIGTIME = float(h['TRIGTIME'])
    CLASS    = h['CLASS'].strip()
    OBJECT   = h['OBJECT'].strip()    
    try: LOC_SRC  = h['LOC_SRC'].strip()
    except: LOC_SRC='nan'
    return (CLASS,OBJECT,RA_OBJ,DEC_OBJ,ERR_RAD,TRIGTIME,LOC_SRC)


def GetFT2(TRIGTIME,BEFORE=_BEFORE,AFTER=_AFTER):
    METMIN  = TRIGTIME - BEFORE
    METMAX  = TRIGTIME + AFTER
    try: FT2 = glob.glob('FT2/FT2_ft2_%d_%d.fits' % (METMIN-3600,METMAX+3600))[0]
    except: FT2 = None
    if FT2 is None:
        FT2 = utils.getFT2('FT2',METMIN-3600,METMAX+3600)
        pass
    if not os.path.exists(FT2):
        FT2=None
        print 'No FT file found!!!!'
        pass
    return FT2


def GetTheta(FT2,TRIGTIME,RA_OBJ,DEC_OBJ):
    i=0
    try:    (THETA,i) = utils.getTheta(FT2,TRIGTIME,RA_OBJ,DEC_OBJ,i)
    except:   return 666
    return THETA

def help():
    print 'Code written by nicola.omodei@slac.stanford.edu'
    print 'options:'
    print '   -drm build the DRM (provided a MC has been run) '
    print '   -pha  build the PHA and FT1 LLE file '
    print '   -mc  create the configuration file for the Monte Carlo generation  '
    print '   -gtgrb  analyize using GRBAnalysis-scons'
    print '   -f <EXPRESSION> filter the GRBtrigctalog'
    print '   -real execute per real the job  '
    pass

def do(**args):
    print args
    results={}
    output_ez   = args['outdir']
    version     = args['version']
    TRIGTIME    = args['ttime']
    OFFSET      = args['tstart']
    DURATION    = args['tstop']-args['tstart']
    RA_OBJ      = args['ra']
    DEC_OBJ     = args['dec']
    DT          = args['deltat']
    OUTPUT_NAME = args['name']
    
    lle         = args['lle']
    drm         = args['drm']
    dete        = args['detect']
    
    ZENITHMAX   = args['zmax']
    THETAMAX    = args['thetamax']
    RADIUS      = args['radius']
    IGNORE_THETA= bool(args['ignore_theta'])
    
    BEFORE      = args['before']- args['tstart']
    AFTER       = args['after'] + args['tstop']
    clobber     = args['clobber']
    regenerate_after_detection = args['regenerate_after_detection']

    _THETA_MIN=GetThetaMin()
    if IGNORE_THETA: _THETA_MIN=180

    if _interactive==0: ROOT.gROOT.SetBatch(True)

    ROOT.gStyle.SetFillStyle(1)
    ROOT.gStyle.SetFrameFillColor(10)
    ROOT.gStyle.SetCanvasColor(10);

    TRIGGER_NAME = OUTPUT_NAME
    #TRIGGER_NAME = OUTPUT_NAME[-9:] #utils.met2date(TRIGTIME,opt="grbname")
    #CLASS        = OUTPUT_NAME[:-9]
    
    print 100*'-'
    print 'TRIGGER_NAME: %s'  % (TRIGGER_NAME)
    print 'TRIGGERTIME= %.4f' % (TRIGTIME)
    print 'RA,DEC = %10.3f, %10.3f ' %(RA_OBJ,DEC_OBJ)
    # STEP 2: GET FT2
    FT2   = GetFT2(TRIGTIME)
    if FT2 is None: exit()
    print 'FT2 FILE:', FT2
    # STEP 3: GET THETA:
    THETA = GetTheta(FT2,TRIGTIME,RA_OBJ,DEC_OBJ)
    print 'THETA: %.2f' % THETA
    print 100*'-'
    
    output_dir_version='%(output_ez)s/%(TRIGGER_NAME)s/v%(version)02d' % locals()
    os.system('mkdir -pv %(output_dir_version)s' % locals())    
    fileout=file('%(output_dir_version)s/jobTag.txt' % locals(),'w')
    fileout.writelines('THETA=%.2f\n' % THETA)
    fileout.close()
    
    if THETA > _THETA_MIN:
        fileout=file('%(output_dir_version)s/theta.txt' % locals(),'w')
        fileout.writelines('THETA=%.2f\n' % THETA)
        fileout.close()
        exit()
        pass

    mode=['pha','forReal']
    cmd_cp = 'cp %(FT2)s %(output_dir_version)s/gll_pt_bn%(TRIGGER_NAME)s_v%(version)02d.fit' %locals()
    print cmd_cp
    os.system(cmd_cp)
    
    # STEP 4: GENERATE LLE FILES:
    selected=0
    if lle:
        print 'GENERATE LLE FILES...'
        if clobber: 
            mymode=mode
            mymode.append('regenerate')
            pass
        selected= GenerateLLE(output_ez,version,TRIGGER_NAME,TRIGTIME,RA_OBJ,DEC_OBJ,DURATION,
                              OFFSET=OFFSET, DT=DT ,
                              BEFORE=BEFORE, AFTER=AFTER,
                              ZENITHMAX=ZENITHMAX,
                              THETAMAX=THETAMAX,RADIUS=RADIUS, mode=mymode)
        fileout=file('%(output_dir_version)s/jobTag.txt' % locals(),'a')
        fileout.writelines('SELECTED=%d\n' % selected)
        fileout.close()
        
        if selected==0:
            os.system('rm %(output_dir_version)s/jobTag.txt' % locals())
            exit()
            pass
        pass
    
    # STEP 5: APPLY BAIESIAN BLOCK TO GET THE BEST BINNING:
    if dete:
        print 'APPLY BAIESIAN BLOCK TO GET THE BEST BINNING...'
        if TRIGGER_NAME in LLE_TIMEWINDOWS_DEF.keys():            
            off_inteval_1_start,off_inteval_1_end, on_inteval_start,on_inteval_end, off_inteval_2_start,off_inteval_2_end = LLE_TIMEWINDOWS_DEF[TRIGGER_NAME]
            print 'USING CUSOM WINDOWS:',off_inteval_1_start,off_inteval_1_end, on_inteval_start,on_inteval_end, off_inteval_2_start,off_inteval_2_end
        else:
            off_inteval_1_end   = OFFSET              - min(5,DURATION/2.0) - 5.0
            off_inteval_1_start = off_inteval_1_end   - max(200,2*DURATION) 
            off_inteval_2_start = OFFSET+DURATION     + min(5,DURATION/2.0) + 5.0
            off_inteval_2_end   = off_inteval_2_start + max(200,5*DURATION)
            on_inteval_start    = off_inteval_1_end   - 5
            on_inteval_end      = off_inteval_2_start + 5
            pass

        off_pulse_intervals='%s %s %s %s' %(off_inteval_1_start,off_inteval_1_end,off_inteval_2_start,off_inteval_2_end)
        search_window      ='%s %s' % ( on_inteval_start, on_inteval_end )

        LLEBBBD_SIG_DETECTED, LLEBBBD_SIG, LLEBBBD_ST0, LLEBBBD_ST1, SIGMA_B,LLEBBBD_T0,LLEBBBD_T1 = ComputeBBBDetection(output_ez,version,TRIGGER_NAME,FT2,search_window,THETAMAX,ZENITHMAX,off_pulse_intervals)
        
        results['LLEBBBD_SIG_DETECTED']= LLEBBBD_SIG_DETECTED
        results['LLEBBBD_SIG']         = LLEBBBD_SIG
        results['LLEBBBD_T0']          = LLEBBBD_T0
        results['LLEBBBD_T1']          = LLEBBBD_T1
        
        output_report_file_name_2 = '%s/%s/v%02d/%s_%.3f_%.3f_res.txt' %(output_ez,TRIGGER_NAME,version,TRIGGER_NAME,RA_OBJ,DEC_OBJ)
        print('Saving output file for GW followup pipeline: %s' % output_report_file_name_2)
        output_report_file_2=file(output_report_file_name_2,'w')
        txt='#name ra dec tstart tstop TS photonIndex photonIndexError flux fluxError photonFlux photonFluxError roi irf zmax thetamax strategy\n'
        print(txt)
        output_report_file_2.write(txt)
        txt='%s %.3f %.3f %.3f %.3f %.1f 0 0 <1e-9 n.a. <1e-9 n.a. 0 LLE 0 0 0 \n' %(TRIGGER_NAME,
                                                                                     RA_OBJ,DEC_OBJ,
                                                                                     LLEBBBD_T0,LLEBBBD_T1,
                                                                                     LLEBBBD_SIG
                                                                                     )
        print(txt)
        output_report_file_2.write(txt)
        output_report_file_2.close()             
        
        if LLEBBBD_SIG_DETECTED==1:
            SUBBIN=1
            #if LLEBBBD_SIG>5:  SUBBIN=4
            #if LLEBBBD_SIG>10: SUBBIN=8
            #if LLEBBBD_SIG>15: SUBBIN=16

            DTS=[(LLEBBBD_ST1-LLEBBBD_ST0)/SUBBIN]
            DSS=[LLEBBBD_ST0]
        else:
            DTS = [0.1,0.3,1.0,3.0,10.0]
            DSS = [0.0]
            pass
        print 'COMPUTE DETECTION USING:'
        print ' DTS = ', DTS
        print ' DSS = ', DSS
        LLE_SIG, LLE_T0, LLE_T1 = ComputeLLEDetection(output_ez,version,TRIGGER_NAME,FT2,RA_OBJ,DEC_OBJ,TRIGTIME,NSIGMA=_NSIGMA,DTS=DTS,DSS=DSS,XMIN_SIG=off_inteval_1_end, XMAX_SIG=off_inteval_2_start)
        LLE_DETECTED=0
        if LLE_SIG>_NSIGMA: LLE_DETECTED=1
        
        results['LLE_SIG']= LLE_SIG
        results['LLE_T0'] = LLE_T0
        results['LLE_T1'] = LLE_T1
        
        fileout=file('%(output_dir_version)s/jobTag.txt' % locals(),'a')
        fileout.writelines('BBBD DETECTED=%d\n' % LLEBBBD_SIG_DETECTED)
        fileout.writelines('BBBD SIGNIFICANCE=%f\n' % LLEBBBD_SIG)
        fileout.writelines('BBBD T0=%f\n' % LLEBBBD_T0)
        fileout.writelines('BBBD T1=%f\n' % LLEBBBD_T1)
        fileout.writelines('DETECTED=%d\n' %  LLE_DETECTED)
        fileout.writelines('SIGNIFICANCE=%f\n' % LLE_SIG)
        fileout.writelines('TFIRST=%f\n' % LLE_T0)
        fileout.writelines('TLAST=%f\n' % LLE_T1)
        fileout.close()
        if  LLE_DETECTED==0:
            os.system('rm %(output_dir_version)s/jobTag.txt' % locals())
            return results
            pass
        pass
    
    # STEP 6: GENERATE MC FILES:
    '''
    if DURATION>0:
    DETECT_TFIRST=OFFSET
    DETECT_TLAST =DURATION+OFFSET
    else:
    DETECT_TFIRST=t_first
    DETECT_TLAST =t_last
    pass
    
    MC_DURATION = DETECT_TLAST - DETECT_TFIRST # ?
    
    if MC_DURATION>0:
    MC_TRIGTIME = TRIGTIME + DETECT_TFIRST    
    mc_generated = GenerateMC(output_ez,version,TRIGGER_NAME,MC_TRIGTIME,RA_OBJ,DEC_OBJ,MC_DURATION,mode)
    fileout=file('%(output_dir_version)s/jobTag.txt' % locals(),'a')
    fileout.writelines('MC_GENERATED=%d\n' % mc_generated)
    fileout.close()
    pass
    mode.append('regenerate')
        if drm: mode.append('drm')
    # STEP 7: REGENERATE THE PHA IN THE PROPER TIME RANGE:
    '''
    if lle and dete and regenerate_after_detection:
        mymode=mode
        mymode.append('regenerate')
        print 'regenerating LLE on the detection time window (%.3f - %.3f0)' %(LLE_T0, LLE_T1)
        selected= GenerateLLE(output_ez,version,TRIGGER_NAME, TRIGTIME, RA_OBJ, DEC_OBJ,
                              DURATION=(LLE_T1-LLE_T0), OFFSET=LLE_T0, DT=DT ,
                              BEFORE=BEFORE, AFTER=AFTER,
                              ZENITHMAX=ZENITHMAX,
                              THETAMAX=THETAMAX, RADIUS=RADIUS,mode=mymode)
        fileout=file('%(output_dir_version)s/jobTag.txt' % locals(),'a')
        fileout.writelines('SELECTED2=%d\n' % selected)
        fileout.close()
        os.system('mv %(output_dir_version)s/jobTag.txt %(output_dir_version)s/job.done' % locals())
        pass
        
    return results


if __name__=='__main__':
    os.environ['LLEIFILE'] ='/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/makeLLEproducts/python/config_LLE_DRM/Pass8.txt'
    os.environ['MCBASEDIR']='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass8'
    import argparse
    desc='Script to compute LLE data files: written by nicola.omodei@stanford.edu'
    parser = argparse.ArgumentParser(description=desc)
    # Mandatory args:
    parser.add_argument('--ttime',help='Trigger time (MET)', type=float, required=True) 
    parser.add_argument('--ra',help='Right Ascension (J2000)', type=float, required=True) 
    parser.add_argument('--dec',help='Declination (J2000)', type=float, required=True) 
    parser.add_argument('--tstart',help='Start Time (from Trigger time)', type=float, required=True) 
    parser.add_argument('--tstop',help='Stop time  (from Trigger time)', type=float, required=True) 
    # Optional:
    parser.add_argument('--deltat',help='binning', type=float, required=False,default=1.0)     
    parser.add_argument('--outdir',help='Name of the output directory', type=str, required=False, default='LLEOUT') 
    parser.add_argument('--version',help='Version of the LLE file', type=int, required=False, default=0) 
    parser.add_argument('--name',help='Name of the trigger GRBYYMMDDFFF format', type=str, required=False, default='GRBYYMMDDFFF') 
    parser.add_argument('--lle',help='generate the LLE files?', type=int, required=False, default=1)
    parser.add_argument('--drm',help='generate the DRM files? (MC must be already generated!)', type=int, required=False, default=0)
    parser.add_argument('--detect',help='run the detection algorithm?', type=int, required=False, default=1)
    parser.add_argument('--clobber',help='Override all existing files', type=int, required=False, default=1)
    parser.add_argument('--regenerate_after_detection',help='Do you want to regenerate the LLE data on the detection time window?', type=int, required=False, default=1)
    parser.add_argument('--radius',help='ROI Radius (if negative is intended as number of PSF)', type=float, required=False, default=-1)
    parser.add_argument('--thetamax',help='Maximum Theta', type=float, required=False, default=90)
    parser.add_argument('--zmax',help='Maximum Zenith', type=float, required=False, default=90)
    parser.add_argument('--ignore_theta',help='Ignore the initial theta', type=float, required=False, default=0)
    parser.add_argument('--before',help='Time before the trigger', type=float, required=False, default=_BEFORE)
    parser.add_argument('--after',help='Time after the trigger', type=float, required=False, default=_AFTER)
    


    import makeLLE
    #args=parser.parse_args()
    #makeLLE.do(vars(parser.parse_args()))
    makeLLE.do(**parser.parse_args().__dict__)
    

                    
    
