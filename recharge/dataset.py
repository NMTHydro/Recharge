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
from recharge.dynamic_raster_finder import get_prisms, get_geo, get_individ_ndvi, get_penman
from recharge.raster import Raster
from recharge.raster_tools import get_tiff_transform_func, get_tiff_transform
from recharge.tools import day_generator
from recharge.dict_setup import make_pairs
from recharge import STATIC_KEYS, INITIAL_KEYS


def extract_prism(day, out):
    keys = ('min_temp', 'max_temp', 'temp', 'precip')

    geo = get_geo(day)
    mask_arr = Raster(paths.mask).as_bool_array
    # nr,nc = mask_arr.shape
    startr, endr = None, None
    for i, ri in enumerate(mask_arr):
        if ri.any():
            if startr is None:
                startr = i
        elif startr is not None:
            endr = i
            break

    geo['rows'] = endr - startr
    startc, endc = None, None
    for i, ri in enumerate(mask_arr.T):
        if ri.any():
            if startc is None:
                startc = i
        elif startc is not None:
            endc = i
            break

    geo['cols'] = endc - startc

    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)
    geo['geotransform'] = transform.to_gdal()

    for k, arr in zip(keys, get_prisms(day)):

        # skip temp
        if k == 'temp':
            continue

        raster = Raster.fromarray(arr)
        marr = raster.unmasked()
        marr = marr[slice(startr, endr), slice(startc, endc)]
        marr = marr * arr
        timestamp = day.strftime('%m_%d_%Y')
        subpath = ''
        if k == 'precip':
            subpath = os.path.join('PRISM','precip','800m_std_all')
        elif k == 'max_temp':
            subpath = os.path.join('PRISM','Temp','Maximum_standard')
        elif k == 'min_temp':
            subpath = os.path.join('PRISM','Temp','Minimum_standard')

        p = os.path.join(out, subpath)
        if not os.path.isdir(p):
            os.makedirs(p)
        p = os.path.join(p, '{}_{}.tif'.format(k, timestamp))

        raster.save(p, marr, geo)


def extract_penman(day, out):
    keys = ('etrs', 'rg')

    geo = get_geo(day)
    mask_arr = Raster(paths.mask).as_bool_array
    # nr,nc = mask_arr.shape
    startr, endr = None, None
    for i, ri in enumerate(mask_arr):
        if ri.any():
            if startr is None:
                startr = i
        elif startr is not None:
            endr = i
            break

    geo['rows'] = endr - startr
    startc, endc = None, None
    for i, ri in enumerate(mask_arr.T):
        if ri.any():
            if startc is None:
                startc = i
        elif startc is not None:
            endc = i
            break

    geo['cols'] = endc - startc

    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)
    geo['geotransform'] = transform.to_gdal()

    for k in keys:
        arr = get_penman(day, k)

        raster = Raster.fromarray(arr)
        marr = raster.unmasked()
        marr = marr[slice(startr, endr), slice(startc, endc)]
        marr = marr * arr

        year = str(day.year)
        yday = day.timetuple().tm_yday
        if k == 'etrs':
            p = os.path.join(out, 'PM_RAD', '{}{}'.format('PM', year))
            name = '{}_{}_{:03n}.tif'.format('PM_NM', year, yday)
        elif k == 'rg':
            p = os.path.join(out, 'PM_RAD', '{}{}'.format('rad', year))
            name = '{}_{}_{:03n}.tif'.format('RTOT', year, yday)

        if not os.path.isdir(p):
            os.makedirs(p)
        p = os.path.join(p, name)

        raster.save(p, marr, geo)


def extract_ndvi(day, out):
    geo = get_geo(day)
    mask_arr = Raster(paths.mask).as_bool_array
    # nr,nc = mask_arr.shape
    startr, endr = None, None
    for i, ri in enumerate(mask_arr):
        if ri.any():
            if startr is None:
                startr = i
        elif startr is not None:
            endr = i
            break

    geo['rows'] = endr - startr
    startc, endc = None, None
    for i, ri in enumerate(mask_arr.T):
        if ri.any():
            if startc is None:
                startc = i
        elif startc is not None:
            endc = i
            break

    geo['cols'] = endc - startc

    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)
    geo['geotransform'] = transform.to_gdal()

    arr = get_individ_ndvi(day)
    raster = Raster.fromarray(arr)
    marr = raster.unmasked()
    marr = marr[slice(startr, endr), slice(startc, endc)]
    marr = marr * arr

    timestamp = day.strftime('%m_%d_%Y')
    year = str(day.year)
    p = os.path.join(out, 'NDVI', 'NDVI', year)
    if not os.path.isdir(p):
        os.makedirs(p)
    p = os.path.join(p, '{}_{}.tif'.format('ndvi', timestamp))

    raster.save(p, marr, geo)


def extract_initial(out):
    mask_arr = Raster(paths.mask).as_bool_array
    # nr,nc = mask_arr.shape
    startr, endr = None, None
    for i, ri in enumerate(mask_arr):
        if ri.any():
            if startr is None:
                startr = i
        elif startr is not None:
            endr = i
            break

    startc, endc = None, None
    for i, ri in enumerate(mask_arr.T):
        if ri.any():
            if startc is None:
                startc = i
        elif startc is not None:
            endc = i
            break

    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)

    pairs = make_pairs(paths.initial_inputs, INITIAL_KEYS)
    for k, pair in pairs:
        raster = Raster(pair, root=paths.initial_inputs)
        geo = raster.geo
        geo['rows'] = endr - startr
        geo['cols'] = endc - startc
        geo['geotransform'] = transform.to_gdal()

        arr = raster.masked()

        raster = Raster.fromarray(arr)
        marr = raster.unmasked()
        marr = marr[slice(startr, endr), slice(startc, endc)]
        marr = marr * arr

        path = os.path.join(out, 'initialize')
        if not os.path.isdir(path):
            os.makedirs(path)
        path = os.path.join(path, '{}_{}.tif'.format(k, 'reduced'))

        raster.save(path, marr, geo)
        print 'initial {} reduced'.format(k)


def extract_static(out):
    mask_arr = Raster(paths.mask).as_bool_array
    # nr,nc = mask_arr.shape
    startr, endr = None, None
    for i, ri in enumerate(mask_arr):
        if ri.any():
            if startr is None:
                startr = i
        elif startr is not None:
            endr = i
            break

    startc, endc = None, None
    for i, ri in enumerate(mask_arr.T):
        if ri.any():
            if startc is None:
                startc = i
        elif startc is not None:
            endc = i
            break

    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)

    pairs = make_pairs(paths.static_inputs, STATIC_KEYS)
    for k, pair in pairs:
        raster = Raster(pair, root=paths.static_inputs)
        geo = raster.geo
        geo['rows'] = endr - startr
        geo['cols'] = endc - startc
        geo['geotransform'] = transform.to_gdal()

        arr = raster.masked()

        raster = Raster.fromarray(arr)
        marr = raster.unmasked()
        marr = marr[slice(startr, endr), slice(startc, endc)]
        marr = marr * arr

        path = os.path.join(out, 'statics')
        if not os.path.isdir(path):
            os.makedirs(path)
        path = os.path.join(path, '{}_{}.tif'.format(k, 'reduced'))

        raster.save(path, marr, geo)
        print 'static {} reduced'.format(k)


def extract_mask(out):
    mask_arr = Raster(paths.mask).as_bool_array
    # nr,nc = mask_arr.shape
    startr, endr = None, None
    for i, ri in enumerate(mask_arr):
        if ri.any():
            if startr is None:
                startr = i
        elif startr is not None:
            endr = i
            break

    startc, endc = None, None
    for i, ri in enumerate(mask_arr.T):
        if ri.any():
            if startc is None:
                startc = i
        elif startc is not None:
            endc = i
            break

    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)

    raster = Raster(paths.mask)
    geo = raster.geo
    geo['rows'] = endr - startr
    geo['cols'] = endc - startc
    geo['geotransform'] = transform.to_gdal()

    arr = raster.masked()

    raster = Raster.fromarray(arr)
    marr = raster.unmasked()
    marr = marr[slice(startr, endr), slice(startc, endc)]
    marr = marr * arr

    path = os.path.join(out, 'Mask')
    if not os.path.isdir(path):
        os.makedirs(path)
    path = os.path.join(path, '{}_{}.tif'.format('mask', 'reduced'))

    raster.save(path, marr, geo)
    print 'mask reduced'


def generate_dataset(daterange, out):
    if not paths.is_set():
        raise PathsNotSetExecption

    extract_initial(out)
    extract_static(out)
    extract_mask(out)

    for day in day_generator(*daterange):
        extract_prism(day, out)
        extract_ndvi(day, out)
        extract_penman(day, out)
        print 'day {}'.format(day.strftime('%m_%d_%Y'))


if __name__ == '__main__':
    paths.build('')
    generate_dataset('12/1/2013', '12/2/2013', '/Users/ross/Sandbox/etrm_dataset')
# ============= EOF =============================================
