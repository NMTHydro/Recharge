# ===============================================================================
# Copyright 2016 dgketchum
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
"""
The purpose of this module is to unstack multi-band rasters and save to inividual (1-band) .tif.

this module provides (1) function -- unstack_rasters.

dgketchum 9 Sept 2016
"""

import os
from datetime import datetime
import gdal
from dateutil import rrule
from subprocess import call

start, end = datetime(2000, 01, 01), datetime(2000, 12, 31)


def unstack_rasters(in_path, out_path, start_date, end_date):

    for day in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
        doy = day.timetuple().tm_yday
        print('day of year: {}'.format(doy))
        obj = [1, 49, 81, 113, 145, 177, 209, 241, 273, 305, 337]
        if doy < 49:
            start = 1
            nd = 48
            raster = 'T{}_{}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(str(start).rjust(3, '0'),
                                                                             str(nd).rjust(3, '0'))
            raster_path = os.path.join(in_path, raster)
            dst = os.path.join(out_path, '{}_{}.tif'.format(day.year, doy))
            print('dst: {}     band {}'.format(dst, doy))
            translate = 'gdal_translate -b {} {} {}'.format(doy, raster_path, dst)
            call(translate)

        else:
            for num in obj[1:]:
                diff = doy - num
                if 0 <= diff <= 31:
                    pos = obj.index(num)
                    start = obj[pos]
                    band_num = diff + 1
                    if num == 337:
                        nd = num + 29
                    else:
                        nd = num + 31
                    raster = 'T{}_{}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(str(start).rjust(3, '0'),
                                                                                     str(nd).rjust(3, '0'))
                    raster_path = os.path.join(in_path, raster)
                    dst = os.path.join(out_path, '{}_{}.tif'.format(day.year, doy))
                    print('dst: {}     band {}'.format(dst, doy))
                    translate = 'gdal_translate -b {} {} {}'.format(band_num, raster_path, dst)
                    call(translate)


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print('home: {}'.format(home))
    root = os.path.join(home)
    stacked_path = os.path.join(root, 'Downloads', 'stacked_ndvi')
    unstacked_path = os.path.join(root, 'Downloads', 'unstacked_ndvi')
    unstack_rasters(stacked_path, unstacked_path, start, end)
# ============= EOF =============================================

