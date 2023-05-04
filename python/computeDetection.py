print '--------------------------------------------------'
now=time.localtime()
print ' GTGRB EXECUTION STARTED %s-%s-%s %s-%s-%s' % (now[0],now[1],now[2],now[3],now[4],now[5])

pfiles  = os.environ['PFILES']
print mode
Set(**ListToDict(sys.argv))
try:    timeShift = float(os.environ['TIMESHIFT']) #=-2.0 * 5733.0672 = 11466.1344)
except: timeShift=0


if timeShift!=0:
    dirToRemove = '%s/%s' % (os.environ['OUTDIR'],grb[0].Name)
    NewtriggerTime = grb[0].Ttrigger+timeShift
    SetVar('GRBTRIGGERDATE',NewtriggerTime)
    SetGRB()
    GRBtheta = lat[0].getGRBTheta()
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print ' WARNING!!!! The trigger time has changed            '
    print ' New Theta of the bursts: %.2f ' % GRBtheta
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print 'removing: %s ' % dirToRemove
    os.system('rm -rf %s' % dirToRemove)
    pass
else:                                               
    if mode=='go':
        EraseOutputDir()
        Set(**ListToDict(sys.argv))
        pass
    pass

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name

print ' GRBNAME    = ',grbname
print ' PFILES     = ',pfiles
print ' PYTHONPATH = ',os.environ['PYTHONPATH']
print ' INDIR      = ',os.environ['INDIR']
print ' OUTDIR     = ',os.environ['OUTDIR']
try:    print ' ROOTISBATCH= ',os.environ['ROOTISBATCH']
except: pass

try:    ignoreTheta = bool(results['IGNORE_THETA'])
except: ignoreTheta = False

if GRBtheta < 89.0 or ignoreTheta:
    # -------------------------------------------------- #
    ResultsFileName = ReadResults()    
    # -------------------------------------------------- #
    try: extended  = results['EXTENDED']
    except: extended=1
    chatter = 2
    # PLOT ANGULAR SEPARATION
    PlotAngularSeparation(mode=mode)
    Print()
    # -------------------------------------------------- #
    # SELECT EVENTS, CALCULATE PROBABILITY OF BEING GRB EVENT
    if MakeSelect(mode=mode,tstart=-100,tstop=1000,plot=0)>0:  ComputeBayesProbabilities()        
    if MakeSelect(mode=mode,tstart=results['GRBT05'],tstop=results['GRBT95'],plot=0)>0: MakeGtFindSrc(mode=mode)
    MakeSelect(mode=mode)
    Print()
    
    # #################################################
    
    Prompt(['MAKELLE'],mode)
    if bool(results['MAKELLE']):
        GetLLE()                                             # This will get the data.
        try:
            print 'Executing MakeLLELightCurves...'
            MakeLLELightCurves(**(ListToDict(sys.argv))) # Jack's code        
            if float(results['LLE_DetMaxSign']) > 4.0:          # Pre Trial Probability in sigma
                tmpdict={'task':'duration'}
                tmpdict.update(ListToDict(sys.argv))        
                MakeLLELightCurves(**(tmpdict))          # Jack's code
                pass    
            print '--------------------------------------------------------------------\n'
            Print()
        except:
            print '##################################################'
            print 'An error occourced in computig MakeLLELightCurves!'
            print '##################################################'
            pass        
        print 'Executing MakeLLEDetectionAndDuration()...'
        try:
            MakeLLEDetectionAndDuration() # Fred's Code
        except:
            print '##################################################'
            print 'An error occourced in computig MakeLLELightCurves!'
            print '##################################################'
            pass
        print '--------------------------------------------------------------------\n'
        pass
    # #################################################
    Print()
    Prompt(['MAKE_LIKE'], mode)

    
    like_max  = None
    like_ts_max = 0
    t0_ts_max = 0
    t1_ts_max = 0
    
    if bool(results['MAKE_LIKE']):
        Prompt(['like_model'], mode)
        if 'PREFIT' in results['like_model']:  MakeComputePreburstBackground(mode)
        # 1 first likelihood in the GBM time window:
        MakeLikelihoodAnalysis(mode=mode,
                               tstart = 0,
                               tstop  = results['GBMT90'],
                               extended=extended,
                               tsmap=0,
                               suffix='LIKE_GBM',
                               pha=0)
        
        #try:
        if 'LIKE_GBM_TS_GRB' in results.keys():            
            like_max    = 'LIKE_GBM'
            like_ts_max = results['LIKE_GBM_TS_GRB']
            t0_ts_max   = 0
            t1_ts_max   = results['GBMT90']
            pass
        
        # except:
        #pass
    
        
        for ts  in [1,3,10,30,100,300,1000]:        
            MakeLikelihoodAnalysis(mode=mode, tstart=0, tstop=ts, extended=0, tsmap=0, pha=0,suffix='LIKE_MY_%d' % ts)            
            #Print()
            #try:
            kkk=('LIKE_MY_%d_TS_GRB' % ts)
            if kkk in results.keys():
                if results[kkk] > like_ts_max:
                    like_max='LIKE_MY_%d' % ts
                    t0_ts_max=0
                    t1_ts_max=ts
                    like_ts_max= results[kkk]
                    pass
                pass
            #pass
            #except:
            #    pass
            pass
        pass
    print '--------------------------------------------------'    
    print 'Rerunning the maximum likelihood analysis on the interval: %s' % like_max
    print '--------------------------------------------------'    
    #Print()
    if like_max is not None:  MakeLikelihoodAnalysis(mode=mode, tstart=0, tstop=t1_ts_max, extended=0, tsmap=1,pha=0,suffix=like_max)
    for k in results.keys():
        if '_UP' in k:
            print k,results[k]
            pass
        pass
    print '--------------------------------------------------'
    Done(True)
    
    pass
else:
    print 'THETA > 89 DEGREES. SKIPPING GRB:%s' %grbname
    Done(True)
    pass
