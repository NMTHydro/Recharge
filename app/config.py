# ===============================================================================
# Copyright 2017 ross
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

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
import os
import sys
from datetime import datetime

import yaml

from app.paths import paths
from recharge import STATIC_KEYS, INITIAL_KEYS

DEFAULT_CFG = '''
---
input_root: /Volumes/Seagate Expansion Drive
output_root: Please Set Me

init_cond_root: /Volumes/Seagate Expansion Drive/ETRM_inputs/initialize
rew_init: drew_4_19_23_11.tif
tew_init: de_4_19_23_11.tif
taw_init: dr_4_19_23_11.tif

start_date: 12/1/2013
end_date: 12/32/2013

mask: masks/please_set_me.tif
polygons: Blank_Geo

save_dates: []

daily_outputs:
 - tot_infil
 - tot_etrs
 - tot_eta
 - tot_precip
 - tot_kcb

ro_reinf_frac: 0.0
swb_mode: fao
allen_ceff: 1.0
winter_evap_limiter: 0.3
output_units: acre-ft

'''

DATETIME_FMT = '%m/%d/%Y'


class RunSpec:
    _obj = None
    nlcd_name = None
    dem_name = None
    aspect_name = None
    slope_name = None
    x_cord_name = None
    y_cord_name = None
    mask = None
    polygons = None
    input_root = None
    output_root = None
    output_path = None
    write_freq = None
    use_verify_paths = None
    taw_modification = 1.0
    ro_reinf_frac = 0.0
    swb_mode = 'swb'
    allen_ceff = 1.0
    winter_evap_limiter = 0.3
    winter_end_day = 92
    winter_start_day = 306
    output_units = 'acre-ft'

    def __init__(self, obj):
        self._obj = obj
        attrs = ('mask', 'polygons', 'use_individual_kcb',
                 'input_root', 'output_root', 'output_path', 'write_freq', 'use_verify_paths',
                 'nlcd_name', 'dem_name', 'aspect_name', 'slope_name', 'x_cord_name',
                 'y_cord_name',
                 'taw_modification',
                 'ro_reinf_frac', 'swb_mode', 'allen_ceff',
                 'winter_evap_limiter', 'winter_end_day', 'winter_start_day',
                 'output_units')

        for attr in attrs:
            setattr(self, attr, self._obj.get(attr))

        initial = self._obj.get('initial')
        if initial:
            for attr in INITIAL_KEYS:
                setattr(self, attr, initial.get(attr))

        static = self._obj.get('static')
        if static:
            for attr in STATIC_KEYS:
                setattr(self, attr, static.get(attr))

    @property
    def initial_pairs(self):
        try:
            return tuple((k, getattr(self, k)) for k in INITIAL_KEYS)
        except AttributeError:
            pass

    @property
    def static_pairs(self):
        try:
            return tuple((k, getattr(self, k)) for k in STATIC_KEYS)
        except AttributeError:
            pass

    @property
    def save_dates(self):
        sd = self._obj.get('save_dates')
        if sd:
            return [datetime.strptime(s, DATETIME_FMT) for s in sd]

    @property
    def date_range(self):
        obj = self._obj
        if 'start_year' in obj:
            return (datetime(obj['start_year'],
                             obj['start_month'],
                             obj['start_day']),
                    datetime(obj['end_year'],
                             obj['end_month'],
                             obj['end_day']))
        else:
            return (datetime.strptime(obj['start_date'], DATETIME_FMT),
                    datetime.strptime(obj['end_date'], DATETIME_FMT))

    @property
    def daily_outputs(self):
        return self._obj.get('daily_outputs', [])


class Config:
    runspecs = None

    def __init__(self, path=None):
        self.load(path=path)

    def load(self, path=None):
        if path is None:
            path = paths.config

        if isinstance(path, (str, unicode)):
            check_config(path)
            rfile = open(path, 'r')
        else:
            rfile = path

        self.runspecs = [RunSpec(doc) for doc in yaml.load_all(rfile)]
        rfile.close()


def check_config(path=None):
    if path is None:
        path = paths.config

    if not os.path.isfile(path):
        print '***** The config file {} does not exist. A default one will be written'.format(path)

        with open(path, 'w') as wfile:
            print '-------------- DEFAULT CONFIG -----------------'
            print DEFAULT_CFG
            print '-----------------------------------------------'
            wfile.write(DEFAULT_CFG)

        print '***** Please edit the config file at {} and rerun the model'.format(path)
        sys.exit()

# ============= EOF =============================================
