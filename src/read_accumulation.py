#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 08:52:19 2023

@author: jason, contact: jeb at geus.dk

read and display Greenland annual accumulation reconstruction 1840 to 1999 after
    Box, J. E., Cressie, N., Bromwich, D. H., Jung, J.-H., van den Broeke, M., van Angelen, J. H., Forster, R. R., Miège, C., Mosley-Thompson, E., Vinther, B., and McConnell, J. R.: Greenland Ice Sheet Mass Balance Reconstruction. Part I: Net Snow Accumulation (1600–2009), J. Clim., 26, 3919–3934, https://doi.org/10.1175/JCLI-D-12-00373.1, 2013.

a triangular irregular network bias correction is described in
    Lewis, G., Osterberg, E., Hawley, R., Whitmore, B., Marshall, H. P., and Box, J.: Regional Greenland accumulation variability from Operation IceBridge airborne accumulation radar, The Cryosphere, 11, 773–788, https://doi.org/10.5194/tc-11-773-2017, 2017.

data has the following elements

['icemask', 'dem', 'acc'] acc is accumulation in mm w e per year

"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

os.chdir('/Users/jason/Dropbox/reconstructions_of_Greenland_T_and_Accumulation/')

# latitude longitude data are in this file
fn='/Users/jason/Dropbox/reconstructions_of_Greenland_T_and_Accumulation/ancil/5km_DEM_w_lat_lon.nc'
ds = xr.open_dataset(fn)
# list(ds.keys())
# ds.variables
lat=np.array(ds.variables['latitude'])
lat=np.flipud(lat)

lon=np.array(ds.variables['longitude'])
lon=np.flipud(lon)

plt.imshow(lon)
plt.colorbar()

#%%
fn='/Users/jason/Dropbox/recon_share/Box_Accumulation_1840-2012_301x561x173_cal.nc' # data from Box et al 2013 available from https://www.dropbox.com/scl/fi/hyj9hry8dlsjilpj10ju9/Box_Accumulation_1840-2012_301x561x173_cal.nc?rlkey=3bnlcvvua55vebg405irexdo2&dl=0
# fn='/Users/jason/Dropbox/recon_share/Box_Accumulation_1840-2012_301x561x173_cal_TIN.nc' # includes a triangular irregular network bias correction attempt, data from Lewis et al 2017 available from data from Box et al 2013 available from
ds = xr.open_dataset(fn)

# np.shape(ds.variables['tmp2m'])
# np.shape(ds.variables['refcclm'])
list(ds.keys())
ds.variables

#%% read from ds various 

C=np.array(ds.variables['acc'])
years=np.array(ds.variables['time']).astype(int)
mask=np.array(ds.variables['icemask'])
mask=np.flipud(mask)


#%% visualise mask
# mask values below 1 mean user should multiply accumulation values by mask values to get sub-grid accumulation rate useful when making regional totals for mass balance estimation
plt.imshow(mask)
plt.colorbar()
#%% visualise data
n_years=len(years)
yy=n_years-1
yy=0
temp=np.flipud(C[yy,:,:])
temp[mask<0.5]=np.nan
plt.imshow(np.flipud(C[yy,:,:]))
plt.colorbar()
plt.axis("off")
plt.title(str(years[yy]))
plt.show()

#%% obtain time series

accum=[]
areax=5000**2

for yy,year in enumerate(years):
    if yy>=0:
        print(year)
        temp=np.flipud(C[yy,:,:])
        temp[mask<0.5]=np.nan
        temp2=np.nansum(temp)*areax/1e12
        accum.append(temp2)
        # print(temp)

#%% output time series
def lowesx(x,y):
    # lowess will return our "smoothed" data with a y value for at every x-value
    lowess = sm.nonparametric.lowess(y, x, frac=.03)
    
    # unpack the lowess smoothed points to their values
    lowess_x = list(zip(*lowess))[0]
    lowess_y = list(zip(*lowess))[1]
    
    # run scipy's interpolation. There is also extrapolation I believe
    # f = interp1d(lowess_x, lowess_y, bounds_error=False)
    
    # xnew = [i/10. for i in range(400)]
    
    # this this generate y values for our xvalues by our interpolator
    # it will MISS values outsite of the x window (less than 3, greater than 33)
    # There might be a better approach, but you can run a for loop
    #and if the value is out of the range, use f(min(lowess_x)) or f(max(lowess_x))
    # ynew = f(xnew)
    
    return lowess_y
import statsmodels.api as sm

accum=np.array(accum)

plt.close()
fig, ax = plt.subplots(figsize=(8,6))

lowess_result=lowesx(years,accum)
plt.plot(years,accum,label='annual accumulation')
ax.plot(years, lowess_result, '-',c='k',linewidth=3,label='smoothed')
plt.ylabel('Gt per year')
out=pd.DataFrame({'year':years,
      'accumulation_annual':accum,
      'accumulation_annual_smoothed':lowess_result,
      })
 
vals=['accumulation_annual','accumulation_annual_smoothed']

for val in vals:
    out[val] = out[val].map(lambda x: '%.2f' % x)
    
print(out)

out.to_csv('./stats/Greenland)accumulation_annual_timeseries_1840-1999.csv',index=None)
ly='p'

if ly == 'x':plt.show()

fig_path='./Figs/'

if ly == 'p':
    plt.savefig('./Figs/Greenland)accumulation_annual_timeseries_1840-1999.png', 
                bbox_inches='tight', dpi=150)
    # if plt_eps:
    #     plt.savefig(fig_path+site+'_'+str(i).zfill(2)+nam+'.eps', bbox_inches='tight')
