# ===============================================================================
# Copyright 2016 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance
# with the License.
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
The purpose of this module is to initialize empty etrm arrays before run.

returns dict with all rasters under keys of etrm variable names

dgketchum 24 JUL 2016
"""

from numpy import zeros, isnan, count_nonzero, where, ones, median
import os
from datetime import datetime
from pandas import DataFrame, date_range, MultiIndex
from osgeo import ogr

from recharge.raster_tools import convert_raster_to_array
from recharge.point_extract_utility import get_inputs_at_point


"""
kc_min is from ASCE pg 199 (0.1 to 0.15 given range, but say to use 0 or nearly 0 for natural settings)
kc_max is from ASCE pg 225 Eq 10.3b (1.05 to 1.3 given range)
et_depletion_factor ASCE pg 226 (0.3 to 0.7 given range) 0.5 common for ag crops
    can adjust p for ETc as eq on ASCE pg. 392
"""
def set_constants(soil_evap_depth=40, et_depletion_factor=0.4,
                  min_basal_crop_coef=0.01,
                  max_basal_crop_coef=1.05, snow_alpha=0.2, snow_beta=11.0,
                  max_ke=1.0, min_snow_albedo=0.45, max_snow_albedo=0.90):
    monsoon_dates = datetime(1900, 7, 1), datetime(1900, 10, 1)
    start_monsoon, end_monsoon = monsoon_dates[0], monsoon_dates[1]

    dictionary = dict(s_mon=start_monsoon, e_mon=end_monsoon, ze=soil_evap_depth, p=et_depletion_factor,
                      kc_min=min_basal_crop_coef,
                      kc_max=max_basal_crop_coef, snow_alpha=snow_alpha, snow_beta=snow_beta,
                      ke_max=max_ke, a_min=min_snow_albedo, a_max=max_snow_albedo)

    print 'constants dict: {}'.format(dictionary)

    return dictionary


def initialize_master_dict(shape=None):
    """create an empty dict that will carry ETRM-derived values day to day
    :param shape: shape of the model domain, (1, 1) or raster.shape
    """

    master = dict()
    if shape:  # distributed
        master['pkcb'] = zeros(shape)
        master['infil'] = zeros(shape)
        master['kcb'] = zeros(shape)
        master['tot_snow'] = zeros(shape)
        master['tot_rain'] = zeros(shape)
        master['tot_melt'] = zeros(shape)
        master['tot_mass'] = zeros(shape)
        master['tot_infil'] = zeros(shape)
        master['tot_etrs'] = zeros(shape)
        master['tot_eta'] = zeros(shape)
        master['tot_precip'] = zeros(shape)
        master['tot_ro'] = zeros(shape)
        master['tot_swe'] = zeros(shape)

    else:
        master['pkcb'] = 0.0
        master['infil'] = 0.0
        master['kcb'] = 0.0
        master['infil'] = 0.0
        master['tot_snow'] = 0.0
        master['tot_rain'] = 0.0
        master['tot_melt'] = 0.0
        master['tot_mass'] = 0.0
        master['tot_infil'] = 0.0
        master['tot_etrs'] = 0.0
        master['tot_eta'] = 0.0
        master['tot_precip'] = 0.0
        master['tot_ro'] = 0.0
        master['tot_swe'] = 0.0

    return master


def initialize_static_dict(inputs_path, point_dict=None):
    """# build list of static rasters from current use file
    # convert rasters to arrays
    # give variable names to each raster"""

    print 'static inputs path: {}'.format(inputs_path)

    # define NLCD land cover land use with a dict of classifications
    # the following is for reference:
    # land_classes = {'unclssified': 1, 'open_water': 11, 'developed_open': 21, 'developed_low': 22,
    #                 'developed_med': 23, 'developed_high': 24, 'barren': 31, 'deciduous': 41,
    #                 'evergreen': 42, 'mixed_forest': 43, 'shrub_scrub': 52, 'grassland': 71,
    #                 'pasture_hay': 81, 'cultivated': 82, 'woody_wetlands': 90}

    # this requires that the alphabetically sorted input rasters correspond to the order of the following inputs
    static_keys = ['bed_ksat', 'land_cover', 'plant_height', 'quat_deposits', 'rew', 'root_z', 'soil_ksat', 'taw',
                   'tew']
    statics = [filename for filename in os.listdir(inputs_path) if filename.endswith('.tif')]
    # print 'len static keys: {} len statics:{}'.format(len(static_keys), len(statics))

    stat_dct = {}
    statics = sorted(statics, key=lambda s: s.lower())

    if point_dict:
        # print 'point dict: {}'.format(point_dict)
        for key, val in point_dict.iteritems():
            try:
                coords = val['Coords']
            except KeyError:
                coords = point_dict['Coords']
            except TypeError:
                coords = point_dict['Coords']
            sub = {}
            for filename, value in zip(statics, static_keys):
                full_path = os.path.join(inputs_path, filename)
                sub[value] = get_inputs_at_point(coords, full_path)
            stat_dct[key] = sub
        print 'static dict {}'.format(stat_dct)

        for key, val in stat_dct.iteritems():
            print key, val
            if val['land_cover'] in [41, 42, 43]:
                print 'previous tew: {}'.format(val['tew'])
                val['tew'] = val['tew'] * 0.25 #I think the line below had a typo; Dan, 1/25/17
                #val['tew'] = val['tew'] * 0.25 + val['rew']
                print 'adjusted tew: {}'.format(val['tew'])
            elif val['land_cover'] == 52:
                val['tew'] = val['tew'] * 0.75  #I think the line below had a typo; Dan, 1/25/17
                #val['tew'] = val['tew'] * 0.75 + val['rew']

            if 320.0 < val['taw']:
                val['taw'] = 320.0
            if 50.0 > val['taw']:
                val['taw'] = 50.0
            if val['taw'] < val['tew'] + val['rew']:
                val['taw'] = val['tew'] + val['rew']
            # I think the plant height raster is in ft instead of meters; DC, 2/6/2017
            # and I don't think Allen's equation is a good way to get the fraction covered (f_cov) in a forest anyway.
            val['plant_height'] *= 0.3048

    else:
        static_arrays = [convert_raster_to_array(inputs_path, filename) for filename in statics]
        for key, data in zip(static_keys, static_arrays):
            stat_dct[key] = data

        for key, data in zip(static_keys, static_arrays):
            if key == 'tew':
                min_val = 10
                # print '{} has {} values of less than {}'.format(key, count_nonzero(where(data <= min_val,
                #                                                                    ones(data.shape),
                #                                                                    zeros(data.shape))), min_val)

                # apply a minimum tew
                data = where(data <= min_val, ones(data.shape) * min_val, data)

            if key == 'soil_ksat':
                min_val = 20
                # print '{} has {} values of less than {}'.format(key, count_nonzero(where(data <= min_val,
                #                                                                    ones(data.shape),
                #                                                                    zeros(data.shape))), min_val)
                data = where(data <= min_val, ones(data.shape) * min_val, data)

            if key == 'root_z':
                min_val = 100
                # print '{} has {} values of less than {}'.format(key, count_nonzero(where(data <= min_val,
                #                                                                    ones(data.shape),
                #                                                                    zeros(data.shape))), min_val)
                data = where(data < min_val, ones(data.shape) * min_val, data)

            #I think plant height is recorded in ft, when it should be m. Not sure if *= works on rasters.
            if key == 'plant_height':
                stat_dct['plant_height'] *= 0.3048

            # apply high TAW to unconsolidated Quaternary deposits
            if key == 'quat_deposits':
                min_val = 250
                # print '{} has {} cells'.format(key, count_nonzero(where(data > 0.0,
                #                                                         ones(data.shape),
                #                                                         zeros(data.shape))), min_val)

                stat_dct['taw'] = where(data > 0.0, ones(data.shape) * min_val, stat_dct['taw'])

            # apply bounds to TAW
            if key == 'taw':

                min_val = 50.0
                max_val = 320.0
                stat_dct['taw'] = where(data < min_val, ones(data.shape) * min_val, stat_dct['taw'])
                stat_dct['taw'] = where(data > max_val, ones(data.shape) * max_val, stat_dct['taw'])
                stat_dct['taw'] = where(stat_dct['taw'] < stat_dct['tew'] + stat_dct['rew'],
                                        stat_dct['tew'] + stat_dct['rew'],
                                        stat_dct['taw'])

                print '{} has {} cells below the minimum'.format(key, count_nonzero(where(data < min_val,
                                                                                          ones(data.shape),
                                                                                          zeros(data.shape))), min_val)
                print 'taw median: {}, mean {}, max {}, min {}'.format(median(stat_dct['taw']), stat_dct['taw'].mean(),
                                                                       stat_dct['taw'].max(),
                                                                       stat_dct['taw'].min())
            else:
                stat_dct[key] = data

        # apply tew adjustment
        _ones = ones(stat_dct['tew'].shape)
        stat_dct['tew'] = where(stat_dct['land_cover'] == 41, stat_dct['tew'] * 0.25 * _ones + stat_dct['rew'],
                                stat_dct['tew'])
        stat_dct['tew'] = where(stat_dct['land_cover'] == 42, stat_dct['tew'] * 0.25 * _ones + stat_dct['rew'],
                                stat_dct['tew'])
        stat_dct['tew'] = where(stat_dct['land_cover'] == 43, stat_dct['tew'] * 0.25 * _ones + stat_dct['rew'],
                                stat_dct['tew'])
        stat_dct['tew'] = where(stat_dct['land_cover'] == 52, stat_dct['tew'] * 0.75 * _ones + stat_dct['rew'],
                                stat_dct['tew'])

    # print 'static dict keys: \n {}'.format(static_dict.keys())
    return stat_dct


def initialize_initial_conditions_dict(initial_inputs_path, point_dict=None):
    # read in initial soil moisture conditions from spin up, put in dict

    initial_cond_keys = ['de', 'dr', 'drew']

    initial_cond = [filename for filename in os.listdir(initial_inputs_path) if filename.endswith('.tif')]
    initial_cond.sort()
    initial_cond_dict = {}
    if point_dict:
        for key, val in point_dict.iteritems():
            coords = val['Coords']
            sub = {}
            for filename, value in zip(initial_cond, initial_cond_keys):
                full_path = os.path.join(initial_inputs_path, filename)
                sub[value] = get_inputs_at_point(coords, full_path)

            initial_cond_dict[key] = sub

    else:
        initial_cond_arrays = [convert_raster_to_array(initial_inputs_path, filename) for filename in initial_cond]
        for key, data in zip(initial_cond_keys, initial_cond_arrays):
            data = where(isnan(data), zeros(data.shape), data)
            initial_cond_dict[key] = data

            print '{} has {} nan values'.format(key, count_nonzero(isnan(data)))
            print '{} has {} negative values'.format(key, count_nonzero(where(data < 0.0, ones(data.shape),
                                                                              zeros(data.shape))))

    return initial_cond_dict


def initialize_point_tracker(master):
    """ Create DataFrame to plot point time series, these are empty lists that will
     be filled as the simulation progresses"""

    tracker_keys = [key for key, val in master.iteritems()]
    tracker_keys.sort()

    tracker = DataFrame(columns=tracker_keys)

    return tracker


def initialize_raster_tracker(tracked_outputs, shape):
    _zeros = zeros(shape)
    raster_track_dict = {'current_year': {}, 'current_month': {}, 'current_day': {}, 'last_mo': {}, 'last_yr': {},
                         'yesterday': {}}
    # emulated initialize_tab_dict here
    for super_key, super_val in raster_track_dict.iteritems():
        sub = {}
        for key in tracked_outputs:
            sub[key] = _zeros
        raster_track_dict[super_key] = sub
    return raster_track_dict


def initialize_tabular_dict(shapes, outputs, date_range_, write_freq):
    folders = os.listdir(shapes)
    units = ['AF', 'CBM']
    outputs_arr = [[output, output] for output in outputs]
    outputs_arr = [val for sublist in outputs_arr for val in sublist]
    # if the write frequency of flux sums over shapes is daily, use normal master keys rather than 'tot_param'
    if write_freq == 'daily':
        outputs_arr = [out.replace('tot_', '') for out in outputs_arr]
    units_arr = units * len(outputs)
    arrays = [outputs_arr, units_arr]
    cols = MultiIndex.from_arrays(arrays)
    ind = date_range(date_range_[0], date_range_[1], freq='D')

    tab_dict = {}
    print 'folders: {}'.format(folders)
    for f in folders:
        print 'folder: {}'.format(f)
        region_type = f.replace('_Polygons', '')
        print 'region type: {}'.format(region_type)
        print 'polygon folder: {}'.format(shapes)
        d = {}
        files = os.listdir(os.path.join(shapes, f))
        polygons = [shape.strip('.shp') for shape in files if shape.endswith('.shp')]
        print 'polygons: {}'.format(polygons)
        for element in polygons:
            df = DataFrame(index=ind, columns=cols).fillna(0.0)
            print 'sub region : {}'.format(element)
            d[element] = df

        tab_dict[region_type] = d

    # print 'your tabular results dict:\n{}'.format(tab_dict)

    return tab_dict


def initialize_master_tracker(master):
    """ Create DataFrame to plot point time series, these are empty lists that will
     be filled as the simulation progresses"""

    tracker_keys = [key for key, val in master.iteritems()]
    tracker_keys.sort()

    tracker = DataFrame(columns=tracker_keys)

    return tracker


def cmb_sample_site_data(shape):
    ds = ogr.Open(shape)
    lyr = ds.GetLayer()
    cmb_dict = {}
    for feat in lyr:
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()
        sample = feat.GetField('Sample')
        print 'location of {}: {}, {}'.format(sample, mx, my)
        loc = feat.GetField('Location_D')
        elev = feat.GetField('Elevation_')
        infil_ind = feat.GetField('Rech_pct') / 100.
        cmb_dict[sample] = {'Name': loc, 'Elevation': elev, 'Infil_index': infil_ind,
                            'Coords': '{} {}'.format(int(mx), int(my))}

    return cmb_dict


if __name__ == '__main__':
    pass

# ============= EOF =============================================
