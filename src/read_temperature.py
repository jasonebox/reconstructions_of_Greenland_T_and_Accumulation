#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 08:26:18 2023

@author: jason
"""
import matplotlib.pyplot as plt
# from matplotlib import cm
# from matplotlib.colors import ListedColormap, LinearSegmentedColormap
# from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import os
# from glob import glob
# from netCDF4 import Dataset
# from mpl_toolkits.basemap import Basemap
import pandas as pd
# from datetime import datetime 

fs=22

# plt.rcParams['font.sans-serif'] = ['Georgia']
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 1
plt.rcParams['grid.color'] = "grey"
plt.rcParams["font.size"] = fs
#params = {'legend.fontsize': 20,
#          'legend.handlelength': 2}
plt.rcParams['legend.fontsize'] = fs*0.8


path='/Users/jason/Dropbox/recon2022/'
os.chdir(path)

ni=301 ; nj=561
N_months=12
iyear=1840 ; fyear=2022
N_years=fyear-iyear+1
years=np.arange(N_years)+iyear

months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',
                             'DJF','MAM','JJA','SON','ANN']    

#%%

outpaths=['/Users/jason/0_dat/']
for outpath in outpaths:
    fn=outpath+'T_recon_'+str(N_years)+'x'+str(N_months)+'x'+str(nj)+'x'+str(ni)+'.npy'
    print('reading')
    T = np.fromfile(fn, dtype='int16')
    # plt.plot(T)
    print('reshaping')
    t_recon=T.reshape(N_years,N_months,nj,ni)/100.
    T=0

#%%
# test
plt.imshow(t_recon[181,4,:,:],vmin=-20,vmax=10)
plt.colorbar()
plt.axis("off")
plt.show()

#%% means for ice sheet

def load_bin_img(ni,nj,filename,dtype):
    data = np.fromfile(filename, dtype=dtype, count=ni*nj)
    array = np.reshape(data, [nj, ni], order='C')
    array=array.byteswap()
    # print(filename,ni,nj)
    return array

# mask
mask=load_bin_img(ni,nj,'./meta/Greenland_ice_mask_fuzzy_v20091101_5km_GRIMICE_merged.img','>f')
v=np.where(mask<0.5)
# mask[v]=np.nan
# print(mask[v])
# #%%
# print(np.max(mask))
# mask = np.reshape(mask, [nj, ni], order='C')
# mask=np.array(mask)
# plt.plot(mask)
# # mask.from_bytes(b'\x00\x01', "little")
plt.imshow(mask)

T_mean=np.zeros((N_years,N_months))

v=mask>=0.5
for yy in range(N_years):
    print('obtaining mean',yy+iyear)
    for mm in range(12):
        temp=t_recon[yy,mm,:,:]
        T_mean[yy,mm]=np.nanmean(temp[v])
        # print(yy+iyear,mm+1)

wo=0 # 1 to write out
if wo:
    df = pd.DataFrame(columns = ['year','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',
                                 'DJF','MAM','JJA','SON','ANN']) 
    df.index.name = 'index'
    df["year"]=pd.Series(years)
    # df["DJF"]=pd.Series(np.nan*N_years)
    v=np.where(years==1851)
    v=v[0][0]
    T_mean[v,6]=(T_mean[v-1,6]+T_mean[v+1,6])/2
    T_mean[v,7]=(T_mean[v-1,7]+T_mean[v+1,7])/2
    T_mean[T_mean==0]=np.nan
    for mm in range(12):
        df[months[mm]]=pd.Series(T_mean[:,mm])

    DJF=np.zeros(N_years)
    MAM=np.zeros(N_years)
    JJA=np.zeros(N_years)
    SON=np.zeros(N_years)
    ANN=np.zeros(N_years)
    

    for yy in range(N_years):
        if ((T_mean[yy,11]!=np.nan)&(T_mean[yy,0]!=np.nan)&(T_mean[yy,1]!=np.nan)):
            DJF[yy]=(T_mean[yy,11]+T_mean[yy,0]+T_mean[yy,1])/3
        if ((T_mean[yy,2]!=np.nan)&(T_mean[yy,3]!=np.nan)&(T_mean[yy,4]!=np.nan)):
            MAM[yy]=(T_mean[yy,2]+T_mean[yy,3]+T_mean[yy,4])/3
        if ((T_mean[yy,5]!=np.nan)&(T_mean[yy,5]!=np.nan)&(T_mean[yy,7]!=np.nan)):
            JJA[yy]=(T_mean[yy,5]+T_mean[yy,6]+T_mean[yy,7])/3
        if ((T_mean[yy,8]!=np.nan)&(T_mean[yy,9]!=np.nan)&(T_mean[yy,10]!=np.nan)):
            SON[yy]=(T_mean[yy,9]+T_mean[yy,9]+T_mean[yy,10])/3
        v=np.where(T_mean[yy,:]!=np.nan)
        # print(len(v[0]))
        if len(v[0])==12:
            ANN[yy]=np.mean(T_mean[yy,:])
    df["DJF"]=pd.Series(DJF)
    df["MAM"]=pd.Series(MAM)
    df["JJA"]=pd.Series(JJA)
    df["SON"]=pd.Series(SON)
    df["ANN"]=pd.Series(ANN)

print(df)
df.to_csv('./stats/T_seasonal_reconstructed_1840_to_2022.csv', float_format='%.2f')
#%% test
# T_mean[T_mean==0]=np.nan

# plt.close()
# # for mm in range(12):
# for mm in np.arange(5,8):
# # for mm in np.arange(0,3):
#     plt.plot(years,T_mean[:,mm],label=str(months[mm]))
# plt.xlim(1839,2023)
# plt.legend()
#%%

import statsmodels.api as sm
import matplotlib.pyplot as plt
# from matplotlib import cm
# from matplotlib.colors import ListedColormap, LinearSegmentedColormap
# from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import os
# from glob import glob
# from netCDF4 import Dataset
# from mpl_toolkits.basemap import Basemap
import pandas as pd
# from datetime import 

def lowesx(x,y,color,label):
    # lowess will return our "smoothed" data with a y value for at every x-value
    lowess = sm.nonparametric.lowess(y, x, frac=.2)
    
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
    
    ax.plot(lowess_x, lowess_y, '-',c=color,linewidth=3,label=label)

def statsx(x,y,namex):
    print(namex)
    T_2000_to_2015=np.nanmean(y[x>=2000])
    T_1950to1981=np.nanmean(y[((x>1950)&(x<1981))])
    T_1840to1900=np.nanmean(y[((x>=1840)&(x<=1900))])
    
    print('2000 to 2020 %.1f'%T_2000_to_2015+' deg. C')
    print('1950 to 1981 %.1f'%T_1950to1981+' deg. C')
    print('1840 to 1900 %.1f'%T_1840to1900+' deg. C')
    print('2000 to end of record minus T_1950to1981 %.1f'%(T_2000_to_2015-T_1950to1981)+' deg. C')
    print('2000 to end of record minus T_1840to1900 %.1f'%(T_2000_to_2015-T_1840to1900)+' deg. C')

months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',
                             'DJF','MAM','JJA','SON','ANN']    

df=pd.read_csv('./stats/T_seasonal_reconstructed_1840_to_2022.csv')

for month in months:
    plt.close()
    fig, ax = plt.subplots(figsize=(10,8))
    
    y=df[month]#-np.nanmean(df2.JJA[((df2.year>=year0)&(df2.year<=year1))])
    ax.plot(df.year,y,'b')
    statsx(df.year,y,'Box updated')
    lowesx(df.year,y,'b',month)
    
    # ax.plot(df.year,df[month],'-o',label=month)
    ax.set_xlim(1839,2023)
    ax.set_title('Greenland ice surface air temperature 1840 to 2021')
    ax.set_ylabel('°C')
    ax.legend()
    

    ly='x'
    if ly == 'p':
        # figpath='./Figs/'
        figpath='//Users/jason/Dropbox/recon2022/Figs/_whole_ice_area/'
        os.system('mkdir -p '+figpath)
        figname=figpath+month
        plt.savefig(figname, bbox_inches='tight', dpi=150)
        
#%% comp with global

df_recon=pd.read_csv('./stats/T_seasonal_reconstructed_1840_to_2022.csv')
df_recon = df_recon.loc[ df_recon.year >1850 ]
df_recon.reset_index(drop=True, inplace=True)

df_recon = df_recon.loc[ df_recon.year <2021 ]
df_recon.reset_index(drop=True, inplace=True)

#%%
# --------------------------------------------------------- Hadley Global
iyear=1851
dataset_name='HadCW04'
dataset_name2='HadCRUT4/HadSST4, Cowtan and Way (2004)'
year0_baseline=1851
year1_baseline=1900
fyear=2020
n_years=fyear-iyear+1

# global
fn='/Users/jason/Dropbox/Arctic_vs_global_SAT/HadCRUT4/ihad4_krig_v2_0-360E_-90-90N_n_0p.dat.txt'
df=pd.read_csv(fn,skiprows=21, delim_whitespace=True)
# n=1 # drops incomplete 2021
# df.drop(df.tail(n).index,inplace=True) # drop last n rows
    
means=np.zeros(n_years)

select_months=[0,1,2,3,4,5,6,7,8,9,10,11]
season_name='annual'
season_name2='annual'

select_months=np.asarray(select_months)
select_months+=1

z=np.asarray(df)
# estimate missing months using avereage of pervious N years
for i in range(12):
    temp=z[:,i+1]
    v=[temp<-990]
    if np.sum(v):
        # print(i,np.mean(temp[-5:-1]))#np.mean())
        z[-1,i+1]=np.mean(temp[-2:-1])

# end estimate missing months using avereage of pervious N years
z[n_years-1,12]=np.mean(z[n_years-12:n_years-2:,12])

for yy in range(0,n_years):
    # print()
    means[yy]=np.mean(z[yy,select_months])
    # print(yy+iyear,z[yy,select_months],len(z[yy,select_months]))
    # ss

x=np.arange(n_years)+iyear
v=((x>=year0_baseline)&(x<=year1_baseline))
y=means-np.mean(means[v])

x_G_Had=x
y_G_Had=y

# --------------------------------------------------------- Hadley Arctic
iyear=1851
dataset_name='HadCW04'
dataset_name2='HadCRUT4/HadSST4, Cowtan and Way (2004)'
year0_baseline=1851
year1_baseline=1900
fyear=2021
n_years=fyear-iyear+1

fn='/Users/jason/Dropbox/Arctic_vs_global_SAT/HadCRUT4/ihad4_krig_v2_0-360E_65-90N_n_0p.dat.txt' # comment this out to obtain global changes
df=pd.read_csv(fn,skiprows=21, delim_whitespace=True)
df=pd.read_csv(fn,skiprows=21, delim_whitespace=True)
# n=1 # drops incomplete 2021
# df.drop(df.tail(n).index,inplace=True) # drop last n rows


means=np.zeros((3,n_years))

for j,select_month in enumerate(range(0,3)):
    # if j>=0:
    if j==2:
        if select_month==0:
            select_months=[0,1,2,3,4,9,10,11]
            season_name='freeze-up season Oct-May'
            season_name2='cold'
        if select_month==1:
            select_months=[5,6,7,8]
            season_name='melt season Jun-Sept'
            season_name2='warm'
        if select_month==2:
            select_months=[0,1,2,3,4,5,6,7,8,9,10,11]
            season_name='annual'
            season_name2='annual'
    
        select_months=np.asarray(select_months)
        select_months+=1
        
        z=np.asarray(df)
        # estimate missing months using avereage of pervious N years
        for i in range(12):
            temp=z[:,i+1]
            v=[temp<-990]
            if np.sum(v):
                # print(i,np.mean(temp[-5:-1]))#np.mean())
                z[-1,i+1]=np.mean(temp[-2:-1])
                z[n_years-1,12]=np.mean(z[n_years-12:n_years-2:,12])
        # end estimate missing months using avereage of pervious N years
        z[n_years-1,12]=np.mean(z[n_years-12:n_years-2:,12])
        for yy in range(0,n_years):
            # print()
            means[j,yy]=np.mean(z[yy,select_months])
            # print(yy+iyear,z[yy,select_months],len(z[yy,select_months]))
            # ss
            
        x=np.arange(n_years)+iyear
        v=((x>=year0_baseline)&(x<=year1_baseline))
        y=means[j,:]-np.mean(means[j,v])

        x_A_Had=x
        y_A_Had=y
#%%

def statsx(x,y,namex):
    print()
    print(namex)
    T_2000_to_2015=np.nanmean(y[x>=2000])
    T_1950to1981=np.nanmean(y[((x>1950)&(x<1981))])
    T_1840to1900=np.nanmean(y[((x>=1840)&(x<=1900))])
    
    print('T anom 2000 to 2020 vs 1951 to 1980: %.1f'%T_2000_to_2015+' deg. C')
    # print('1950 to 1981 %.1f'%T_1950to1981+' deg. C')
    print('T anom 1851 to 1900 vs 1951 to 1980: %.1f'%T_1840to1900+' deg. C')
    print('T anom (2000 to 2020) minus (1950 to 1981) %.1f'%(T_2000_to_2015-T_1950to1981)+' deg. C')
    print('T anom (2000 to 2020) minus (1840 to 1900) %.1f'%(T_2000_to_2015-T_1840to1900)+' deg. C')
    
fig, ax = plt.subplots(figsize=(10,10))

# ax.plot(x,y-np.nanmean(y[(x>=1951)&(x<=1980)]),'k',label=)
# ax.plot(df_recon.year,df_recon.ANN-np.nanmean(df_recon.ANN[(df_recon.year>=1951)&(df_recon.year<=1980)]),'b',label='Box Greenland reconstruction Annual')

label='HadCRUT4 global annual' ; co='k' ; y=y_G_Had-np.nanmean(y_G_Had[(x_G_Had>=1951)&(x_G_Had<=1980)])
# ax.plot(x_G_Had,y,co)
statsx(x_G_Had,y,label)
lowesx(x_G_Had,y,co,label)

label='HadCRUT4 Arctic annual' ; co='c' ; y=y_A_Had-np.nanmean(y_A_Had[(x_A_Had>=1951)&(x_A_Had<=1980)])
# ax.plot(x_G_Had,y,co)
statsx(x_A_Had,y,label)
lowesx(x_A_Had,y,co,label)

label='Box Greenland annual' ; co='b' ; y=df_recon.ANN-np.nanmean(df_recon.ANN[(df_recon.year>=1951)&(df_recon.year<=1980)])
# ax.plot(df_recon.year,y,co)
statsx(df_recon.year,y,label)
lowesx(df_recon.year,y,co,label)

label='Box Greenland JJA' ; co='r' ; y=df_recon.JJA-np.nanmean(df_recon.JJA[(df_recon.year>=1951)&(df_recon.year<=1980)])
# ax.plot(df_recon.year,y,co)
statsx(df_recon.year,y,label)
lowesx(df_recon.year,y,co,label)

ax.set_xlim(1850,2021)
ax.set_title('1851 to 2020')
ax.set_ylabel('°C anomaly relative to 1951 to 1980')
ax.legend()