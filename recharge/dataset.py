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


def setup_extract(day):
    geo = get_geo(day)
    mask_arr = Raster(paths.mask).as_bool_array
    startc, endc, startr, endr = bounding_box(mask_arr)
    geo['rows'] = endr - startr
    geo['cols'] = endc - startc
    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)
    geo['geotransform'] = transform.to_gdal()
    return geo, startc, endc, startr, endr


def bounding_box(arr):
    startr, endr = None, None
    for i, ri in enumerate(arr):
        if ri.any():
            if startr is None:
                startr = i-1
        elif startr is not None:
            endr = i+1
            break

    startc, endc = None, None
    for i, ri in enumerate(arr.T):
        if ri.any():
            if startc is None:
                startc = i-1
        elif startc is not None:
            endc = i+1
            break

    return startc, endc, startr, endr


def extract_prism(day, out):
    keys = ('min_temp', 'max_temp', 'temp', 'precip')
    bases = ('Temp/Minimum_standard', 'Temp/Maximum_standard', None, 'precip/800m_std_all')

    geo, startc, endc, startr, endr = setup_extract(day)

    # build directories
    for a, b in (('precip', '800m_std_all'), ('Temp', 'Maximum_standard'), ('Temp', 'Minumum_standard')):
        p = os.path.join(out, 'PRISM', a, b)
        print 'build', a,b,p
        if not os.path.isdir(p):
            print 'making', p
            os.makedirs(p)

    timestamp = day.strftime('%m_%d_%Y')
    for k, base, arr in zip(keys, bases, get_prisms(day)):
        # skip temp
        if k == 'temp':
            continue

        # raster = Raster.fromarray(arr)
        # marr = raster.unmasked()
        # marr = marr[slice(startr, endr), slice(startc, endc)]
        # marr = marr * arr
        p = os.path.join(out, 'PRISM', base, '{}_{}.tif'.format(k, timestamp))
        #
        # raster.save(p, marr, geo)

        print 'primsim', p, os.path.isdir(os.path.dirname(p))
        slice_and_save(p, arr, geo, startc, endc, startr, endr)


def slice_and_save(p, arr, geo, startc, endc, startr, endr):
    raster = Raster.fromarray(arr)
    print arr
    marr = raster.unmasked()
    marr = marr[slice(startr, endr), slice(startc, endc)]
    print marr
    marr = marr * arr
    # timestamp = day.strftime('%m_%d_%Y')

    # p = os.path.join(p, '{}_{}.tif'.format(k, timestamp))

    raster.save(p, marr, geo)


def extract_penman(day, out):
    keys = ('etrs', 'rg')

    geo, startc, endc, startr, endr = setup_extract(day)

    for k in keys:
        arr = get_penman(day, k)

        # raster = Raster.fromarray(arr)
        # marr = raster.unmasked()
        # marr = marr[slice(startr, endr), slice(startc, endc)]
        # marr = marr * arr

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

        slice_and_save(p, arr, geo, startc, endc, startr, endr)
        # raster.save(p, marr, geo)


def extract_ndvi(day, out):
    geo, startc, endc, startr, endr = setup_extract(day)

    arr = get_individ_ndvi(day)
    # raster = Raster.fromarray(arr)
    # marr = raster.unmasked()
    # marr = marr[slice(startr, endr), slice(startc, endc)]
    # marr = marr * arr

    timestamp = day.strftime('%Y_%m_%d')
    year = str(day.year)
    p = os.path.join(out, 'NDVI', 'NDVI', year)
    if not os.path.isdir(p):
        os.makedirs(p)
    p = os.path.join(p, '{}{}.tif'.format('NDVI', timestamp))

    # raster.save(p, marr, geo)
    slice_and_save(p, arr, geo, startc, endc, startr, endr)


def extract_initial(out):
    mask_arr = Raster(paths.mask).as_bool_array
    startc, endc, startr, endr = bounding_box(mask_arr)

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

        # raster = Raster.fromarray(arr)
        # marr = raster.unmasked()
        # marr = marr[slice(startr, endr), slice(startc, endc)]
        # marr = marr * arr

        # p = os.path.join(out, 'initialize')
        # if not os.path.isdir(p):
        #     os.makedirs(p)
        # p = os.path.join(p, '{}_{}.tif'.format(k, 'reduced'))

        p = make_reduced_path(out, 'initialize', k)
        slice_and_save(p, arr, geo, startc, endc, startr, endr)

        # raster.save(path, marr, geo)
        print 'initial {} reduced'.format(k)


def extract_static(out):
    mask_arr = Raster(paths.mask).as_bool_array
    startc, endc, startr, endr = bounding_box(mask_arr)

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

        # raster = Raster.fromarray(arr)
        # marr = raster.unmasked()
        # marr = marr[slice(startr, endr), slice(startc, endc)]
        # marr = marr * arr

        # p = os.path.join(out, 'statics')
        # if not os.path.isdir(p):
        #     os.makedirs(p)
        # p = os.path.join(p, '{}_{}.tif'.format(k, 'reduced'))
        p = make_reduced_path(out, 'statics', k)

        slice_and_save(p, arr, geo, startc, endc, startr, endr)

        # raster.save(path, marr, geo)
        print 'static {} reduced'.format(k)


def extract_mask(out):
    mask_arr = Raster(paths.mask).as_bool_array
    startc, endc, startr, endr = bounding_box(mask_arr)

    transform = get_tiff_transform(paths.mask)
    transform *= Affine.translation(startc, startr)

    raster = Raster(paths.mask)
    geo = raster.geo
    geo['rows'] = endr - startr
    geo['cols'] = endc - startc
    geo['geotransform'] = transform.to_gdal()

    arr = raster.masked()

    # raster = Raster.fromarray(arr)
    # marr = raster.unmasked()
    # marr = marr[slice(startr, endr), slice(startc, endc)]
    # marr = marr * arr

    # p = os.path.join(out, 'Mask')
    # if not os.path.isdir(p):
    #     os.makedirs(p)
    # p = os.path.join(p, '{}_{}.tif'.format('mask', 'reduced'))
    #
    p = make_reduced_path(out, 'Mask', 'mask')

    slice_and_save(p, arr, geo, startc, endc, startr, endr)

    # raster.save(path, marr, geo)
    print 'mask reduced'


def make_reduced_path(out, tag, k):
    p = os.path.join(out, tag)
    if not os.path.isdir(p):
        os.makedirs(p)
    p = os.path.join(p, '{}_reduced.tif'.format(k))
    return p


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
