#!/usr/bin/env python

def Do(RA          = 0,
       DEC         = 0,
       ZENITHTHETA = 180,
       THETAMAX    = 0.0,
       THETA       = 0.0,
       RADIUS      = 1.0,
       myCut       = '1==1',
       verbose     = 0,
       ENERGYVAR   = 'EvtEnergyCorr'):
    # This define the cut on zenith angle
    ZenithCut='FT1ZenithTheta<%s' % ZENITHTHETA
    ThetaCut ='FT1Theta<=%.1f' %(THETAMAX)
    # This defines the cut on the ROI
    if(RADIUS==0): # No ROI CUT
        ROICut ="1==1"
        pass
    elif(RADIUS<0): # Use a abs(RADIUS) number of PSF cuts, where the PSF is defined as:
        SIGMA_68_GT40 ="(10.5*min(pow(%s/100., -0.65), pow(%s/100., -0.81)))" %(ENERGYVAR,ENERGYVAR);
        SIGMA_68_LE40 ="(11.5*min(pow(%s/59., -0.55), pow(%s/59.,  -0.87)))" % (ENERGYVAR,ENERGYVAR);
        
        if THETA>40.:   sigma=SIGMA_68_GT40
        else:           sigma=SIGMA_68_LE40
        
        # print 'Chosing LLE selection RA,DEC = (%RA,%DEC) at %s degrees. Generated cut:' %(RA,DEC,th)
        PSFModel = sigma 
        ROICut ="((cos(FT1Dec*0.0174533)*(FT1Ra - (%s)))^2+(FT1Dec- (%s))^2)< (%s*%s)^2 " %(RA,DEC,RADIUS,PSFModel)
    elif (RADIUS==888):
        ROICut = "((Tkr1FirstLayer > 5.5)*(sqrt((cos(FT1Dec*0.0174533)*(FT1Ra - (%s)))**2+(FT1Dec-(%s))**2)<0.6)+(Tkr1FirstLayer<5.5)*(sqrt((cos(FT1Dec*0.0174533)*(FT1Ra-(%s)))**2+(FT1Dec-(%s))**2)<1.2))" % (RA,DEC,RA,DEC)
    else:
        ROICut ="((cos(FT1Dec*0.0174533)*(FT1Ra - (%s)))^2+(FT1Dec- (%s))^2)< (%s)^2 " %(RA,DEC,RADIUS)
        pass
    myCut='(%s) && (%s) && (%s) && (%s)' %(myCut, ZenithCut, ThetaCut, ROICut)
    if verbose : print 'Final Selection: ', myCut
    return myCut
