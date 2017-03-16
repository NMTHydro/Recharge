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
from recharge.raster import Raster
from recharge.raster_tools import convert_raster_to_array, apply_mask, save_daily_pts
import time

from app.config import Config
from app.paths import paths


def run():
    cfg = Config()

    outdir = os.path.dirname(cfg.output_path)
    if not os.path.isdir(outdir):
        print 'output directory does not exist. making it now: {}'.format(outdir)
        os.makedirs(outdir)

    # startday = datetime(2000, 1, 1)
    # endday = datetime(2013, 12, 31)

    startday, endday = cfg.date_range

    # mask_path = os.path.join(root, 'Mask')
    # statics_to_save = os.path.join(root, 'NDVI_statics')
    # ndvi = os.path.join(root, 'NDVI_spline',)
    # prism = os.path.join(root, 'PRISM')
    # penman = os.path.join(root, 'PM_RAD')
    # nlcd_name = 'nlcd_nm_utm13.tif'
    # dem_name = 'NMbuffer_DEM_UTM13_250m.tif'
    # aspect_name = 'NMbuffer_DEMAspect_UTM13_250m.tif'
    # slope_name = 'NMbuffer_DEMSlope_UTM13_250m.tif'
    # x_cord_name = 'NDVI_1300ptsX.tif'
    # y_cord_name = 'NDVI_1300ptsY.tif'

    # Gets the arrays using function convert_raster_to_array() in raster_tools.py
    # apply_mask is done on the same array.
    # nlcd = apply_mask(mask_path, convert_raster_to_array(statics_to_save, nlcd_name, 1))
    # dem = apply_mask(mask_path, convert_raster_to_array(statics_to_save, dem_name, 1))
    # slope = apply_mask(mask_path, convert_raster_to_array(statics_to_save, slope_name, 1))
    # aspect = apply_mask(mask_path, convert_raster_to_array(statics_to_save, aspect_name, 1))
    # x_cord = apply_mask(mask_path, convert_raster_to_array(statics_to_save, x_name, 1))
    # y_cord = apply_mask(mask_path, convert_raster_to_array(statics_to_save, y_name, 1))

    root = paths.ndvi_statics

    nlcd = Raster(cfg.nlcd_name, root).masked()
    dem = Raster(cfg.dem_name, root).masked()
    x_cord = Raster(cfg.x_cord_name, root).masked()
    y_cord = Raster(cfg.y_cord_name, root).masked()

    rslope = Raster(cfg.slope_name, root)
    raspect = Raster(cfg.aspect_name, root)

    rslope.apply_mask()
    rslope.filter_less(0,0)
    slope = rslope.array()

    raspect.apply_mask()
    raspect.filter_less(0, 0)
    raspect.filter_greater(360, 0)
    aspect = raspect.array()

    keys = ('Year', 'Month', 'Day', 'X', 'Y', 'NDVI', 'Tavg', 'Precip', 'ETr',
            'PminusEtr', 'NLCD_class', 'Elev', 'Slope', 'Aspect')
    st_begin = time.time()

    # do you really want to be appending to the output file every time you run this script?
    # is so then 'a' is appropriate otherwise 'w' is the correct choice.
    # notice also in my write the file is only opened *once* as apposed to every iteration.
    with open(cfg.output_path, 'w') as wfile:
        wfile.write('{}\n'.format(','.join(keys)))

        for day in rrule.rrule(rrule.DAILY, dtstart=startday, until=endday):
            st = time.time()

            ndvi_data = get_kcb(paths.ndvi_spline, day)
            precip_data = get_prism(paths.prism, day, variable="precip")
            tmin_data = get_prism(paths.prism, day, variable="min_temp")
            tmax_data = get_prism(paths.prism, day, variable="max_temp")
            tavg = tmin_data + tmax_data / 2
            # Finds the penman image.
            etrs_data = get_penman(paths.penman, day, variable="etrs")

            p_minus_etr = precip_data - etrs_data

            data = array([x_cord, y_cord, ndvi_data, tavg, precip_data,
                          etrs_data, p_minus_etr, nlcd, dem, slope, aspect]).T

            save_daily_pts(wfile, day, data)

            runtime = time.time() - st

            print('Time for day = {}'.format(runtime))

    runtime_full = time.time() - st_begin

    print('Time to save entire period = {}'.format(runtime_full))


if __name__ == '__main__':
    # paths.build('F:')
    # output_path = os.path.join(paths.etrm_input_root, 'NDVI_pts_out', 'NDVI_Spline_2000_2013.csv')
    run()
# =================================== EOF =========================
