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

from datetime import datetime
from dateutil import rrule
from numpy import array, where
import os
from recharge.dynamic_raster_finder import get_penman, get_prism, get_spline_kcb as get_kcb
from recharge.raster_tools import convert_raster_to_array, apply_mask, save_daily_pts
import time


def run(root, output_path):

    outdir = os.path.dirname(output_path)
    if not os.path.isdir(outdir):
        print 'output directory does not exist. making it now: {}'.format(outdir)
        os.makedirs(outdir)

    startday = datetime(2000, 1, 1)
    endday = datetime(2013, 12, 31)

    mask_path = os.path.join(root, 'Mask')
    statics_to_save = os.path.join(root, 'NDVI_statics')
    ndvi = os.path.join(root, 'NDVI_spline',)
    prism = os.path.join(root, 'PRISM')
    penman = os.path.join(root, 'PM_RAD')
    nlcd_name = 'nlcd_nm_utm13.tif'
    dem_name = 'NMbuffer_DEM_UTM13_250m.tif'
    aspect_name = 'NMbuffer_DEMAspect_UTM13_250m.tif'
    slope_name = 'NMbuffer_DEMSlope_UTM13_250m.tif'
    x_name = 'NDVI_1300ptsX.tif'
    y_name = 'NDVI_1300ptsY.tif'

    nlcd = apply_mask(mask_path, convert_raster_to_array(statics_to_save, nlcd_name, 1))
    dem = apply_mask(mask_path, convert_raster_to_array(statics_to_save, dem_name, 1))
    slope = apply_mask(mask_path, convert_raster_to_array(statics_to_save, slope_name, 1))
    aspect = apply_mask(mask_path, convert_raster_to_array(statics_to_save, aspect_name, 1))
    x_cord = apply_mask(mask_path, convert_raster_to_array(statics_to_save, x_name, 1))
    y_cord = apply_mask(mask_path, convert_raster_to_array(statics_to_save, y_name, 1))
    keys = ('Year', 'Month', 'Day', 'X', 'Y', 'NDVI', 'Tavg', 'Precip', 'ETr',
            'PminusEtr', 'NLCD_class', 'Elev', 'Slope', 'Aspect')

    slope = where(slope < 0.0, 0, slope)
    aspect = where(aspect < 0.0, 0, aspect)
    aspect = where(aspect > 360.0, 0, aspect)

    st_begin = time.time()

    # do you really want to be appending to the output file every time you run this script?
    # is so then 'a' is appropriate otherwise 'w' is the correct choice.
    # notice also in my write the file is only opened *once* as apposed to every iteration.
    with open(output_path, 'a') as wfile:
        wfile.write('{}\n'.format(','.join(keys)))

        for day in rrule.rrule(rrule.DAILY, dtstart=startday, until=endday):
            st = time.time()

            ndvi_data = get_kcb(mask_path, ndvi, day)
            precip_data = get_prism(mask_path, prism, day, variable="precip")
            tmin_data = get_prism(mask_path, prism, day, variable="min_temp")
            tmax_data = get_prism(mask_path, prism, day, variable="max_temp")
            tavg = tmin_data + tmax_data / 2
            etrs_data = get_penman(mask_path, penman, day, variable="etrs")
            p_minus_etr = precip_data - etrs_data

            data = array([x_cord, y_cord, ndvi_data, tavg, precip_data,
                          etrs_data, p_minus_etr, nlcd, dem, slope, aspect]).T

            save_daily_pts(wfile, day, data)

            # save_daily_pts(output_path, day, x_cord, y_cord, ndvi_data, tavg, precip_data, etrs_data,
            #                p_minus_etr, nlcd, dem, slope, aspect)

            runtime = time.time() - st

            print('Time for day = {}'.format(runtime))

    runtime_full = time.time() - st_begin

    print('Time to save entire period = {}'.format(runtime_full))


if __name__ == '__main__':
    root = 'F:\\ETRM_Inputs'
    output_path = os.path.join(root, 'NDVI_pts_out', 'NDVI_Spline_2000_2013.csv')
    run(root, output_path)
# =================================== EOF =========================
