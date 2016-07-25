# ===============================================================================
# Copyright 2016 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
"""
The purpose of this module is to calculate recharge over a defined geographic area.

this module provides (1) function -- run_distributed_ETRM.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""
from datetime import datetime
from calendar import monthrange
import os
from dateutil import rrule
from osgeo import gdal
from numpy import set_printoptions, ones, zeros, array, maximum, minimum, where, exp, isnan
from recharge.raster_manager import ManageRasters
from recharge.etrm_processes import Processes
from raster_finder import get_ndvi, get_prism, get_penman
from user_constants import set_constants
from master_dict import initialize_master_dict

set_printoptions(linewidth=700, precision=2)

# Set start datetime object
start, end = datetime(2000, 1, 1), datetime(2000, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime(start.year, 11, 1), datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime(start.year, 6, 1), datetime(start.year, 10, 1)

tracker_coords = [480, 940]


def run_distributed_etrm(start_date, end_date, extent):

    start_time = datetime.now()
    print start_time

    def cells(raster):
        window = array[480:485, 940:945]
        return window

    def count_elements(raster):
        from numpy import unique
        unique, counts = unique(array, return_counts=True)
        count_dict = dict(zip(unique, counts))
        return count_dict
    
    def print_check(variable, category):
        print 'raster is {}'.format(category)
        print 'example values from data: {}'.format(cells(variable))
        print ''

    # instantiate the rasters classes
    make_array = ManageRasters()

    # build list of static rasters from current use file
    statics = [filename for filename in os.listdir(static_inputs_path) if filename.endswith('.tif')]
    statics = sorted(statics, key=lambda s: s.lower())
    # convert rasters to arrays
    static_arrays = [make_array.convert_raster_to_array(static_inputs_path, filename) for filename in statics]
    # give variable names to each raster
    static_keys = ['bedksat', 'plant_height', 'quat_deposits', 'root_z', 'soilksat', 'taw', 'tew']
    static = {}
    for key, data in zip(static_keys, static_arrays):
        print_check(key, 'static')
        static.update({key: data})

    # read in initial soil moisture conditions from spin up, put in dict
    initial_cond = [filename for filename in os.listdir(initial_conditions_path) if filename.endswith('.tif')]
    initial_cond.sort()
    initial_cond_arrays = [make_array.convert_raster_to_array(static_inputs_path, filename) for filename in statics]
    initial_cond_keys = ['de', 'dr', 'drew']
    initial_cond_dict = {}
    for key, data in zip(initial_cond_keys, initial_cond_arrays):
        print_check(key, 'initial conditions')
        initial_cond_dict.update({key: data})

    # Create indices to plot point time series, these are empty lists that will
    # be filled as the simulation progresses
    tracker = {}
    tracker_keys = ['rain', 'eta', 'snowfall', 'runoff', 'dr', 'pdr', 'de', 'pde', 'drew',
                    'pdrew', 'temp', 'max_temp', 'recharge', 'ks', 'pks', 'etrs', 'kcb', 'ke', 'pke', 'melt',
                    'swe', 'fs1', 'precip', 'kr', 'pkr', 'mass']
    for key in tracker_keys:
        tracker.update({key: []})

    # figure out what to do with previous month empty rasters
    shape = static['taw'].shape
    ones_shaped = ones(shape)
    zeros_shaped = zeros(shape)
    p_mo_Et = zeros_shaped

    # figure out what to do with monthly and annual updates
    snow_ras_yr = []
    # what's this?
    tot_snow = zeros_shaped
    delta_s_yr = []

    # Define user-controlled constants, these are constants to start with day one, replace
    # with spin-up data when multiple years are covered
    constants = set_constants(soil_evap_depth=40, et_depletion_factor=0.4, min_basal_crop_coef=0.15,
                              max_ke=1.0, min_snow_albedo=0.45, max_snow_albedo=0.90)

    empty_array_list = ['albedo', 'de', 'dp_r', 'dr', 'drew', 'eta', 'etrs', 'evap', 'fs1', 'infil', 'kcb',
                        'kr', 'ks', 'max_temp', 'min_temp', 'pde', 'pdr', 'pdrew', 'pkr', 'pks', 'ppt',
                        'precip', 'rg', 'runoff', 'swe', 'temp', 'transp']

    master = initialize_master_dict(empty_array_list, shape)

    process = Processes(master, static, constants, shape)

    for dday in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
        print "Time : {a} day {b}_{c}".format(a=str(datetime.datetime.now() - start_time),
                                              b=dday.timetuple().tm_yday, c=dday.year)

        if dday != start_date:
            pkcb = master['kcb']
        master['kcb'] = get_ndvi(ndvi_path, pkcb, shape)
        print_check(master['kcb'], 'daily kcb')

        master['min_temp'] = get_prism(prism_path, dday, variable='min_temp')
        print_check(master['min_temp'], 'daily kcb')

        master['max_temp'] = get_prism(prism_path, dday, variable='max_temp')
        print_check(master['max_temp'], 'daily kcb')

        master['temp'] = (master['min_temp'] + master['max_temp']) / 2
        print_check(master['temp'], 'daily kcb')

        master['ppt'] = get_prism(prism_path, dday, variable='precip')
        print_check(master['ppt'], 'daily kcb')

        master['etrs'] = get_penman(penman_path, dday, variable='etrs')
        print_check(master['etrs'], 'daily kcb')

        master['rg'] = get_penman(penman_path, dday, variable='rg')
        print_check(master['rg'], 'daily kcb')
        # Net Longwave  Radiation Data is with the PM data
        # rlin = get_penman(penman_path, dday, variable='rlin')
        # print_check(rlin, 'daily kcb')
        # Net Shortwave Radiation Data


        #  ETRM Daily Run  #######################################################################

        # day_of_year = dday.timetuple().tm_yday
        if dday == start_date:
            #  Total evaporable water is depth of water in the evaporable
            #  soil layer, i.e., the water available to both stage 1 and 2 evaporation
            rew = minimum((2+(static['tew']/3.)), 0.8 * static['tew'])
            master.update({'rew': rew})
            #  should have all these from previous model runs
            master['pdr'] = initial_cond_dict['dr']
            master['pde'] = initial_cond_dict['de']
            master['pdrew'] = initial_cond_dict['drew']
            dr = master['pdr']
            de = master['pde']
            drew = master['pdrew']

        if sMon.timetuple().tm_yday <= dday.timetuple().tm_yday <= eMon.timetuple().tm_yday:
            ksat = static['ksat'] * 2/24.
        else:
            ksat = static['ksat'] * 6/24.

        process.do_dual_crop_coefficient()

        process.do_snowmelt()

        process.do_soil_moisture_depletion()

        process.do_soil_moisture_depletion()
        # Create cumulative rasters to show net over entire run


        # use monthrange check to find last day of each month and save rasters
        mo_date = monthrange(dday.year, dday.month)
        if dday.day == mo_date[1]:
                infil_mo = infil - p_mo_Infil
                infil_mo = maximum(infil_mo, zeros_shaped)

                ref_et_mo = etrs - p_mo_Etrs
                et_mo = et - p_mo_Et
                et_mo = where(isnan(et_mo) == True, p_mo_Et, et_mo)
                et_mo = where(et_mo > ref_et, ref_et / 2., et_mo)
                et_mo = maximum(et_mo, ones_shaped * 0.001)

                precip_mo = precip - p_mo_Precip
                precip_mo = maximum(precip_mo, zeros_shaped)

                runoff_mo = ro - p_mo_Ro
                runoff_mo = maximum(runoff_mo, zeros_shaped)

                snow_ras_mo = swe
                snow_ras_mo = maximum(snow_ras_mo, zeros_shaped)

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
                infil_yr = maximum(infil_yr, zeros_shaped)

                ref_et_yr = etrs - p_yr_Etrs
                et_yr = et - p_yr_Et
                et_yr = where(isnan(et_yr) == True, p_yr_Et, et_yr)
                et_yr = where(et_yr > ref_et, ref_et / 2., et_yr)
                et_yr = maximum(et_yr, ones_shaped * 0.001)

                precip_yr = precip - p_yr_Precip
                precip_yr = maximum(precip_yr, zeros_shaped)

                runoff_yr = ro - p_yr_Ro
                runoff_yr = maximum(runoff_yr, zeros_shaped)

                snow_ras_yr = swe
                snow_ras_yr = maximum(snow_ras_yr, zeros_shaped)

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
        mass = rain + mlt - (ro + transp + evap + dp_r + ((pdr - dr) + (pde - de) + (pdrew - drew)))
        tot_mass += abs(mass)
        cum_mass += mass
        print mass[480, 940]
        print tot_mass[480, 940]


    # fdata = column_stack((pltSnow_fall, pltRain, pltMlt, pltEta, pltRo, pltDp_r, pltDr, pltDe, pltDrew, pltMass))
    # savetxt('C:\\Recharge_GIS\\Array_Results\\array_records\\10apr16_ETRM_mass.csv',
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

    return None

if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    static_inputs_path = os.path.join(os.path.abspath(os.sep), 'Recharge_GIS', 'OSG_Data', 'current_use')
    initial_conditions_path = os.path.join(os.path.abspath(os.sep), 'Recharge_GIS', 'Array_Results', 'initialize')
    dynamic_inputs_path = os.path.join('F:\\', 'ETRM_Inputs')
    ndvi_path = os.path.join(dynamic_inputs_path, 'NDVI', 'NDVI_std_all')
    prism_path = os.path.join(dynamic_inputs_path, 'PRISM')
    penman_path = os.path.join(dynamic_inputs_path, 'PM_RAD')
    output_path = os.path.join('F', 'output')
    fig_save = os.path.join(home, 'Documents', 'ArcGIS', 'results', 'July_results')
    csv_save = os.path.join(home, 'Documents', 'ArcGIS', 'results', 'July_results')
    run_distributed_etrm(start, end, extent='NM')

# ============= EOF =============================================

