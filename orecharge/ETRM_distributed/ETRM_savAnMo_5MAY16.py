# ETRM - Evapotranspiration and Recharge Model, DISTRIBUTED
# David Ketchum, April 2016
import datetime
import calendar
import os
from dateutil import rrule
from osgeo import gdal
import numpy as np

np.set_printoptions(linewidth=700, precision=2)

startTime = datetime.datetime.now()
print startTime


def cells(array):
    window = array[480:510, 940:970]
    return window


def count_elements(array):
    unique, counts = np.unique(array, return_counts=True)
    count_dict = dict(zip(unique, counts))
    return count_dict

# Set start datetime object
start, end = datetime.datetime(2000, 1, 1), datetime.datetime(2000, 12, 31)
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

raster = 'aws_mod_4_21_10_0'
aws_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
taw = np.array(aws_open.GetRasterBand(1).ReadAsArray(), dtype=float)
dataset = aws_open
# taw = aws[480:520, 940:980]
# initialize ones and zeros arrays for use later
taw = np.maximum(taw, min_val)
taw = np.where(qDeps == 1.0, ones * 300.0, taw)
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

raster = 'Soil_Ksat_15apr'  # convert from micrometer/sec to mm/day
ksat_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
ksat = np.array(ksat_open.GetRasterBand(1).ReadAsArray(), dtype=float) * 86.4
# ksat = ksat[480:520, 940:980]
ksat1 = np.maximum(ksat, min_val)
ksat_open = []

raster = 'tew_250_15apr'
tew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
tew = np.array(tew_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# tew = tew[480:520, 940:980]
tew = np.maximum(tew, min_val)
tew_open = []

path = 'C:\\Recharge_GIS\\Array_Results\\initialize'
raster = 'de_4_19_23_11'
de_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
de1 = np.array(de_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# de = de[480:520, 940:980]
de1 = np.where(np.isnan(de1) == True, np.zeros(taw.shape), de1)
de_open = []

raster = 'dr_4_19_23_11'
dr_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
dr1 = np.array(dr_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# dr = dr[480:520, 940:980]
dr1 = np.where(np.isnan(dr1) == True, np.zeros(taw.shape), dr1)
dr_open = []

raster = 'drew_4_19_23_11'
drew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
drew1 = np.array(drew_open.GetRasterBand(1).ReadAsArray(), dtype=float)
# dr = dr[480:520, 940:980]
drew1 = np.where(np.isnan(drew1) == True, np.zeros(taw.shape), drew1)
drew_open = []

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
pltKr = []
pltMass = []

p_mo_Et = np.zeros(taw.shape)
p_mo_Precip = np.zeros(taw.shape)
p_mo_Ro = np.zeros(taw.shape)
p_mo_deps = dr1 + de1 + drew1
p_mo_Infil = np.zeros(taw.shape)
p_mo_Etrs = np.zeros(taw.shape)

p_yr_Et = np.zeros(taw.shape)
p_yr_Precip = np.zeros(taw.shape)
p_yr_Ro = np.zeros(taw.shape)
p_yr_deps = dr1 + de1 + drew1
p_yr_Infil = np.zeros(taw.shape)
p_yr_Etrs = np.zeros(taw.shape)

dp_r_mo = []
ref_et_mo = []
et_mo = []
precip_mo = []
runoff_mo = []
snow_ras_mo = []
delta_s_mo = []

dp_r_yr = []
ref_et_yr = []
et_yr = []
precip_yr = []
runoff_yr = []
snow_ras_yr = []
tot_snow = np.zeros(taw.shape)
delta_s_yr = []

# Define user-controlled constants, these are constants to start with day one, replace
# with spin-up data when multiple years are covered
ze = np.ones(taw.shape) * 40
p = np.ones(taw.shape) * 0.4
kc_min = np.ones(taw.shape) * 0.15
infil = np.zeros(taw.shape)
precip = np.zeros(taw.shape)
ref_et = np.zeros(taw.shape)
kr = np.zeros(taw.shape)
ks = np.zeros(taw.shape)
pKcb = np.zeros(taw.shape)
pKr = np.zeros(taw.shape)
pKs = np.zeros(taw.shape)
et = np.zeros(taw.shape)
runoff = np.zeros(taw.shape)
ppt_tom = np.zeros(taw.shape)
fb = np.ones(taw.shape) * 0.25
swe = np.zeros(taw.shape)
ke_max = 1.0
tot_mass = np.zeros(taw.shape)
cum_mass = np.zeros(taw.shape)
tot_transp = np.zeros(taw.shape)
tot_evap = np.zeros(taw.shape)
a_min = np.ones(taw.shape) * 0.45
a_max = np.ones(taw.shape) * 0.90
a = a_max
pA = a_min

for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
    if dday != start:
        pKcb = kcb
    doy = dday.timetuple().tm_yday
    print "Time : {a} day {b}_{c}".format(a=str(datetime.datetime.now() - startTime), b=doy, c=dday.year)
    #  NDVI to kcb
    if dday.year == 2000:
        path = 'F:\\ETRM_Inputs\\NDVI\\NDVI_std_all'
        ras_list = os.listdir('F:\\ETRM_Inputs\\NDVI\\NDVI_std_all')
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
        path = 'F:\\ETRM_Inputs\\NDVI\\NDVI_std_all'
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
        path = 'F:\\ETRM_Inputs\\NDVI\\NDVI_std_all'
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
    kcb = np.where(np.isnan(kcb) == True, pKcb, kcb)

    #  PRISM to ppt
    #  Remember to use the new PRISM!
    path = 'F:\\ETRM_Inputs\\PRISM\Precip\\800m_std_all'
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
    ppt_open = []
    ppt_tom_open = []
    # ppt = ppt[480:520, 940:980]
    # ppt_tom = ppt_tom[480:520, 940:980]
    ppt = np.maximum(ppt, np.zeros(taw.shape))
    ppt_tom = np.maximum(ppt_tom, np.zeros(taw.shape))

    #  PRISM to mintemp, maxtemp, temp
    if dday.year in [2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013]:
        path = 'F:\\ETRM_Inputs\\PRISM\\Temp\\Minimum_standard'
        raster = '{a}\\cai_tmin_us_us_30s_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                                c=str(dday.month).rjust(2, '0'),
                                                                d=str(dday.day).rjust(2, '0'))
        minTemp_open = gdal.Open(raster)
        min_temp = np.array(minTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
        minTemp_open = []
    else:
        path = 'F:\\ETRM_Inputs\\PRISM\\Temp\\Minimum_standard'
        raster = '{a}\\TempMin_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                               c=str(dday.month).rjust(2, '0'),
                                                               d=str(dday.day).rjust(2, '0'))
        minTemp_open = gdal.Open(raster)
        min_temp = np.array(minTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
        minTemp_open = []
    path = 'F:\\ETRM_Inputs\\PRISM\\Temp\\Maximum_standard'
    raster = '{a}\\TempMax_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                           c=str(dday.month).rjust(2, '0'),
                                                           d=str(dday.day).rjust(2, '0'))
    maxTemp_open = gdal.Open(raster)
    max_temp = np.array(maxTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    maxTemp_open = []

    temp = (min_temp + max_temp)/2

    # min_temp = min_temp[480:520, 940:980]
    # max_temp = max_temp[480:520, 940:980]
    # temp = temp[480:520, 940:980]

    #  PM data to etrs
    path = 'F:\\ETRM_Inputs\\PM_RAD'
    raster = '{a}\\PM{d}\\PM_NM_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
    etrs_open = gdal.Open(raster)
    etrs = np.array(etrs_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    etrs_open = []
    # etrs = etrs[480:520, 940:980]
    etrs = np.maximum(etrs, min_val)

    # Net Longwave  Radiation Data is with the PM data
    path = 'F:\\ETRM_Inputs\\PM_RAD'
    raster = '{a}\\PM{d}\\RLIN_NM_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
    rlin_open = gdal.Open(raster)
    rlin = np.array(rlin_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    rlin_open = []
    # rlin = rlin[480:520, 940:980]
    rlin = np.maximum(rlin, np.zeros(taw.shape))

    # Net Shortwave Radiation Data
    path = 'F:\\ETRM_Inputs\\PM_RAD'
    raster = '{a}\\rad{d}\\RTOT_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
    rg_open = gdal.Open(raster)
    rg = np.array(rg_open.GetRasterBand(1).ReadAsArray(), dtype=float)
    rg_open = []
    # rg = rg[480:520, 940:980]
    rg = np.maximum(rg, np.zeros(taw.shape))

    #  ETRM Daily Run  #######################################################################

    day_of_year = dday.timetuple().tm_yday
    if dday == start:
        #  Total evaporable water is depth of water in the evaporable
        #  soil layer, i.e., the water available to both stage 1 and 2 evaporation

        rew = np.minimum((2+(tew/3.)), 0.8 * tew)
        # del tew1, tew2

        # you should have all these from previous model runs
        pDr = dr1
        pDe = de1
        pDrew = drew1
        dr = dr1
        de = de1
        drew = drew1

    if sMon.timetuple().tm_yday <= dday.timetuple().tm_yday <= eMon.timetuple().tm_yday:
        ksat = ksat1 * 2/24.
    else:
        ksat = ksat1 * 6/24.

    kc_max_1 = kcb + 0.0001
    min_val = np.ones(taw.shape) * 0.0001
    kc_max = np.maximum(min_val, kc_max_1)
    # del kc_max_1

    nlcd_plt_hgt = nlcd_plt_hgt * 0.5 + 1
    numr = np.maximum(kcb - kc_min, min_val * 10)
    denom = np.maximum((kc_max - kc_min), min_val * 10)
    fcov_ref = (numr / denom) ** nlcd_plt_hgt
    fcov_min = np.minimum(fcov_ref, np.ones(taw.shape))
    fcov = np.maximum(fcov_min, min_val * 10)
    few = np.maximum(1 - fcov, 0.01)   # exposed ground
    # del numr, denom, fcov_ref, fcov_min

    pKr = kr
    kr = np.minimum(((tew - de) / (tew - rew)), np.ones(taw.shape))
    kr = np.where(np.isnan(kr) == True, pKr, kr)

    pKs = ks
    ks_ref = np.where(((taw - pDr) / (0.6 * taw)) < np.zeros(taw.shape), np.ones(taw.shape) * 0.001,
                      ((taw - pDr) / (0.6 * taw)))
    ks_ref = np.where(np.isnan(ks) == True, pKs, ks_ref)
    ks = np.minimum(ks_ref, np.ones(taw.shape))

    # Ke evaporation reduction coefficient; stage 1 evaporation
    fsa = np.where(np.isnan((rew - drew) / (ke_max * etrs)) == True, np.zeros(taw.shape), (rew - drew) / (ke_max * etrs))
    fsb = np.minimum(fsa, np.ones(taw.shape))
    fs1 = np.maximum(fsb, np.zeros(taw.shape))
    ke = np.where(drew < rew, np.minimum((fs1 + (1 - fs1) * kr) * (kc_max - ks * kcb), few * kc_max), np.zeros(taw.shape))

    transp = (ks * kcb) * etrs
    et_init = (ks * kcb + ke) * etrs
    eta = np.maximum(et_init, np.zeros(taw.shape))
    evap_init = ke * etrs
    evap_min = np.maximum(evap_init, np.zeros(taw.shape))
    evap = np.minimum(evap_min, kc_max)

    # Load temp, find swe, melt, and precipitation, load Ksat
    # Use SNOTEL data for precip and temps:
    # df_snow : (stel_date, stel_snow, stel_precip, stel_tobs, stel_tmax, stel_tmin, stel_tavg, stel_snwd)

    snow_fall = np.where(temp <= 0.0, ppt, np.zeros(taw.shape))
    rain = np.where(temp >= 0.0, ppt, np.zeros(taw.shape))

    pA = a
    a = np.where(snow_fall > 3.0, np.ones(taw.shape) * a_max, a)
    a = np.where(snow_fall <= 3.0, a_min + (pA - a_min) * np.exp(-0.12), a)
    a = np.where(snow_fall == 0.0, a_min + (pA - a_min) * np.exp(-0.05), a)
    a = np.where(a < a_min, a_min, a)

    swe += snow_fall

    mlt_init = np.maximum(((1 - a) * rg * 0.2) + (temp - 1.8) * 11.0, np.zeros(taw.shape))  # use calibrate coefficients
    mlt = np.minimum(swe, mlt_init)

    swe -= mlt

    # Find depletions
    pDr = dr
    pDe = de
    pDrew = drew
    watr = rain + mlt
    deps = dr + de + drew
    # print cells(watr)
    # print cells(deps)

    ro = np.zeros(taw.shape)
    ro = np.where(watr > ksat + deps, watr - ksat - deps, ro)
    ro = np.maximum(ro, np.zeros(taw.shape))
    # print cells(ro)

    dp_r = np.zeros(taw.shape)
    id1 = np.where(watr > deps, np.ones(taw.shape), np.zeros(taw.shape))
    id2 = np.where(ksat > watr - deps, np.ones(taw.shape), np.zeros(taw.shape))
    dp_r = np.where(id1 + id2 > 1.99, np.maximum(watr - deps, np.zeros(taw.shape)), dp_r)
    # print cells(dp_r)
    dp_r = np.where(watr > ksat + deps, ksat, dp_r)
    dp_r = np.maximum(dp_r, np.zeros(taw.shape))
    # print cells(dp_r)

    drew_1 = np.minimum((pDrew + ro + (evap - (rain + mlt))), rew)
    drew = np.maximum(drew_1, np.zeros(taw.shape))
    diff = np.maximum(pDrew - drew, np.zeros(taw.shape))

    de_1 = np.minimum((pDe + (evap - (rain + mlt - diff))), tew)
    de = np.maximum(de_1, np.zeros(taw.shape))
    diff = np.maximum(((pDrew - drew) + (pDe - de)), np.zeros(taw.shape))

    dr_1 = np.minimum((pDr + ((transp + dp_r) - (rain + mlt - diff))), taw)
    dr = np.maximum(dr_1, np.zeros(taw.shape))
    # dr = (pDr + dr_2) / 2.

    # Create cumulative rasters to show net over entire run

    infil += dp_r
    infil = np.maximum(infil, np.zeros(taw.shape))

    prev_et = et
    ref_et += etrs
    et = et + evap + transp
    et_ind = et / ref_et
    et = np.where(np.isnan(et) == True, prev_et, et)
    et = np.where(et > ref_et, ref_et / 2., et)
    et = np.maximum(et, np.ones(taw.shape) * 0.001)

    precip = precip + rain + snow_fall
    precip = np.maximum(precip, np.zeros(taw.shape))

    runoff += ro
    runoff = np.maximum(runoff, np.zeros(taw.shape))

    snow_ras = swe + snow_fall - mlt
    snow_ras = np.maximum(snow_ras, np.zeros(taw.shape))

    tot_snow += snow_fall

    # use monthrange check to find last day of each month and save rasters
    mo_date = calendar.monthrange(dday.year, dday.month)
    if dday.day == mo_date[1]:
            infil_mo = infil - p_mo_Infil
            infil_mo = np.maximum(infil_mo, np.zeros(taw.shape))

            ref_et_mo = etrs - p_mo_Etrs
            et_mo = et - p_mo_Et
            et_mo = np.where(np.isnan(et_mo) == True, p_mo_Et, et_mo)
            et_mo = np.where(et_mo > ref_et, ref_et / 2., et_mo)
            et_mo = np.maximum(et_mo, np.ones(taw.shape) * 0.001)

            precip_mo = precip - p_mo_Precip
            precip_mo = np.maximum(precip_mo, np.zeros(taw.shape))

            runoff_mo = ro - p_mo_Ro
            runoff_mo = np.maximum(runoff_mo, np.zeros(taw.shape))

            snow_ras_mo = swe
            snow_ras_mo = np.maximum(snow_ras_mo, np.zeros(taw.shape))

            mo_deps = drew + de + dr
            delta_s_mo = p_mo_deps - mo_deps

            outputs = [infil_mo, et_mo, precip_mo, runoff_mo, snow_ras_mo, delta_s_mo, mo_deps]
            output_names = ['infil', 'et', 'precip', 'runoff', 'snow_ras', 'delta_s_mo', 'mo_deps']

            x = 0
            now = datetime.datetime.now()
            tag = 'saved_on_{}_{}'.format(now.month, now.day)
            for element in outputs:
                name = output_names[x]
                print "Saving {a}_{b}_{c}".format(a=name, b=dday.month, c=dday.year)
                driver = gdal.GetDriverByName('GTiff')
                filename = 'F:\\ETRM_Results\\Monthly_results\\{a}_{b}_{c}_23MAY.tif'.format(a=name, b=dday.month,
                                                                                             c=dday.year)
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

            p_mo_Et = et
            p_mo_Precip = precip
            p_mo_Ro = ro
            p_mo_deps = mo_deps
            p_mo_Infil = infil
            p_mo_Etrs = etrs

    if dday.day == 31 and dday.month == 12:
            infil_yr = infil - p_yr_Infil
            infil_yr = np.maximum(infil_yr, np.zeros(taw.shape))

            ref_et_yr = etrs - p_yr_Etrs
            et_yr = et - p_yr_Et
            et_yr = np.where(np.isnan(et_yr) == True, p_yr_Et, et_yr)
            et_yr = np.where(et_yr > ref_et, ref_et / 2., et_yr)
            et_yr = np.maximum(et_yr, np.ones(taw.shape) * 0.001)

            precip_yr = precip - p_yr_Precip
            precip_yr = np.maximum(precip_yr, np.zeros(taw.shape))

            runoff_yr = ro - p_yr_Ro
            runoff_yr = np.maximum(runoff_yr, np.zeros(taw.shape))

            snow_ras_yr = swe
            snow_ras_yr = np.maximum(snow_ras_yr, np.zeros(taw.shape))

            yr_deps = drew + de + dr
            delta_s_yr = p_yr_deps - yr_deps

            outputs = [infil_yr, et_yr, precip_yr, runoff_yr, snow_ras_yr, delta_s_yr, yr_deps]
            output_names = ['infil', 'et', 'precip', 'runoff', 'snow_ras', 'delta_s_yr', 'yr_deps']

            x = 0
            for element in outputs:
                name = output_names[x]
                print "Saving {a}_{c}".format(a=name, c=dday.year)
                driver = gdal.GetDriverByName('GTiff')
                filename = 'F:\\ETRM_Results\\Annual_results\\{a}_{c}_23MAY.tif'.format(a=name, c=dday.year)
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

            p_yr_Et = et
            p_yr_Precip = precip
            p_yr_Ro = ro
            p_mo_deps = yr_deps
            p_yr_Infil = infil
            p_yr_Etrs = etrs

    # Check MASS BALANCE for the love of WATER!!!
    mass = rain + mlt - (ro + transp + evap + dp_r + ((pDr - dr) + (pDe - de) + (pDrew - drew)))
    tot_mass += abs(mass)
    cum_mass += mass
    print mass[480, 940]
    print tot_mass[480, 940]

    pltDay.append(dday)
    pltRain.append(rain[480, 940])
    pltEta.append(eta[480, 940])
    pltSnow_fall.append(snow_fall[480, 940])
    pltRo.append(ro[480, 940])
    pltDr.append(dr[480, 940])
    pltDe.append(de[480, 940])
    pltDrew.append(drew[480, 940])
    pltTemp.append(temp[480, 940])
    pltDp_r.append(dp_r[480, 940])
    pltKs.append(ks[480, 940])
    pltPdr.append(pDr[480, 940])
    pltEtrs.append(etrs[480, 940])
    pltKcb.append(kcb[480, 940])
    pltPpt.append(ppt[480, 940])
    pltKe.append(ke[480, 940])
    pltKr.append(kr[480, 940])
    pltMlt.append(mlt[480, 940])
    pltSwe.append(swe[480, 940])
    pltTempM.append(max_temp[480, 940])
    pltFs1.append(fs1[480, 940])
    pltMass.append(mass[480, 940])


# fdata = np.column_stack((pltSnow_fall, pltRain, pltMlt, pltEta, pltRo, pltDp_r, pltDr, pltDe, pltDrew, pltMass))
# np.savetxt('C:\\Recharge_GIS\\Array_Results\\array_records\\10apr16_ETRM_mass.csv',
#     fdata, fmt=['%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f'],
#            delimiter=',')
#
# outputs = [infil, et, precip, runoff, snow_ras, tot_mass, cum_mass, dr, de, drew, tot_snow, taw, tew, rew]
# output_names = ['infil', 'et', 'precip', 'runoff', 'snow_ras', 'tot_mass', 'cum_mass', 'dr', 'de', 'drew', 'tot_snow',
#                 'taw', 'tew', 'rew']
#
# # outputs = [taw, qDeps, nlcd_plt_hgt]
# # output_names = ['taw', 'qDeps', 'nlcd_plt_hgt']
# x = 0
# now = datetime.datetime.now()
# tag = '{}_{}_{}_{}'.format(now.month, now.day, now.hour, now.minute)
# for element in outputs:
#     name = output_names[x]
#     print "Saving {a}".format(a=name)
#     driver = gdal.GetDriverByName('GTiff')
#     filename = 'F:\\ETRM_14yr_results\\{a}_23may.tif'.format(a=name)
#     cols = dataset.RasterXSize
#     rows = dataset.RasterYSize
#     bands = dataset.RasterCount
#     band = dataset.GetRasterBand(1)
#     datatype = band.DataType
#     outDataset = driver.Create(filename, cols, rows, bands, datatype)
#     geoTransform = dataset.GetGeoTransform()
#     outDataset.SetGeoTransform(geoTransform)
#     proj = dataset.GetProjection()
#     outDataset.SetProjection(proj)
#     outBand = outDataset.GetRasterBand(1)
#     outBand.WriteArray(element, 0, 0)
#     x += 1



