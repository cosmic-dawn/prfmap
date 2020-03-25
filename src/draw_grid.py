import numpy as np
import subprocess
import utils as utl


def draw_grid(frame_list,opt={},verbose=False,debug=False):
    """ draw_grid(frame_list,opt={},verbose=False,debug=False)
        
        Read the mosaic properties from its FITS file and define a grid of points where the PRF will be estimated.
        Grid coordinates (and ID of the nodes) are saved into an ASCII file (FILE_GRID).

        frame_list: str 
            ASCII file with list of frames (*_bcd.fits files) resulting in the final image mosaic 
            (same file is indicated as FILE_FRAMELIST in PRFMap config file)
        opt: dict
            all the other parameters of PRFMap config file (FILE_MOSAIC, PRF_RAD, etc.)
        verbose: bool
            print on screen additional information
        debug: bool
            if True, a sub-folder $PATH_OUTPUT/frame_grids/ is created and the individual grid for each frame 
            is saved in *_GRID.dat ASCII files

    """

    if verbose: print('--- Make the grid over the entire mosaic    \n--- which is {} ---'.format(opt['FILE_MOSAIC']))

    points = utl.make_grid(opt['FILE_MOSAIC'],step=opt['PRF_RAD']*opt['GRID_SPACE'],ra_lim=opt['RA_LIM'],dec_lim=opt['DEC_LIM'],write=opt['FILE_GRID'])
    if verbose: print('--- Ouput file with list of grid points    \n--- is located in {} ---'.format(opt['FILE_GRID']))

    ### select the grid points within each frame
    if debug:
        print("------ Print a DS9 .reg file in the same directory ------")
        gr = np.loadtxt(opt['FILE_GRID'])
        fds9 = open(opt['FILE_GRID']+'.reg','w')
        fds9.write('# Region file format \nfk5\n')
        for i in gr:  
            fds9.write("circle({:.6f},{:.6f}, 1.0\") # text = {{ {:g} }}\n".format(i[0],i[1],i[4]))
        fds9.close()
        for f,fname in enumerate(frame_list):
            if verbose: print('------ Processing frame #{}'.format(f+1))
            #extract just the name of the frame, not the full path
            points1 = utl.grid_in_frame(points,fname)
            subprocess.run(['mkdir','-p','{}/frame_grids/'.format(opt['PATH_OUTPUT'])])
            points1.write('{}/{}_GRID.dat'.format(opt['PATH_OUTPUT']+'/frame_grids/',opt['NAME_FRAME'][f]),format='ascii.commented_header',formats={'ID_GRIDPT':'%8g','RA':'%12.6f','Dec':'%12.6f','X':'%12.3f','Y':'%12.3f'},overwrite=False)  

               
