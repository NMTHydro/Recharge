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
input_root: Please Set Me      ## /Volumes/Seagate Expansion Drive/ETRM_input
output_root: Please Set Me     ## /Users/ross/Desktop

# === START (No earlier than year 2000) ===

start_day: SET ME # dd
start_month: SET ME # mm
start_year: SET ME # YYYY

# === Finish (No later than year 2013) ===

end_day: SET ME #dd
end_month: SET ME # mm
end_year: SET ME # YYYY

# === MASKS ===
mask: SET ME # mask of study area (e.g. Mask/my_mask.tif)
binary_shapefile: SET ME # Set path to raster for individual tracker output (e.g binary_shapefile/my_b_shp.tif)
polygons: Blank_Geo # (default)
tiff_shape: None

#  === Saving specific dates as rasters ===
save_dates: [] # list in format -> 'mm/dd/YYY' such as ['mm/dd/YYY', 'mm/dd/YYY', 'mm/dd/YYY']
write_freq: SET ME # modify to output monthly or yearly rasters. OPTIONS -> daily|monthly|yearly
daily_outputs:[dr, de, drew] # OPTIONS -> anything that appears in the tracker

# === Misc settings ===
is_reduced: False # (default)
winter_evap_limiter: 0.3  # (default)
polygons: Blank_Geo # (default)
evap_ceff: 1.0 # (default)
ro_reinf_frac: 0.0 # (default) Runoff Reinfiltration Fraction. To increase runoff into soil.
rew_ceff: 1.0 # (default)
output_units: mm # (default) OPTIONS -> mm|acre-ft|?
winter_end_day: 92 # (default)
winter_start_day: 306 # (default)
use_individual_kcb: True # (default)
new_mexico_extent: True

# === Don't Change ===
swb_mode: fao # FAO 56 Water Balance Method
use_verify_paths: True

# === individual pixel tracker related ===
plot_output: SET ME # (for plots of the binary shapefile pixel tracker time series)
xplot: ['Date'] # (default)
yplot: ['rain', 'eta', 'rzsm'] # (default) OPTIONS -> anything in master dict.

# # === TAW parametrization (default is commented out) ====
# taw_modification: 1.0 # (default) Will increase TAW by a specified factor.
# uniform_taw: 25 # changes entire raster to a given TAW value

---

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
    uniform_taw = None
    taw_modification = 1.0
    ro_reinf_frac = 0.0
    swb_mode = 'fao'
    rew_ceff = 1.0
    evap_ceff = 1.0
    winter_evap_limiter = 0.3
    winter_end_day = 92
    winter_start_day = 306
    output_units = 'acre-ft'
    is_reduced = False
    binary_shapefile = None # TODO point_tracker
    new_mexico_extent = False
    xplot = None
    yplot = None
    plot_output = None
    tiff_shape = None

    def __init__(self, obj):
        self._obj = obj
        attrs = ('mask', 'polygons', 'use_individual_kcb',
                 'input_root', 'output_root', 'write_freq', 'use_verify_paths',
                 'nlcd_name', 'dem_name', 'aspect_name', 'slope_name',
                 'taw_modification',
                 'ro_reinf_frac', 'swb_mode', 'rew_ceff', 'evap_ceff',
                 'winter_evap_limiter', 'winter_end_day', 'winter_start_day',
                 'output_units', 'is_reduced', 'uniform_taw', 'binary_shapefile', 'new_mexico_extent',
                 'tiff_shape',
                 'xplot', 'yplot','plot_output') # GELP removed 'output_path', 'x_cord_name','y_cord_name', 5/4/2017

        for attr in attrs:
            # print "last attr out", attr
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
    path = None

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
        # print paths.config
        # print rfile
        #rfile = path

        # for doc in yaml.load_all(rfile):
        #     if doc != None:
        #         print doc
        #     else:
        #         print "here's the bad one"
        #         print doc
        self.runspecs = [RunSpec(doc) for doc in yaml.load_all(rfile)]
        print "runspecs", self.runspecs
        rfile.close()
        self.path = path


        # self.runspecs = [RunSpec(i, doc) for i, doc in enumerate(yaml.load_all(rfile))]
        # rfile.close()


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
