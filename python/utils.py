#!/usr/bin/env python
import datetime,calendar
import math,os
import pyfits
import ROOT

_data = 'FT2'
def getNativeCoordinate( (alpha, delta), (alpha0, delta0) ):
    da = alpha - alpha0
    sina = math.sin(math.radians(da) )
    sind = math.sin(math.radians(delta) )
    sin0 = math.sin(math.radians(delta0) )
    cosa = math.cos(math.radians(da) )
    cosd = math.cos(math.radians(delta) )
    cos0 = math.cos(math.radians(delta0) )
    
    phi = math.atan2(cosd*sina, cos0*cosd*cosa+sin0*sind )
    theta = math.asin( -sin0*cosd*cosa + cos0*sind )
    
    return (math.degrees(phi),math.degrees(theta) )

def getAngle(theta,phi):
    cost=math.cos(math.radians(theta))
    sint=math.sin(math.radians(theta))
    cosp=math.cos(math.radians(phi))
    sinp=math.sin(math.radians(phi))
    ang=math.atan2(math.sqrt((cost*sinp)**2+sint**2),cost*cosp)    
    return ang


def getTheta(FT2,MET_GRB,RA_GRB,DEC_GRB,i=0):
    ft2=pyfits.open(FT2)    
    SC_data=ft2['SC_DATA'].data
    # SPACECRAFT:
    #ra_zenith   = SC_data.field('RA_ZENITH')
    #dec_zenith    = SC_data.field('DEC_ZENITH')
    # BORESIGHT:
    RA_SCZ  = SC_data.field('RA_SCZ')
    DEC_SCZ = SC_data.field('DEC_SCZ')
    # TIME
    SC_TSTART=SC_data.field('START')
    SC_TSTOP=SC_data.field('STOP')    
    ft2.close()        
    while (SC_TSTOP[i]-MET_GRB)<0:
        i=i+1
        pass
    (phi,theta) = getNativeCoordinate((RA_GRB,DEC_GRB),(RA_SCZ[i],DEC_SCZ[i]))
    theta_grb   = math.degrees(getAngle(phi,theta))    
    return theta_grb,i


def getThetaPhi(FT2,MET_GRB,RA_GRB,DEC_GRB,i=0):
    #    (ra_#grb,dec_grb,MET_grb,ft2file,i=0):

    ft2=pyfits.open(FT2)    
    SC_data=ft2['SC_DATA'].data
    # BORESIGHT:
    RA_SCZ  = SC_data.field('RA_SCZ')
    DEC_SCZ = SC_data.field('DEC_SCZ')
    
    RA_SCX  = SC_data.field('RA_SCX')
    DEC_SCX = SC_data.field('DEC_SCX')
    
    # TIME
    SC_TSTART=SC_data.field('START')
    SC_TSTOP=SC_data.field('STOP')    
    ft2.close()
    if max(SC_TSTOP) < MET_GRB or min(SC_TSTART)> MET_GRB:
        raise Exception('Error, FT2 file does not cover the MET of the GRB FT2 Time min,max= (%s,%s)' % (min(SC_TSTART)-MET_GRB,
                                                                                                         max(SC_TSTOP)-MET_GRB))
    
    while (SC_TSTOP[i]-MET_GRB)<0:
        i=i+1
        pass
    
    (phi,theta) = getNativeCoordinate((RA_GRB,DEC_GRB),(RA_SCZ[i],DEC_SCZ[i]))
    theta_grb = math.degrees(getAngle(phi,theta))
    
    (phi,theta) = getNativeCoordinate((RA_GRB,DEC_GRB),(RA_SCX[i],DEC_SCX[i]))

    phi_grb   = math.degrees(getAngle(phi,theta))    
    return theta_grb, phi_grb, i

def computeDate(MET):    
    from GTGRB import genutils
    grb_date,fff=genutils.met2date(MET,'FFF')    
    return grb_date

def datetime2string(adate, fff=0.0):
    yy=adate.year
    mm=adate.month
    dd=adate.day
    hr=adate.hour
    mi=adate.minute
    ss=adate.second
    #fff=float(ss+60.*mi+3600.*hr)/86.4
    if    fff==0: string='%i-%02i-%02iT%02i:%02i:%02i' % (yy,mm,dd,hr,mi,ss)
    else: string='%i-%02i-%02iT%02i:%02i:%07.4f' % (yy,mm,dd,hr,mi,ss+fff)
    return string


def getFT1(name,tstart,tend,class_name='Source'):    
    os.system('mkdir %s' % _data)
    ft1name='%s/%s_ft1_%.0f_%.0f.fits' %(_data,name,tstart,tend)
    wdir   ='%s/%s_%.0f_%.0f' %(_data,name,tstart,tend)
    
    if class_name == 'Source':
        cmd2='getLATFitsFiles.py --wdir %(wdir)s --outfile %(ft1name)s --minTimestamp %(tstart)s --maxTimestamp %(tend)s --type FT1 --verbose 1 --overwrite 0' %locals()
    else:
        cmd2='getLATFitsFiles.py --wdir %(wdir)s --outfile %(ft1name)s --minTimestamp %(tstart)s --maxTimestamp %(tend)s --type EXTENDEDFT1 --verbose 1 --overwrite 0' %locals()
        pass
    os.system(cmd2)
    print '--> file FT1: %s' % ft1name
    return ft1name

def getFT2(name,tstart,tend,oneSec=True):    
    os.system('mkdir %s' % _data)

    #sample='P6_public_v2'
    #sample='P6_public_v3'
    #sample='P7.6_P120_BASE'
    #FT2REPOSITORY = os.getenv('FT2REPOSITORY','P8_P302')
    #sample=FT2REPOSITORY+'_BASE'                 
                     
    ft2name='%s/%s_ft2_%.0f_%.0f.fits' %(_data,name,tstart,tend)
    wdir   ='%s/%s_%.0f_%.0f' %(_data,name,tstart,tend)

    if oneSec:
        #cmd2='~glast/astroserver/prod/astro --event-sample %s --output-ft2-1s %s --event-sample --minTimestamp %s --maxTimestamp %s storeft2 ' % (sample,ft2name,tstart,tend)
        cmd2='getLATFitsFiles.py --wdir %(wdir)s --outfile %(ft2name)s --minTimestamp %(tstart)s --maxTimestamp %(tend)s --type FT2SECONDS --verbose 1 --overwrite 0' %locals()
    else:
        #cmd2='~glast/astroserver/prod/astro --event-sample %s --output-ft2-30s %s --event-sample --minTimestamp %s --maxTimestamp %s storeft2 ' % (sample,ft2name,tstart,tend)
        cmd2='getLATFitsFiles.py --wdir %(wdir)s --outfile %(ft2name)s --minTimestamp %(tstart)s --maxTimestamp %(tend)s --type FT2 --verbose 1 --overwrite 0' %locals()
        pass
    print cmd2
    os.system(cmd2)
    print '--> file FT2: %s' % ft2name
    return ft2name

def ReadTimeBins(ascii):
    BEFORE = par['BEFORE']
    AFTER = par['AFTER']
    fin=file(ascii,'r')
    bins=[]
    for l in fin.readlines():
        try:
            p=l.split()
            t0=float(p[0])
            t1=float(p[1])                        
            bins.add(t0)
        except:
            pass
        pass
    bins.add(t1)
    return bins

def GetGTI(ft1, time):
    hdulist = pyfits.open(ft1)
    start   = hdulist['GTI'].data.field('START')
    stop    = hdulist['GTI'].data.field('STOP')
    start.sort()
    stop.sort()
    return (start[start.searchsorted(time)-1] - time, stop[stop.searchsorted(time)]-time)


def GetLiveTimeFraction(ft2,t1,t2,index1=0):
    data        = ft2[1].data
    SC_TSTART   = data.field('START')
    SC_TSTOP    = data.field('STOP')    
    SC_LIVETIME = data.field('LIVETIME')

    while (SC_TSTART[index1] < t1):
        index1+=1
        pass        
    index2=index1
    while (SC_TSTOP[index2] < t2):
        index2 +=1
        pass
    x1=0
    x2=0
    TIMEINSAA = 0
    for i in range(index1,index2+1):
        x1 += SC_LIVETIME[i]
        x2 += (SC_TSTOP[i]-SC_TSTART[i])
        if i+1<len(SC_TSTART):
            if SC_TSTART[i+1] > SC_TSTOP[i]:
                TIMEINSAA += (SC_TSTART[i+1]-SC_TSTOP[i])
                pass
            pass
        pass
    
    LTF = x1/x2       # This takes into account only the time spent outside the SAA.
    LTF2 = x1/(t2-t1) # This includes also the SAA
    
    #print '==> Get the LIVETIME from %.3f (%d/%d), to %.3f (%d/%d), [%.3f, %.3f] *** ELAPSED TIME: %s, LIVETIME: %s, LTF1: %s, TIME SPENT IN SAA: %s, LTF2 (including the SAA): %s' % (t1, index1,len(SC_TSTART),
    #                                                                                                                                                                                   t2, index2,len(SC_TSTOP),
    #                                                                                                                                                                                   SC_TSTART[0],SC_TSTOP[-1],
    #                                                                                                                                                                                   t2-t1, x1, LTF, TIMEINSAA,LTF2)
    
    # I NEED TO FIND A BETTER WAY TO DEAL WITH THAT. THIS IS IMPLY THAT dt>resolution of the FT2 file
    if TIMEINSAA>0:
        return LTF# 2
    else:
        return LTF
    
    pass
    ##################################################
# New Implementation of the geometry
def getVector(ra,dec):
    ra1  = math.radians(ra)
    dec1 = math.radians(dec)    
    # here we construct the cartesian equatorial vector
    dir = ROOT.TVector3(math.cos(ra1)*math.cos(dec1), math.sin(ra1)*math.cos(dec1) , math.sin(dec1))
    return dir

class FT2:
    def __init__(self,filename):
        ft2            = pyfits.open(filename)
        SC_data        = ft2['SC_DATA'].data

        # TIME
        self.SC_TSTART     = SC_data.field('START')
        self.SC_TSTOP      = SC_data.field('STOP')
        

        # BORESIGHT:
        self.RA_SCZ    = SC_data.field('RA_SCZ')
        self.DEC_SCZ   = SC_data.field('DEC_SCZ')
        
        self.RA_SCX    = SC_data.field('RA_SCX')
        self.DEC_SCX   = SC_data.field('DEC_SCX')

        self.ROCK_ANGLE  = SC_data.field('ROCK_ANGLE')
        
        self.RA_ZENITH   = SC_data.field('RA_ZENITH')
        self.DEC_ZENITH  = SC_data.field('DEC_ZENITH')
        
        # SC POSITION
        self.SC_POSITION         = SC_data.field('SC_POSITION')
        self.GEOMAG_LAT  = SC_data.field('GEOMAG_LAT')
        
        self.LAT_GEO     = SC_data.field('LAT_GEO')
        self.LON_GEO     = SC_data.field('LON_GEO')
        
        self.B_MCILWAIN  = SC_data.field('B_MCILWAIN')
        self.L_MCILWAIN  = SC_data.field('L_MCILWAIN')

        #ORBITAL POLES
        self.RA_NPOLE    = SC_data.field('RA_NPOLE')
        self.DEC_NPOLE   = SC_data.field('DEC_NPOLE')
        
        self.max_SC_TSTOP  = max(self.SC_TSTOP) 
        self.min_SC_TSTART = min(self.SC_TSTART)
        print self.min_SC_TSTART, self.max_SC_TSTOP
        ft2.close()
        
        
    def getThetaPhi(self,MET,RA,DEC,i=0):
        #print MET
        if self.max_SC_TSTOP < MET or self.min_SC_TSTART> MET:
            raise Exception('Error, FT2 file does not cover the MET (%s) of the GRB FT2 Time min,max= (%s,%s)' % (MET,self.min_SC_TSTART-MET,self.max_SC_TSTOP-MET))        
        while (self.SC_TSTOP[i]-MET)<0: i=i+1
        
        v0    = getVector(RA,DEC)
        vz    = getVector(self.RA_SCZ[i],self.DEC_SCZ[i])
        vx    = getVector(self.RA_SCX[i],self.DEC_SCX[i])
        vy    = vz.Cross(vx)
        theta = math.degrees(v0.Angle(vz))    
        phi   = math.degrees(math.atan2(vy.Dot(v0),vx.Dot(v0)))
        if phi<0: phi+=360
        return theta, phi, i
    
    def getRaDec(self,MET,theta,phi,i=0):
        if self.max_SC_TSTOP < MET or self.min_SC_TSTART> MET:
            raise Exception('Error, FT2 file does not cover the MET (%s) of the GRB FT2 Time min,max= (%s,%s)' % (MET,self.min_SC_TSTART-MET,self.max_SC_TSTOP-MET))
        
        while (self.SC_TSTOP[i]-MET)<0: i=i+1
        
        
        vz    = getVector(self.RA_SCZ[i],self.DEC_SCZ[i])
        vx    = getVector(self.RA_SCX[i],self.DEC_SCX[i])
        vx.Rotate(math.radians(phi),vz)
        vy    = vz.Cross(vx)
        vz.Rotate(math.radians(theta),vy)
        dec = math.degrees(math.asin(vz.z()))
        ra  = math.degrees(math.atan2(vz.y(),vz.x()))
        if ra<0: ra+=360
        return ra,dec,i
    def getSAA(self):
        self.SAA_TSTART = []
        self.SAA_TSTOP  = []        
        for t0,t1 in zip(self.SC_TSTART[1:],self.SC_TSTOP[:-1]):
            if t0-t1>30:
                self.SAA_TSTART.append(t1) 
                self.SAA_TSTOP.append(t0) 
                pass
            pass
        return self.SAA_TSTART,self.SAA_TSTOP
    
    def isSAA(self,MET,i):
        if self.SC_TSTART[i]>MET: inSAA=1
        else:   inSAA=0
        return inSAA

        #for t0,t1 in zip(self.SAA_TSTART,self.SAA_TSTOP):
        #    if t>t0 and t<t1: return 1
        #    if t0>t: return 0 
        #    pass
        #return 0
        
        
def getLiveTimeCubes(LTCFILE,RA,DEC):
    import pyfits
    lc_file=pyfits.open(LTCFILE)
    table2 = lc_file[2].data
    ra =table2.field('RA')
    dec=table2.field('DEC')
    cos=table2.field('COSBINS')
    h0=lc_file[2].header
    tstart=h0['TSTART']
    tstop =h0['TSTOP']
    print 'ltcubeFile: %s tstart: %s tstop: %s duration: %s '%(LTCFILE,tstart,tstop,tstop-tstart)
    #dist=sqrt((ra[i]-RA)*(ra[i]-RA)+(dec[i]-DEC)*(dec[i]-DEC))
    nbins=len(ra)
    distMin=180.0
    iMin=0
    for i in xrange(nbins):
        dist=sqrt((ra[i]-RA)*(ra[i]-RA)+(dec[i]-DEC)*(dec[i]-DEC))
        if dist<distMin:
            distMin=dist
            iMin=i
            pass
        pass
    print iMin,ra[iMin],dec[iMin],distMin
    print cos[iMin]
    pass

