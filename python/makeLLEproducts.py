#This is just a wrapper around mkdrm_ez.py, which has been written by Nicola Omodei

#Author: G.Vianello (giacomov@slac.stanford.edu)

import os

def makeLLEproducts(**kwargs):
  #### Mandatory parameters
  #GRB coordinates
  RA                          = None
  DEC                         = None
  #GRB name (the same used in the Montecarlo production)
  basename                    = None
  #Trigger time
  TRIGTIME                    = None
  #Start and stop time for the response matrix
  rspTstart                   = 0.0
  rspTstop                    = None
  
  ### Optional parameters with default values
  #Configuration file
  configFile                  = "config/DefaultLLE.txt"
  
  #Mode: if this is None both RSP both PHA are produced.
  #if mode="rsp" only the response is made, if mode="pha"
  #only the CSPEC is made  
  mode                        = None
  #Input FT2 file (if no ft2 file is passed, the code will download
  #a new one)
  ft2file                     = None
  #Time step for CSPEC file
  dt                          = 1.0
  #Radius for the ROI: if this is a positive value, it means
  #a fixed ROI with that size (in degrees). If this is negative,
  #it means a energy dependent ROI with the containment radius
  #equal to a certain number of sigma (for example, -1 means
  #a energy dependent ROI with 68% containment radius)
  RADIUS_ROI                  = 12
  #Maximum allowed zenith angle (the Zenith cut)
  ZENITHTHETA                 = 100.0
  #Maximum allowed distance from the LAT boresight
  THETA                       = 90.0
  #Turn on or off the use of the SSD cut
  SSD                         = None
  #Turn on or off the exclusion of Transient events from the sample
  NOTRANS                     = None
  #Output directory
  outdir                      = "output_ez"

  ### Process the user input
  for key in kwargs.keys():
    if   key.lower()=="ra":          RA          = float(kwargs[key])
    elif key.lower()=="dec":         DEC         = float(kwargs[key])
    elif key.lower()=="configfile":  configFile  = str(kwargs[key])        
    elif key.lower()=="basename":    basename    = str(kwargs[key])
    elif key.lower()=="trigtime":    TRIGTIME    = float(kwargs[key])
    elif key.lower()=="rsptstart":   rspTstart   = float(kwargs[key])
    elif key.lower()=="rsptstop":    rspTstop    = float(kwargs[key])
    elif key.lower()=="mode":        mode        = str(kwargs[key])
    elif key.lower()=="dt":          dt          = float(kwargs[key])
    elif key.lower()=="radius_roi":  RADIUS_ROI  = float(kwargs[key])
    elif key.lower()=="zeniththeta": ZENITHTHETA = float(kwargs[key])
    elif key.lower()=="theta":       THETA       = int(kwargs[key])
    elif key.lower()=="ssd":         SSD         = int(kwargs[key])
    elif key.lower()=="notransient": NOTRANS     = int(kwargs[key])
    elif key.lower()=="outdir":      outdir      = str(kwargs[key])
    elif key.lower()=="ft2file":     ft2file     = str(kwargs[key])               
  pass
  
  #Check for proper input
  if(RA==None or DEC==None or basename==None or TRIGTIME==None 
     or rspTstart==None or rspTstop==None):
     raise RuntimeError("MakeLLEproducts():you have to give all the mandatory parameters (ra,dec,basename,trigtime,rspTstart,rspTstop)")
  pass
  
  #mkdrm_ez takes as argument OFFSET and DURATION, instead of simple tstart and tstop,
  #for the response matrix. Thus, translate from rspTstart and rspTstop to offset and
  #duration
  OFFSET                      = rspTstart
  DURATION                    = rspTstop-rspTstart
  
  #Here we should have everything we need, let's build the command line for mkdrm_ez:
  cmdLine                     = "python -m mkdrm_ez -i %s -ra %s -dec %s -n %s -t %s -d %s -off %s" %(configFile,RA,DEC,basename,TRIGTIME,DURATION, OFFSET)
  cmdLine                    += " -dt %s -r %s -zenith %s -theta %s" %(dt,RADIUS_ROI,ZENITHTHETA,THETA)
  cmdLine                    += " -outdir %s -ft2 %s" %(outdir,ft2file)
  
  if(mode!=None):
    cmdLine                  += " -m %s" %(mode)
  if(SSD!=0 and SSD!=None):
    cmdLine                  += " -ssd"
  if(NOTRANS!=0 and NOTRANS!=None):
    cmdLine                  += " -notransient"

  print("About to run mkdrm_ez with this parameters:")
  print("%s" %(cmdLine))
  
  os.system(cmdLine)
    
pass
