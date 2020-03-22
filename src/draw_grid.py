import numpy as np
import subprocess
import make_grids


def draw_grid(frame_list,opt={},verbose=False,debug=False):
    """ draw_grid(frame_list,opt={},verbose=False,debug=False)
        
        Read the mosaic properties from its FITS file and define a grid of points where the PRF will be estimated.
        Grid coordinates (and ID of the nodes) are saved into a *_GRID.dat file.

        frame_list: str 
            ASCII file with list of frames (*_bcd.fits files) resulting in the final image mosaic 
            (same file is indicated as FILE_FRAMELIST in PRFMap config file)
        opt: dict
            all the other parameters of PRFMap config file (FILE_MOSAIC, PRF_RAD, etc.)
        verbose: bool
            print on screen additional information
        debug: bool
            if True, a folder ./frame_grids/ is created and individual grid for each frame 
            are saved in *_GRID.dat ASCII files

    """

    if verbose: print('--- MAKE THE GRID OVER THE ENTIRE MOSAIC ---\n--- located in {} '.format(opt['FILE_MOSAIC']))

    points = make_grids.make_grid(opt['FILE_MOSAIC'],step=opt['PRF_RAD']*opt['GRID_SPACE'],ra_lim=opt['RA_LIM'],dec_lim=opt['DEC_LIM'],write='{}/{}_GRID.dat'.format(opt['PATH_OUTPUT'],opt['NAME_MOSAIC']))
    ### select the grid points within each frame
    if debug:
        for f,fname in enumerate(frame_list):
            if verbose: print('------- Processing frame #{}'.format(f+1))
            #extract just the name of the frame, not the full path
            points1 = make_grids.grid_in_frame(points,fname)
            subprocess.run(['mkdir','-p','{}/frame_grids/'.format(opt['PATH_OUTPUT'])])
            points1.write('{}/{}_GRID.dat'.format(opt['PATH_OUTPUT']+'/frame_grids/',opt['NAME_FRAME'][f]),format='ascii.commented_header',formats={'ID_GRIDPT':'%8g','RA':'%12.6f','Dec':'%12.6f','X':'%12.3f','Y':'%12.3f'},overwrite=False)  
        
    if verbose: print('--- OUPUT FILE WITH LIST OF GRID POINTS ---\n--- located in {} '.format('{}/{}_GRID.dat'.format(opt['PATH_OUTPUT'],opt['NAME_MOSAIC'])))

