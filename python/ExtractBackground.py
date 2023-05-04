#!/usr/bin/env python
import pyfits,math,sys
import skymaps
import ROOT
import numpy as np
import utils
import makeLLE
import os

def _dist(v1,v2):
    x1   = v1[0]    
    y1   = v1[1]
    z1   = v1[2]
    x2   = v2[0]
    y2   = v2[1]
    z2   = v2[2]    
    dist=math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    return dist

def angsep(x1,y1,x2,y2):
    """
    spherical angle separation, aka haversine formula
    input and output are in degrees
    """
    dlat = np.math.radians(y2 - y1)
    dlon = np.math.radians(x2 - x1)
    y1 = np.math.radians(y1)
    y2 = np.math.radians(y2)
    a = np.sin(dlat/2.)*np.sin(dlat/2.) + np.cos(y1)*np.cos(y2)*np.sin(dlon/2.)*np.sin(dlon/2.)
    c  = 2*np.arctan2(np.sqrt(a), np.sqrt(1.-a))
    return np.math.degrees(c)


def getSimilarOrbit(ft2='/u/gl/omodei/GRBSimulator-GR-v17r35p1gr04/data/VELA-2yr_ft2_239471020_302619601.fits',
                    myMET = 301619574,
                    RA=0,DEC=0,orbit=0):

    FT2=utils.FT2(ft2)
    tstart      = FT2.SC_TSTART
    xyz         = FT2.SC_POSITION
    ra_npole    = FT2.RA_NPOLE
    dec_npole   = FT2.DEC_NPOLE
    ROCK_ANGLE  = FT2.ROCK_ANGLE
    ra_scz      = FT2.RA_SCZ
    dec_scz     = FT2.DEC_SCZ
    
    ra_scx      = FT2.RA_SCX
    dec_scx     = FT2.DEC_SCX
    
    RA_ZENITH   = FT2.RA_ZENITH
    DEC_ZENITH  = FT2.DEC_ZENITH
    
    GEOMAG_LAT  = FT2.GEOMAG_LAT
    
    LAT_GEO     = FT2.LAT_GEO
    LON_GEO     = FT2.LON_GEO

    B_MCILWAIN  = FT2.B_MCILWAIN
    L_MCILWAIN  = FT2.L_MCILWAIN
    
    i0           = tstart.searchsorted(myMET)-1
    
    mypos = xyz[i0]

    ra_npole0  = ra_npole[i0]
    dec_npole0 = dec_npole[i0]

    ra_scz_0     =  ra_scz[i0]
    dec_scz_0    = dec_scz[i0]
    ra_scx_0     =  ra_scx[i0]
    dec_scx_0    = dec_scx[i0]
    
    ROCK_ANGLE_0 = ROCK_ANGLE[i0]
    GEOMAG_LAT_0 = GEOMAG_LAT[i0]
    LAT_GEO_0    = LAT_GEO[i0]
    LON_GEO_0    = LON_GEO[i0]


    orbit_period = 5733.0672
    print '--------------------------------------------------'
    print 'ROCK_ANGLE_0=%.3f, GEOMAG_LAT_0=%.3f LAT_GEO_0=%.3f LON_GEO_0 =%.3f' % (ROCK_ANGLE_0, GEOMAG_LAT_0, LAT_GEO_0, LON_GEO_0)
    print '--------------------------------------------------'
    
    Th0,Ph0,pippo=FT2.getThetaPhi(myMET,RA,DEC)
    
    RA_test,DEC_test,pippo=FT2.getRaDec(myMET,Th0,Ph0,pippo)
    
    print 'GRB RA=%.3f, DEC=%.3f' % (RA,DEC)
    print 'SCZ0 RA=%.3f, DEC=%.3f' % (ra_scz_0,dec_scz_0)
    print 'SCX0 RA=%.3f, DEC=%.3f' % (ra_scx_0,dec_scx_0)
    print 'THETA,PHI= %.3f, %.3f' % (Th0,Ph0 )
    print 'TEST RA=%.3f, DEC=%.3f' % (RA_test,DEC_test)

    sd=skymaps.SkyDir(RA,DEC)
    sz=skymaps.SkyDir(float(ra_scz_0),float(dec_scz_0))
    print 'theta=' , math.degrees(math.acos(sd.dot(sz)))
    print '....>',i0,myMET,tstart[i0],ra_scz_0,dec_scz_0
    print '....>',pippo,myMET,tstart[pippo],ra_scz[pippo],dec_scz[pippo]
    
    newmet       = tstart[i0]
    t1 = newmet+(orbit)*orbit_period
    print '--------------------------------------------------'
    print 'Orbit %s, MET=%.3f, DAY=%.3f' %(orbit,t1,(myMET-t1)/86400)    
    Th1,Ph1,pippo  = FT2.getThetaPhi(t1,RA,DEC)    
    RA1,DEC1,pippo = FT2.getRaDec(t1,Th0,Ph0,pippo)
    print 'GRB RA=%.3f, DEC=%.3f' % (RA,DEC)        
    print 'new THETA,PHI= %.3f, %.3f' % (Th1,Ph1 )
    print 'new RA=%.3f, DEC=%.3f (corresponding to the old Theta Phi)' % (RA1,DEC1)
    return t1,RA1,DEC1




if __name__=='__main__':
    import utils
    import AverageBackgroundFiles as ABF
    MET=None
    RA=0
    DEC=0
    mode=['pha']
    DURATION=300
    OFFSET=0
    DRM=False
    BEFORE=1000
    AFTER=1000
    ROI=-1
    def myhelp():
        print 'This script extract the =LLE data and the background from +/- 30 otbits'
        txt= '''
        USAGE:
        \t -t [MET]
        \t -ra [RA]
        \t -dec [DEC]
        \t -dur [DUR]
        \t -real execute the script'''
        print txt
        pass
    version=0
    output_ez = 'LLEProduct/BACKGROUNDS-2'
    for i,a in enumerate(sys.argv):
        if a=='-t': MET=float(sys.argv[i+1])
        elif a=='-ra': RA=float(sys.argv[i+1])
        elif a=='-dec': DEC=float(sys.argv[i+1])
        elif a=='-r': ROI=float(sys.argv[i+1])
        elif a=='-off': OFFSET=float(sys.argv[i+1])
        elif a=='-dur': DURATION=float(sys.argv[i+1])
        elif a=='-before': BEFORE=float(sys.argv[i+1])
        elif a=='-after': AFTER=float(sys.argv[i+1])
        elif a=='-v': version=int(sys.argv[i+1])                
        elif a=='-real': forReal=True
        elif a=='-pha': PHA = int(sys.argv[i+1])
        elif a=='-drm': DRM = int(sys.argv[i+1])
        elif a=='-o': output_ez = sys.argv[i+1]
        elif a=='-h':
            myhelp()
            exit()
            pass
        pass
    print '--------------------------------------------------'
    print 'MET = %s, RA: %.2f DEC: %.2f (ROI=%s)' %(MET,RA,DEC,ROI)
    print 'getting FT2 fle... 60 days'
    FT2 = utils.getFT2('FT2',MET-40*5733.0672,MET+40*5733.0672,oneSec=False)

    os.system('mkdir -p %s' % output_ez)
    files={}
    for o in [-30,0,30]:    
        print '--------------------------------------------------'
        YYMMDDFF=utils.met2date(MET,opt='name')
        print 'COMPUTING ORBIT: %i, OBJECT: %s' %(o,YYMMDDFF)
        mode=[]
        if o==0:
            if PHA: mode=['pha']
            if DRM: mode.append('drm')
            if forReal: mode.append('forReal')            
            OBJECT='SRC%s' % YYMMDDFF # THIS MUST MATCH THE MC
            newMET,newRA,newDEC=MET,RA,DEC
        else:
            if PHA: mode=['pha']
            if forReal: mode.append('forReal')
            OBJECT='BKG-orb%i-bn%s' % (o,YYMMDDFF)
            newMET,newRA,newDEC=getSimilarOrbit(FT2,MET,RA,DEC,orbit=o)
            pass
        if len(mode)==0: continue
        
        fileName='%s/%s/v%02d/gll_cspec_bn%s_v%02d.pha' %(output_ez,OBJECT,version,YYMMDDFF,version)
        files['PHA2ORB%i'%o]=fileName
        
        fileName='%s/%s/v%02d/gll_pha_bn%s_v%02d.fit' %(output_ez,OBJECT,version,YYMMDDFF,version)
        files['PHA1ORB%i'%o]=fileName
        
        makeLLE.GenerateLLE(output_ez,version,OBJECT, newMET, newRA,newDEC,
                            OFFSET=OFFSET,DURATION=DURATION,DT=1.0,
                            BEFORE=BEFORE,AFTER=AFTER,
                            ZENITHMAX=90,THETAMAX=90,RADIUS=ROI,mode=mode)
        
        if o==0: mc_generated = makeLLE.GenerateMC(output_ez,version,OBJECT,newMET,newRA,newDEC,DURATION,mode=mode)        
        pass
    f1n=files['PHA2ORB-30']
    f2n=files['PHA2ORB30']
    f3n=files['PHA2ORB0']
    print 'Now calling:'
    print './AverageBackgroundFiles.py %s %s %s' %(f1n,f2n,f3n)
    ABF.AveragePHA2(f1n,f2n,f3n)
    
    f1n=files['PHA1ORB-30']
    f2n=files['PHA1ORB30']
    f3n=files['PHA1ORB0']
    
    print './AverageBackgroundFiles.py %s %s %s pha1' %(f1n,f2n,f3n)    
    ABF.AveragePHA1(f1n,f2n,f3n)
    
    
    
    
