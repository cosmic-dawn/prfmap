import numpy as np
from astropy.io import ascii,fits

def read_fits(filename,hdu=0):
    """extract a table from a FITS file"""
    hdul = fits.open(filename)
    dat = hdul[hdu].data
    hdul.close()
    return dat

def read_fits_head(filename,hdu=0):
    """extract the header from a FITS file"""
    hdul = fits.open(filename)
    hdr = hdul[hdu].header
    hdul.close()
    return hdr

def xy_to_sky(img_hdr,x,y,start=1):
    """convert a set of points from pxl coordinates to RA,Dec 
       using a FITS header to extract WCS info."""
    from astropy.wcs import WCS
    wcs = WCS(header=img_hdr)
    return wcs.all_pix2world(x,y,start)

def sky_to_xy(img_hdr,ra,dec,start=1):
    """convert a set of points from RA,Dec to image coordinates 
       using a FITS header to extract WCS info."""
    from astropy.wcs import WCS
    wcs = WCS(header=img_hdr)
    return wcs.all_world2pix(ra,dec,start)


