# PRFMAP v2.0
Pythonic version of PRFMAP, with also several changes in the intimate structure of the code. 
The original PRFMAP was developed by Andreas Faisst (afaisst@ipac.caltech.edu) and Peter Capak. 

### Main improvements in the present version:
 - 100% Python 3, no need to install IRAF and/or R;
 - "verbose" and "debug" options to run the code in different modes;
 - higher computational efficency and less disk space needed (To Be Completed);
 - additional tools e.g. to resample the pixel grid of output PRF models;
 - ...

### Known issues:
 - Parallelization has been designed to work on Candide cluster computer: it may be sub-optimal on other machines. 
 - Centroid of PRF models still offset with respect to their FITS file pixel grid.  
