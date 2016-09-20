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


from numpy import zeros, isnan, count_nonzero, where, ones
import os
from datetime import datetime
from pandas import DataFrame, date_range, MultiIndex


from recharge.raster_tools import convert_raster_to_array
from recharge.point_extract_utility import get_static_inputs_at_point


def set_constants(soil_evap_depth=40, et_depletion_factor=0.4,
                  min_basal_crop_coef=0.15,
                  max_basal_crop_coef=1.05, snow_alpha=0.2, snow_beta=11.0,
                  max_ke=1.1, min_snow_albedo=0.45, max_snow_albedo=0.90):

    monsoon_dates = datetime(1900, 7, 1), datetime(1900, 9, 1)
    start_monsoon, end_monsoon = monsoon_dates[0], monsoon_dates[1]

    dictionary = dict(s_mon=start_monsoon, e_mon=end_monsoon, ze=soil_evap_depth, p=et_depletion_factor,
                      kc_min=min_basal_crop_coef,
                      kc_max=max_basal_crop_coef, snow_alpha=snow_alpha, snow_beta=snow_beta,
                      ke_max=max_ke, a_min=min_snow_albedo, a_max=max_snow_albedo)

    print 'constants dict: {}'.format(dictionary)

    return dictionary


def initialize_master_dict(shape):
    """create an empty dict that will carry ETRM-derived values day to day
    :param shape: shape of the model domain, (1, 1) or raster.shape
    """

    master = dict()

    master['pkcb'] = zeros(shape)
    master['infil'] = zeros(shape)
    master['kcb'] = zeros(shape)
    master['dp_r'] = zeros(shape)
    master['tot_snow'] = zeros(shape)
    master['tot_rain'] = zeros(shape)
    master['tot_melt'] = zeros(shape)
    master['tot_mass'] = zeros(shape)
    master['tot_infil'] = zeros(shape)
    master['tot_ref_et'] = zeros(shape)
    master['tot_eta'] = zeros(shape)
    master['tot_precip'] = zeros(shape)
    master['tot_ro'] = zeros(shape)
    master['tot_swe'] = zeros(shape)

    return master


def initialize_static_dict(inputs_path, point_dict=None):

    """# build list of static rasters from current use file
    # convert rasters to arrays
    # give variable names to each raster"""

    print 'static inputs path: {}'.format(inputs_path)
    static_keys = ['bed_ksat', 'plant_height', 'quat_deposits', 'root_z', 'soil_ksat', 'taw', 'tew']

    statics = [filename for filename in os.listdir(inputs_path) if filename.endswith('.tif')]
    static_dict = {}
    statics = sorted(statics, key=lambda s: s.lower())

    if point_dict:
        for key, val in point_dict.iteritems():
            coords = val['Coords']
            sub = {}
            for filename, value in zip(statics, static_keys):
                full_path = os.path.join(inputs_path, filename)
                sub[value] = get_static_inputs_at_point(coords, full_path)
            static_dict[key] = sub

    else:
        static_arrays = [convert_raster_to_array(inputs_path, filename) for filename in statics]
        for key, data in zip(static_keys, static_arrays):
            static_dict[key] = data

        for key, data in zip(static_keys, static_arrays):
            if key == 'tew':
                min_val = 15
                # print '{} has {} values of less than {}'.format(key, count_nonzero(where(data <= min_val,
                #                                                                    ones(data.shape),
                #                                                                    zeros(data.shape))), min_val)
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

            if key == 'quat_deposits':
                min_val = 250
                # print '{} has {} cells'.format(key, count_nonzero(where(data > 0.0,
                #                                                         ones(data.shape),
                #                                                         zeros(data.shape))), min_val)

                static_dict['taw'] = where(data > 0.0, ones(data.shape) * min_val, static_dict['taw'])

            static_dict[key] = data

    return static_dict


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
                sub[value] = get_static_inputs_at_point(coords, full_path)

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
                             'last_day': {}}
        # emulated initialize_tab_dict here
        for super_key, super_val in raster_track_dict.iteritems():
            sub = {}
            for key in tracked_outputs:
                sub[key] = _zeros
            raster_track_dict[super_key] = sub
        return raster_track_dict


def initialize_tabular_dict(shapes, outputs, date_range_):

        folders = os.listdir(shapes)
        units = ['AF', 'CBM']
        outputs_arr = [[output, output] for output in outputs]
        outputs_arr = [val for sublist in outputs_arr for val in sublist]
        units_arr = units * len(outputs)
        arrays = [outputs_arr, units_arr]
        cols = MultiIndex.from_arrays(arrays)
        ind = date_range(date_range_[0], date_range_[1], freq='D')

        tab_dict = {}
        for f in folders:
            region_type, toss = f.split('_Poly')
            d = {}
            files = os.listdir(os.path.join(shapes, f))
            shapes = [shape.strip('.shp') for shape in files if shape.endswith('.shp')]
            print 'shapes: {}'.format(shapes)
            for element in shapes:
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

if __name__ == '__main__':
    pass

# ============= EOF =============================================
