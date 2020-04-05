import sys,os,getopt
import subprocess
from scipy.ndimage import zoom
from astropy.io import fits
from read_par import read_par

if __name__ == '__main__':

    #################################
    ### GET OPTIONS from COMMAND LINE
    verbose = False #default value
    debug = False #default value
    prll = False #default value
    overwrite = False  #default value
    options, args=getopt.getopt(sys.argv[1:],"hvdpwc:r:",["help","verbose","debug","parallel","overwrite","config=","resample="])
    for opt, arg in options:
        if opt in ('-r','--resample'): pxl  = float(arg)  #the final image grid in arcsec/pixel units
        if opt in ('-c','--config'):  paramfile = arg
        if opt in ('-v','--verbose'): verbose = True
        if opt in ('-d','--debug'): debug = True
        if opt in ('-p','--parallel'): print('Multi-thread not avilable (yet)')
        if opt in ('-w','--overwrite'): overwrite = True
        if opt in ('-h','--help'):
            print("""
        Usage:
              $ python resample_psf.py -c configfile.par -r 0.6 [-v -d -p -w]
              $ python resample_psf.py --config configfile.par --resample=0.6 [--verbose --debug --parallel -overwrite]
              
              Rescale all the PRF models stored in the directory indicated in the config file ($PATH_OUTPUT/PRFstack/)
              to the arcsec/pixel value set by the option -r or --resample. The config file must have the PRFMAP v2 format.
              The output PRFs are FITS files stored in a new directory called e.g. PRFstack_06/, with the suffix depeneding
              on the rescaling option (in this case 0.6"/pxl). The parent directory is $PATH_OTUPUT as indicated in the
              PRFMAP config file. 
              
        Options: 
              -c | --config : specify the confi file (PRFMAPv2 format)
              -r | --resample : specify the grid scale of the output (arcsec/pixel units)
              -v | --verbose : print more std output
              -d | --debug : perform additional sanity checks [TBD]
              -p | --parallel : multi-thread [TBD]
              -w | --overwrite : write the resampled FITS file even if it is already present in the target directory.
              -h | --help : print this help page.
                   """)
            sys.exit()

    opt = read_par(paramfile)
    
    pxl0 = 1.22/opt['PRF_SAMP']  #1.2" is the native pixel scale in IRAC detectors
    factor = pxl0/pxl  #zoom factor
    suff = str(pxl).replace('.','')
   
    
    
    dir_in = opt['PATH_OUTPUT']+'PRFstack/'
    dir_out = opt['PATH_OUTPUT']+'PRFstack_{}/'.format(suff)
    if verbose: print("results in directory",dir_out)
    subprocess.run(["mkdir","-p",dir_out])
    
    a = subprocess.run(["ls", dir_in],stdout=subprocess.PIPE)
    l = a.stdout.decode("utf-8")  # ls output in a single string
    l = l.split("\n")  #create the list of files
    if l[-1]=='': l = l[:-1]  #split may create an empty item if the original string ends with "\n"
    if verbose: print("Resample {} PSFs".format(len(l)))
    #ensure output has odd number of pxl
    prf0 = fits.getdata(dir_in+l[0])  #assuming all PRFs have same size
    side_in = prf0.shape[0]  #assuming the PRF cutout is a square (NAXIS1==NAXIS2)
    side_out = round(side_in*factor)
    if side_out%2==0: 
        pad = round(1/factor)//2   
        if verbose: print('Pad =', pad)
    else:
        pad = 0
    x0 = pad; x1 = side_in-pad
    y0 = x0; y1 = x1 #assuming the PRF cutout is a square (NAXIS1==NAXIS2)

    for fits_in in l:
        if os.path.isfile(dir_out+fits_in) and not overwrite:
             if verbose: print(dir_out+fits_in,' already exists')
             continue
        prf_in,hdr = fits.getdata(dir_in+fits_in,header=True)
        prf_out = zoom(prf_in[x0:x1,y0:y1],factor,mode='nearest')
        if verbose: print('PRF model rescaled from {}x{} to {}x{} pxl'.format(prf_in.shape[0],prf_in.shape[1],prf_out.shape[0],prf_out.shape[1]))
        prf_out /= sum(prf_out.flat)  #normalize
        hdr['SAMP_ORI'] = opt['PRF_SAMP']
        hdr['SAMP_NEW'] = opt['PRF_SAMP']*factor
        hdu_new = fits.PrimaryHDU(prf_out,hdr)
        #hdu_new.writeto(dir_out+fits_in.replace('.fits',suff+'.fits'))
        hdu_new.writeto(dir_out+fits_in,overwrite=overwrite)
        
