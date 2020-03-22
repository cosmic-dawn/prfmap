import os,sys,string
import subprocess
import numpy as np
from astropy.io import fits,ascii
from scipy import ndimage
import multiprocessing as mp
import utils as utl


def rotate(fits_in,fits_out,angle):
    """To ratate a PRF model by a PA angle. This replaces pyraf/IRAF imlintran"""
    iin = fits.getdata(fits_in)
    return ndimage.interpolation.rotate(iin,-angle,reshape=False,axes=(1,0))


def stack_at_gp(igp,dat,paths):
    """To stack all PRFs at a given grid point. 
       This is an individual function to allow parallelization."""
    sel_frames = np.where(dat['ID_GRIDPT']==igp)
    if len(sel_frames[0])==0: return
    #avoid overwriting
    if os.path.isfile('{}/mosaic_gp{:05d}.fits'.format(paths[1],igp)): return
    i0 = sel_frames[0][0]
    #copy header from the first PRF
    stack_hdr = utl.read_fits_head(paths[0]+dat['FILENAME'][i0])
    stack_img = np.zeros([stack_hdr['NAXIS1'],stack_hdr['NAXIS2']])
    for i in sel_frames[0]:
        i_frm = dat['FRAME'][i][:-9]
        img_in = paths[0]+dat['FILENAME'][i]
        # rotation and stacking
        stack_img += rotate(img_in,'N/A',dat['PA'][i])
    # save the stacking into a new fits file
    new_hdu = fits.PrimaryHDU(stack_img,stack_hdr)
    #add new info in the header    
    new_hdu.header['MOSAIC'] = 'N/A'
    new_hdu.header['GRID_PT'] = igp
    new_hdu.header['RA_PT'] = dat['RA_CEN'][i0]
    new_hdu.header['DEC_PT'] = dat['DEC_CEN'][i0]
    new_hdu.header['NFRAMES'] = len(sel_frames[0])
    new_hdu.writeto('{}/mosaic_gp{:05d}.fits'.format(paths[1],igp))
    return

def worker(ids,dat,paths):
    for i in ids:
        stack_at_gp(i,dat,paths) 

def rotate_and_stack(models,opt={},id_list=[],parallel=False,verbose=False):
    """ rotate_and_stack(filein,paths=['./','./'],id_list=[],parallel=False,verbose=False)

        From the info collected in previous steps of PRFMap, individual PRFs are stacked
        according to 

         
        paths : list

    """
    #Two paths are needed. The first is the location of the input PRF models (PATH_PRFMOD)
    #while the second is the output directory (PATH_OUTPUT or any other place where results
    #can be saved).
    filein = opt['FILE_PRFS']
    paths=[opt['PATH_PRFMOD'],opt['PATH_OUTPUT']]
    #dat = utl.read_fits(filein,hdu=1)
    dat = ascii.read(filein)
    dat['FILENAME'] = [models[i-1] for i in dat['PRF_NUMBER']]
    ids = dat['ID_GRIDPT'] # all grid points with repetitions (x N_frames)
    uniq_id = set(ids)
    if len(id_list)==0: 
        id_list = list(set(uniq_id))
    nid = len(id_list)
    paths[1] += 'PRFstack/'  
    subprocess.run(['mkdir','-p',paths[1]])  #subdirectory for the stacking result
    if parallel:
        n_avail =  mp.cpu_count() - 1  #keep a core free, just in case
        chunk = nid//n_avail
        if verbose: print(n_avail,' cores parallel run')
        #loop over grid_points
        pool = mp.Pool(processes=n_avail-1)  #no real reason to keep one core free
        pool.starmap(worker,[(id_list[i:i+chunk],dat,paths) for i in range(0,nid,chunk)])
        pool.close() 
    else:
        if verbose: print('Single thread (parallel=False)')
        #TBRemoved:
        for igp in id_list[::-1]:
            stack_at_gp(igp,dat,paths)
    if verbose: print('results are stored in ',paths[1])


