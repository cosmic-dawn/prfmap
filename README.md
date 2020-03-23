# PRFMap v2.0
Pythonic version of PRFMap, with also several changes in the intimate structure of the code. 
The original PRFMap was developed by Andreas Faisst (afaisst@ipac.caltech.edu) and Peter Capak. The program creates a set of FITS files modelling the Spizter/IRAC Point Response Function (PRF) at different positions of an IRAC mosaic.

**PRFMap in a nutshell**. The code creates a grid of points across an IRAC mosaic (provided in input as FITS image). For each point, it finds the overlapping frames (i.e., the observing blocks) that contributed to the mosaic. PRFMap creates a specific PRF model for each of those frames, as the IRAC PRF is *not* rotationally symmetric and it does depend on the orientation of the frame (its Position Angle, PA). All these PRFs are stackeded and the result is the PRF profile of the mosaic at that location.  

## Main improvements in the present version
 - 100% Python 3, no need to install IRAF and/or R;
 - "verbose" and "debug" options to run the code in different modes;
 - higher computational efficency and less disk space needed (To Be Completed);
 - additional tools e.g. to resample the pixel grid of output PRF models;
 - ...

## Known issues
 - Parallelization has been designed to work on Candide cluster computer: it may be sub-optimal on other machines. 
 - Centroid of PRF models still offset with respect to their FITS file pixel grid.  

## Installing PRFMap v2
Besides the python scripts in the `src/` folder, one has to populate the `prfmod/` folder, which should contain the basic PRF models of the IRAC camera, which have been characterized as a function of the IRAC channel (from 1 to 4) and the position orelative to the detector (i.e., the PRF at the center of a frame is different from the corner). These **basic models** can be downloaded from [the IPAC website](https://irsa.ipac.caltech.edu/data/SPITZER/docs/irac/calibrationfiles/psfprf/).  

## How it works
The main program is `prfmap.py` and is executed as a python script via command line. It has several functionalities ("actions") that can ve specified with the corresponding argument. It also requires a **configuration file** where the most important parameters are specified. The list of functionalities and options that can be printed out with the command `python src/prfmap.py -h`. Note that all the example codes are in a bash shell assuming that the present working directory is the one where you cloned/installed the PRFMAPv2 package. 

### Explaining the configuration file
See `example.par`:
```
# Input config file for PRFMap v2.0
#############################
# paths to useful directories
PATH_PRFMOD  prfmod/cryo  #the directory where the basic PRF models are stored
PATH_OUTPUT prfout_test  #the directory where the output will be saved
#############################
# file names
FILE_MOSAIC example_data/mosaic/A2744.0.irac.1.mosaic.fits   #the IRAC mosaic to be mapped
FILE_FRAMELIST example_data/frames.lst   #frames that made the mosaic (list of *_bcd.fits file)
FILE_PRFMOD  ch1_prfmap_x10.tbl   #table (from the IPAC website) with the carachteristics of the basic models (must be located in PATH_PRFMOD)
FILE_GRID TBD    #grid where to evaluate the PRF (it can be created 'by hand' by the user)
FILE_PRFS  prfout_test/prfmap_models_ch1.txt   #list of all frames associated to every grid point

PRF_RAD  8   # core of the PRF (in mosaic's pixels)
GRID_SPACE  6  # to set the distance between two nodes on the PRF map (=PRF_RAD*GRID_SPACE)
PRF_SAMP 100  # (over-)sampling of the basic PRF models listed in FILE_PRFMOD

### Facultative (comment out to activate):
#RA_LIM  149.05,151.07   #min and max RA of the grid
#DEC_LIM  1.38,3.08    #min and max Dec of the grid
```

### Other options
 - `-v` or `--verbose`: print out comments while running
 - `-d` or `--debug`: save additional files for sanity checks
 - `-p` or `--parallel`: multi-thread processing
 - Moreover, all the paths and file names can be set also via command line, over-writing the parameter in the configuration file. For example: `python src/prfmap.py action -v -d -p PATH_OUTPUT /new/path/` 

### Action 1

```bash
$ python src/prfmap.py grid  
```
