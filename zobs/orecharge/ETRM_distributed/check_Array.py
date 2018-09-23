# ETRM - Evapotranspiration and Recharge Model, Point version, DISTRIBUTED
# ETRM - Evapotranspiration and Recharge Model, Point version, DISTRIBUTED
# David Ketchum, April 2016
import datetime
import calendar
import os
from dateutil import rrule
from osgeo import gdal
import numpy as np
import collections

np.set_printoptions(linewidth=700, precision=2)

startTime = datetime.datetime.now()
print(startTime)


def cells(array):
    window = array[480:510, 940:970]
    return window


def count_elements(array):
    unique, counts = np.unique(array, return_counts=True)
    count_dict = dict(zip(unique, counts))
    return count_dict

# Set start datetime object
start, end = datetime.datetime(2000, 1, 1), datetime.datetime(2013, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime.datetime(start.year, 11, 1), datetime.datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime.datetime(start.year, 6, 1), datetime.datetime(start.year, 10, 1)

# Read in static data as arrays
path = 'C:\\Recharge_GIS\\OSG_Data\\current_use'
raster = 'Q_deps_std'
qDeps_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
qDeps = np.array(qDeps_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_rt_z = nlcd_rt_z[480:520, 940:980]
min_val = np.ones(qDeps.shape) * 0.001
ones = np.ones(qDeps.shape)
qDeps = np.maximum(qDeps, min_val)
qDeps_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\clipped_results\\tots_MAY13'
raster = 'infil_tot_clp'
infil_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
infil = np.array(infil_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_rt_z = nlcd_rt_z[480:520, 940:980]
# infil = np.maximum(infil, min_val)
infil_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\clipped_results\\tots_MAY13'
raster = 'runoff_tot_clp'
ro_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
ro = np.array(ro_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_rt_z = nlcd_rt_z[480:520, 940:980]
# ro = np.maximum(ro, min_val)
ro_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\clipped_results\\tots_MAY13'
raster = 'et_tot_clp'
et_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
et = np.array(et_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_rt_z = nlcd_rt_z[480:520, 940:980]
# et = np.maximum(et, min_val)
et_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\clipped_results\\tots_MAY13'
raster = 'final_snow_tot_clp'
snow_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
snow = np.array(snow_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_rt_z = nlcd_rt_z[480:520, 940:980]
# snow = np.maximum(snow, min_val)
snow_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\clipped_results\\tots_MAY13'
raster = 'ppt_tot_clp'
ppt_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
ppt = np.array(ppt_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_rt_z = nlcd_rt_z[480:520, 940:980]
min_val = np.ones(ppt.shape) * 0.001
ppt = np.maximum(ppt, min_val)
ppt_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\clipped_results\\tots_MAY13'
raster = 'de1_tot_clp'
de_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
de1 = np.array(de_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# de = de[480:520, 940:980]
de1 = np.where(np.isnan(de1) == True, np.zeros(infil.shape), de1)
de_open = []

raster = 'dr1_tot_clp'
dr_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
dr1 = np.array(dr_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# dr = dr[480:520, 940:980]
dr1 = np.where(np.isnan(dr1) == True, np.zeros(infil.shape), dr1)
dr_open = []

raster = 'drew1_tot_clp'
drew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
drew1 = np.array(drew_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# dr = dr[480:520, 940:980]
drew1 = np.where(np.isnan(drew1) == True, np.zeros(infil.shape), drew1)
drew_open = []

raster = 'de_tot_clp'
de_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
de2 = np.array(de_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# de = de[480:520, 940:980]
de2 = np.where(np.isnan(de2) == True, np.zeros(infil.shape), de2)
de_open = []

raster = 'dr_tot_clp'
dr_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
dr2 = np.array(dr_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# dr = dr[480:520, 940:980]
dr2 = np.where(np.isnan(dr2) == True, np.zeros(infil.shape), dr2)
dr_open = []

raster = 'drew_tot_clp'
drew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
drew2 = np.array(drew_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# dr = dr[480:520, 940:980]
drew2 = np.where(np.isnan(drew2) == True, np.zeros(infil.shape), drew2)
drew_open = []

raster = 'mass_tot_clp'
mass_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
mass = np.array(mass_open.GetRasterBand(1).ReadAsArray(), dtype=float)
mass = np.where(np.isnan(mass) == True, np.zeros(infil.shape), mass)
mass = np.where(mass < 0.0, np.zeros(infil.shape), mass)
mass = np.where(mass > ppt, np.nan, mass)
mass_open = []

raster = 'fin_mass_tot_clp'
fin_mass_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
fin_mass = np.array(fin_mass_open.GetRasterBand(1).ReadAsArray(), dtype=float)
fin_mass = np.where(np.isnan(fin_mass) == True, np.zeros(infil.shape), fin_mass)
fin_mass = np.where(fin_mass < 0.0, np.zeros(infil.shape), fin_mass)
fin_mass = np.where(fin_mass > ppt, np.zeros(infil.shape), fin_mass)
fin_mass_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\misc_analysis_etc'
raster = 'et_index'
et_index_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
et_index = np.array(et_index_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# et_index = et_index[480:520, 940:980]
et_index = np.where(np.isnan(et_index) == True, np.zeros(infil.shape), et_index)
et_index_open = []

path = 'C:\\Recharge_GIS\\NM_DEM'
raster = 'NM_DEM_250_UTM'
dem_index_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
dem = np.array(dem_index_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# dem_index = dem_index[480:520, 940:980]
# dem_index = np.where(np.isnan(dem_index) == True, np.zeros(infil.shape), dem_index)
dem = np.where(dem < 867.0, np.ones(dem.shape)*867.0, dem)
dem_index_open = []

path = 'C:\\Recharge_GIS\\ABQ'
raster = 'abq_mean_ppt_27MAY'
abq_index_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
abq = np.array(abq_index_open.GetRasterBand(1).ReadAsArray(), dtype=float)
abq = np.where(abq < 0.0, 0.0, abq)
abq_index_open = []

def find_pct(raster, window, *target):
    if target:
        bound = target
        pass
    else:
        bound = np.mean(raster)
    lower_bound, upper_bound = bound * (1 - window), bound * (1 + window)
    pct_high = np.where(raster < upper_bound, np.ones(raster.shape), np.zeros(raster.shape))
    pct_low = np.where(raster > lower_bound, np.ones(raster.shape), np.zeros(raster.shape))
    cover = pct_low + pct_high
    truth = np.where(cover == 2, np.ones(raster.shape), np.zeros(raster.shape))
    total = raster.shape[0] * raster.shape[1]
    return np.sum(truth) / total


def sum(raster):
    sum = np.sum(raster) * 250**2 * 0.001 * 0.000810714
    return sum

diff = sum(de1 + dr1 + drew1) - sum(de2 + dr2 + drew2)

low, high = np.mean(dem) * 0.9, np.mean(dem) * 1.1


# b = np.array([['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
#                'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z']])















