import numpy as np
from astropy import table
import utils as utl

def make_grid(filename,step=8,ra_lim=[],dec_lim=[],hdu=0,write=False):
    """Given a FITS image, create a grid spanning the entire area
    with a given `step` in pixels"""
    hdr = utl.read_fits_head(filename,hdu=hdu)
    xmax = hdr['NAXIS1']
    ymax = hdr['NAXIS2']
    box_pxl = [(1,1), (1,xmax), (xmax,ymax), (1,ymax)]
    #grid in pixel, over the whole image
    x_gr = []; y_gr = [] 
    buff = 24  #put a buffer on the borders
    for i in range(1+buff,xmax-buff,step):
        for j in range(1+buff,ymax-buff,step):
            x_gr.append(i)
            y_gr.append(j)
    x_gr = np.array(x_gr)
    y_gr = np.array(y_gr)
    #convert to WCS
    ra_gr,dec_gr = utl.xy_to_sky(hdr,x_gr,y_gr)
    #keep grid points only inside the limits (if they are given)
    if len(ra_lim)==2: 
        in_ra = np.where( (ra_gr>ra_lim[0])&(ra_gr<ra_lim[1]) )[0]
        x_gr = x_gr[in_ra]; y_gr = y_gr[in_ra]
        ra_gr = ra_gr[in_ra]; dec_gr = dec_gr[in_ra]
    if len(dec_lim)==2: 
        in_dec = np.where( (dec_gr>dec_lim[0])&(dec_gr<dec_lim[1]) )[0]
        x_gr = x_gr[in_dec]; y_gr = y_gr[in_dec]
        ra_gr = ra_gr[in_dec]; dec_gr = dec_gr[in_dec]
    xy_grid = np.array([x_gr,y_gr])
    radec_grid = np.array([ra_gr,dec_gr])
    points = table.Table()
    points['RA'] = radec_grid[0]
    points['Dec'] = radec_grid[1]
    points['X'] = xy_grid[0]
    points['Y'] = xy_grid[1]
    points['ID_GRIDPT'] = np.arange(1,len(xy_grid[0])+1,dtype='int32')
    if write:
        points.write(write,format='ascii.commented_header')

    return points


def grid_in_frame(points,fname):
    """take the list of all the grid points and select those inside the given frame"""
    # find which grid points are within this frame
    frame_hdr = utl.read_fits_head(fname)
    type = frame_hdr['BITPIX']
    edges_xy = np.array([ (1,1), (1,frame_hdr['NAXIS1']), (frame_hdr['NAXIS2'],1), (frame_hdr['NAXIS2'],frame_hdr['NAXIS1'])])
    edges_sky = utl.xy_to_sky(frame_hdr,x=edges_xy[:,0],y=edges_xy[:,1]) 
    gp_in = np.where( (points['RA']>edges_sky[0].min()) & (points['RA']<edges_sky[0].max()) & (points['Dec']>edges_sky[1].min()) & (points['Dec']<edges_sky[1].max()) )[0]
    points_frm = points['RA','Dec'][gp_in]
    #and convert them to pixel coord in the frame ref system
    x,y = utl.sky_to_xy(frame_hdr,ra=points_frm['RA'],dec=points_frm['Dec'],start=1)
    points_frm['X'] = x    
    points_frm['Y'] = y    
    points_frm['ID_GRIDPT'] = [int(i) for i in points['ID_GRIDPT'][gp_in]]  #dirty trick to make integer type
    gp_in2 = np.where( (x>0.) & (y>0.) & (x<frame_hdr['NAXIS1']) & (y<frame_hdr['NAXIS2']) )  #this is because RA,Dec approx takes also points outside the image
    return points_frm[gp_in2]

    
