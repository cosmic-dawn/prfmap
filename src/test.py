import sys,os,getopt
import numpy as np

#################################
### GET OPTIONS from COMMAND LINE
action = sys.argv[1]
print(action)
options, args=getopt.getopt(sys.argv[2:],"hc:",["help","config="])
for opt, arg in options:
    if opt in ('-c','--config'): 
        paramfile = arg
    if opt in ('-h','--help'):
        print("""
    Help message TBD
               """)


##################
### PARAMETERS ###

# Read parameters from a config file (ASCII, see example.par)
# These are the parameter names should be included in that file:
keywords = ('PATH_MOSAIC','PATH_PRFMOD','PATH_OUTPUT','FILE_MOSAIC','FILE_PRFMOD','FRAMELIST','PRF_RAD','GRID_SPACE','PRF_SAMP')
opt = {}
with open(paramfile) as f:
    for l in f:
        if len(l)<=1 or l[0]=="#": 
            continue
        elif l.split()[0] in keywords:
            par = l.split()[0]
            val = l.split()[1] 
            if par in opt.keys(): sys.exit("ERROR: keword defined more than once in param file {}".format(paramfile))
            opt[par] = val

#sanity check and format conversion
for par in keywords:
    if par not in opt.keys(): sys.exit("ERROR: missing parameter {} in the config file {}".format(par,paramfile))
    if par in ('PRF_RAD','GRID_SPACE','PRF_SAMP'): opt[par] = int(opt[par])

print(opt)
