# ETRM - Evapotranspiration and Recharge Model, Point version, SNOW CALIBRATION
# For use with multiple SNOTEL stations
# David Ketchum, December 2015
import datetime
import os
from dateutil import rrule
from osgeo import gdal
from gdalconst import *
from osgeo import osr
import numpy as np

startTime = datetime.datetime.now()
print(startTime)

# np.seterr(divide='ignore', invalid='ignore')


def cells(array):
    window = array[480:520, 940:980]
    return window

# Define user-controlled constants, these are constants to start with day one, replace
# with spin-up data when multiple years are covered
ze = 10
p = 0.4
kc_min = 0.15

# Set start datetime object
start, end = datetime.datetime(2002, 1, 1), datetime.datetime(2003, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime.datetime(start.year, 11, 1), datetime.datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime.datetime(start.year, 6, 1), datetime.datetime(start.year, 10, 1)

# Create indices to plot point time series, these are empty lists that will
# be filled as the simulation progresses
pltRain = []
pltEta = []
pltSnow_fall = []
pltRo = []
pltDr = []
pltPdr = []
pltDe = []
pltDrew = []
pltTemp = []
pltTempM = []
pltDp_r = []
pltKs = []
pltEtrs = []
pltKcb = []
pltKe = []
pltMlt = []
pltSwe = []
pltDay = []
pltFs1 = []
pltPpt = []

infil = 0.0
precip = 0.0
et = 0.0
runoff = 0.0
drew = 2.0
ppt_tom = 0.0

# Read in static data as arrays
path = 'C:\\Recharge_GIS\\OSG_Data\\current_use'
raster = 'Bedrock_Ksat_Ras1_std'
bdrk_ksat_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
bdrk_ksat = np.array(bdrk_ksat_open.GetRasterBand(1).ReadAsArray(), dtype=float) * 1000 / 3.281  # ft/day to mm/day
# bdrk_ksat = bdrk_ksat[480:520, 940:980]
min_val = np.ones(bdrk_ksat.shape) * 0.001
bdrk_ksat = np.maximum(bdrk_ksat, min_val)
bdrk_ksat_open = []

raster = 'aws_ras_15apr1'
aws_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
taw = np.array(aws_open.GetRasterBand(1).ReadAsArray(), dtype=float) * 10.  # name this taw for now
# taw = aws[480:520, 940:980]
taw = np.maximum(taw, min_val)
aws_open = []

raster = 'nlcd_root_dpth_15apr'
nlcd_rt_z_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
nlcd_rt_z = np.array(nlcd_rt_z_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_rt_z = nlcd_rt_z[480:520, 940:980]
nlcd_rt_z = np.maximum(nlcd_rt_z, min_val)
nlcd_rt_z_open = []

raster = 'nlcd_plnt_hgt1_250_m_degraded1'
nlcd_plt_hgt_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
nlcd_plt_hgt = np.array(nlcd_plt_hgt_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# nlcd_plt_hgt = nlcd_plt_hgt[480:520, 940:980]
nlcd_plt_hgt = np.maximum(nlcd_plt_hgt, min_val)
nlcd_plt_hgt_open = []

# raster = 'FC_Ras_SSGO1'
# FC_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
# fc = np.array(FC_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# # fc = fc[480:520, 940:980]
# fc = np.maximum(fc, min_val)
# FC_open = []
#
# raster = 'WP_Ras_SSGO1'
# WP_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
# wp = np.array(WP_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# # wp = wp[480:520, 940:980]
# wp = np.maximum(wp, min_val)
# WP_open = []

raster = 'Soil_Ksat_15apr'  # convert from micrometer/sec to mm/day
ksat_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
ksat = np.array(ksat_open.GetRasterBand(1).ReadAsArray(), dtype=float) * 86.4
# ksat = ksat[480:520, 940:980]
ksat = np.maximum(ksat, min_val)
ksat_open = []

raster = 'tew_250_15apr'
taw_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
taw = np.array(taw_open.GetRasterBand(1).ReadAsArray(), dtype=float)
taw = taw[480:520, 940:980]
taw = np.maximum(taw, min_val)
taw_open = []

# raster = 'REW_Float1_std'
# rew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
# rew = np.array(rew_open.GetRasterBand(1).ReadAsArray(), dtype=float) * 1000.
# rew = rew[480:520, 940:980]
# rew = np.maximum(rew, min_val)
# rew_open = []

for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
    doy = dday.timetuple().tm_yday
    print("Time : {a} day {b}_{c}".format(a=str(datetime.datetime.now() - startTime), b=doy, c=dday.year))

    #  NDVI to kcb
    if dday.year == 2000:
        path = 'F:\\NDVI\\NDVI_std_all'
        ras_list = os.listdir('F:\\NDVI\\NDVI_std_all')
        obj = [1, 49, 81, 113, 145, 177, 209, 241, 273, 305, 337]
        if doy < 49:
            strt = 1
            band = doy
            nd = 48
            raster = '{a}\\T{b}_{c}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(a=path,
                                                                                         b=str(strt).rjust(3, '0'),
                                                                                         c=str(nd).rjust(3, '0'))
            ndvi_open = gdal.Open(raster)
            ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
            ndvi_open = []
            kcb = ndvi * 1.25
        else:
            for num in obj[1:]:
                diff = doy - num
                if 0 <= diff <= 31:
                    pos = obj.index(num)
                    strt = obj[pos]
                    band = diff + 1
                    if num == 337:
                        nd = num + 29
                    else:
                        nd = num + 31
                    raster = '{a}\\T{b}_{c}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(a=path,
                                                                                            b=str(strt).rjust(3, '0'),
                                                                                            c=str(nd).rjust(3, '0'))
                    ndvi_open = gdal.Open(raster)
                    ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
                    ndvi_open = []
                    kcb = ndvi * 1.25

    elif dday.year == 2001:
        path = "F:\\NDVI\\NDVI_std_all"
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        for num in obj:
            diff = doy - num
            if 0 <= diff <= 15:
                pos = obj.index(num)
                strt = obj[pos]
                band = diff + 1
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15
                raster = '{a}\\{b}_{c}_{d}.tif'.format(a=path, b=dday.year, c=strt, d=nd)
                ndvi_open = gdal.Open(raster)
                ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
                ndvi_open = []
                kcb = ndvi * 1.25

    else:
        path = "F:\\NDVI\\NDVI_std_all"
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        for num in obj:
            diff = doy - num
            if 0 <= diff <= 15:
                pos = obj.index(num)
                strt = obj[pos]
                band = diff + 1
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15
                raster = '{a}\\{b}_{c}.tif'.format(a=path, b=dday.year, c=pos+1, d=nd)
                ndvi_open = gdal.Open(raster)
                ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
                ndvi_open = []
                kcb = ndvi * 1.25
    # kcb = kcb[480:520, 940:980]
    kcb = np.maximum(kcb, min_val)

    #  PRISM to ppt
    #  Remember to use the new PRISM!
    path = 'F:\\PRISM\Precip\\800m_std_all'
    raster = '{a}\\PRISMD2_NMHW2mi_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                         c=str(dday.month).rjust(2, '0'),
                                                         d=str(dday.day).rjust(2, '0'))
    ppt_open = gdal.Open(raster)
    ppt = np.array(ppt_open.GetRasterBand(1).ReadAsArray(), dtype=float)

    dday_tom = dday + datetime.timedelta(days=1)
    raster_tom = '{a}\\PRISMD2_NMHW2mi_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                               c=str(dday_tom.month).rjust(2, '0'),
                                                               d=str(dday_tom.day).rjust(2, '0'))
    ppt_tom_open = gdal.Open(raster_tom)
    ppt_tom = np.array(ppt_tom_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    dataset = ppt_tom_open
    ppt_open = []
    ppt_tom_open = []
    # ppt = ppt[480:520, 940:980]
    # ppt_tom = ppt_tom[480:520, 940:980]
    ppt = np.maximum(ppt, min_val)
    ppt_tom = np.maximum(ppt_tom, min_val)

    #  PRISM to mintemp, maxtemp, temp
    if dday.year in [2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013]:
        path = "F:\\PRISM\\Temp\\Minimum_standard"
        raster = '{a}\\cai_tmin_us_us_30s_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                                c=str(dday.month).rjust(2, '0'),
                                                                d=str(dday.day).rjust(2, '0'))
        minTemp_open = gdal.Open(raster)
        min_temp = np.array(minTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
        minTemp_open = []
    else:
        path = "F:\\PRISM\\Temp\\Minimum_standard"
        raster = '{a}\\TempMin_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                               c=str(dday.month).rjust(2, '0'),
                                                               d=str(dday.day).rjust(2, '0'))
        minTemp_open = gdal.Open(raster)
        min_temp = np.array(minTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
        minTemp_open = []
    path = "F:\\PRISM\\Temp\\Maximum_standard"
    raster = '{a}\\TempMax_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                           c=str(dday.month).rjust(2, '0'),
                                                           d=str(dday.day).rjust(2, '0'))
    maxTemp_open = gdal.Open(raster)
    max_temp = np.array(maxTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    maxTemp_open = []

    temp = (min_temp + max_temp)/2

    min_temp = np.maximum(min_temp, min_val)
    max_temp = np.maximum(max_temp, min_val)
    temp = np.maximum(temp, min_val)
    # min_temp = min_temp[480:520, 940:980]
    # max_temp = max_temp[480:520, 940:980]
    # temp = temp[480:520, 940:980]

    #  PM data to etrs
    path = "F:\\PM_RAD"
    raster = '{a}\\PM{d}\\PM_NM_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
    etrs_open = gdal.Open(raster)
    etrs = np.array(etrs_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    etrs_open = []
    # etrs = etrs[480:520, 940:980]
    etrs = np.maximum(etrs, min_val)

    # Net Longwave  Radiation Data is with the PM data
    path = "F:\\PM_RAD"
    raster = '{a}\\PM{d}\\RLIN_NM_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
    rlin_open = gdal.Open(raster)
    rlin = np.array(rlin_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    rlin_open = []
    # rlin = rlin[480:520, 940:980]
    rlin = np.maximum(rlin, min_val)

    # Net Shortwave Radiation Data
    path = "F:\\PM_RAD"
    raster = '{a}\\rad{d}\\RTOT_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
    rg_open = gdal.Open(raster)
    rg = np.array(rg_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    rg_open = []
    # rg = rg[480:520, 940:980]
    rg = np.maximum(rg, min_val)

    #  ETRM Daily Run  #######################################################################

    day_of_year = dday.timetuple().tm_yday
    if dday == start:
        #  Total evaporable water is depth of water in the evaporable
        #  soil layer, i.e., the water available to both stage 1 and 2 evaporation
        tew1 = (fc - 0.5 * wp) * ze * 1.0
        tew2 = (fc - 0.5 * wp) * ze * (etrs/5)**1/2
        tew = np.minimum(tew1, tew2)
        rew = np.minimum((2+(tew/3.)), 0.8 * tew)
        # del tew1, tew2

        pDr = taw * 0.6
        pDe = tew * 0.6
        pDrew = rew * 0.6
        dr = pDr
        de = pDe
        drew = pDrew
        swe = np.ones(ppt.shape, dtype=float) * 5

    if sMon.timetuple().tm_yday <= dday.timetuple().tm_yday <= eMon.timetuple().tm_yday:
        ksat = ksat * 2/24.
    else:
        ksat = ksat * 6/24.

    kc_max_1 = kcb + 0.05
    min_val = np.ones(ppt.shape) * 0.01
    kc_max = np.maximum(min_val, kc_max_1)
    # del kc_max_1

    ks_ref = (taw - pDr) / (0.6 * taw)
    ks_min = np.maximum(min_val, ks_ref)
    ks = np.minimum(ks_min, np.ones(ppt.shape))
    # del ks_ref, ks_min

    nlcd_plt_hgt = nlcd_plt_hgt * 0.5 + 1
    numr = np.maximum(kcb - kc_min, min_val * 10)
    denom = np.maximum((kc_max - kc_min), min_val * 10)
    fcov_ref = (numr / denom) ** nlcd_plt_hgt
    fcov_min = np.minimum(fcov_ref, np.ones(ppt.shape))
    fcov = np.maximum(fcov_min, min_val * 10)
    # del numr, denom, fcov_ref, fcov_min

    fsa = (rew - drew) / (kc_max * etrs)
    fsb = np.minimum(fsa, np.ones(ppt.shape))
    fs1 = np.maximum(fsb, np.zeros(ppt.shape))
    #  few is the wetted fraction of vegetation
    few = np.maximum(1 - fcov, min_val * 10)
    kr_1 = (tew - pDe) / (tew - rew)
    kr_2 = np.minimum(kr_1, np.ones(ppt.shape))
    # tew_max
    kr = np.maximum(kr_2, np.zeros(ppt.shape))
    # kr = fs1 + (1 - fs1) * tew_max


    # Ke evaporation reduction coefficient; stage 1 evaporation
    ke_init = kr * (kc_max - (ks * kcb))
    cond = few * kc_max
    ke_min = np.minimum(ke_init, cond)
    ke = np.maximum(ke_min, np.zeros(ppt.shape))

    transp = (ks * kcb) * etrs

    et_init = (ks * kcb + ke) * etrs
    eta = np.maximum(et_init, np.zeros(ppt.shape))

    evap_init = ke * etrs
    evap_min = np.maximum(evap_init, np.zeros(ppt.shape))
    evap = np.minimum(evap_min, kc_max)


    # Load temp, find swe, melt, and precipitation, load Ksat
    # Use SNOTEL data for precip and temps:
    # df_snow : (stel_date, stel_snow, stel_precip, stel_tobs, stel_tmax, stel_tmin, stel_tavg, stel_snwd)
    if dday == end:
        ppt_tom = np.zeros(ppt.shape, dtype=float)
    zeros = np.zeros(ppt.shape).reshape(ppt.shape)
    snow_fall = zeros
    rain = zeros
    for x in range(0, len(temp[0, :])):
        for y in range(0, len(temp[:, 0])):
            z = temp[y, x]
            if z < 0.0:
                snow_fall[y, x] = ppt[y, x]
                rain[y, x] = 0.0
            else:
                rain[y, x] = ppt[y, x]
                snow_fall[y, x] = 0.0

    swe = snow_fall + swe

    if dday.timetuple().tm_yday > sWin.timetuple().tm_yday or dday.timetuple().tm_yday < eWin.timetuple().tm_yday:
        mlt_init = np.maximum((temp + 1.8) * 0.95, np.zeros(ppt.shape))  # winter day
        # mlt1 = swe - mlt_init
        mlt = np.minimum(swe, mlt_init)
    else:
        mlt_init = np.maximum((max_temp + 1.8) * 1.25, np.zeros(ppt.shape))  # non-winter day
        # mlt1 = swe - mlt_init
        mlt = np.minimum(swe, mlt_init)

    swe = swe - mlt

    # Find depletions
    pDr = dr
    pDe = de
    pDrew = drew

    watr = rain + mlt
    deps = dr + de + drew

    ro = zeros
    dp_r = zeros
    for x in range(0, len(watr[0, :])):
        for y in range(0, len(watr[:, 0])):
            if watr[y, x] < deps[y, x]:
                ro[y, x] = 0.0
                dp_r[y, x] = 0.0
            elif ksat[y, x] > watr[y, x] > deps[y, x]:
                ro[y, x] = 0.0
                dp_r[y, x] = watr[y, x] - deps[y, x]
            elif watr[y, x] > ksat[y, x] + deps[y, x]:
                ro[y, x] = watr[y, x] - ksat[y, x] - deps[y, x]
                dp_r[y, x] = ksat[y, x]
            else:  # deps > ksat
                ro[y, x] = 0.0
                dp_r[y, x] = 0.0
                pass

    drew = np.minimum((pDrew + (1 - fcov) * ((ro + dp_r + evap) - (rain + mlt))), rew)
    drew = np.maximum(drew, np.zeros(ppt.shape))
    diff = np.maximum((pDrew - drew), np.zeros(ppt.shape))

    de = np.minimum((pDe + fcov * ((ro + dp_r + evap) - (rain + mlt - diff))), tew)
    de = np.maximum(de, np.zeros(ppt.shape))
    diff = np.maximum((pDe - de + diff), np.zeros(ppt.shape))

    dr = np.minimum((pDr - (rain + mlt - diff) + (ro + transp + dp_r)), taw)
    dr = np.maximum(dr, np.zeros(ppt.shape))

# Create cumulative rasters to show net over entire run

    infil = infil + dp_r
    infil = np.maximum(infil, zeros)

    et = et + evap + transp
    et = np.maximum(et, zeros)

    precip = precip + rain + snow_fall
    precip = np.maximum(precip, zeros)

    runoff = runoff + ro
    runoff = np.maximum(runoff, zeros)

    snow_ras = swe + snow_fall - mlt
    snow_ras = np.maximum(snow_ras, zeros)

    # Check MASS BALANCE for the love of WATER!!!
    mass = rain + mlt - ro - transp - evap - dp_r - ((drew - pDrew) + (de - pDe) + (pDr - dr))


outputs = [infil, et, precip, runoff, snow_ras, mass, dr, de, drew]
output_names = ['infil', 'et', 'precip', 'runoff', 'snow_ras', 'mass', 'dr', 'de', 'drew']
x = 0
for element in outputs:
    name = output_names[x]
    print("Saving {a}".format(a=name))
    driver = gdal.GetDriverByName('GTiff')
    filename = 'C:\\Recharge_GIS\\Array_Results\\{a}.tif'.format(a=name)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    bands = dataset.RasterCount
    band = dataset.GetRasterBand(1)
    datatype = band.DataType
    outDataset = driver.Create(filename, cols, rows, bands, datatype)
    geoTransform = dataset.GetGeoTransform()
    outDataset.SetGeoTransform(geoTransform)
    proj = dataset.GetProjection()
    outDataset.SetProjection(proj)
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(element, 0, 0)
    x += 1



