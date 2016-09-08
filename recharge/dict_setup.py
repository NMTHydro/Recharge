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

from numpy import zeros
import os
from datetime import datetime
from pandas import DataFrame


from recharge.raster_manager import Rasters
from recharge.point_extract_utility import get_static_inputs_at_point


def set_constants(soil_evap_depth=40, et_depletion_factor=0.4,
                  min_basal_crop_coef=0.15,
                  max_basal_crop_coef=1.05, snow_alpha=0.2, snow_beta=11.0,
                  max_ke=1.1, min_snow_albedo=0.45, max_snow_albedo=0.90):

    monsoon_dates = datetime(1900, 6, 1), datetime(1900, 10, 1)
    start_monsoon, end_monsoon = monsoon_dates[0], monsoon_dates[1]

    dictionary = dict(s_mon=start_monsoon, e_mon=end_monsoon, ze=soil_evap_depth, p=et_depletion_factor,
                      kc_min=min_basal_crop_coef,
                      kc_max=max_basal_crop_coef, snow_alpha=snow_alpha, snow_beta=snow_beta,
                      ke_max=max_ke, a_min=min_snow_albedo, a_max=max_snow_albedo)

    print 'constants dict: {}'.format(dictionary)

    return dictionary


def initialize_master_dict(zeros):
    """create an empty dict that will carry ETRM-derived values day to day"""

    master = dict()
    master['pkcb'] = zeros
    master['kcb'] = zeros
    master['dp_r'] = zeros
    master['tot_mass'] = zeros
    master['tot_mass'] = zeros
    master['tot_infil'] = zeros
    master['tot_ref_et'] = zeros
    master['infil'] = zeros
    master['tot_eta'] = zeros
    master['tot_precip'] = zeros
    master['tot_ro'] = zeros
    master['tot_swe'] = zeros

    return master


def initialize_static_dict(inputs_path, point_dict=None):

    """# build list of static rasters from current use file
    # convert rasters to arrays
    # give variable names to each raster"""

    static_keys = ['bed_ksat', 'plant_height', 'quat_deposits', 'root_z', 'soil_ksat', 'taw', 'tew']

    ras = Rasters()
    statics = [filename for filename in os.listdir(inputs_path) if filename.endswith('.tif')]
    static_dict = {}
    statics = sorted(statics, key=lambda s: s.lower())

    if point_dict:
        for key, val in point_dict.iteritems():
            coords = val['Coords']
            static_dict.update({key: {}})
            for filename, value in zip(statics, static_keys):
                full_path = os.path.join(inputs_path, filename)
                static_dict[key].update({value: get_static_inputs_at_point(coords, full_path)})

    else:
        static_arrays = [ras.convert_raster_to_array(inputs_path, filename, minimum_value=0.0) for filename in statics]
        for key, data in zip(static_keys, static_arrays):
            static_dict.update({key: data})

    return static_dict


def initialize_initial_conditions_dict(initial_inputs_path, point_dict=None):
    # read in initial soil moisture conditions from spin up, put in dict

    initial_cond_keys = ['de', 'dr', 'drew']

    ras = Rasters()
    initial_cond = [filename for filename in os.listdir(initial_inputs_path) if filename.endswith('.tif')]
    initial_cond.sort()
    initial_cond_dict = {}
    if point_dict:
        for key, val in point_dict.iteritems():
            coords = val['Coords']
            initial_cond_dict.update({key: {}})
            for filename, value in zip(initial_cond, initial_cond_keys):
                full_path = os.path.join(initial_inputs_path, filename)
                initial_cond_dict[key].update({value: get_static_inputs_at_point(coords, full_path)})

    else:
        initial_cond_arrays = [ras.convert_raster_to_array(initial_inputs_path, filename) for filename in initial_cond]
        for key, data in zip(initial_cond_keys, initial_cond_arrays):
            initial_cond_dict.update({key: data})
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
        raster_track_dict = {'output_an': {}, 'output_mo': {}, 'last_mo': {}, 'last_yr': {}}
        for super_key, super_val in raster_track_dict.iteritems():
            for key in tracked_outputs:
                raster_track_dict[super_key].update({key: _zeros})

        return raster_track_dict


def initialize_tabular_dict(shapes, outputs):

            folders = os.listdir(shapes)
            af_cbs_expand = [[x + '_[AF]', x + '_[cbm]'] for x in outputs]
            tabular_cols = [item for sublist in af_cbs_expand for item in sublist]
            tabular_output = DataFrame(columns=tabular_cols)
            tab_dict = {}
            for in_fold in folders:
                region_type = os.path.basename(in_fold).strip('_Polygons')
                tab_dict.update({region_type: {}})
                os.chdir(os.path.join(shapes, in_fold))
                for root, dirs, files in os.walk(".", topdown=False):
                    for element in files:
                        if element.endswith('.shp'):
                            sub_region = element.strip('.shp')
                            tab_dict[region_type].update({sub_region: tabular_output})

            print 'your tabular results dict:\n'.format(tab_dict)

            return tab_dict

# ============= EOF =============================================
