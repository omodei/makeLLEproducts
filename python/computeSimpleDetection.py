#!/usr/bin/env python
import os,sys,math
import pyfits,ROOT
##################################################
#gROOT.SetStyle("Plain");
ROOT.gStyle.SetPalette(5);
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetFrameBorderMode(0)
#ROOT.gStyle.SetPadBottomMargin(0)
ROOT.gStyle.SetOptTitle(0)

#ROOT.gStyle.SetCanvasColor(10)
#ROOT.gStyle.SetPadColor(10)
ROOT.gStyle.SetFrameFillColor(10)
#ROOT.gStyle.SetPadLeftMargin(0.13);
#ROOT.gStyle.SetPadBottomMargin(0.13);
#ROOT.gStyle.SetTitleYOffset(1.3);
#ROOT.gStyle.SetTitleXOffset(1.);
##################################################
import numpy as np


def GetThetaGraph(FT2,tmin,tmax,RA_GRB,DEC_GRB,TRIGTIME):
    thetaGraph = ROOT.TGraph()
    delta_t=10.0
    import utils
    t=tmin
    i=0
    j=0
    while t<tmax:            
        (th,i)=utils.getTheta(FT2,t+TRIGTIME,RA_GRB,DEC_GRB,i)
        t+=delta_t
        #print 'Time:%s Theta=%s' %(t,th)
        thetaGraph.SetPoint(j,t,th)
        j+=1
        pass    
    return thetaGraph


    
class Fitter(object):
    def __init__(self,thetaGraph):
        self.tstart=0
        self.tstop =0
        self.graph = thetaGraph

    
    def ExcludeInterval(self,tstart,tstop):
        self.tstart             = tstart
        self.tstop              = tstop
        pass
    
    def __call__(self, x, par):
        x=x[0]
        if (x >= self.tstart and x <= self.tstop):
            ROOT.TF1.RejectPoint()
            pass #return 0
        y = math.radians(min(self.graph.Eval(x),89.9))
        Cy=math.cos(y)
        return (par[0] + par[1]*x + par[2]*x*x)*Cy# + par[2]*x #Cy*Cy
      
def LiMa(Non, Noff, Tin, Tout):
    a=Tin/(Tout)
    R=math.pow((1.0+Noff/Non)*a/(1.0+a),Non)*math.pow((1.0+Non/Noff)/(1.0+a),Noff);
    Sigma=math.sqrt(-2.0*math.log(R))
    print 'Number of expected photons: %s'%Non
    print 'Number of observed event: %s' %Noff
    print 'Probability: %f %% (%.1f sigma)' %(R*100,Sigma)
    print a,R,Sigma
    pass

def li_and_ma_equivalent_for_gaussian_background(Nobs, Nexp,sigma_b):
    if Nobs==0: return 0.,0.
    b0 = 0.5 * (np.sqrt(Nexp ** 2 - 2 * sigma_b ** 2 * (Nexp - 2 * Nobs) + sigma_b ** 4) + Nexp - sigma_b ** 2)
    P=Nobs * np.log(Nobs / b0) + (b0 - Nexp) ** 2 / (2 * sigma_b ** 2) + b0 - Nobs
    S = np.sqrt(2) * np.sqrt(P)
    sign = np.where(Nobs > Nexp, 1, -1)
    #print 'Nobs=%10.3f  Nexp=%10.3f sigma_b=%10.3f P=%10.3f sign * S=%10.3f' %(Nobs, Nexp,sigma_b,P,sign * S)
    return P,sign * S

def Poisson(Nobs, Nexp):
    if Nobs==0: return 0,0
    if Nexp<0: Nexp=0
    try: 
        R = math.pow(Nexp,Nobs)*math.exp(-Nexp)/math.factorial(Nobs)
    except:
        R=1
        pass
    
    if R==0:
        sigma = 0
    else:
        sigma = math.sqrt(-2.0*math.log(R))
    #print 'Nobs=%d, Nexp=%.1e, P=%.2f, (%.1f)' %(Nobs,Nexp,R,sigma) 
    return R,sigma
    # print 'Number of expected photons: %s'%Nexp
    #   print 'Number of observed event: %s' %Nobs
    #   print 'Probability: %e (%.1f sigma)' %(R,sigma)



def LiMa2(Non, Noff, Tin, Tout):
    a=Tin/(Tout)
    R=math.pow((1.0+Noff/Non)*a/(1.0+a),Non)*math.pow((1.0+Non/Noff)/(1.0+a),Noff);
    Sigma=math.sqrt(-2.0*math.log(R))
    print 'Number of expected photons: %s'%Non
    print 'Number of observed event: %s' %Noff
    print 'Probability: %f %% (%.1f sigma)' %(R*100,Sigma)
    print a,R,Sigma
    pass


def defineBins(times,ds,dt):
    tmin=min(times)
    tmax=max(times)
    N=0
    i=0
    _t=ds    
    while _t>tmin:
        i+=1
        _t-=dt
        pass
    N=(i-1)
    tmin=ds-N*dt
    i=0
    _t=ds
    while _t<tmax:
        i+=1
        _t+=dt
        pass
    N+=(i-1)
    tmax=ds+(i-1)*dt
    time_bins=np.linspace(tmin,tmax,N+1)
    #print  time_bins
    return tmin,tmax,N
    

def makeLC(fitsFile,name,t0=0,dt=1.0,ds=0.0,EMIN=10,EMAX=10000):
    #print dt,EMIN,EMAX
    fin = pyfits.open(fitsFile)
    #fin.info()
    hd=fin['EVENTS']
    data=hd.data
    head=hd.header
    #print head
    #print data.names
    time=data.field('TIME')
    energy=data.field('ENERGY')
    #t0=head['TRIGTIME']
    time=time-t0
    tmin,tmax,Nbins=defineBins(time,ds,dt)
    histo=ROOT.TH1D(name,'Light Curve',Nbins,tmin,tmax)
    histo.GetXaxis().SetTitle("Time [s]")
    histo.GetXaxis().CenterTitle(1)
    histo.GetYaxis().SetTitle("Rate [Hz]")
    histo.GetYaxis().CenterTitle(1)
    for i,t in enumerate(time):
        if energy[i]>EMIN and energy[i]<EMAX:  histo.Fill(t)
        pass
    return histo

    
def detectExcess(fitsFile,w=10,s=1,x=100):
    fin    = pyfits.open(fitsFile)
    hd     = fin['EVENTS']
    data   = hd.data
    head   = hd.header
    time   = data.field('TIME')    
    energy = data.field('ENERGY')
    if len(time)<=w : return None,None,0
    tt=head['TRIGTIME']
    time=time-tt
    tmin=min(time)
    tmax=max(time)
    N   = len(time)
    t0  = time[0]
    t1  = time[w]
    R01 = w/(t1-t0)
    histo_rates=ROOT.TH1D('rates','rates',100,0,100)
    histo_rates_test=ROOT.TH1D('test','test',100,0,100)
    histo_rates_test.SetLineColor(ROOT.kBlue)
    M=N
    S=N
    detected=0
    for i in range(N-s-w):
        t2  = time[i+s]
        t3  = time[i+s+w]
        R23 = w/(t3-t2)
        histo_rates.Fill(R23)
        if t2<0:
            histo_rates_test.Fill(R23)            
        else:
            M = histo_rates_test.GetMean()
            S = histo_rates_test.GetRMS()
            pass
        if R23 > M+x*S :
            detected=1
            #print 'detection at %s (%s - %s) (%.1f)' % ((t3+t2)/2.,R01,R23,(R23-M)/S)
        # x*R01: print 'detection at %s (%s - %s) (%.1f)' % ((t3+t2)/2,R01,R23,R23/R01)
        R01=R23
        pass    
    return histo_rates,histo_rates_test,detected



def detectExcess2(histo,ThetaGraph,XMIN_SIG=-10,XMAX_SIG=100,NSIGMA=4,FUN='bkg', gauss=False):
    
    NBins    = histo.GetNbinsX()
    tmin     = histo.GetBinLowEdge(1)
    binwidth = histo.GetBinWidth(NBins)
    tmax     = histo.GetBinLowEdge(NBins)+binwidth
    name     = histo.GetName()
    
    XMAX_SIG = min(XMAX_SIG,tmax-1.5*binwidth)
    
    print name,' In file: ',tmin,tmax,'to fit:',XMIN_SIG,XMAX_SIG,'<--------------------------------------------------'

    
    #if tmin>0: return None,None,0
    histo2=ROOT.TH1D(name+'bkg','Background Subtraction',NBins,tmin,tmax)
    histo_p=ROOT.TH1D(name+'pro','Signal Significance',NBins,tmin,tmax)
    histo_p2=ROOT.TH1D(name+'propoiss','Signal Significance',NBins,tmin,tmax)

    histo2.GetXaxis().SetTitle("Time [s]")
    histo2.GetXaxis().CenterTitle(1)
    histo2.GetYaxis().SetTitle("Counts")
    histo2.GetYaxis().CenterTitle(1)
    
    histo_p.GetXaxis().SetTitle("Time [s]")
    histo_p.GetXaxis().CenterTitle(1)
    histo_p.GetYaxis().SetTitle("Standard Deviations [#sigma]")
    histo_p.GetYaxis().CenterTitle(1)

    sigma_b=[]
    for i in range(NBins):
        x=histo.GetBinCenter(i+1)
        y=histo.GetBinContent(i+1)
        dy=histo.GetBinError(i+1)
        histo2.SetBinContent(i+1,y)
        histo2.SetBinError(i+1,dy)
        pass
    
    fitter = Fitter(ThetaGraph)
    fitter.ExcludeInterval(XMIN_SIG,XMAX_SIG)
    myFitFunction_name=name+"fitfun"
    
    if 'pol' in FUN:
        myFitFunction = ROOT.TF1(myFitFunction_name,FUN,tmin,tmax)
        myFitFunction.SetParameters(1.0,1.0,1.0)
    else:
        myFitFunction = ROOT.TF1(myFitFunction_name,fitter,tmin,tmax,3)
        myFitFunction.SetParameters(1.0,1.0,1.0)
        pass
    print 'FITTING WITH FUNCTION %s' % myFitFunction_name
    histo2.Fit(myFitFunction_name)
    
    functions= histo2.GetListOfFunctions()
    bkg      = functions.FindObject(myFitFunction_name)
    
    sign_gauss   = 0
    sign_poiss   = 0
    t_first      = 666
    t_last       = -666
    
    sigma_b_array=[]
    for i in range(NBins):   
        x=histo.GetBinCenter(i+1)
        if x < XMIN_SIG or x > XMAX_SIG: 
            y = histo.GetBinContent(i+1)
            b = max(0,bkg.Eval(x))
            #print x,y,b
            sigma_b_array.append(y-b)
            pass
        pass
    sigma_b_array=np.array(sigma_b_array)
    sigma_b=np.std(sigma_b_array)
        
    for i in range(NBins):        
        x = histo.GetBinCenter(i+1)
        y = histo.GetBinContent(i+1)
        dy= histo.GetBinError(i+1)
        b = max(0,bkg.Eval(x))
        #d = b+math.sqrt(b)+dy        
        # if d==0: sigma = 0
        # else:
        if dy==0: sigma_g=0
        else: sigma_g = (y-b)/(dy)
        histo_p.SetBinContent(i+1,sigma_g)
        Nobs, Nexp = y,b
        #prob,sigma_p=Poisson(Nobs, Nexp)
        prob,sigma_p=li_and_ma_equivalent_for_gaussian_background(Nobs, Nexp, sigma_b)
        histo_p2.SetBinContent(i+1,sigma_p)

        if  gauss: _sigma = sigma_g
        else:      _sigma = sigma_p

        #if x > XMIN_SIG and x < XMAX_SIG:
        sign_gauss  =max(sign_gauss,sigma_g)
        sign_poiss  =max(sign_poiss,sigma_p)
        # print '%d %d x:%.2f dx:%.2f y:%.2f dy:%.2f b:%.2f db:%.2f [g:%.2f p:%.2f]' %(i,NBins,x,binwidth,y,dy,b,sigma_b,sigma_g,sigma_p)            
        # ESTIMATE THE DURATION:
        if _sigma > NSIGMA:
            print '%d %d x:%.2f dx:%.2f y:%.2f dy:%.2f b:%.2f db:%.2f [g:%.2f p:%.2f]' %(i,NBins,x,binwidth,y,dy,b,sigma_b,sigma_g,sigma_p)            
            if histo.GetBinLowEdge(i+1)<t_first: t_first = histo.GetBinLowEdge(i+1)
            t_last = histo.GetBinLowEdge(i+1)+histo.GetBinWidth(i+1)
            pass
        # pass
    pass
    histo_p.SetMinimum(0)
    histo_p.SetMaximum(10)
    histo_p.SetLineColor(ROOT.kRed)
    histo_p2.SetLineColor(ROOT.kGreen)

    histo2.SetLineColor(ROOT.kBlue)
    histo2.SetLineWidth(2)
    histo_p.SetLineWidth(2)
    histo_p2.SetLineWidth(2)
    histo2.SetMinimum(0.0)# histo.GetMinimum())
    histo2.SetMaximum(histo.GetMaximum()+math.sqrt(histo.GetMaximum()))    
    return histo2,histo_p,histo_p2,sign_gauss,sign_poiss,t_first,t_last

if __name__=='__main__':
    fitsFile=sys.argv[1]
    dt=1,
    EMIN=10
    EMAX=10000
    x=10
    w=20
    s=1
    plot=False
    for i,a in enumerate(sys.argv):
        if a=='-plot': plot=True
        if a=='-dt': dt=float(sys.argv[i+1])
        if a=='-s':  s=float(sys.argv[i+1])
        if a=='-x':  x=float(sys.argv[i+1])
        if a=='-w':  w=float(sys.argv[i+1])
        if a=='-emin': EMIN=float(sys.argv[i+1])
        if a=='-emax': EMAX=float(sys.argv[i+1])
        pass
    
    histo=makeLC(fitsFile,dt,EMIN,EMAX)
    histo_rates,histo_rates_test,detected=detectExcess(fitsFile,w,s,x)
    if plot:
        C=ROOT.TCanvas("C","C")
        C.Divide(1,2)
        C.cd(1)
        
        histo.Draw('E0')
        C.cd(2)
        ROOT.gPad.SetLogy()
        histo_rates.SetMaximum(histo.GetMaximum())
        histo_rates.SetMinimum(0)
        histo_rates.Draw()
        histo_rates_test.Draw('same')
        ROOT.gPad.Update()
        a=raw_input('Continue')
        pass
    
    #sig=histo.ShowPeaks(sigma=2,threshold=0.1)

    #bkg=histo.ShowBackground()
    #functions = histo.GetListOfFunctions()
    #peaks = functions.FindObject("TPolyMarker")
    #peaks.SetMarkerColor(ROOT.kGray)
    #Npeaks=peaks.GetN()
    #Xpeaks=peaks.GetX()
    #Ypeaks=peaks.GetY()
    #obj=[]
    #for i in range(Npeaks):
    #    Ybkg = bkg.GetBinContent(bkg.FindBin(Xpeaks[i]))
    #    Prob,sigmaPoisson=Poisson(int(Ypeaks[i]),Ybkg)
    #    if sigmaPoisson>4.0:
    #        print i, Xpeaks[i],Ypeaks[i],Ybkg,Ypeaks[i]/math.sqrt(Ybkg),sigmaPoisson
    #        m=ROOT.TMarker(Xpeaks[i],Ypeaks[i],23)
    #        m.SetMarkerColor(2)
    #        m.Draw()
    #        obj.append(m)
    #    pass

