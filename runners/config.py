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
from datetime import datetime

import yaml

from runners.paths import paths

DEFAULT_CFG = '''
---
input_root: /Volumes/Seagate Expansion Drive

start_date = 12/1/2013
end_date = 12/32/2013

mask: Mask
polygons: Blank_Geo

save_dates: []

daily_outputs:
 - tot_infil
 - tot_etrs
 - tot_eta
 - tot_precip
 - tot_kcb

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

    def __init__(self, obj):
        self._obj = obj
        attrs = ('mask', 'polygons', 'use_individual_kcb',
                 'input_root', 'output_root', 'output_path', 'write_freq', 'use_verify_paths',
                 'nlcd_name', 'dem_name', 'aspect_name', 'slope_name', 'x_cord_name',
                 'y_cord_name')
        for attr in attrs:
            setattr(self, attr, self._obj.get(attr))

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

        if not os.path.isfile(path):
            print '***** The config file {} does not exist. A default one will be written'.format(path)

            with open(path, 'w') as wfile:
                print '-------------- DEFAULT CONFIG -----------------'
                print DEFAULT_CFG
                print '-----------------------------------------------'
                wfile.write(DEFAULT_CFG)

        with open(path, 'r') as rfile:
            # self._obj = yaml.load(rfile)
            self.runspecs = [RunSpec(doc) for doc in yaml.load_all(rfile)]

# ============= EOF =============================================
