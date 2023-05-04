#!/usr/bin/env python
from ROOT import *
import astropy.io.fits as pyfits
from pyfits import Column, HDUList, PrimaryHDU, TableHDU,BinTableHDU#, new_table
import os
import numpy as num
import math
import utils
import datetime

##################################################

def fitsPHA2(TH2D,FT2,DETNAM,DIRECTORY, TRIGTIME,METMIN,METMAX,GRBNAME, CORRECTION = 0, KEYWORDS=None):
    try: version=int(KEYWORDS['VERSION'])
    except: version=0
    
    filename='%s/gll_cspec_bn%s_v%02d.pha' % (DIRECTORY,GRBNAME[-9:],version)
    
    print 'Creating PHA2 file with: ',FT2,DETNAM,DIRECTORY, TRIGTIME,METMIN,METMAX,GRBNAME, CORRECTION
    ft2=pyfits.open(FT2)    
    ft2.info()
    data=ft2[1].data
    cols=ft2[1].columns
    cols.info()
    SC_TSTART=data.field('START')
    SC_TSTOP=data.field('STOP')    
    SC_LIVETIME=data.field('LIVETIME')    
    
    nt=TH2D.GetNbinsX()
    ne=TH2D.GetNbinsY()
    NREC=ne
    aTIME   =num.arange(int(nt))
    aENDTIME=num.arange(int(nt))
    aBOUNDS=num.arange(int(ne))
    aSPEC_NUM=num.arange(int(nt))
    aQUALITY=num.zeros(int(nt))
    aCHANNEL=num.zeros((int(nt),int(ne)))
    aCOUNTS =num.zeros((int(nt),int(ne)))
    aEXPOSURE=num.zeros(int(nt))
    aROWID=[]
    ##########
    aE_MIN=num.zeros(int(ne))
    aE_MAX=num.zeros(int(ne))

    index1=0
    index2=0
    EXPOSURE=0.0
    for t in range(nt):
        BinWidth=TH2D.GetXaxis().GetBinWidth(t+1)
        BinLowEdge=TH2D.GetXaxis().GetBinLowEdge(t+1)

        aTIME[t]=1.0*BinLowEdge-TRIGTIME
        aENDTIME[t] = aTIME[t] + 1.0*BinWidth
        if t>0: aTIME[t]=aENDTIME[t-1]
        
        aSPEC_NUM[t]=t+1

        # print aTIME[t],aENDTIME[t]

        aROWID.append('') #t+1

        #This Compute the expsure:
        if CORRECTION:
            # Here METMIN and METMAX should be 0 and 1.
            LTF = CORRECTION/(METMAX-METMIN) # * utils.GetLiveTimeFraction(ft2,aTIME[t]+TRIGTIME,aENDTIME[t]+TRIGTIME,index1)
        else:
            LTF = utils.GetLiveTimeFraction(ft2,aTIME[t]+TRIGTIME,aENDTIME[t]+TRIGTIME,index1)
            pass
        
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
    ##################################################
    # HDU:
    ##################################################
    # header    
    prim        = PrimaryHDU() 
    primary_hdr = prim.header

    now         = utils.datetime2string(datetime.datetime.today())
    
    start_date  = utils.datetime2string(utils.computeDate(METMIN),0)#METMIN-int(METMIN))
    end_date    = utils.datetime2string(utils.computeDate(METMAX),0)#METMAX-int(METMAX))
    trig_date   = utils.datetime2string(utils.computeDate(TRIGTIME),0)#TRIGTIME-int(TRIGTIME))
    
    print 'Now: ',now
    print 'MET MIN:   ',METMIN,' => ',start_date
    print 'MET MAX:   ',METMAX,' => ',end_date
    print 'TRIG TIME: ',TRIGTIME,' => ',trig_date
    
    #Get the selection
    splitted       = DETNAM.split('_')
    thisSelection  = "_".join(splitted[1:])
    detnam         = splitted[0]

    ##################################################
    # UPDATE KEYWORD OF THE PRIMARY HEADER
    ##################################################
    
    primary_hdr.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
    primary_hdr.set('INSTRUME','LAT',comment='Name of instrument generating data')
    primary_hdr.set('ORIGIN','LISOC',comment="Name of organization making file")
    primary_hdr.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')

    # primary_hdr.set('DETNAM',detnam)
    # primary_hdr.set('FILTER','None')

    # VERSION KEYWORDS
    primary_hdr.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
    primary_hdr.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")            
    primary_hdr.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
    primary_hdr.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
    primary_hdr.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
    
    # DATE AND TIME KEYWORDS
    primary_hdr.set('DATE',now,comment="Date file was made")
    primary_hdr.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
    primary_hdr.set('DATE-END',end_date,comment="[UTC] date of end of observation")
    primary_hdr.set('TIMESYS','TT',comment="Time system used in time keywords")
    primary_hdr.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
    primary_hdr.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
    primary_hdr.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
    primary_hdr.set('TSTART',METMIN,comment="Observation's start time relative to MJDREF, double precision")
    primary_hdr.set('TSTOP',METMAX,comment="Observation's stop time relative to MJDREF, double precision")    
    primary_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")         

    # REFERENCE SYSTEM AND POSITION
    primary_hdr.set('RADECSYS','FK5',comment="Stellar reference frame")
    primary_hdr.set('EQUINOX',2000.0,comment="Equinox for RA and Dec")
    primary_hdr.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
    primary_hdr.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
    primary_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')

    # TYPE AND CREATOR
    primary_hdr.set('FILETYPE','PHAII',comment="The file format is OGIP PHAII which contains multiple spectra.")
    primary_hdr.set('DATATYPE','CSPEC',comment="Name of the primary datatype making up this file")
    primary_hdr.set('CREATOR','mkdrm_ez',comment="Software and version creating file")
    primary_hdr.set('FILENAME',filename.split('/')[-1].strip(),comment="Name of this file")    
    
    #prim.name = 'Primary'
    output = HDUList()
    output.append(prim)

    ##################################################    
    # EBOUNDS
    ##################################################
    
    E1=Column(name='CHANNEL', format='I',  array = num.arange(1,en+2))
    E2=Column(name='E_MIN',   format='1E', array = aE_MIN,unit='keV')
    E3=Column(name='E_MAX',   format='1E', array = aE_MAX,unit='keV')
    columns2=[E1,E2,E3]
    output.append(BinTableHDU.from_columns(columns2))
    ext2hdr=output[1]        
    ext2hdr.name = 'EBOUNDS'
    ebounds_hdr = ext2hdr.header
    ##################################################
    # EBOUNDS KEYWORDS
    ##################################################
    ebounds_hdr.set('TLMIN1',1,comment='Channel numbers are positive')
    ebounds_hdr.set('TLMAX1',NREC,comment='Greater than the number of channels')
    
    ebounds_hdr.set('TLMIN2',KEYWORDS['EMIN']*1000.,comment='Lowest channel energy')
    ebounds_hdr.set('TLMAX2',KEYWORDS['EMAX']*1000.,comment='Highest channel energy')
    ebounds_hdr.set('TUNIT2','keV',comment='physical unit of field')
    
    ebounds_hdr.set('TLMIN3',KEYWORDS['EMIN']*1000.,comment='Lowest channel energy')
    ebounds_hdr.set('TLMAX3',KEYWORDS['EMAX']*1000.,comment='Highest channel energy')
    ebounds_hdr.set('TUNIT3','keV',comment='physical unit of field')

    ebounds_hdr.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
    ebounds_hdr.set('INSTRUME','LAT',comment='Name of instrument generating data')
    ebounds_hdr.set('ORIGIN','LISOC',comment="Name of organization making file")
    ebounds_hdr.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')

    ebounds_hdr.set('CHANTYPE','PI',comment='Reconstructed energy')
    ebounds_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')    
    ebounds_hdr.set('DETCHANS',NREC,comment='Total number of Energy channels')
    ebounds_hdr.set('HDUCLASS','OGIP',comment='Conforms to OGIP standard indicated in HDUCLAS')
    ebounds_hdr.set('HDUCLAS1','RESPONSE',comment='These are typically found in RMF files')
    ebounds_hdr.set('HDUCLAS2','EBOUNDS',comment='Energy Channels')
    ebounds_hdr.set('HDUVERS','1.0.0',comment='Version of HDUCLAS1 format in use')
    ebounds_hdr.set('EXTVER',1,comment='Version of this extension format')
    # VERSION
    ebounds_hdr.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
    ebounds_hdr.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")
    #ebounds_hdr.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
    ebounds_hdr.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
    ebounds_hdr.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
    
    # DATE AND TIME KEYWORDS
    
    ebounds_hdr.set('DATE',now,comment="Date file was made")
    ebounds_hdr.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
    ebounds_hdr.set('DATE-END',end_date,comment="[UTC] date of end of observation")
    ebounds_hdr.set('TIMESYS','TT',comment="Time system used in time keywords")
    ebounds_hdr.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
    ebounds_hdr.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
    ebounds_hdr.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
    ebounds_hdr.set('TSTART',METMIN,comment="Observation's start time relative to MJDREF, double precision")
    ebounds_hdr.set('TSTOP',METMAX,comment="Observation's stop time relative to MJDREF, double precision")
    ebounds_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")         

    # REFERENCE SYSTEM AND POSITION
    
    ebounds_hdr.set('RADECSYS','FK5',comment="Stellar reference frame")
    ebounds_hdr.set('EQUINOX',2000.0,comment="Equinox for RA and Dec")
    ebounds_hdr.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
    ebounds_hdr.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
    ebounds_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')
 

    for k in ebounds_hdr.keys(): print '---->',k,ebounds_hdr[k]
    
    ##################################################
    # SPECTRUM
    ##################################################
    
    S1=Column(name='TIME', format='D', array=aTIME,unit='s')
    S2=Column(name='ENDTIME', format='D', array=aENDTIME,unit='s')
    S3=Column(name='QUALITY', format='1I', array=aQUALITY,unit='')
    # S3=Column(name='SPEC_NUM', format='I', array=aSPEC_NUM)
    # S4=Column(name='CHANNEL', format='%iI'%NREC, array=aCHANNEL,unit='')
    S5=Column(name='COUNTS', format='%iJ'%NREC, array=num.array(aCOUNTS),unit='Counts')
    # S6=Column(name='ROWID', format='A',array=num.array(aROWID))#num.arange(1,nt+1),unit='')
    S7=Column(name='EXPOSURE', format='1E', array=num.array(aEXPOSURE),unit='s')
    
    columns1=[S5,S7,S3,S1,S2]
    output.append(BinTableHDU.from_columns(columns1))
    ext1hdr=output[2]        
    spectrum_hdr = ext1hdr.header
    ext1hdr.name = 'SPECTRUM'
    
    ##################################################
    # SPECTRUM KEYWORDS
    ##################################################
    
    #spectrum_hdr.set('TTYPE1','TIME',after)
    #spectrum_hdr.set('TUNIT1','s')
    #spectrum_hdr.set('TTYPE2','ENDTIME')
    #spectrum_hdr.set('TUNIT2','s')
    
    spectrum_hdr.set('TZERO4',TRIGTIME,after='TFORM1',comment='Offset, equal to TRIGTIME')
    spectrum_hdr.set('TZERO5',TRIGTIME,after='TFORM2',comment='Offset, equal to TRIGTIME')
    spectrum_hdr.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
    spectrum_hdr.set('INSTRUME','LAT',comment='Name of instrument generating data')
    spectrum_hdr.set('ORIGIN','LISOC',comment="Name of organization making file")
    spectrum_hdr.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')
    
    #    spectrum_hdr.set('DETNAM',detnam)
    #spectrum_hdr.set('FILTER','None')
    spectrum_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")
    spectrum_hdr.set('HDUCLASS','OGIP',comment='Format conforms to OGIP standard')
    spectrum_hdr.set('HDUCLAS1','SPECTRUM',comment='PHA dataset (OGIP memo OGIP-92-007)')
    spectrum_hdr.set('HDUCLAS2','TOTAL',comment='Indicates gross data (source + background)')
    spectrum_hdr.set('HDUCLAS3','COUNT',comment='Indicates data stored as counts')
    spectrum_hdr.set('HDUCLAS4','TYPEII',comment='Indicates PHA Type II file format')
    spectrum_hdr.set('HDUVERS','1.0.0',comment='Version of HDUCLAS1 format in use')
    spectrum_hdr.set('DETCHANS',NREC,comment='Total number of channels in each rate')
    spectrum_hdr.set('POISSERR',True,comment='Assume Poisson Errors')
    spectrum_hdr.set('BACKFILE','none',comment='ame of corresponding background file (if any)')
    spectrum_hdr.set('CORRFILE','none',comment='Name of corresponding correction file (if any)')
    spectrum_hdr.set('CORRSCAL',1,comment='orrection scaling file')
    spectrum_hdr.set('RESPFILE','none',comment='ame of corresponding RMF file (if any)')
    spectrum_hdr.set('ANCRFILE','none',comment='Name of corresponding ARF file (if any)')
    spectrum_hdr.set('SYS_ERR',0.,comment='No systematic errors')
    #spectrum_hdr.set('QUALITY',0,comment='')
    spectrum_hdr.set('GROUPING',0,comment='No special grouping has been applied')
    spectrum_hdr.set('AREASCAL',1.,comment='No special scaling of effective area by channel')
    spectrum_hdr.set('BACKSCAL',1.,comment='No scaling of background')
    spectrum_hdr.set('CHANTYPE','PI',comment='Reconstructed energy')

     # REFERENCE SYSTEM AND POSITION
    
    spectrum_hdr.set('RADECSYS','FK5',comment="Stellar reference frame")
    spectrum_hdr.set('EQUINOX',2000.0,comment="Equinox for RA and Dec")
    spectrum_hdr.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
    spectrum_hdr.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
    spectrum_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')

    # DATE AND TIME KEYWORDS
    spectrum_hdr.set('DATE',now,comment="Date file was made")
    spectrum_hdr.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
    spectrum_hdr.set('DATE-END',end_date,comment="[UTC] date of end of observation")
    spectrum_hdr.set('TIMESYS','TT',comment="Time system used in time keywords")
    spectrum_hdr.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
    spectrum_hdr.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
    spectrum_hdr.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
    spectrum_hdr.set('TSTART',METMIN,comment="Observation's start time relative to MJDREF, double precision")
    spectrum_hdr.set('TSTOP',METMAX,comment="Observation's stop time relative to MJDREF, double precision")
    spectrum_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")             
    spectrum_hdr.set('NDSKEYS',4)
    spectrum_hdr.set('EXTVER',1,comment='Version of this extension format')

    # VERSION
    spectrum_hdr.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
    spectrum_hdr.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")
    #spectrum_hdr.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
    spectrum_hdr.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
    spectrum_hdr.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 

    ##################################################
    # GTI EXTENSION
    ##################################################
    
    G1=Column(name='START', format='D', unit='s',array=num.array([METMIN]))
    G2=Column(name='STOP', format='D', unit='s', array=num.array([METMAX]))
    columns3=[G1,G2]
    output.append(BinTableHDU.from_columns(columns3))
    ext3hdr=output[3]
    ext3hdr.name = 'GTI'
    gti_hdr = ext3hdr.header
    ##################################################
    # GTI KEYWORDS
    ##################################################
    
    #gti_hdr.set

    gti_hdr.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
    gti_hdr.set('INSTRUME','LAT',comment='Name of instrument generating data')
    gti_hdr.set('ORIGIN','LISOC',comment="Name of organization making file")
    gti_hdr.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')
    gti_hdr.set('DATE',now,comment="Date file was made")
    gti_hdr.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
    gti_hdr.set('DATE-END',end_date,comment="[UTC] date of end of observation")
    gti_hdr.set('TIMESYS','TT',comment="Time system used in time keywords")
    gti_hdr.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
    gti_hdr.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
    gti_hdr.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
    gti_hdr.set('TSTART',METMIN,comment="Observation's start time relative to MJDREF, double precision")
    gti_hdr.set('TSTOP',METMAX,comment="Observation's stop time relative to MJDREF, double precision")
    gti_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")         

            
    #gti_hdr.set('DETNAM',detnam)
    #gti_hdr.set('FILTER','None')    
    gti_hdr.set('HDUCLASS','OGIP',comment='Conforms to OGIP standard indicated in HDUCLAS')
    gti_hdr.set('HDUCLAS1','GTI',comment='Indicates good time intervals')
    gti_hdr.set('HDUVERS','1.0.0',comment='Version of HDUCLAS1 format in use')
    gti_hdr.set('CREATOR','mkdrm_ez',comment="Software and version creating file")
    #gti_hdr.set('ONTIME',METMAX-METMIN)
    gti_hdr.set('EXTVER',1,comment='Version of this extension format')

    # VERSION
    gti_hdr.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
    gti_hdr.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")
    #gti_hdr.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
    gti_hdr.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
    gti_hdr.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
        

    gti_hdr.set('RADECSYS','FK5',comment="Stellar reference frame")
    gti_hdr.set('EQUINOX',2000.0,comment="Equinox for RA and Dec")
    gti_hdr.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
    gti_hdr.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
    gti_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')

    
    ##################################################
    # UPDATE THE FILE AND FIX CHECKSUM
    ##################################################
    output.info()
    output.writeto(filename,clobber=True,output_verify='fix')
    os.system('fchecksum %s update=yes ' % filename)
    return filename


def fitsDRM(DRM,DETNAM,DIRECTORY,TRIGTIME,METMIN,METMAX, RSPTMIN, RSPTMAX, GRBNAME,KEYWORDS=None):
    try: version=int(KEYWORDS['VERSION'])
    except: version=0
    print 'This response matrix is valid from %.2f to %.2f' % (RSPTMIN,RSPTMAX)
    
    filename='%s/gll_cspec_bn%s_v%02d.rsp' % (DIRECTORY,GRBNAME[-9:],version)
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

    now=utils.datetime2string(datetime.datetime.today())
    
    start_date=utils.datetime2string(utils.computeDate(RSPTMIN),0)#RSPTMIN-int(RSPTMIN))
    end_date=utils.datetime2string(utils.computeDate(RSPTMAX),0)#RSPTMAX-int(RSPTMAX))
    trig_date=utils.datetime2string(utils.computeDate(TRIGTIME),0)#TRIGTIME-int(TRIGTIME))

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
    
    #Get the selection
    splitted       = DETNAM.split('_')
    thisSelection  = "_".join(splitted[1:])
    detnam         = splitted[0]

    ##################################################
    # PRIMARY
    ##################################################

    prim=PrimaryHDU() 
    primary_hdr=prim.header
    primary_hdr.set('CREATOR','mkdrm_ez',comment="Software and version creating file")
    primary_hdr.set('FILENAME',filename.split('/')[-1].strip(),comment="This file name")
    primary_hdr.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
    primary_hdr.set('INSTRUME','LAT',comment='Name of instrument generating data')
    primary_hdr.set('ORIGIN','LISOC',comment="Name of organization making file")
    primary_hdr.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')
    #primary_hdr.set('DETNAM',detnam)
    #primary_hdr.set('FILTER','None')
    primary_hdr.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
    primary_hdr.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")            
    primary_hdr.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
    primary_hdr.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
    primary_hdr.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
        
    # DATE AND TIME KEYWORDS
    primary_hdr.set('DATE',now,comment="Date file was made")
    primary_hdr.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
    primary_hdr.set('DATE-END',end_date,comment="[UTC] date of end of observation")
    primary_hdr.set('TIMESYS','TT',comment="Time system used in time keywords")
    primary_hdr.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
    primary_hdr.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
    primary_hdr.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
    primary_hdr.set('TSTART',RSPTMIN,comment="Observation's start time relative to MJDREF, double precision")
    primary_hdr.set('TSTOP',RSPTMAX,comment="Observation's stop time relative to MJDREF, double precision")    
    primary_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')
    
    primary_hdr.set('DRM_NUM',1,comment='Number of DRMs stored in this file')
    primary_hdr.set('DRM_TYPE','CSPEC',comment='Data type for which DRM is intended')
    primary_hdr.set('FILETYPE','LAT LLE DRM',comment='Name for this type of FITS file')

    primary_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")
    primary_hdr.set('RADECSYS','FK5')
    primary_hdr.set('EQUINOX',2000.0)
    primary_hdr.set('RA_OBJ',KEYWORDS['RA_OBJ'])
    primary_hdr.set('DEC_OBJ',KEYWORDS['DEC_OBJ'])
    ##################################################$
    output = HDUList()
    output.append(prim)

    ##################################################
    # EBOUNDS
    ##################################################

    E1=Column(name='CHANNEL',format='I',array=num.arange(1,NREC+1))
    E2=Column(name='E_MIN',format='1E',unit='keV',array=aE_MIN)
    E3=Column(name='E_MAX',format='1E',unit='keV',array=aE_MAX)
    columns2=[E1,E2,E3]
    output.append(BinTableHDU.from_columns(columns2))
    ext2hdr=output[1]        
    ebounds_hdr = ext2hdr.header
    ext2hdr.name = 'EBOUNDS'

    ebounds_hdr.set('TLMIN1',1,comment='Channel numbers are positive')
    ebounds_hdr.set('TLMAX1',NREC,comment='Greater than the number of channels')
    
    ebounds_hdr.set('TLMIN2',KEYWORDS['EMIN']*1000.,comment='Lowest channel energy')
    ebounds_hdr.set('TLMAX2',KEYWORDS['EMAX']*1000.,comment='Highest channel energy')
    ebounds_hdr.set('TUNIT2','keV',comment='physical unit of field')
    
    ebounds_hdr.set('TLMIN3',KEYWORDS['EMIN']*1000.,comment='Lowest channel energy')
    ebounds_hdr.set('TLMAX3',KEYWORDS['EMAX']*1000.,comment='Highest channel energy')
    ebounds_hdr.set('TUNIT3','keV',comment='physical unit of field')

    # TELESCOPE AND ORIGIN
    
    ebounds_hdr.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
    ebounds_hdr.set('INSTRUME','LAT',comment='Name of instrument generating data')
    ebounds_hdr.set('ORIGIN','LISOC',comment="Name of organization making file")
    ebounds_hdr.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')

    ebounds_hdr.set('CHANTYPE','PI',comment='Reconstructed energy')
    ebounds_hdr.set('DETCHANS',NREC,comment='Total number of channels in each rate')
    ebounds_hdr.set('HDUCLASS','OGIP',comment='Conforms to OGIP standard indicated in HDUCLAS')
    ebounds_hdr.set('HDUCLAS1','RESPONSE',comment='These are typically found in RMF files')
    ebounds_hdr.set('HDUCLAS2','EBOUNDS',comment='Energy bins')
    ebounds_hdr.set('HDUVERS','1.0.0',comment='Version of HDUCLAS1 format in use')
    ebounds_hdr.set('EXTVER',1,comment='Version of this extension format')
    # VERSION
    ebounds_hdr.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
    ebounds_hdr.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")
    #ebounds_hdr.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
    ebounds_hdr.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
    ebounds_hdr.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
                
    # DATE AND TIME KEYWORDS
    ebounds_hdr.set('DATE',now,comment="Date file was made")
    ebounds_hdr.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
    ebounds_hdr.set('DATE-END',end_date,comment="[UTC] date of end of observation")
    ebounds_hdr.set('TIMESYS','TT',comment="Time system used in time keywords")
    ebounds_hdr.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
    ebounds_hdr.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
    ebounds_hdr.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
    ebounds_hdr.set('TSTART',RSPTMIN,comment="Observation's start time relative to MJDREF, double precision")
    ebounds_hdr.set('TSTOP',RSPTMAX,comment="Observation's stop time relative to MJDREF, double precision")    
    ebounds_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")

    # REFERENCE SYSTEM AND POSITION
    ebounds_hdr.set('RADECSYS','FK5',comment="Stellar reference frame")
    ebounds_hdr.set('EQUINOX',2000.0,comment="Equinox for RA and Dec")
    ebounds_hdr.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
    ebounds_hdr.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
    ebounds_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')

    ##################################################
    #      MATRIX 
    ##################################################
    
    M1=Column(name='ENERG_LO',format='E',unit='keV',array=aENERG_LO)
    M2=Column(name='ENERG_HI',format='E',unit='keV',array=aENERG_HI)
    M3=Column(name='N_GRP',format='I',array=aN_GRP)
    M4=Column(name='F_CHAN',format='PI(1)',array=aF_CHAN)
    M5=Column(name='N_CHAN',format='PI(1)',array=aN_CHAN)
    M6=Column(name='MATRIX',format='PE(%i)'% NREC, unit='cm**2',array=aMATRIX)
    columns1=[M1,M2,M3,M4,M5,M6]
    output.append(BinTableHDU.from_columns(columns1))
    ext1hdr=output[2]        
    matrix_hdr = ext1hdr.header
    ext1hdr.name = 'SPECRESP MATRIX'
    ##################################################
    # KEYWORDS MATRIX
    ##################################################
    
    matrix_hdr.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
    matrix_hdr.set('INSTRUME','LAT',comment='Name of instrument generating data')
    matrix_hdr.set('ORIGIN','LISOC',comment="Name of organization making file")
    matrix_hdr.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')
    matrix_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')
    matrix_hdr.set('CHANTYPE','PI','Reconstructed energy')
    matrix_hdr.set('DETCHANS',NREC,comment='Total number of Energy channels')
    matrix_hdr.set('HDUCLASS','OGIP',comment='Conforms to OGIP standard indicated in HDUCLAS')
    matrix_hdr.set('HDUCLAS1','RESPONSE',comment='These are typically found in RMF files')
    matrix_hdr.set('HDUCLAS2','RSP_MATRIX',comment='Response Matrix')
    matrix_hdr.set('HDUVERS','1.0.0',comment='Version of HDUCLAS1 format in use')
    matrix_hdr.set('EXTVER',1,comment='Version of this extension format')
    # VERSION
    matrix_hdr.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
    matrix_hdr.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")
    #matrix_hdr.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")
    matrix_hdr.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
    matrix_hdr.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
    
    # DATE AND TIME KEYWORDS
    matrix_hdr.set('DATE',now,comment="Date file was made")
    matrix_hdr.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
    matrix_hdr.set('DATE-END',end_date,comment="[UTC] date of end of observation")
    matrix_hdr.set('TIMESYS','TT',comment="Time system used in time keywords")
    matrix_hdr.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
    matrix_hdr.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
    matrix_hdr.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
    matrix_hdr.set('TSTART',RSPTMIN,comment="Start time for generating the response matrix")
    matrix_hdr.set('TSTOP',RSPTMAX,comment="End  time for generating the response matrix")
    matrix_hdr.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")

    # REFERENCE SYSTEM AND POSITION
    matrix_hdr.set('RADECSYS','FK5',comment="Stellar reference frame")
    matrix_hdr.set('EQUINOX',2000.0,comment="Equinox for RA and Dec")
    matrix_hdr.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
    matrix_hdr.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
    matrix_hdr.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')
    
    matrix_hdr.set('TLMIN4',1,comment='Channel numbers are positive')    
    matrix_hdr.set('TLMAX4',NREC,comment='Maximum number of energy channel')
    #matrix_hdr.set('TLMIN5',1,comment='Channel numbers are positive')
    #matrix_hdr.set('TLMAX5',NREC,comment='Maximum number of energy channel')
    ##################################################
    # SAVE THE FILE AND VERYFY CHCKSUM
    ##################################################
    
    output.info()
    output.writeto(filename,clobber=True,output_verify='fix')
    os.system('fchecksum %s update=yes' % filename)
    return filename


def fitsLLE(EVENTS,ROOT2FITS,METMIN,METMAX,TRIGTIME,DIRECTORY,GRBNAME,
            KEYWORDS):
    try: version=int(KEYWORDS['VERSION'])
    except: version=0
    filename='%s/gll_lle_bn%s_v%02d.fit' % (DIRECTORY,GRBNAME[-9:],version)
    N=EVENTS.GetEntries()
    print 'Number of entry in EVENTS',N
    #ENERGY=num.array([eval('EVENTS.%s'%ROOT2FITS['ENERGY'])])
    ENERGY=[]
    RA=[]
    DEC=[]
    L=[]
    B=[]    
    TIME=[]
    THETA=[]
    PHI=[]    
    ZENITH_ANGLE=[]
    EARTH_AZIMUTH_ANGLE=[]
    EVENT_ID=[]
    RUN_ID=[]
    CTBCLASSLEVEL=[]
    LIVETIME=[]
    
    for i in range(N):
        EVENTS.GetEntry(i)        
        ENERGY.append(eval('EVENTS.%s'%ROOT2FITS['ENERGY']))
        RA.append(eval('EVENTS.%s'%ROOT2FITS['RA']))
        DEC.append(eval('EVENTS.%s'%ROOT2FITS['DEC']))
        L.append(eval('EVENTS.%s'%ROOT2FITS['L']))
        B.append(eval('EVENTS.%s'%ROOT2FITS['B']))   
        TIME.append(eval('EVENTS.%s'%ROOT2FITS['TIME']))
        THETA.append(eval('EVENTS.%s'%ROOT2FITS['THETA']))
        PHI.append(eval('EVENTS.%s'%ROOT2FITS['PHI']))
        ZENITH_ANGLE.append(eval('EVENTS.%s'%ROOT2FITS['ZENITH_ANGLE']))
        EARTH_AZIMUTH_ANGLE.append(eval('EVENTS.%s'%ROOT2FITS['EARTH_AZIMUTH_ANGLE']))
        EVENT_ID.append(eval('EVENTS.%s'%ROOT2FITS['EVENT_ID']))
        RUN_ID.append(eval('EVENTS.%s'%ROOT2FITS['RUN_ID']))
        CTBCLASSLEVEL.append(eval('EVENTS.%s'%ROOT2FITS['CTBCLASSLEVEL']))
        LIVETIME.append(eval('EVENTS.%s'%ROOT2FITS['LIVETIME']))
        pass
    
    Columns=[]
    Columns.append(Column(name='ENERGY',              format='E', array=ENERGY,              unit='MeV'))
    Columns.append(Column(name='RA',                  format='E', array=RA,                  unit='deg'))
    Columns.append(Column(name='DEC',                 format='E', array=DEC,                 unit='deg'))
    Columns.append(Column(name='L',                   format='E', array=L,                   unit='deg'))
    Columns.append(Column(name='B',                   format='E', array=B,                   unit='deg'))
    Columns.append(Column(name='THETA',               format='E', array=THETA,               unit='deg'))
    Columns.append(Column(name='PHI',                 format='E', array=PHI,                 unit='deg'))
    Columns.append(Column(name='ZENITH_ANGLE',        format='E', array=ZENITH_ANGLE,        unit='deg'))
    Columns.append(Column(name='EARTH_AZIMUTH_ANGLE', format='E', array=EARTH_AZIMUTH_ANGLE, unit='deg'))
    Columns.append(Column(name='TIME',                format='D', array=TIME,                unit='s'))
    Columns.append(Column(name='EVENT_ID',            format='J', array=EVENT_ID,            unit=''))
    Columns.append(Column(name='RUN_ID',              format='J', array=RUN_ID,              unit=''))
    Columns.append(Column(name='CTBCLASSLEVEL',       format='J', array=CTBCLASSLEVEL,       unit=''))
    Columns.append(Column(name='LIVETIME',            format='E', array=LIVETIME,            unit=''))    

    Columns_GTI=[Column(name='START', format='D', unit='s',array=num.array([METMIN])),
                 Column(name='STOP', format='D', unit='s', array=num.array([METMAX]))]
    
    prim   = PrimaryHDU() 
    output = HDUList()
    output.append(prim)
    output.append(BinTableHDU.from_columns(Columns))
    output.append(BinTableHDU.from_columns(Columns_GTI))
    output.info()
    # NOW UPDATE THE KEYWORDS:
    now=utils.datetime2string(datetime.datetime.today())
    start_date= utils.datetime2string(utils.computeDate(METMIN),0)#METMIN-int(METMIN))
    end_date  = utils.datetime2string(utils.computeDate(METMAX),0)#METMAX-int(METMAX))
    trig_date = utils.datetime2string(utils.computeDate(TRIGTIME),0)#TRIGTIME-int(TRIGTIME))    
    print 'Now: ',now
    print 'MET MIN:   ',METMIN,' => ',start_date
    print 'MET MAX:   ',METMAX,' => ',end_date
    print 'TRIG TIME: ',TRIGTIME,' => ',trig_date
    output[1].name='EVENTS'
    output[2].name='GTI'
    for i in [0,1,2]:        
        my_header=output[i].header
        
        my_header.set('TELESCOP','GLAST',comment='Name of mission / spacecraft')
        my_header.set('INSTRUME','LAT',comment='Name of instrument generating data')
        my_header.set('ORIGIN','LISOC',comment="Name of organization making file")
        my_header.set('OBSERVER','Peter Michelson',comment='GLAST/LAT PI')
        # VERSION KEYWORDS
        my_header.set('PASS_VER',KEYWORDS['PASS_VER'],comment="Version of Event Analysis")
        my_header.set('PROC_VER',KEYWORDS['PROC_VER'],comment="Version of LLE Data Analysis")            
        my_header.set('LLECUT',KEYWORDS['MY_CUT'],comment="String used to select LLE events")
        my_header.set('LONGSTRN','OGIP 1.0',comment='The OGIP Long String Convention may be used.') 
        if i==0:
            # #################################################
            # UPDATE KEYWORD OF THE PRIMARY HEADER
            # #################################################
            my_header.set('FILETYPE','LAT PHOTON LIST',comment="Selected Fermi LAT events.")
            my_header.set('DATATYPE','LLE',comment="Name of the primary datatype making up this file")
            my_header.set('CREATOR','mkdrm_ez',comment="Software and version creating file")
            my_header.set('FILENAME',filename.split('/')[-1].strip(),comment="Name of this file")
            my_header.set('VERSION', KEYWORDS['VERSION'],comment="Version of the file")

        elif i==1:
            my_header.set('HDUCLASS','OGIP',comment='format conforms to OGIP standard')

            my_header.set('HDUCLAS1','EVENTS',comment='extension contains events')
            my_header.set('HDUCLAS2','ALL',comment='extension contains all events detected')
            my_header.set('EXTVER',1,comment='Version of this extension format')

            my_header.set('NDSKEYS',1)
            my_header.set('DSTYP1','TIME')
            my_header.set('DSUNI1','s')
            my_header.set('DSVAL1','TABLE')
            my_header.set('DSREF1',':GTI')

            my_header.set('TLMIN1',0.0,'minimum value')
            my_header.set('TLMIN2',0.0,'minimum value')
            my_header.set('TLMIN3',-90.0,'minimum value')
            my_header.set('TLMIN4',0.0,'minimum value')
            my_header.set('TLMIN5',-90.0,'minimum value')
            my_header.set('TLMIN6',0.0,'minimum value')
            my_header.set('TLMIN7',0.0,'minimum value')
            my_header.set('TLMIN8',0.0,'minimum value')
            my_header.set('TLMIN9',0.0,'minimum value')
            my_header.set('TLMIN10',0.0,'minimum value')
            my_header.set('TLMIN11',0,'minimum value')
            my_header.set('TLMIN12',0,'minimum value')

            my_header.set('TLMAX1',1e7,'maximum value')
            my_header.set('TLMAX2',360.0,'maximum value')
            my_header.set('TLMAX3',90.0,'maximum value')
            my_header.set('TLMAX4',360.0,'maximum value')
            my_header.set('TLMAX5',90.0,'maximum value')
            my_header.set('TLMAX6',180.0,'maximum value')
            my_header.set('TLMAX7',360.0,'maximum value')
            my_header.set('TLMAX8',180.0,'maximum value')
            my_header.set('TLMAX9',360.0,'maximum value')
            my_header.set('TLMAX10',1e10,'maximum value')
            my_header.set('TLMAX11',2147483647,'maximum value')
            my_header.set('TLMAX12',2147483647,'maximum value')

        elif i==2:
            my_header.set('HDUCLASS','OGIP',comment='format conforms to OGIP standard')

            my_header.set('HDUCLAS1','GTI',comment='extension contains good time intervals')
            my_header.set('HDUCLAS2','ALL',comment='extension contains all science time')
            my_header.set('TLMIN1',0.0,'minimum value')
            my_header.set('TLMIN2',0.0,'minimum value')
            my_header.set('TLMAX1',1e10,'maximum value')
            my_header.set('TLMAX2',1e10,'maximum value')
            my_header.set('TELAPSE',METMAX-METMIN,comment="TSTOP - TSTART")
            my_header.set('ONTIME',METMAX-METMIN,comment="sum of GTI lengths")        
            my_header.set('EXTVER',1,comment='Version of this extension format')
            pass
        # DATE AND TIME KEYWORDS
        my_header.set('DATE',now,comment="Date file was made")
        my_header.set('DATE-OBS',start_date,comment="[UTC] date of start of observation")
        my_header.set('DATE-END',end_date,comment="[UTC] date of end of observation")
        my_header.set('TIMESYS','TT',comment="Time system used in time keywords")
        my_header.set('TIMEUNIT','s',comment="Time unit used in TSTART, TSTOP")
        my_header.set('TIMEZERO',0.0,comment="clock correction")    
        my_header.set('TIMEREF','LOCAL',comment="reference frame used for times")
        my_header.set('CLOCKAPP',False,comment="whether a clock drift correction has been appli")
        my_header.set('GPS_OUT',False,comment="whether GPS time was unavailable at any time du")
        my_header.set('MJDREFI',51910.,comment="MJD date of reference epoch, integer part")
        my_header.set('MJDREFF',7.428703703703703E-4,comment="MJD date of reference epoch, fractional part")
        my_header.set('TSTART',METMIN,comment="mission time of the start of the observation")
        my_header.set('TSTOP',METMAX,comment="mission time of the end of the observation")    
        my_header.set('TRIGTIME',TRIGTIME,comment="Trigger time (s) relative to MJDREF, double precision")    
        # REFERENCE SYSTEM AND POSITION
        my_header.set('RADECSYS','FK5',comment="Stellar reference frame")
        my_header.set('EQUINOX',2000.0,comment="Equinox for RA and Dec")
        my_header.set('RA_OBJ',KEYWORDS['RA_OBJ'],comment="RA of the source")
        my_header.set('DEC_OBJ',KEYWORDS['DEC_OBJ'],comment="DEC of the source")
        my_header.set('OBJECT',GRBNAME,comment='Object name in standard format, yymmddfff')
        # TYPE AND CREATOR
        # my_header.set('DATATYPE','CSPEC',comment="Name of the primary datatype making up this file")
        # my_header.set('CREATOR','mkdrm_ez',comment="Software and version creating file")
        # my_header.set('FILENAME',filename.split('/')[-1].strip(),comment="Name of this file")    
        # Comments:
        my_header.add_comment('TRIGTIME=%s' %(TRIGTIME))
        pass
    #ext_gti=output[2]
    #ext_gti.name = 'GTI'
    #gti_hdr = ext_gti.header
    ##################################################
    # GTI KEYWORDS
    ##################################################
        
    #gti_hdr.set
    #gti_hdr.set('HDUVERS','1.0.0',comment='Version of HDUCLAS1 format in use')
    #gti_hdr.set('CREATOR','mkdrm_ez',comment="Software and version creating file")
    #gti_hdr.set('ONTIME',METMAX-METMIN)
    #gti_hdr.set('EXTVER',1,comment='Version of this extension format')

    
    ##################################################
    # UPDATE THE FILE AND FIX CHECKSUM
    ##################################################
    output.info()
    output.writeto(filename,clobber=True,output_verify='fix')
    os.system('fchecksum %s update=yes ' % filename)
    return filename

