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

from affine import Affine

from app.paths import paths, PathsNotSetExecption
from recharge.dynamic_raster_finder import get_prisms, get_geo, get_individ_ndvi, get_penman, get_prism
from recharge.raster import Raster
from recharge.raster_tools import get_tiff_transform_func, get_tiff_transform
from recharge.tools import day_generator
from recharge.dict_setup import make_pairs, tiff_list
from recharge import STATIC_KEYS, INITIAL_KEYS


def generate_dataset(daterange, out):
    if not paths.is_set():
        raise PathsNotSetExecption

    geo, bounds = setup_geo()
    args = out, geo, bounds
    extract_initial(*args)
    extract_static(*args)
    extract_mask(*args)

    for day in day_generator(*daterange):
        extract_prism(day, *args)
        extract_ndvi(day, *args)
        extract_penman(day, *args)
        print '----------------- day {} -------------------'.format(day.strftime('%m_%d_%Y'))


# ============= data extract ==================================================
def extract_prism(day, out, geo, bounds):
    out_root = os.path.join(out, 'PRISM')
    timestamp = day.strftime('%Y%m%d')

    pp = os.path.join(out_root, 'precip', '800m_std_all')
    matp = os.path.join(out_root, 'Temp', 'Maximum_standard')
    mitp = os.path.join(out_root, 'Temp', 'Minimum_standard')

    for base, key in ((pp, 'precip'), (mitp, 'min_temp'), (matp, 'max_temp')):
        arr = get_prism(day, key)
        name = '{}_{}.tif'.format(key, timestamp)
        p = os.path.join(base, name)
        slice_and_save(p, arr, geo, *bounds)


def extract_penman(day, out, geo, bounds):
    keys = ('etrs', 'rg')

    for k in keys:
        arr = get_penman(day, k)

        year = str(day.year)
        yday = day.timetuple().tm_yday
        if k == 'etrs':
            p = os.path.join(out, 'PM_RAD', '{}{}'.format('PM', year))
            name = '{}_{}_{:03n}.tif'.format('PM_NM', year, yday)
        elif k == 'rg':
            p = os.path.join(out, 'PM_RAD', '{}{}'.format('rad', year))
            name = '{}_{}_{:03n}.tif'.format('RTOT', year, yday)

        # if not os.path.isdir(p):
        #     os.makedirs(p)

        p = os.path.join(p, name)
        slice_and_save(p, arr, geo, *bounds)


def extract_ndvi(day, out, geo, bounds):
    arr = get_individ_ndvi(day)

    timestamp = day.strftime('%Y_%m_%d')
    year = str(day.year)
    p = os.path.join(out, 'NDVI', 'NDVI', year)
    # if not os.path.isdir(p):
    #     os.makedirs(p)
    p = os.path.join(p, '{}{}.tif'.format('NDVI', timestamp))
    slice_and_save(p, arr, geo, *bounds)


# ============= initial/static extract ========================================

def save_initial(p, raster, transform, startc, endc, startr, endr):
    geo = raster.geo
    geo['rows'] = endr - startr
    geo['cols'] = endc - startc
    geo['geotransform'] = transform.to_gdal()

    arr = raster.masked()

    slice_and_save(p, arr, geo, startc, endc, startr, endr)


def extract_initial(*args):
    pairs = make_pairs(paths.initial_inputs, INITIAL_KEYS)
    root = paths.initial_inputs
    _extract('initialize', pairs, root, *args)


def extract_static(*args):
    pairs = make_pairs(paths.static_inputs, STATIC_KEYS)
    root = paths.static_inputs
    _extract('static', pairs, root, *args)


def _extract(tag, pairs, root, out, geo, bounds):
    for k, pair in pairs:
        raster = Raster(pair, root=root)
        p = make_reduced_path(out, tag, k)
        arr = raster.masked()
        slice_and_save(p, arr, geo, *bounds)

        print '{} {} reduced'.format(tag, k)


def extract_mask(out, geo, bounds):
    raster = Raster(paths.mask)
    p = make_reduced_path(out, 'Mask', 'mask')
    arr = raster.masked()
    slice_and_save(p, arr, geo, *bounds)

    print 'mask reduced'


# ============= helpers =========================================
def setup_geo():
    raster = Raster(paths.mask)
    mask_arr = raster.as_bool_array

    # get raster to provide geo data (need one that is not "Byte")
    root = paths.initial_inputs
    name = tiff_list(root)[0]
    raster = Raster(name, root=root)
    geo = raster.geo

    startc, endc, startr, endr = bounding_box(mask_arr)
    geo['rows'] = endr - startr
    geo['cols'] = endc - startc
    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)
    geo['geotransform'] = transform.to_gdal()

    return geo, (startc, endc, startr, endr)


def bounding_box(arr, padding=1):
    startr, endr = None, None
    for i, ri in enumerate(arr):
        if ri.any():
            if startr is None:
                startr = i - padding
        elif startr is not None:
            endr = i + padding
            break

    startc, endc = None, None
    for i, ri in enumerate(arr.T):
        if ri.any():
            if startc is None:
                startc = i - padding
        elif startc is not None:
            endc = i + padding
            break

    return startc, endc, startr, endr


def slice_and_save(p, arr, geo, startc, endc, startr, endr):
    if not os.path.isdir(os.path.dirname(p)):
        os.makedirs(os.path.dirname(p))
    raster = Raster.fromarray(arr)
    marr = raster.unmasked()
    marr = marr[slice(startr, endr), slice(startc, endc)]
    marr = marr * arr
    # print 'saving {}'.format(p)
    raster.save(p, marr, geo)


def make_reduced_path(out, tag, k):
    p = os.path.join(out, tag)
    # if not os.path.isdir(p):
    #     os.makedirs(p)
    p = os.path.join(p, '{}_reduced.tif'.format(k))
    return p


def get_transform(startc, startr):
    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)
    transform = transform.to_gdal()
    return transform


if __name__ == '__main__':
    paths.build('')
    generate_dataset('12/1/2013', '12/2/2013', '/Users/ross/Sandbox/etrm_dataset')
# ============= EOF =============================================
