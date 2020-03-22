# Script to fast rotate images
# USAGE
#
# python rotate.py INPUTFILE
#
# where INPUTFILE is file name of file containing:
#
# img_in_1   img_out_1   pa_1
# img_in_2   img_out_2   pa_2
# img_in_3   img_out_3   pa_3
#
# Jan 21, 2016 by AF (anfaisst@gmail.com)
#
# MODIFICATION HISTORY
# Aug 17, 2016 by AF: changed dtype=('S1000','S1000','f6') to dtype=('S1000','S1000','f')
#
######################

import os,sys,string
import subprocess
import numpy as np
from pyraf import iraf
#from iraf import images,imgeom,stsdas

# which file
file_name = sys.argv[1]
txt = np.genfromtxt(file_name,dtype=('U1000','U1000','f'))

for ii in range(0,txt.size):

    # talk
    if (ii % 10) == 0:
        prec = round((ii*1.)/(txt.size*1.)*100.,2)
        print("{:5.2f}".format(prec))
        
    img_in = txt[ii][0]
    img_out = txt[ii][1]
    pa = txt[ii][2]
    #dirty trick: copy the file in the same partition
    subprocess.run(['cp',img_in,'tmp.fits'])
    iraf.imlintran('tmp.fits', 'tmpout.fits', 
          xmag=1, ymag=1,
          xin="INDEF",yin="INDEF",
          xout="INDEF",yout="INDEF",
          interp="drizzle",
          xrot=pa, yrot=pa, verbose=0)
    subprocess.run(['cp','tmpout.fits',img_out])
    subprocess.run(['rm','tmp.fits','tmpout.fits'])

