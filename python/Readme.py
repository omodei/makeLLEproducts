#! /usr/local/bin python

class ReadmeFile:
    def __init__(self,fileName):
        self.filename = fileName
        self.myfile   = file(fileName,'w')
        pass
    
    def cutFile(self,longFileName):
        if longFileName is None: return None
        return longFileName[longFileName.rfind('/')+1:]
    
    def WriteReadme(self):
        txt=''
        txt+=75*'-'+'\n'
        txt+='''This directory contains LAT Low Energy (LLE) data products in FITS
format and quicklook PNG images, which display diagnostic information
regarding the quality of the LLE data product.

The naming scheme used is bnyymmddfff, where yymmdd is the date of the
burst (yy, the year minus 2000; mm, the two-digit month; and dd, the
two-digit day of the month), fff = fraction of day, and xx = version number.

The files are:

    gll_lle_bnyymmddff_vxx.fit:  An event file containing the events passing
    the LLECUT (saved in the header of each file extension). Events in this
    file can be used with gtselect and gtbin (part of the ScienceTools) to
    select or bin events. Events from -1000.0 to +1000.0 seconds from the
    trigger time have been selected. Additionally, a cut centered on the
    region-of-interest has been applied.

    gll_cspec_bnyymmddff_vxx.fit:  LLE data binned in energy and time, with
    1 second resolution. These files have the same format as the GBM CSPEC
    files and are suitable to be used in rmfit.

    gll_cpsec_bnyymmddff_vxx.rsp:  This file contains the matrix describing
    the detector response, when available. The response is produced with the
    same event selection of the CSPEC file, and it is meant to be used for
    spectral fitting in rmfit or XSPEC.

    gll_pha_bnyymmddff_vxx.fit:  This file contains the count spectrum
    (PHA-I). The PHA-I file is created from the same time interval used
    to compute the response matrix.

    gll_selected_bnyymmddff_vxx.fit:  This file is identical to the
    LLE event file with an additional time selection applied to match the
    cut used to compute response matrix and PHA-I files.

    gll_pt_bnyymmddff_vxx.fit: A LAT pointing and livetime history file but
    with entries every second (instead of every 30 seconds). It spans 4600
    seconds before and 4600 after the trigger time.

    gll_quick_bnyymmddff_vxx.png: The four plots on the canvas are relative
    to the selected events.  The first plot (upper left) is a light curve
    displaying the time series of LLE events. Vertical dashed lines
    correspond to the sub selection of events (If the response matrix is
    computed, these lines delimit the interval of time in which the response
    file is computed). The second plot (upper right) shows the distribution
    of reconstructed angles with respect the LAT boresight. Zero degrees
    corresponds to normal incidence. The third plot (lower left) displays
    the distribution of reconstructed energies (count spectrum) of the LLE
    selected events. The last plot (lower right) is a two dimensional
    histogram showing the reconstructed direction (in J2000 equatorial
    coordinates) of events after LLE selection.

    gll_cspec_bnyymmddff_vxx.png:  This 2 dimensional histogram displays the
    LLE events binned in time and energy. This is the graphical equivalent
    of the binned CSPEC file.

    gll_edisp_bnyymmddff_vxx.png:  This series of plots show the energy
    dispersion (Reconstructed-Montecarlo)/Montecarlo for different incident
    "Montecarlo" energy beams.
    
    gll_effarea_bnyymmddff_vxx.png: In this canvas two plots are displayed.
    The plot on the top shows the response of the instrument to a flat in
    log10(MCEnergy) spectrum (N(E)~1/E), as a function of the true (x-axis)
    and of the reconstructed (y-axis) energy. This is the graphical
    representation of the Detector Response Matrix. The second plot shows
    the projection of the DRM along the y-axis, which is conventionally
    defined as "effective area". It shows the efficiency of the LLE
    selection to a flat incident spectrum.
    
    gll_mcvar_bnyymmddff_vxx.png:  This four panel plot shows the light
    curve (upper left), the distribution of reconstructed incident angles
    (upper right), the reconstructed directions in instrument (lower left)
    and celestial (lower right) coordinates for the Montecarlo simulation.
    '''
        txt+=75*'='+'\n'
        print 'Read-me file:',self.filename
        print txt
        self.myfile.write(txt)
        self.myfile.close()        
        pass
    pass

if __name__=='__main__':
    R=ReadmeFile('README.txt')
    R.WriteReadme()
    
