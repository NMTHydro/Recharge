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

from pandas import DataFrame

from recharge.raster_tools import get_mask, convert_raster_to_array
from utils.pixel_coord_finder import coord_getter


def extract_keys(tiff_list):
    keys = [tname.split('_')[0] for tname in tiff_list]
    return keys


def tiff_framer(root, mask_path, tiff_list):
    print 'started tiff framer'
    mask_arr = get_mask(mask_path)

    # TODO - build the mask into the config object.
    northing, easting = coord_getter(mask_path)
    print 'got n/e'

    arrs = [convert_raster_to_array(root, tiff_name) for tiff_name in tiff_list]
    print 'got arrs'

    ref_arr = arrs[0]
    nrows, ncols = ref_arr.shape

    rows = []
    for ri in xrange(nrows):
        for ci in xrange(ncols):
            mask_values = mask_arr[ri, ci]
            if mask_values:
                x = int(easting[ri, ci])
                y = int(northing[ri, ci])
                data = [arr[ri, ci] for arr in arrs]
                print data
                data.insert(0, y)
                data.insert(0, x)

                rows.append(data)

    df = DataFrame(rows)
    return df


if __name__ == '__main__':
    hard_drive_path = os.path.join('/Volumes', 'Seagate Expansion Drive')
    inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')
    mp = os.path.join(inputs_path, 'Mask')

    root = '/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_02_24/monthly_rasters'
    tnames = ['eta_7_2012.tif', 'etrs_7_2012.tif']
    mp = os.path.join(mp, 'zuni_1.tif')
    tiff_framer(root, mp, tnames)
# ============= EOF =============================================
