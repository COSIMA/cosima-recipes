#!/usr/bin/env python

# Centralised code to set model and experiment names.

# This is just an initial stab at it. More functionality is planned:
# https://github.com/OceansAus/ACCESS-OM2-1-025-010deg-report/issues/6

# load this with
#     import sys, os
#     sys.path.append(os.path.join(os.getcwd(), '..'))  # so we can import ../exptdata
#     import exptdata
# in figures/subdir/your_notebook.ipynb

from collections import OrderedDict
import os

import pandas as pd
import numpy as np
import xarray as xr



basedir = '/g/data3/hh5/tmp/cosima/'

# Model data sources. 
# More experiments (or variables each experiment) can be added here if needed.
# locals().update(exptdata.exptdict['1deg']) will define all variables for the '1deg' experiment (dangerous!).
# exptdir = exptdata.expdict[expkey]['exptdir'] etc is safer.
# desc is a short descriptor for use in figure titles.
# n_files is a negative number - designed to find data from just the last IAF cycle.
# Uses OrderedDict so that iteration on exptdict will be in this order.
# NB: offset changes effect of time_units: https://github.com/OceansAus/cosima-cookbook/issues/113
# Also MOM and CICE have different time_units: https://github.com/OceansAus/access-om2/issues/117#issuecomment-446465761
# so the time_units specified here may need to be overridden when dealing with CICE data - e.g. see ice_validation.ipynb
exptdict = OrderedDict([
    ('1deg',   {'model':'access-om2', 'expt':'1deg_jra55_iaf_omip2_cycle4',  
                'desc': 'ACCESS-OM2','n_files': None,
                'time_units': None,'offset': None}),
    ('025deg', {'model':'access-om2-025', 'expt':'025deg_jra55_iaf_omip2_cycle4',
                    'desc': 'ACCESS-OM2-025', 'n_files': None,
                    'time_units': None, 'offset': None}),
    ('01deg',  {'model':'access-om2-01',  'expt':'01deg_jra55v140_iaf_cycle4',
                'desc': 'ACCESS-OM2-01','n_files':None,
                    'time_units':None, 'offset': None})
])

# Now add expdirs programmatically where they don't already exist.
# This allows expdir to be overridden by specifying it above if needed.
for k in exptdict.keys():
    if not('exptdir' in exptdict[k]):
        exptdict[k]['exptdir'] = os.path.join(os.path.join(
            basedir, 
            exptdict[k]['model']),
            exptdict[k]['expt' ])


# Lists of models, experiments dirs and descriptors in consistent order

models    = [exptdict[k]['model']   for k in exptdict.keys()]

expts     = [exptdict[k]['expt']    for k in exptdict.keys()]

exptdirs  = [exptdict[k]['exptdir'] for k in exptdict.keys()]

descs     = [exptdict[k]['desc']    for k in exptdict.keys()]

def model_expt_exptdir_desc(keyname):
    """
    Return (model, expt, exptdir, desc) strings for keyname in exptdict.keys()
    
    Examples:
    
    (model, expt, exptdir, desc) = model_expt_exptdir_desc('1deg')
    
    for k in exptdict.keys():
        (model, expt, exptdir, desc) = model_expt_exptdir_desc(k)
    
    """
    return (exptdict[keyname]['model'],
            exptdict[keyname]['expt'],
            exptdict[keyname]['exptdir'],
            exptdict[keyname]['desc'])


# define common start and end dates for climatologies
clim_tstart = pd.to_datetime('1993', format='%Y')
clim_tend = clim_tstart + pd.DateOffset(years=25)


#################################################################################################
# functions to share across all notebooks

def joinseams(d, lon=False, tripole_flip=False):
    """
    Concat duplicated western edge data along eastern edge and flipped data along tripole seam 
    to avoid gaps in plots.
    Assumes the last dimension of d is x and second-last is y.
    
    d: xarray.DataArray or numpy.MaskedArray (or numpy.Array - UNTESTED!)
    
    lon: boolean indicating whether this is longitude data in degrees 
        (in which case 360 is added to duplicated eastern edge).
        Ignored if d is a DataArray.

    tripole_flip: boolean indicating whether to reverse duplicated data on tripole seam.
        You'd normally only do this with coord data.
        Ignored if d is a DataArray.
    
    Returned array shape has final 2 dimensions increased by 1.
    """
    if type(d) is xr.core.dataarray.DataArray:
        dims = d.dims
        out = xr.concat([d, d.isel({dims[-1]: 0})], dim=dims[-1])
        out = xr.concat([out, out.isel({dims[-2]: -1})], dim=dims[-2])
    elif type(d) is np.ma.core.MaskedArray:
        dims = range(len(d.shape))
        if lon:
            out = np.ma.concatenate([d, d[:,0,None]+360], axis=-1)
        else:
            out = np.ma.concatenate([d, d[:,0,None]], axis=-1)
        if tripole_flip:
            out = np.ma.concatenate([out, np.flip(out[None,-1,:], axis=-1)], axis=-2)
        else:
            out = np.ma.concatenate([out, out[None,-1,:]], axis=-2)
    else:  # NB: UNTESTED!!
        assert type(d) is np.ndarray
        dims = range(len(d.shape))
        if lon:
            out = np.concatenate([d, d[:,0,None]+360], axis=-1)
        else:
            out = np.concatenate([d, d[:,0,None]], axis=-1)
        if tripole_flip:
            out = np.concatenate([out, np.flip(out[None,-1,:], axis=-1)], axis=-2)
        else:
            out = np.concatenate([out, out[None,-1,:]], axis=-2)
    return out

#################################################################################################


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=
        'Centralised definition of model and experiment names.')
    parser.add_argument('-l', '--latex',
                        action='store_true', default=False,
                        help='Output data as latex table')
    if vars(parser.parse_args())['latex']:
        print(r'''
\begin{tabularx}{\linewidth}{lXp{0.4\linewidth}}
\hline
\textbf{Configuration} & \textbf{Experiment} & \textbf{Path to output data on NCI} \\
\hline
''')
        for k in exptdict.keys():
            e = exptdict[k]
            print(r'{} & {} & {}\\'.format(e['desc'].replace('°','$^\circ$'), e['expt'],  
                      r'\texttt{' + e['exptdir'].replace('/', '\\slash ') + r'}'))
        print(r'''
\hline
\hline
\end{tabularx}''')
    else:
        print(' '.join(e for e in exptdirs), end='')  # for use in get_namelists.sh
