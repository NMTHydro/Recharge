# Copyright 2016 pmrevelle
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

import os
import datetime
from dateutil import rrule

from recharge import NUMS
from recharge.raster_tools import convert_raster_to_array
from recharge.tools import write_map, read_map
from app.paths import paths


def get_kcb(in_path, date_object):
    """
    Find NDVI image and convert to Kcb.

    :param in_path: NDVI input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :return: numpy array object
    """
    # print date_object
    doy = date_object.timetuple().tm_yday
    year = date_object.year
    # print('date object', date_object)

    if year == 2000:
        band = 1
        raster = '{}_{}.tif'.format(year, doy)
    elif year == 2001:
        for num in NUMS:
            diff = doy - num
            if 0 <= diff <= 15:
                start = num
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15

                band = diff + 1
                raster = '{}_{}_{}.tif'.format(year, start, nd)
                print('raster', raster)
                break
    else:
        for i, num in enumerate(NUMS):
            diff = doy - num
            if 0 <= diff <= 15:
                band = diff + 1
                raster = '{}_{}.tif'.format(year, i + 1)
                break

    ndvi = convert_raster_to_array(in_path, raster, band=band)

    return ndvi


def run():
    paths.build('F:')

    penman_example = 'PM_NM_2000_001.tif'
    map_for_reference = os.path.join(paths.penman, '2000', penman_example)
    _, _, _, _, x, y, _, prj, fill_val = read_map(map_for_reference, 'Gtiff')

    start = datetime.datetime(2000, 1, 1, 0)
    end = datetime.datetime(2001, 12, 31, 0)

    fill_val = -999.

    for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        year = day.strftime('%Y')
        month = day.strftime('%m')
        day_mth = day.strftime('%d')

        # yearstr = str(year)
        # output = os.path.join(output_dir, new_dir, year)
        # print(output_dir)

        ndvi = get_kcb(paths.ndvi_std_all, day)

        # kcb = remake_array(mask_path, kcb)
        ndvi[ndvi == fill_val] = 0
        # print(ndvi, ndvi.shape)

        new_ndvi = 'NDVI{}_{}_{}.tif'.format(year, month, day_mth)

        output_dir = os.path.join(paths.etrm_input_root, 'NDVI_individ', str(year))
        ndvi_out = os.path.join(output_dir, new_ndvi)

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        print('Saving New NDVI file as {}'.format(ndvi_out))
        write_map(ndvi_out, 'Gtiff', x, y, ndvi, prj, fill_val)

if __name__ == '__main__':
   run()

# ============= EOF =============================================
