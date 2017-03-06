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
print startTime

# np.seterr(divide='ignore', invalid='ignore')


# def cells(array):
#     window = array[320:350, 320:350]
#     return window

# Define user-controlled constants, these are constants to start with day one, replace
# with spin-up data when multiple years are covered
ze = 10
p = 0.4
kc_min = 0.15

# Set start datetime object
start, end = datetime.datetime(2000, 1, 1), datetime.datetime(2000, 12, 31)
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
path = 'C:\\Recharge_GIS\\OSG_Data'
raster = 'Bedrock_Ksat_Ras1_std'
bdrk_ksat_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
bdrk_ksat = np.array(bdrk_ksat_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
bdrk_ksat = bdrk_ksat[1000:1010, 1000:1010]
min_val = np.ones(bdrk_ksat.shape) * 0.01
bdrk_ksat = np.maximum(bdrk_ksat, min_val)
bdrk_ksat_open = []

raster = 'AWS_merge_ras1'
aws_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
aws = np.array(aws_open.GetRasterBand(1).ReadAsArray(), dtype='int64')  # name this taw for now
taw = aws[1000:1010, 1000:1010]
aws_open = []

raster = 'nlcd_root_dpth1_std'
nlcd_rt_z_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
nlcd_rt_z = np.array(nlcd_rt_z_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
nlcd_rt_z = nlcd_rt_z[1000:1010, 1000:1010]
nlcd_rt_z = np.maximum(nlcd_rt_z, min_val)
nlcd_rt_z_open = []

raster = 'nlcd_plnt_hgt1_250_m_degraded1_std'
nlcd_plt_hgt_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
nlcd_plt_hgt = np.array(nlcd_plt_hgt_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
nlcd_plt_hgt = nlcd_plt_hgt[1000:1010, 1000:1010]
nlcd_plt_hgt_open = []

raster = 'FC_Ras_SSGO'
FC_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
fc = np.array(FC_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
fc = fc[1000:1010, 1000:1010]
fc = np.maximum(fc, min_val)
FC_open = []

raster = 'WP_Ras_SSGO1'
WP_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
wp = np.array(WP_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
wp = wp[1000:1010, 1000:1010]
wp = np.maximum(wp, min_val)
WP_open = []

raster = 'Soil_Ksat_Ras_SSGO1'
ksat_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
ksat = np.array(ksat_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
ksat = ksat[1000:1010, 1000:1010]
ksat = np.maximum(ksat, min_val)
ksat_open = []

# raster = 'taw_250_m_degraded1_std'
# taw_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
# taw = np.array(taw_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
# taw = taw[1000:1010, 1000:1010]
# taw = np.maximum(taw, min_val)
# taw_open = []

raster = 'REW_Float1_std'
rew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
rew = np.array(rew_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
rew = rew[1000:1010, 1000:1010]
rew = np.maximum(rew, min_val)
rew_open = []

for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
    doy = dday.timetuple().tm_yday
    print "Time : {a} day {b}_{c}".format(a=str(datetime.datetime.now() - startTime), b=doy, c=dday.year)

    #  NDVI to kcb
    if dday.year == 2000:
        path = 'E:\\NDVI_std_2000'
        ras_list = os.listdir('E:\\NDVI_std_2000')
        for raster in ras_list:
            if raster == 'temp.tif':
                print 'found temp tif'
                os.remove(raster)
            if doy > 48:
                start_band = str(raster)[1:4]
                end_band = str(raster)[5:8]
                if int(start_band) <= doy <= int(end_band):
                    ndvi_open = gdal.Open('{a}\\{b}'.format(a=path, b=raster))
                    ndvi = np.array(ndvi_open.GetRasterBand(doy - int(start_band) + 1).ReadAsArray(), dtype='int64')
                    ndvi_open = []
                    kcb = ndvi * 1.25

            else:
                    ndvi_open = gdal.Open('{a}\\{b}'.format(a=path, b=raster))
                    ndvi = np.array(ndvi_open.GetRasterBand(doy).ReadAsArray(), dtype='int64')
                    ndvi_open = []
                    kcb = ndvi * 1.25
                    break

    elif dday.year == 2001:
        path = "E:\\NDVI\\2001"
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
                ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype='int64')
                ndvi_open = []
                kcb = ndvi * 1.25

    else:
        path = "E:\\NDVI\\2002_2013"
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
                ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype='int64')
                ndvi_open = []
                kcb = ndvi * 1.25
    kcb = kcb[1000:1010, 1000:1010]

    #  PRISM to ppt
    #  Remember to use the new PRISM!
    path = 'E:\\PRISM_std_ppt_std_2000'
    raster = '{a}\\PRISM_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                         c=str(dday.month).rjust(2, '0'),
                                                         d=str(dday.day).rjust(2, '0'))
    ppt_open = gdal.Open(raster)
    ppt = np.array(ppt_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
    ppt_map = ppt
    dday_tom = dday + datetime.timedelta(days=1)
    raster_tom = '{a}\\PRISM_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                             c=str(dday_tom.month).rjust(2, '0'),
                                                             d=str(dday_tom.day).rjust(2, '0'))
    ppt_tom_open = gdal.Open(raster_tom)
    ppt_tom = np.array(ppt_tom_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
    dataset = ppt_tom_open
    ppt_open = []
    ppt_tom_open = []
    ppt = ppt[1000:1010, 1000:1010]
    ppt_tom = ppt_tom[1000:1010, 1000:1010]

    #  PRISM to mintemp, maxtemp, temp
    path = "E:\\PRISM_std_temp_min_std_2000"
    raster = '{a}\\cai_tmin_us_us_30s_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                            c=str(dday.month).rjust(2, '0'),
                                                            d=str(dday.day).rjust(2, '0'))
    minTemp_open = gdal.Open(raster)
    min_temp = np.array(minTemp_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
    minTemp_open = []

    path = "E:\\PRISM_std_temp_max_std_2000"
    raster = '{a}\\TempMax_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                           c=str(dday.month).rjust(2, '0'),
                                                           d=str(dday.day).rjust(2, '0'))
    maxTemp_open = gdal.Open(raster)
    max_temp = np.array(maxTemp_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
    maxTemp_open = []

    temp = (min_temp + max_temp)/2
    min_temp = min_temp[1000:1010, 1000:1010]
    max_temp = max_temp[1000:1010, 1000:1010]
    temp = temp[1000:1010, 1000:1010]

    #  PM data to etrs
    path = "E:\\PM_std_2000"
    raster = '{a}\\PM_NM_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'))
    etrs_open = gdal.Open(raster)
    etrs = np.array(etrs_open.GetRasterBand(1).ReadAsArray(), dtype='int64')
    etrs_open = []
    etrs = etrs[1000:1010, 1000:1010]

    #  ETRM Daily Run  #######################################################################

    day_of_year = dday.timetuple().tm_yday
    if dday == start:
        tew1 = (fc - 0.5 * wp) * ze * 1.0
        tew2 = (fc - 0.5 * wp) * ze * (etrs/5)**1/2
        tew = np.minimum(tew1, tew2)
        # del tew1, tew2

        pDr = np.ones(ppt.shape, dtype='int64') * 125
        pDe = np.ones(ppt.shape, dtype='int64') * 40
        pDrew = np.ones(ppt.shape, dtype='int64') * 5
        dr = pDr
        de = pDe
        drew = pDrew
        swe = np.ones(ppt.shape, dtype='int64') * 5

    if dday.timetuple().tm_yday > sMon.timetuple().tm_yday or dday.timetuple().tm_yday < eMon.timetuple().tm_yday:
        print "monsoon day"
        ksat = ksat * 2/24.
    else:
        print "non-monsoon day"
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
    fcov = np.maximum(fcov_min, min_val * 100)
    # del numr, denom, fcov_ref, fcov_min

    fsa = (rew - drew) / (kc_max * etrs)
    fsb = np.minimum(fsa, np.ones(ppt.shape))
    fs1 = np.maximum(fsb, np.zeros(ppt.shape))
    few = np.maximum(1 - fcov, min_val * 10)
    tew_rat = (tew - pDe) / (tew - rew)
    tew_min = np.minimum(tew_rat, np.ones(ppt.shape))

    # tew_max
    kr = np.maximum(tew_min, np.zeros(ppt.shape))
    # kr = fs1 + (1 - fs1) * tew_max
    # del fsa, fsb, tew_rat, tew_min
    # Ke; stage 1 evaporation
    ke_init = kr * (kc_max - (ks * kcb))
    cond = few * kc_max
    ke_min = np.minimum(ke_init, cond)
    ke = np.maximum(ke_min, np.zeros(ppt.shape))
    # del ke_init, cond, ke_min
    et_init = (ks * kcb + ke) * etrs
    eta = np.maximum(et_init, np.zeros(ppt.shape))
    # print "ks {a}, kcb {b}, ke {c}".format(a=ks, b=kcb, c=ke)
    # print "drew {a}, de {b}, dr {c}, pDrew {d}, pDe {e}, pDr {f}".format(a=drew, b=de, c=dr, d=pDrew,e=pDe, f=pDr)
    # print "etrs {d}, eta {a}, dp_r {b}, ro {c}".format(a=eta, b=dp_r, c=ro, d=etrs)
    evap_init = ke * etrs
    evap_min = np.maximum(evap_init, np.zeros(ppt.shape))
    evap = np.minimum(evap_min, kc_max)
    # del evap_init, evap_min

    # Load temp, find swe, melt, and precipitation, load Ksat
    # Use SNOTEL data for precip and temps:
    # df_snow : (stel_date, stel_snow, stel_precip, stel_tobs, stel_tmax, stel_tmin, stel_tavg, stel_snwd)
    if dday == end:
        ppt_tom = np.zeros(ppt.shape, dtype='int64')
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

    del watr, deps

    dr = np.minimum((pDr - rain - mlt + ro + eta + dp_r), taw)
    dr = np.maximum(dr, np.zeros(ppt.shape))
    # dr = (pDr + dr_2) / 2.
    de = np.minimum(pDe + (evap / few) - rain - mlt, tew)
    de = np.maximum(de, np.zeros(ppt.shape))
    drew = np.minimum(pDrew - ((1 - fs1) * (rain - ro) + fs1), rew)  # * (rain_tom - ro_tom)
    drew = np.maximum(drew, np.zeros(ppt.shape))


# Create cumulative rasters to show net over entire run

    infil = infil + dp_r
    infil = np.maximum(infil, zeros)

    et = et + eta
    et = np.maximum(et, zeros)

    precip = precip + rain + snow_fall
    precip = np.maximum(precip, zeros)

    runoff = runoff + ro
    runoff = np.maximum(runoff, zeros)

    snow_ras = swe + snow_fall - mlt
    snow_ras = np.maximum(snow_ras, zeros)

# Check MASS BALANCE for the love of WATER!!!
    mass = snow_fall + rain - ro - eta - dp_r


outputs = [infil, et, precip, runoff, snow_ras, mass, dr, de, drew]
output_names = ['infil', 'et', 'precip', 'runoff', 'snow_ras', 'mass', 'dr', 'de', 'drew']
x = 0
for element in outputs:
    name = output_names[x]
    print "Saving {a}".format(a=name)
    driver = gdal.GetDriverByName('GTiff')
    filename = 'C:\\Recharge_GIS\\Array_Results\\{a}.tiff'.format(a=name)
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



