# PRFMAP v2.0
Pythonic version of PRFMAP, with also several changes in the intimate structure of the code. 
The original PRFMAP was developed by Andreas Faisst (afaisst@ipac.caltech.edu) and Peter Capak. The program creates a set of FITS files modelling the Spizter/IRAC Point Response Function (PRF) at different positions of an IRAC mosaic. The user decides how coarse/fine the grid of PRFs should be. At any given "node" (or "grid point") PRFMAP evaluate the PRF profile resulting from the different Spitzer observations at that location, as each frame may have a different orientation (and the IRAC PRF is *not* rotationally symmetric). 

### Main improvements in the present version
 - 100% Python 3, no need to install IRAF and/or R;
 - "verbose" and "debug" options to run the code in different modes;
 - higher computational efficency and less disk space needed (To Be Completed);
 - additional tools e.g. to resample the pixel grid of output PRF models;
 - ...

### Known issues
 - Parallelization has been designed to work on Candide cluster computer: it may be sub-optimal on other machines. 
 - Centroid of PRF models still offset with respect to their FITS file pixel grid.  

### Installing PRFMAP
Besides the python scripts in the `src/` folder, one has to populate the `prfmod/` folder, which should contain the basic PRF models of the IRAC camera, which have been characterized as a function of the IRAC channel (from 1 to 4) and the position orelative to the detector (i.e., the PRF at the center of a frame is different from the corner). These **basic models** can be downloaded from [the IPAC website](https://irsa.ipac.caltech.edu/data/SPITZER/docs/irac/calibrationfiles/psfprf/).  
