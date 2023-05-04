#!/usr/bin/env python
import pyfits,math,sys
import ROOT
import numpy as np

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


def plotLAT(TIME,TMIN,TMAX,LAT,LON):
    g=ROOT.TGraph()
    i1 = TIME.searchsorted(TMIN)
    i2 = TIME.searchsorted(TMAX)
    p=0
    for i in range(i1,i2):
        x=LON[i]
        y=LAT[i]
        g.SetPoint(p,x,y)
        p+=1
        pass
    return g


def plotBoresight(TIME,TMIN,TMAX,ra_scz,dec_scz,RA=0,DEC=0):
    g=ROOT.TGraph()
    i1 = TIME.searchsorted(TMIN)
    i2 = TIME.searchsorted(TMAX)
    p=0
    for i in range(i1,i2):
        x=TIME[i]-TMIN
        ra1=ra_scz[i]
        dec1=dec_scz[i]
        y=angsep(RA,DEC,ra1,dec1)
        g.SetPoint(p,x,y)
        p+=1
        pass
    return g


def plotZenith(TIME,TMIN,TMAX,RA_ZENITH,DEC_ZENITH,RA=0,DEC=0):
    g=ROOT.TGraph()
    i1 = TIME.searchsorted(TMIN)
    i2 = TIME.searchsorted(TMAX)
    p=0
    for i in range(i1,i2):
        x=TIME[i]-TMIN
        ra1=RA_ZENITH[i]
        dec1=DEC_ZENITH[i]
        y=angsep(RA,DEC,ra1,dec1)
        
        g.SetPoint(p,x,y)
        p+=1
        pass
    return g
    
    
def getSimilarOrbit(ft2='/u/gl/omodei/GRBSimulator-GR-v17r35p1gr04/data/VELA-2yr_ft2_239471020_302619601.fits',myMET = 301619574,RA=0,DEC=0):
    
    
    fin = pyfits.open(ft2)

    header = fin['SC_DATA'].header
    print header
    data        = fin['SC_DATA'].data
    tstart      = data.field('START')
    xyz         = data.field('SC_POSITION')
    ra_npole    = data.field('RA_NPOLE')
    dec_npole   = data.field('DEC_NPOLE')
    ROCK_ANGLE  = data.field('ROCK_ANGLE')
    ra_scz      = data.field('RA_SCZ')
    dec_scz     = data.field('DEC_SCZ')
    RA_ZENITH   = data.field('RA_ZENITH')
    DEC_ZENITH  = data.field('DEC_ZENITH')
    
    GEOMAG_LAT  = data.field('GEOMAG_LAT')
    LAT_GEO     = data.field('LAT_GEO')
    LON_GEO     = data.field('LON_GEO')
    
    i0           = tstart.searchsorted(myMET)
    i60          = tstart.searchsorted(myMET-60*86400)
    i50          = tstart.searchsorted(myMET-50*86400)
    
    mypos = xyz[i0]

    ra_npole0  = ra_npole[i0]
    dec_npole0 = dec_npole[i0]

    ra_scz_0     =  ra_scz[i0]
    dec_scz_0    = dec_scz[i0]
    ROCK_ANGLE_0 = ROCK_ANGLE[i0]
    GEOMAG_LAT_0 = GEOMAG_LAT[i0]
    LAT_GEO_0    = LAT_GEO[i0]
    LON_GEO_0    = LON_GEO[i0]
    myX   = mypos[0]
    myY   = mypos[1]
    myZ   = mypos[2]
    distances = []
    imin      = 0
    dmin=1e20
    for i in range(i60,i50):
        _pos =  xyz[i]
        
        _x   = _pos[0]
        _y   = _pos[1]
        _z   = _pos[2]
        
        ra_npole1  =  ra_npole[i]
        dec_npole1 = dec_npole[i]

        d=_dist(mypos , _pos)
        a= angsep(ra_npole0,dec_npole0, ra_npole1,dec_npole1)
        
        if a<dmin:    
            dmin = a
            imin = i
            pass
        #distances.append(a)
        pass
    ra_scz_1     = ra_scz[imin]
    dec_scz_1    = dec_scz[imin]
    ROCK_ANGLE_1 = ROCK_ANGLE[imin]
    GEOMAG_LAT_1 = GEOMAG_LAT[imin]
    LAT_GEO_1    = LAT_GEO[imin]
    LON_GEO_1    = LON_GEO[imin]
    orbit_period = 5733.0672
    newmet       = tstart[imin]
    
    norbits      = (myMET-newmet)/orbit_period

    print 'i: %s, dist=%s, MET=%s (days=%s,%.1f orbits) ' % (imin, dmin, newmet, (myMET-newmet)/86400.,norbits)
    print 'RA0, DEC0= %.3f,%.3f - RA1, DEC1= %.3f,%.3f (Sep: %.3f)'%(ra_scz_0,dec_scz_0, ra_scz_1,dec_scz_1, angsep(ra_scz_0,dec_scz_0, ra_scz_1,dec_scz_1))
    print 'ROCK_ANGLE_0=%.3f, ROCK_ANGLE_1=%.3f' % (ROCK_ANGLE_0, ROCK_ANGLE_1)
    print 'GEOMAG_LAT_0=%.3f, GEOMAG_LAT_1=%.3f' % (GEOMAG_LAT_0, GEOMAG_LAT_1)    
    print 'LAT_GEO_0=%.3f, LAT_GEO_1=%.3f' % (LAT_GEO_0,LAT_GEO_1)
    print 'LON_GEO_0=%.3f, LON_GEO_1=%.3f' % (LON_GEO_0,LON_GEO_1)

    g0=plotLAT(tstart,myMET,myMET+orbit_period,LAT_GEO,LON_GEO)
    b0=plotBoresight(tstart,myMET,myMET+orbit_period,ra_scz,dec_scz,RA,DEC)
    z0=plotZenith(tstart,myMET,myMET+orbit_period,RA_ZENITH,DEC_ZENITH,RA,DEC)

    gg1=ROOT.TGraph()
    gg1.SetPoint(0,0,-30)
    gg1.SetPoint(1,180,30)
    
    gg2=ROOT.TGraph()
    gg2.SetPoint(0,0,0)
    gg2.SetPoint(1,orbit_period,180)

    gg3=ROOT.TGraph()
    gg3.SetPoint(0,0,0)
    gg3.SetPoint(1,orbit_period,180)

    canvas=ROOT.TCanvas('C','C',800,800)
    canvas.Divide(1,3)
    canvas.cd(1)
    gg1.Draw('ap') 
    g0.Draw('p')
    canvas.cd(2)
    gg2.Draw('ap') 
    b0.Draw('p')
    canvas.cd(3)
    gg3.Draw('ap') 
    z0.Draw('p')
    
    cont = 1
    orbit = 0
    while cont:
        newmet       = tstart[i0]
        #newmet       = tstart[imin]
        t1 = newmet-(orbit)*orbit_period
        t2 = t1 + orbit_period        
        print 'Orbit %s, MET=%.3f, DAY=%.3f' %(orbit,t1,(myMET-t1)/86400)

        canvas.cd(1)
        g1=plotLAT(tstart,t1,t2,LAT_GEO,LON_GEO)
        g1.SetMarkerColor(ROOT.kRed)        
        g1.Draw('p')
        
        canvas.cd(2)
        b1=plotBoresight(tstart,t1,t2,ra_scz,dec_scz,RA,DEC)
        b1.SetMarkerColor(ROOT.kRed)        
        b1.Draw('p')
        
        canvas.cd(3)
        z1=plotZenith(tstart,t1,t2,RA_ZENITH,DEC_ZENITH,RA,DEC)
        z1.SetMarkerColor(ROOT.kRed)        
        z1.Draw('p')

        canvas.cd()
        ROOT.gPad.Update()
        
        a=raw_input('enter to continue, type something to exit.')
        try:
            orbit=int(a)
        except:
            if len(a)>0: cont=0
            orbit+=1
            pass
        pass
    
    pass




if __name__=='__main__':
    import utils
    MET = float(sys.argv[1])    
    print 'MET = %s' %(MET)
    print 'getting FT2 fle... 60 days'    
    FT2 = utils.getFT2('FT2',MET-60*86400,MET+86400,oneSec=False)
    getSimilarOrbit(FT2,MET)
    
    
