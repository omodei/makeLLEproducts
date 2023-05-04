#!/usr/bin/env python
from ROOT import *
from makeFits import *

#time -p makeLLE infile="@/u/gl/omodei/GBMTRIGCAT-v2/DATA/LAT2CATALOG-v1-LTF/081207680/v01/meritList.txt" outfile=/u/gl/omodei/GBMTRIGCAT-v2/DATA/LAT2CATALOG-v1-LTF/081207680/v01/gll_lle_bn081207680_v01.fit scfile=FT2/FT2_ft2_250354928_250364128.fits t0=250359527.936 ra=112.4 dec=70.5 dtstart=-1000.0 dtstop=1000.0 TCuts="(FswGamState==0 && TkrNumTracks>0 && (GltEngine==6 || GltEngine==7 || GltEngine==9) && EvtJointEnergy > 0 && ((FT1Theta<=40)*(Acd2VetoCount==0)+(FT1Theta>40)*(Acd2VetoFaces<2 && Acd2Tkr1TriggerEnergy45==0))) && (FT1ZenithTheta<90.0) && (FT1Theta<=90.0) && (((cos(FT1Dec*0.0174533)*(FT1Ra - (112.4)))^2+(FT1Dec- (70.5))^2)< (-1.0*(11.5*min(pow(EvtJointEnergy/59., -0.55), pow(EvtJointEnergy/59.,  -0.87))))^2 )" zmax=180.0 dict_file=/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-11-05-03/fitsGen/data/FT1variables mc_data=no file_version="1" proc_ver=1 apply_psf=no chatter=2 clobber=yes debug=no gui=no mode="ql"

def makeLLE_FT1(GRBFILES, FT2, 
                TRIGTIME, METMIN,METMAX,
                MYCUT, 
                DETNAM,
                DIRECTORY,
                GRBNAME,
                DATAENERGYVAR='EvtEnergyCorr',
                KEYWORDS=None):

    TREE           = 'MeritTuple'    
    #DATAENERGYVAR  ='EvtEnergyCorr'
    EvtElapsedTime = 'EvtElapsedTime'
    FT1ZenithTheta = 'FT1ZenithTheta'
    FT1EarthAzimuth= 'FT1EarthAzimuth'
    FT1Theta       = 'FT1Theta'
    FT1Phi         = 'FT1Phi'
    FT1Dec         = 'FT1Dec'
    FT1Ra          = 'FT1Ra'
    FT1L           = 'FT1L'
    FT1B           = 'FT1B'
    EvtEventId     = 'EvtEventId'
    EvtRun         = 'EvtRun'
    CTBClassLevel  = 'CTBClassLevel'
    FT1Livetime='FT1Livetime'
    
    ROOT_BRANCES=[DATAENERGYVAR,EvtElapsedTime,FT1ZenithTheta,FT1EarthAzimuth,FT1Theta,FT1Phi,FT1Dec,FT1Ra,FT1L,FT1B,EvtEventId,EvtRun,CTBClassLevel,FT1Livetime,
                  'FswGamState','TkrNumTracks','GltEngine','EvtJointEnergy','Acd2VetoCount','Acd2VetoFaces','Acd2Tkr1TriggerEnergy45']
    
    ROOT2FITS={'ENERGY':DATAENERGYVAR,
               'RA':FT1Ra,
               'DEC':FT1Dec,
               'L':FT1L,
               'B':FT1B,
               'TIME':EvtElapsedTime,
               'THETA':FT1Theta,
               'PHI':FT1Phi,
               'ZENITH_ANGLE':FT1ZenithTheta,
               'EARTH_AZIMUTH_ANGLE':FT1EarthAzimuth,
               'EVENT_ID':EvtEventId,
               'RUN_ID':EvtRun,
               'CTBCLASSLEVEL':CTBClassLevel,
               'LIVETIME':FT1Livetime
               }
    
    print '##################################################'    
    print '           MAKING THE LLE FT1 file'
    print '##################################################'
    print 'Number of GRB files...: %s' %len(GRBFILES)
    print 'FT2 file:.............: ',FT2,
    print 'Trigger Time..........: %s ' % TRIGTIME
    print ' + START   ..........: %s ' % (METMIN-TRIGTIME)
    print ' + STOP... ..........: %s ' % (METMAX-TRIGTIME)
    print '--------------------------------------------------'
    print ' Selection:...........: %s ' % MYCUT    
    print '--------------------------------------------------'
    CHAINGRB=TChain(TREE)
    for GRBFILE in GRBFILES:
        CHAINGRB.Add(GRBFILE.strip())
        pass
    #CHAINGRB.Print()
    CHAINGRB.SetBranchStatus('*',0)
    for _BRABNCH in ROOT_BRANCES:
        CHAINGRB.SetBranchStatus(_BRABNCH,1)
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
    EVENTS=CHAINGRB.CopyTree(myCut)
    return fitsLLE(EVENTS,ROOT2FITS,METMIN,METMAX,TRIGTIME,DIRECTORY,GRBNAME,KEYWORDS)    
            
if __name__=='__main__':
    import os
    import argparse
    default_TCut='(FswGamState==0 && TkrNumTracks>0 && (GltEngine==6 || GltEngine==7 || GltEngine==9) && EvtJointEnergy > 0 && ((FT1Theta<=40)*(Acd2VetoCount==0)+(FT1Theta>40)*(Acd2VetoFaces<2 && Acd2Tkr1TriggerEnergy45==0)))'
    desc = '''Make a LLE FT1 file - author nicola.omodei@stanford.edu'''
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-infile',help='Input list of merit file', type=str, required=True,default=None)
    parser.add_argument('-outfile',help='Output fits file', type=str, required=True,default=None)
    parser.add_argument('-scfile',help='Input FT2 fits file', type=str, required=True,default=None)
    parser.add_argument('-trigtime',help='Trigger time T0', type=float, required=True,default=None)
    parser.add_argument('-ra',help='Output fits file', type=float, required=True,default=None)
    parser.add_argument('-dec',help='Output fits file', type=float, required=True,default=None)
    parser.add_argument('-dtstart',help='start time relative to trigger time', type=float, required=True,default=1000)
    parser.add_argument('-dtstop',help='stop time relative to trigger time', type=float, required=True,default=-1000)
    parser.add_argument('-TCuts',help='TCut string to apply', type=str, required=False,default=default_TCut)    
    args = parser.parse_args()
    GRBFILES=[]
    for iFile in file(args.infile.replace('@',''),'r').readlines():
        GRBFILES.append(iFile)
        print iFile
        
    myfile=makeLLE_FT1(GRBFILES=GRBFILES,
                       FT2=args.scfile, 
                       TRIGTIME=args.trigtime, 
                       METMIN=args.trigtime+args.dtstart,
                       METMAX=args.trigtime+args.dtstop,
                       MYCUT=args.TCuts,
                       DETNAM='lle',
                       DIRECTORY='.',
                       GRBNAME='XXYYMMFFF',
                       DATAENERGYVAR='EvtEnergyCorr',
                       KEYWORDS={'PASS_VER':'P8v4','PROC_VER':1,'VERSION':1,'MY_CUT':args.TCuts,'RA_OBJ':args.ra,'DEC_OBJ':args.dec})
    os.system('mv %s %s' % (myfile,args.outfile))
    
