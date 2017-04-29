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
from recharge.dynamic_raster_finder import get_prisms, get_geo
from recharge.raster import Raster
from recharge.raster_tools import get_tiff_transform_func, get_tiff_transform
from recharge.tools import day_generator


def extract_prism(day, out):
    if not os.path.isdir(out):
        os.makedirs(out)

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

        print k
        raster = Raster.fromarray(arr)
        marr = raster.unmasked()
        marr = marr[slice(startr, endr), slice(startc, endc)]
        marr = marr * arr
        timestamp = day.strftime('%m_%d_%Y')
        p = os.path.join(out, '{}_{}.tif'.format(k, timestamp))
        print raster.array
        print marr
        raster.save(p, marr, geo)


def extract_penman(day, out):
    pass


def generate_dataset(daterange, out):
    if not paths.is_set():
        raise PathsNotSetExecption

    extract_initial
    extract_static

    for day in day_generator(*daterange):
        extract_prism(day, out)
        extract_NDVI(day, out)
        extract_penman(day, out)
        # extract_penman(day, out)


if __name__ == '__main__':
    paths.build('')
    generate_dataset('12/1/2013', '12/2/2013', '/Users/ross/Sandbox/etrm_dataset')
# ============= EOF =============================================
