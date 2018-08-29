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
from pprint import pprint, pformat

from numpy import zeros, isnan, count_nonzero, where, median, minimum, maximum, ones, nonzero, argwhere
from osgeo import ogr
from pandas import DataFrame, date_range, MultiIndex

from app.paths import paths
from recharge import STATIC_KEYS, OUTPUTS, INITIAL_KEYS, TRACKER_KEYS
from recharge.raster import Raster
import csv
from recharge.raster_tools import apply_mask, convert_raster_to_array

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

    print 'constants dict: {}\n'.format(pformat(d, indent=2))

    return d


def initialize_master_dict(shape):
    """create an empty dict that will carry ETRM-derived values day to day
    :param shape: shape of the model domain, (1, 1) or raster.shape
    """

    keys = ('infil', 'kcb', 'snow', 'rain', 'melt', 'mass', 'etrs', 'eta', 'precip', 'ro', 'swe', 'dry_days')
    master = {'tot_{}'.format(key): zeros(shape) for key in keys}

    master['pkcb'] = None
    master['albedo'] = ones(shape) * 0.45
    master['swe'] = zeros(shape)
    master['dry_days'] = zeros(shape)

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
        return maximum(r, 0.01) * 86.4 / 10  # KSat raster is in um/s; convert using 1 um/s = 86.4 mm/day
                                     # This / 10 is temporary, to reduce k-sat until better estimate can be obtained

    def initial_tew(r):
        return maximum(minimum(r, 10), 0.001)

    def initial_rew(r):
        return maximum(r, 0.001)

    d = {}
    if pairs is None:
        print 'Using default static inputs path: {}'.format(paths.static_inputs)
        pairs = make_pairs(paths.static_inputs, STATIC_KEYS)

    print '-------------------------------------------------------'
    print '       Key                  Name'
    for k, p in pairs:
        print 'static {:<20s} {}'.format(k, p)
        raster = Raster(p, root=paths.static_inputs)
        # print 'raster jjj', raster
        arr = raster.masked()

        if k == 'plant_height':
            arr = initial_plant_height(arr)
            # print arr
        elif k == 'rew':
            arr = initial_rew(arr)
        elif k == 'root_z':
            arr = initial_root_z(arr)
        elif k == 'soil_ksat':
            arr = initial_soil_ksat(arr)
            # print arr
        elif k == 'tew':
            arr = initial_tew(arr)

        d[k] = arr
    print '-------------------------------------------------------'

    q = d['quat_deposits']
    taw = d['taw']
    tew = d['tew']
    land_cover = d['land_cover']
    print 'original Ksat = {}, REW = {}, TAW = {}, land cover = {}'.format(d['soil_ksat'],d['rew'],d['taw'],d['land_cover'])

    # apply high TAW to unconsolidated Quaternary deposits
    min_val = 250
    taw = where(q > 0.0, maximum(min_val, taw), taw)

    # apply bounds to TAW
    # min_val = 50.0
    # max_val = 320.0
    #data = d['taw']
    #taw = where(data < min_val, min_val, taw)
    #taw = where(data > max_val, max_val, taw)

    # v = tew + d['rew']
    taw = where(taw < tew, tew, taw)

    # non_zero = count_nonzero(data < min_val)
    # print 'taw has {} cells below the minimum'.format(non_zero, min_val)
    print 'taw median: {}, mean {}, max {}, min {}\n'.format(median(taw), taw.mean(), taw.max(), taw.min())
    d['taw'] = taw

    # apply tew adjustment
    # tew = where(land_cover == 41, tew * 0.25, tew)
    # tew = where(land_cover == 42, tew * 0.25, tew)
    # tew = where(land_cover == 43, tew * 0.25, tew)
    # d['tew'] = where(land_cover == 52, tew * 0.75, tew)

    return d


def make_pairs(root, keys):
    """
    tiff files must be in right alphabetical order, and no capitals, in order to work
    """
    fs = tiff_list(root)
    return [(k, s) for k, s in zip(keys, fs)]


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
        print 'Using default initial inputs path: {}'.format(paths.initial_inputs)
        pairs = make_pairs(paths.initial_inputs, INITIAL_KEYS)

    d = {}

    print '-------------------------------------------------------'
    print '        Key                  Name'
    for k, p in pairs:
        print 'initial {:<20s} {}'.format(k, p)
        raster = Raster(p, root=paths.initial_inputs)
        data = raster.masked()
        d[k] = data

        nans = count_nonzero(isnan(data))
        if nans:
            print '{} has {} nan values'.format(k, nans)
        nons = count_nonzero(data < 0.0)
        if nons:
            print '{} has {} negative values'.format(k, nons)

    print '-------------------------------------------------------\n'

    return d


def initialize_raster_tracker(shape):
    """

    :param shape:
    :return:
    """

    d = {k: {tk: zeros(shape) for tk in OUTPUTS} for k in TRACKER_KEYS}
    # print 'd itself', d
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

# TODO - point_tracker: define initialize_point_tracker

def initialize_point_tracker(master, point_arr):
    """Create multiple DataFrames to plot point time series for selected pixels in the point_arr
    Returns a list of tuples of a (Dataframe, point_arr.index)
    :param master:
    :param point_arr:
    :return:
    """



    # TODO iterate through array and get array address out.

    # print point_arr
    #stuff = where(nonzero(point_arr))

    # print "shape of array -> {}".format(point_arr.shape)
    # I'm nor sure that argwhere will get the pixels in the order that I want them in.
    arr_elements = argwhere(a=point_arr) # finds the indices of array elements that are non-zero, grouped by element
    # print "nonzero(point_arr", nonzero(point_arr)
    # arr_elements = nonzero(point_arr)[0]
    # print 'stuff', arr_elements

    # TODO - Figure out why the arr_elements isn't working like it's supposed to. GELP 4/27/2018

    # keys = master.keys()
    # # print 'masterkeyshape', master[keys[0].shape()]# Here's a problem. master key shape is different \
    # # from the array shape.
    #
    #
    # #  _update_point_tracker so cols are the same
    #
    # # add columns for TAW and RZSM - July 9 2017
    # # columns.append('TAW')
    # # columns.append('RZSM')
    # #
    # # item_tracker = [master[key][index] for key in sorted(master) if key not in ('transp_adj', )]
    #
    # item_tracker = []
    # for key in sorted(master.keys()):
    #     if key not in ('transp_adj', ):
    #         print "MASTER KEY" , key
    # #
    # # # columns = sorted(columns)
    # # columns = sorted(master.keys())
    # # print "COLUMNS", columns
    #
    #
    #
    # #=======
    #
    # # columns = [master[key] for key in sorted(master) if key not in ('transp_adj',)]
    #
    # # print "columns master", columns
    #
    # # print "MASTA", master
    #
    #
    # columns = sorted(master.keys())

    # The master dictionary doesnt get populated with some of these headers until the daily timestep thing kicks in so
    #  we manually add them here.
    columns = ['Date', 'albedo', 'de', 'dr', 'drew', 'dry_days', 'eta', 'etrs', 'evap', 'evap_1', 'evap_2',
               'fcov', 'few', 'infil', 'kcb', 'ke', 'ke_init', 'kr', 'ks', 'mass', 'max_temp', 'melt',
               'min_temp', 'pde', 'pdr', 'pdrew', 'pkcb', 'precip', 'rain', 'rg', 'ro', 'rzsm', 'snow_fall',
               'soil_ksat', 'soil_storage', 'soil_storage_all', 'st_1_dur', 'st_2_dur', 'swe', 'taw', 'temp',
               'tot_dry_days', 'tot_eta', 'tot_etrs', 'tot_infil', 'tot_kcb', 'tot_mass', 'tot_melt',
               'tot_precip', 'tot_rain', 'tot_ro', 'tot_snow', 'tot_swe', 'transp']

    tracker_list = []
    for i, item in enumerate(arr_elements):

        # store the location in the array where you need to get the value from...
        item = item.tolist()[0]
        tracker_list.append(([i, item], columns))


    # avoid a memory leak and write to a csv...
    # make the directory first
    try:
        if not os.path.isfile(paths.tracker_csv_path):
            os.mkdir(paths.tracker_csv_path)
    except WindowsError:
        pass
    # path for all the csvs to go to
    csv_path = paths.tracker_csv_path
    # make the csvs...
    for index, dataframe in tracker_list:
        print "COLS", columns
        # dataframe.to_csv(os.path.join(csv_path, "tracker_pixel_{}.csv".format(index)))
        # print "writing cols headers"
        print "where the trackers go", os.path.join(csv_path, "tracker_pixel_{}.csv".format(index))
        with open(os.path.join(csv_path, "tracker_pixel_{}.csv".format(index[0])), 'w') as wfile:
            writer = csv.writer(wfile)
            writer.writerow(columns) #TODO - in windows writes double spaced.

    # Still send out the list of pixels and columns
    return tracker_list

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
