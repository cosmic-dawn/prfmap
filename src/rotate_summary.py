import sys,os
import numpy as np
from astropy.io import ascii,fits
from astropy import table 
import utils as utl
import make_grid

### set the grid points
for f,fname in enumerate(frame_list):
    print("--- PROCESSING FRAME {} ---".format(f+1))
    #extract just the name of the frma, not the full path
    i0 = fname[::-1].find('/')-1
    nam = fname[i0:]
    # find which grid points are within this frame
    hdu = fits.open(fname)
    frame_hdr = hdu[0].header
    hdu.close()
    type = frame_hdr['BITPIX']
    edges_xy = np.array([ (1,1), (1,frame_hdr['NAXIS1']), (frame_hdr['NAXIS2'],1), (frame_hdr['NAXIS2'],frame_hdr['NAXIS1'])])
    edges_sky = utl.xy_to_sky(frame_hdr,x=edges_xy[:,0],y=edges_xy[:,1]) 
    gp_in = np.where( (points['RA']>edges_sky[0].min()) & (points['RA']<edges_sky[0].max()) & (points['Dec']>edges_sky[1].min()) & (points['Dec']<edges_sky[1].max()) )[0]
    points_frm = points['RA','Dec'][gp_in]
    #and convert them to pixel coord in the frame ref system
    x,y = utl.sky_to_xy(frame_hdr,ra=points_frm['RA'],dec=points_frm['Dec'],start=1)
    points_frm['X'] = x    
    points_frm['Y'] = y    
    points_frm['ID'] = [int(i) for i in points['ID'][gp_in]]  #dirty trick to make integer type
    gp_in2 = np.where( (x>0.) & (y>0.) & (x<frame_hdr['NAXIS1']) & (y<frame_hdr['NAXIS2']) )  #this is because RA,Dec approx takes also points outside the image
    points_frm[gp_in2].write('{}_GRID.dat'.format(nam[:nam.find('_bcd.fits')]),format='ascii.commented_header',formats={'ID':'%8g','RA':'%12.6f','Dec':'%12.6f','X':'%12.3f','Y':'%12.3f'})


