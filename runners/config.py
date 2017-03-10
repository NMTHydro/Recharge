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

import yaml
from datetime import datetime

from runners.paths import paths

DEFAULT_CFG = '''
start_day: 1
start_month: 12
start_year: 2013

end_day: 29
end_month: 12
end_year: 2013

input_root: /Volumes/Seagate Expansion Drive
mask: Mask
polygons: Blank_Geo
'''
DATETIME_FMT = '%m/%d/%Y'


class Config:
    _obj = None

    def __init__(self):
        self.load()

    def load(self):
        p = paths.config
        if not os.path.isfile(p):
            print '***** The config file {} does not exist. A default one will be written'.format(p)

            with open(p, 'w') as wfile:
                print '-------------- DEFAULT CONFIG -----------------'
                print DEFAULT_CFG
                print '-----------------------------------------------'
                wfile.write(DEFAULT_CFG)

        with open(p, 'r') as rfile:
            self._obj = yaml.load(rfile)

    @property
    def save_dates(self):
        sd = self._obj.get('save_dates')
        if sd:
            return [datetime.strptime(s, DATETIME_FMT) for s in sd]

    @property
    def use_individual_kcb(self):
        return self._obj.get('use_individual_kcb')

    @property
    def mask(self):
        return self._obj.get('mask')

    @property
    def polygons(self):
        return self._obj.get('polygons')

    @property
    def input_root(self):
        return self._obj.get('input_root')

    @property
    def output_root(self):
        return self._obj.get('output_root')

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
    def write_freq(self):
        return self._obj.get('write_freq')

    @property
    def use_verify_paths(self):
        return self._obj.get('use_verify_paths')

# ============= EOF =============================================
