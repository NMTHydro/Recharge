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
The purpose of this module is to initialize empty etrm arrays before run.

returns dict with all rasters under keys of etrm variable names

dgketchum 24 JUL 2016
"""

from numpy import ones
import os


from recharge.raster_manager import ManageRasters
from recharge.point_extract_utility import get_static_inputs_at_point


def initialize_master_dict(list_of_variables):
    """create an empty dict that will carry ETRM-derived values day to day"""

    dictionary = {}
    for key in list_of_variables:
        dictionary.update({key: None})
    return dictionary


def initialize_static_dict(inputs_path, point_dict=None):

    """# build list of static rasters from current use file
    # convert rasters to arrays
    # give variable names to each raster"""

    static_keys = ['bed_ksat', 'plant_height', 'quat_deposits', 'root_z', 'soil_ksat', 'taw', 'tew']

    ras = ManageRasters()
    statics = [filename for filename in os.listdir(inputs_path) if filename.endswith('.tif')]
    static_dict = {}
    statics = sorted(statics, key=lambda s: s.lower())
    if point_dict:
        for key, val in point_dict.iteritems():
            coords = val['Coords']
            for filename, value in zip(statics, static_keys):
                full_path = os.path.join(inputs_path, filename)
                point_dict[key].update({value: get_static_inputs_at_point(coords, full_path)})
    else:
        static_arrays = [ras.convert_raster_to_array(inputs_path, filename, minimum_value=0.0) for filename in statics]
        for key, data in zip(static_keys, static_arrays):
            static_dict.update({key: data})
        return static_dict


def initialize_initial_conditions_dict(initial_inputs_path, point_dict=None):
    # read in initial soil moisture conditions from spin up, put in dict

    initial_cond_keys = ['de', 'dr', 'drew']

    ras = ManageRasters()
    initial_cond = [filename for filename in os.listdir(initial_inputs_path) if filename.endswith('.tif')]
    initial_cond.sort()
    initial_cond_dict = {}

    if point_dict:
        for key, val in point_dict.iteritems():
            coords = val['Coords']
            for filename, value in zip(initial_cond, initial_cond_keys):
                full_path = os.path.join(initial_inputs_path, filename)
                point_dict[key].update({value: get_static_inputs_at_point(coords, full_path)})

    else:
        initial_cond_arrays = [ras.convert_raster_to_array(initial_inputs_path, filename) for filename in initial_cond]
        for key, data in zip(initial_cond_keys, initial_cond_arrays):
            initial_cond_dict.update({key: data})
    return initial_cond_dict


def initialize_tracker():

    """ Create indices to plot point time series, these are empty lists that will
     be filled as the simulation progresses"""

    tracker = {}
    tracker_keys = ['rain', 'eta', 'snowfall', 'runoff', 'dr', 'pdr', 'de', 'pde', 'drew',
                    'pdrew', 'temp', 'max_temp', 'recharge', 'ks', 'pks', 'etrs', 'kcb',
                    'ke', 'pke', 'melt', 'swe', 'fs1', 'precip', 'kr', 'pkr', 'mass']
    for key in tracker_keys:
        tracker.update({key: []})
    return tracker

# ============= EOF =============================================
