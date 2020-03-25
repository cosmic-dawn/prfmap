import sys,os,getopt
import numpy as np
import subprocess
from astropy.io import ascii
import utils as utl
from read_par import read_par
from draw_grid import draw_grid
from find_models import find_models
from manip_prf import rotate_and_stack


#############################################


if __name__ == '__main__':

    #################################
    ### GET OPTIONS from COMMAND LINE

    verbose = False #default value
    debug = False #default value
    prll = False #default value
    task = sys.argv[1]
    if task!='-h' and task!='--help' and task[0] == '-': sys.exit("ERROR: it seems you forgot to define the task to perform")
    options, args=getopt.getopt(sys.argv[2:],"hvdpc:",["help","verbose","debug","parallel","config="])
    for opt, arg in options:
        if opt in ('-c','--config'):  paramfile = arg
        if opt in ('-v','--verbose'): verbose = True
        if opt in ('-d','--debug'): debug = True
        if opt in ('-p','--parallel'): prll = True
        if opt in ('-h','--help'):
            print("""
        Help message TBD
                   """)
    if verbose and prll: print('--- Multi-thread ON')

    ##################
    ### PARAMETERS ###

    opt = read_par(paramfile)  #get parameters from the config file
    #modify options from command line
    for a,arg in enumerate(args):  
        if arg in read_par(paramfile,list_out=True):
            opt[arg] = args[a+1]
            if verbose: print("--- Option {} set to {} from command line".format(arg,args[a+1]))
    # create the output dir
    subprocess.run(['mkdir','-p',opt['PATH_OUTPUT']])

    #############################################
    ### GATHER INFO ON PRF MODELS and FRAMES  ###  

    modelfile = opt['FILE_PRFMOD']
    prfmod = ascii.read(modelfile,format='ipac') #(PRFNum NAXIS1 NAXIS2 PRFPos1 PRFPos2)
    # file names are in the header but for some reason astropy doesnt read the meta values as it should
    # thus, a dirty trick is used
    # \char PRF_Filename_1 =  apex_sh_IRAC1_col025_row025_x100.fits
    fin = open(modelfile,'r')
    fin.readline()  #first line is not used
    n_mod = fin.readline().split()[-1]
    n_mod = int(n_mod)
    xmax_mod = fin.readline().split()[-1]
    ymax_mod = fin.readline().split()[-1]
    if debug: print('----- The basic PRF models are:')
    f_mod = []
    for i in range(n_mod): 
        f_mod.append(fin.readline().split()[-1])
        if debug: print(f_mod[i])
    if debug: print('----- ')
    # list of frames to analyse
    frame_list = np.loadtxt(opt['FILE_FRAMELIST'],comments="#",dtype='str')
    nam = []  #only the file names
    for inm in frame_list:
        r = inm[::-1]
        r = r[:r.find('/')]
        nam.append(r[::-1])
    opt['NAME_FRAME'] = [f[:f.find('_bcd.fits')] for f in nam]
    
    
    ###############
    ###  TASKS  ###

    #Step 1: MAKE THE GRID OVER THE ENTIRE MOSAIC 
    # (or a sub-region, if RA_LIM and DEC_LIM are set in the config file)
    if task=='grid':  
        draw_grid(frame_list,opt=opt,verbose=verbose,debug=debug)
    #Step 2:  CREATE A LIST WITH INDIVIDUAL PRFs IN EACH GRID POINT
    # for every frame overlapping on any grid point
    elif task=='models':  
        find_models(frame_list,prfmod,opt=opt,verbose=verbose,debug=debug,parallel=prll)
    #Step 3:  STACK THE INDIVIDUAL PRFs
    # (use `id_list` to specify a sub-sample of grid points where to stack)
    elif task=='stack': 
        rotate_and_stack(f_mod,opt=opt,id_list=[],parallel=prll,verbose=verbose)
    #Wrong task in input
    else:
        sys.exit("ERROR: task '{}' does not exist".format(task))

