

def read_par(paramfile,list_out=False):

    # These are the parameter names should be included in that file:
    keywords = ('PATH_PRFMOD','PATH_OUTPUT','FILE_MOSAIC','FILE_PRFMOD','FILE_FRAMELIST','FILE_GRID','FILE_PRFS','PRF_RAD','GRID_SPACE','PRF_SAMP','RA_LIM','DEC_LIM')
    if list_out:
        return keywords
    optpar = 2 #number of optinal parameters (to be added at the end of tuple `keywords`)
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
    #adjust RA_LIM and DEC_LIM
    if 'RA_LIM' in opt.keys():  opt['RA_LIM'] = [float(i) for i in opt['RA_LIM'].split(',')]
    else:  opt['RA_LIM'] = []
    if 'DEC_LIM' in opt.keys():  opt['DEC_LIM'] = [float(i) for i in opt['DEC_LIM'].split(',')]
    else:  opt['DEC_LIM'] = []
    #sanity check and format conversion
    for par in keywords[:-optpar]:  
        if par not in opt.keys(): sys.exit("ERROR: missing parameter {} in the config file {}".format(par,paramfile))
        if par in ('PRF_RAD','GRID_SPACE','PRF_SAMP'): opt[par] = int(opt[par])
        if 'PATH_' in par and opt[par][-1]!='/' : opt[par]+='/'  #add slash at the end of a directory path
    dumm = opt['FILE_MOSAIC'].strip('.fits')
    i_dumm = dumm[::-1].index('/')
    opt['NAME_MOSAIC'] = dumm[-i_dumm:]

    return opt
