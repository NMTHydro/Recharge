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

import os
from datetime import datetime

from numpy import zeros, isnan, count_nonzero, where, median, minimum, maximum, ones
from osgeo import ogr
from pandas import DataFrame, date_range, MultiIndex

from app.paths import paths
from recharge import STATIC_KEYS, OUTPUTS, INITIAL_KEYS
from recharge.raster import Raster

"""
kc_min is from ASCE pg 199 (0.1 to 0.15 given range, but say to use 0 or nearly 0 for natural settings)
kc_max is from ASCE pg 225 Eq 10.3b (1.05 to 1.3 given range)
et_depletion_factor ASCE pg 226 (0.3 to 0.7 given range) 0.5 common for ag crops
    can adjust p for ETc as eq on ASCE pg. 392
"""


def set_constants(ze=40, p=0.4,
                  kc_min=0.01, kc_max=1.0,
                  snow_alpha=0.2, snow_beta=11.0,
                  ke_max=1.0,
                  a_min=0.45, a_max=0.90):
    """

    :param ze:
    :param p:
    :param kc_min:
    :param kc_max:
    :param snow_alpha:
    :param snow_beta:
    :param ke_max:
    :param a_min:
    :param a_max:
    :return:
    """
    d = dict(s_mon=datetime(1900, 7, 1),
             e_mon=datetime(1900, 10, 1),
             ze=ze, p=p,
             kc_min=kc_min, kc_max=kc_max,
             snow_alpha=snow_alpha, snow_beta=snow_beta,
             ke_max=ke_max,
             a_min=a_min, a_max=a_max)

    print 'constants dict: {}'.format(d)

    return d


def initialize_master_dict(shape):
    """create an empty dict that will carry ETRM-derived values day to day
    :param shape: shape of the model domain, (1, 1) or raster.shape
    """

    keys = ('infil', 'kcb', 'snow', 'rain', 'melt', 'mass', 'etrs', 'eta', 'precip', 'ro', 'swe', 'dry_days')
    master = {'tot_{}'.format(key): zeros(shape) for key in keys}

    master['pkcb'] = None
    master['albedo'] = ones(shape) * 0.45

    # master['swe'] = zeros(shape)  # this should be initialized correctly using simulation results
    # s['rew'] = minimum((2 + (s['tew'] / 3.)), 0.8 * s['tew'])  # this has been replaced
    # by method of Ritchie et al (1989), rew derived from percent sand/clay

    # master['dry_days'] = zeros(shape)

    return master


def initialize_static_dict(pairs=None):
    """

    :return:
    """

    def initial_plant_height(r):
        # I think plant height is recorded in ft, when it should be m. Not sure if *= works on rasters.
        return r * 0.3048

    def initial_root_z(r):
        return minimum(r, 100)

    def initial_soil_ksat(r):
        return maximum(minimum(r, 20), 0.1)

    def initial_tew(r):
        return maximum(minimum(r, 10), 0.001)

    def initial_rew(r):
        return maximum(r, 0.001)

    d = {}
    if pairs is None:
        print 'static inputs path: {}'.format(paths.static_inputs)
        pairs = make_pairs(paths.static_inputs, STATIC_KEYS)

    for k, p in pairs:
        raster = Raster(p, root=paths.etrm_input_root)
        arr = raster.masked()

        if k == 'plant_height':
            arr = initial_plant_height(arr)
        elif k == 'rew':
            arr = initial_rew(arr)
        elif k == 'root_z':
            arr = initial_root_z(arr)
        elif k == 'soil_ksat':
            arr = initial_soil_ksat(arr)
        elif k == 'tew':
            arr = initial_tew(arr)

        d[k] = arr

    q = d['quat_deposits']
    taw = d['taw']
    tew = d['tew']
    land_cover = d['land_cover']

    # apply high TAW to unconsolidated Quaternary deposits
    min_val = 250
    taw = where(q > 0.0, min_val, taw)

    # apply bounds to TAW
    min_val = 50.0
    max_val = 320.0

    data = d['taw']
    taw = where(data < min_val, min_val, taw)
    taw = where(data > max_val, max_val, taw)

    v = tew + d['rew']
    taw = where(taw < v, v, taw)

    non_zero = count_nonzero(data < min_val)
    print 'taw has {} cells below the minimum'.format(non_zero, min_val)
    print 'taw median: {}, mean {}, max {}, min {}'.format(median(taw), taw.mean(), taw.max(), taw.min())
    d['taw'] = taw

    # apply tew adjustment
    tew = where(land_cover == 41, tew * 0.25, tew)
    tew = where(land_cover == 42, tew * 0.25, tew)
    tew = where(land_cover == 43, tew * 0.25, tew)
    d['tew'] = where(land_cover == 52, tew * 0.75, tew)

    return d


def make_pairs(root, keys):
    fs = tiff_list(root)
    return [(k, os.path.join(root, s)) for k, s in zip(keys, fs)]


def tiff_list(root, sort=True):
    """

    :type sort: bool
    :param root:
    :param sort:
    :return:
    """
    fs = [fn for fn in os.listdir(root) if fn.endswith('.tif')]
    if sort:
        fs = sorted(fs)
    return fs


def initialize_initial_conditions_dict(pairs=None):
    """

    :return:
    """
    # read in initial soil moisture conditions from spin up, put in dict

    if pairs is None:
        print 'initial inputs path: {}'.format(paths.initial_inputs)
        pairs = make_pairs(paths.initial_inputs, INITIAL_KEYS)

    d = {}
    for k, p in pairs:
        raster = Raster(p, root=paths.etrm_input_root)
        data = raster.masked()
        d[k] = data

        print '{} has {} nan values'.format(k, count_nonzero(isnan(data)))
        print '{} has {} negative values'.format(k, count_nonzero(data < 0.0))

    return d


def initialize_raster_tracker(shape):
    """

    :param shape:
    :return:
    """
    keys = ('current_year', 'current_month', 'current_day', 'last_mo', 'last_yr', 'yesterday')
    d = {k: {tk: zeros(shape) for tk in OUTPUTS} for k in keys}
    return d


def initialize_tabular_dict(date_range_, write_frequency):
    """

    :param date_range_:
    :param write_frequency:
    :return:
    """
    units = ('AF', 'CBM')

    outputs = OUTPUTS
    outputs_arr = [o for output in outputs for o in (output, output)]

    # if the write frequency of flux sums over input_root is daily, use normal master keys rather than 'tot_param'
    if write_frequency == 'daily':
        outputs_arr = [out.replace('tot_', '') for out in outputs_arr]

    units_arr = units * len(outputs)

    cols = MultiIndex.from_arrays((outputs_arr, units_arr))
    ind = date_range(date_range_[0], date_range_[1], freq='D')

    tab_dict = {}

    input_root = paths.polygons
    print 'polygon folder: {}'.format(input_root)
    for f in os.listdir(input_root):
        print 'folder: {}'.format(f)
        region_type = f.replace('_Polygons', '')
        print 'region type: {}'.format(region_type)

        d = {}
        for ff in os.listdir(os.path.join(input_root, f)):
            if ff.endswith('.shp'):
                subreg = ff[:-4]
                print 'sub region : {}'.format(subreg)
                df = DataFrame(index=ind, columns=cols).fillna(0.0)
                d[subreg] = df

        tab_dict[region_type] = d

    # print 'your tabular results dict:\n{}'.format(tab_dict)

    return tab_dict


def initialize_master_tracker(master):
    """ Create DataFrame to plot point time series, these are empty lists that will
     be filled as the simulation progresses

     :param master: dict

     """
    tracker = DataFrame(columns=sorted(master.keys()))
    return tracker


def cmb_sample_site_data(shape):
    """

    :param shape:
    :return:
    """
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

# ============= EOF =============================================
