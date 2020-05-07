# PRFMap v2.0
Pythonic version of PRFMap, also including several changes in the intimate structure of the code. 
The original PRFMap was developed by Andreas Faisst (afaisst@ipac.caltech.edu) and Peter Capak. The program creates a set of FITS files modelling the Spizter/IRAC Point Response Function (PRF) at different positions across an IRAC mosaic.

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
If you prefer to learn by examples, go to the **Test run** section below. The main program is `prfmap.py` and is executed as a python script via command line. It has several functionalities ("tasks") that can be specified with the corresponding argument right after the script name (see below). It also requires a **configuration file** where the most important parameters are specified. The list of functionalities and options that can be printed out with the command `python src/prfmap.py -h`. Note that all the example codes are in a bash shell assuming that the present working directory is the one where you cloned/installed the PRFMAPv2 package. 

### The configuration file
It is compulsory to specify the location of the configuration file through the `-c` or `--config` option:
```
$ python task -c /path/to/config.file
$ python task --config=/path/to/config.file
```
where `task` can be any of the tasks decribed in the following. To have an example of configuration file, open `example.par`:
```
## Input config file for PRFMap v2.0 ##

### paths to useful directories
PATH_OUTPUT example_data/prfout_test  #the directory where the output will be saved

### file names
FILE_MOSAIC example_data/mosaic/A2744.0.irac.1.mosaic.fits   #the IRAC mosaic to be mapped
FILE_FRAMELIST example_data/frames.lst   #frames that made the mosaic (list of *_bcd.fits file)
FILE_PRFMOD  ch1_prfmap_x10.tbl   #full path to the table (downloaded from the IPAC website) including the basic PRF models (in different detector coordinates). FILE_PRFMOD must be located in the directory where those basic PRF models are stored.
FILE_GRID example_data/prfout_test/map_prf_grid.txt    #full path to grid file indicating where to evaluate the PRF 
FILE_PRFS  example_data/prfout_test/prfmap_models_ch1.txt   #full path to file listing all frames associated to every grid point

### PRF details
PRF_RAD  8   # core of the PRF (in mosaic's pixels)
GRID_SPACE  6  # to set the distance between two nodes on the PRF map (=PRF_RAD*GRID_SPACE)
PRF_SAMP 100  # (over-)sampling of the basic PRF models listed in FILE_PRFMOD

### Facultative (comment out to activate):
#RA_LIM  149.05,151.07   #min and max RA of the grid
#DEC_LIM  1.38,3.08    #min and max Dec of the grid
```

Please note that any of the input FITS frames listed in FILE_FRAMELIST, or FILE_MOSAIC, can be replaced by an ASCII file containing the FITS header. When the file name does not end with '.fits', PRFMAP assumes it is a header-only ASCII file. 
### Other options
 - `-v` or `--verbose`: print out comments while running
 - `-d` or `--debug`: save additional files for sanity checks
 - `-p` or `--parallel`: multi-thread processing
 - Moreover, all the paths and file names can be set also via command line, over-writing the parameter in the configuration file. For example: `python src/prfmap.py task -v -d -p PATH_OUTPUT /new/path/`.

### Task 1: draw the grid

```bash
$ python src/prfmap.py grid -c example.par 
```

The program analyses the geometry of the IRAC mosaic (specified as FITS file `FILE_MOSAIC`) and draw a rectangular grid where the distance between points is set in the configuration file (`PRF_RAD` times `GRID_SPACE`). To cover only a portion of the mosaic, use the parameters `RA_LIM` and `DEC_LIM` in the configuration file. Coordinates of the grid points, and their ID number, are saved in the ASCII file `FILE_GRID`. The user can create their own (e.g., irregualr) grid, as long as the `FILE_GRID` format is respected: 
```
# RA Dec X Y ID_GRIDPT
3.7558143 -30.4636978 25  25 1
3.7558042 -30.4465922 25 105 2
...
```
See and example in `example_data/comparison_output/map_prf_grid.txt`. The match between grid points and IRAC frames is made in WCS, so the RA,Dec coordinates of a hand-made `FILE_GRID` must be correct; X,Y are not used in the process so in principle they can be dummy values like -99.
The `--debug` option will pring a .reg file to visualize the grid in DS9, and individual grids for each frame in a dedicated sub-folder of the `PATH_OUTPUT` directory. 

### Task 2: associate frame PRFs to each grid point

```bash
$ python src/prfmap.py models -c example.par 
```

This is a preliminary step analysizing each grid point included in `FILE_GRID`, before preparing their PRF model (Task 3). All frames (`*_bcd.fits` files) overlapping a given grid point are identified, with their orientation (PA) and position on the detector (corrsiponding to a specific PRF among the basic models included in `FILE_PRFMOD`). This information is saved in the ASCII file `FILE_PRFS` and will be used in the next step of the PRFMAP proceudre. Note that the file may be very large: a frame  appears multiple times, depending on how many grid points overlap the area of the frame. See below (**Large mosaics and parallelization**) for more details about mosaics made by a large number of frames (or fine grids with a very large number of points). 

### Task 3: create the final PRF model for each grid point

```bash
$ python src/prfmap.py stack -c example.par 
```

The individual PRFs (corresponding to single frames) that are associated to the same grid point are rotated (accordingly to their PA value) and stacked together. Corresponding grid point IDs and PAs are found in `FILE_PRFS`. The stacked image is the final PRF in that point of the mosaic. All PRFs are stored in `PATH_OUTPUT` in the sub-folder `PRFstack`. Their file names are always `mosaic_gp??????.fits` where ?????? is the integer ID number of that grid point. 

### Large mosaics and parallelization

Very deep IRAC observations are made by thousands of frames, and result in a computationally expensive run of PRFMAP. Moreover, the size of `FILE_PRFS` might be so big that Python would not read it.  Parameters `RA_LIM` and `DEC_LIM` can be used to create several (Samller) grids to run in parallel. Another possibility is to run the script `break_list.py`, which will fragment a large `FILE_PRFS` into smaller files:
```bash
$ python src/break_list.py -c example.par -b 3
```
In this example, the original `FILE_PRFS` indicated in the configuration file will be divided in there (shorter) files, easier to handle possibly in parallel. 

Both Task 2 and 3 can be executed in multi-thread mode with the option `-p`. To comply with the structure of the computer cluster *Candide*, the parallelization is very simple: the list of grid points is divided among the threads and each one (for Task 2) creates a temporary file to stor the results. After using `break_list.py`, Task 3 can also be parallelized in the following way (Torque example):
```
#!/bin/bash
#PBS -l nodes=1:ppn=1
#PBS -t 0-2

python src/prfmap.py stack -c example.par  FILE_PRFS example_data/prfout_test/prfmap_models_ch1.txt_sub${PBS_ARRAYID}.txt
```

## Test run

```
$ python src/prfmap.py grid -c example.par 
$ python src/prfmap.py models -c example.par 
$ python src/prfmap.py stack -c example.par 
```

Results should be compared to the files included in `example_data/comparison_output/`

## Other utility scripts

To change the resolution of the PRF models generated by PRFMAP, e.g. rescale the FITS file to a 0.6 arcsec/pixel grid:
```
$ python src/resample_prf.py -c example.par -r 0.6 [-v -d -w]
$ python src/resample_prf.py --config=example.par --resample=0.6 [--verbose --debug --overwrite]
```
This takes *all* the FITS file from $PATH_OUTPUT/PRFstack/ and save the resampled PRFs into $PATH_OUTPUT/PRFstack_06/ (in case the new pixel scale is 0.6"/pxl). If for example --rescale=0.15 the new directory will be `PRFstack_015`. A given PRF is not rescaled if the corresponding file already exists in the target directory, unless option -w or --overwrite is activated.
