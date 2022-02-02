import sys,os,getopt
from astropy.io import fits,ascii
from read_par import read_par
import numpy as np

if __name__ == '__main__':

    #################################
    ### GET OPTIONS from COMMAND LINE
    verbose = False #default value
    debug = False #default value
    prll = False #default value
    options, args=getopt.getopt(sys.argv[1:],"hvdpc:b:",["help","verbose","debug","parallel","config=","break="])
    for opt, arg in options:
        if opt in ('-b','--break'): pcs  = int(arg)  #number of pieces (ie, sub-lists) to divide the original prf_models list
        elif opt in ('-c','--config'):  
            paramfile = arg
            fopt = read_par(paramfile)
        elif opt in ('-v','--verbose'): verbose = True
        elif opt in ('-d','--debug'): debug = True
        elif opt in ('-p','--parallel'): print('Multi-thread not avilable (yet)')
        elif opt in ('-h','--help'):
            print("""
        Help message TBD
                   """)
            sys.exit()
        else:
            sys.exit("Incorrect syntax. Use -h to print list of options.")
    for a,arg in enumerate(args):  
        if arg in read_par(paramfile,list_out=True):
            fopt[arg] = args[a+1]
            print("Option {} manually set to {}".format(arg,args[a+1]))
                   

    
    # original list
    
    lgp = ascii.read(fopt['FILE_GRID'])
    # create the new sub-lists
    lof = [] #list of output files (ie, the sub-lists)
    for i in range(pcs):
        lof.append(open(fopt['FILE_PRFS']+'_sub{}.txt'.format(i),'w')) 
    bpt = len(lgp)//pcs  #number of grid pt per sub-list
    break_id = [] #list of grid pt IDs where to cut the original list
    for i,idgp in enumerate(lgp['ID_GRIDPT']):
        if (i+1)%bpt==0: break_id.append(idgp)
    break_id[-1] = max(lgp['ID_GRIDPT'])+1
    if verbose:
        print('ID numbers where to divide the original list:\n',break_id)
    break_id = np.array(break_id)
    with open(fopt['FILE_PRFS'],'r') as filein:
        for l in filein:
            if l[0]=="#":
                for i in range(pcs): lof[i].write(l) #write header
            else:
                idgp = int(l.split()[0])
                pc = np.where(idgp//break_id==0)[0][0]
                lof[pc].write(l)
    for i in range(pcs): lof[i].close() #write header
    
       
