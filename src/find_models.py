import sys,os
import subprocess
import numpy as np
from astropy import table 
from astropy.io import ascii
import utils as utl
import multiprocessing as mp
from pathlib import Path

#global 
# this are the column names of FILE_PRFS
colnames = ['ID_GRIDPT','PRF_NUMBER','RA_CEN','DEC_CEN','PA','FRAME']

# need this because np.argmin breaks in multiprocessing (why?)
def argmin(a):
    return min(range(len(a)), key=lambda x: a[x])

#select models for single frame
def single_frame(fname,points,coord,verbose):
    points1 = utl.grid_in_frame(points,fname)
    #extract just the name of the frame, not the full path
    rows = []
    for i in range(len(points1)):
        x0 = points1['X'][i]; y0 = points1['Y'][i]
        x = coord[0]; y = coord[1]
        # simple Euclidean distance; k-tree should be faster for findinf the nearest neighbor model
        dist = (x-x0)**2 + (y-y0)**2  #this is the squared distance
        i0 = argmin(dist.data)   # nearest model to grid point i (np.argmin doesnt work in parallel!)
        if fname[-5:]=='.fits':
            pa = utl.read_fits_head(fname)['PA']  #rotation
        else:
            pa = utl.read_ascii_head(fname)['PA']
        rows.append( [points1['ID_GRIDPT'][i],i0+1,points1['RA'][i],points1['Dec'][i],pa,fname[fname.rfind('/')+1:]] )
    if verbose: print('--- Inspected frame {} ---'.format(fname))
    return rows  

#select models for a list of frames
def multi_frame(fnames,points,coord,verbose,queue):
    out_tmp = open(queue,'w')
    for fname in fnames:
        points1 = utl.grid_in_frame(points,fname)
        #extract just the name of the frame, not the full path
        for i in range(len(points1)):
            x0 = points1['X'][i]; y0 = points1['Y'][i]
            x = coord[0]; y = coord[1]
            # simple Euclidean distance; k-tree should be faster for findinf the nearest neighbor model
            dist = (x-x0)**2 + (y-y0)**2  #this is the squared distance
            i0 = argmin(dist.data)   # nearest model to grid point i (np.argmin doesnt work in parallel!)
            if fname[-5:]=='.fits':
                pa = utl.read_fits_head(fname)['PA']  #rotation
            else:
                pa = utl.read_ascii_head(fname)['PA']
            out_tmp.write('{:9d} {:6d} {:11.6f} {:11.6f} {:9.4f}  {}\n'.format( points1['ID_GRIDPT'][i],i0+1,points1['RA'][i],points1['Dec'][i],pa,fname[fname.rfind('/')+1:] ))
        #if verbose: print('--- Inspected frame {} ---'.format(fname))
    out_tmp.close()



#body of the program to associate PRF models to grid points 
def find_models(frame_list,prfmap,opt={},debug=False,verbose=False,parallel=False):
    """ 
     To associate PRF models to each grid point, with PA accoring to frames;
     the summary file resulting from this is a new table (named as the FILE_PRFS variable),
     with columns:
     ##REDO###
     grid-point_ID |total_prfs|prf_model_id|frame_name|rotation_angle

     total_prf = the number of prfs in that position (depends on the number of overlapping frames)
     prf_model_id = range of models from 1 to 25
     frame_name = filename of each frame that will be stacked at this grid point
     rotation angle = PRF orientation as the PA of the given frame  
    """
    if verbose: 
        modelfile = opt['FILE_PRFMOD']
        print('--- Select PRF models  \n--- originary in {} \n--- and now re-arranged in {} ---'.format(modelfile,opt['FILE_GRID']))
    points = ascii.read(opt['FILE_GRID'])
    filename = '{}'.format(opt['FILE_PRFS'])
    if Path(filename).is_file(): sys.exit('--- ERROR: file exists ({}) '.format(filename))
    fout = open(filename,'w')
    fout.write('# {} {} {} {} {} {}\n'.format(colnames[0],colnames[1],colnames[2],colnames[3],colnames[4],colnames[5]))
    fout.close
    if parallel:
        nproc = mp.cpu_count()-1 #no real reason to keep one CPU free
        nfram = len(frame_list)
        nchunk = nfram//nproc
        nproc = 0
        proc = []
        output0 = '{}/fm_tmp_{}.txt'
        df = nchunk
        for b in range(0,nfram,df):
            if b+nchunk>=nfram: df = nfram-b
            if verbose: print('frames from {} to {}'.format(b+1,b+df+1))
            fnames = frame_list[b:b+df]
            output = output0.format(opt['PATH_OUTPUT'],nproc)
            proc.append( mp.Process(target=multi_frame,args=(fnames,points,(prfmap['PRFPos1'],prfmap['PRFPos2']),verbose,output)) )
            nproc += 1
        if verbose: print('--- There are {} frames split into {} cores for parallel run'.format(nfram,nproc))
 
        for p in proc:  p.start()
        for p in proc:  p.join()
        if verbose: print('--- Writing output now for the {} processes'.format(nproc))
        for p in range(nproc):
            fin = open(output0.format(opt['PATH_OUTPUT'],p),'r')
            #d = ascii.read(output0.format(opt['PATH_OUTPUT'],p),guess=False,delimiter=' ',data_start=0,names=colnames)    
            lines = fin.readlines()
            fin.close()
            fout = open(filename,'a')
            for l in lines: fout.write(l)
            fout.close()
            subprocess.run(['rm',output0.format(opt['PATH_OUTPUT'],p)])
    else:
        for fname in frame_list:
            rows = single_frame(fname,points,(prfmap['PRFPos1'],prfmap['PRFPos2']),verbose=verbose)
            for r in rows:
                fout.write('{:9d} {:6d} {:11.6f} {:11.6f} {:9.4f}  {}\n'.format(r[0],r[1],r[2],r[3],r[4],r[5]))
    if verbose: print('--- The PRF models correctly oriented  \n--- are described in {} ---'.format(filename))


