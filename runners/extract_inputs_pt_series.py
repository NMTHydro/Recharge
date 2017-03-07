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
import os
import time
from numpy import array

from recharge.dynamic_raster_finder import get_kcb, get_penman, get_prism
from recharge.raster_tools import convert_raster_to_array, apply_mask, save_daily_pts


def run(root, output, start, end):

    mask_path = os.path.join(root, 'Mask')

    statics_to_save = os.path.join (root,'statics')
    ndvi = os.path.join(root, 'NDVI', 'NDVI_std_all')
    prism = os.path.join(root, 'PRISM')
    penman = os.path.join(root, 'PM_RAD')
    ### test test
    nlcd_name = 'nlcd_nm_utm13.tif'
    #dem_name = 'NMbuffer_DEM_UTM13_250m.tif'
    #aspect_name = 'NMbuffer_DEMAspect_UTM13_250m.tif'
    #slope_name = 'NMbuffer_DEMSlope_UTM13_250m.tif'
    taw_name = 'taw_mod_4_21_10_0.tif'

    # Gets the arrays using function convert_raster_to_array() in raster_tools.py
    # apply_mask is done on the same array.
    nlcd = apply_mask(mask_path, convert_raster_to_array(statics_to_save, nlcd_name, 1))
    #dem = apply_mask(mask_path, convert_raster_to_array(statics_to_save, dem_name, 1))
    #slope = apply_mask(mask_path, convert_raster_to_array(statics_to_save, slope_name, 1))
    #aspect = apply_mask(mask_path, convert_raster_to_array(statics_to_save, aspect_name, 1))
    # I added this one to test. GP
    taw = apply_mask(mask_path, convert_raster_to_array(statics_to_save, taw_name, 1))

    st_begin = time.time()
    #remove 'Elev', 'slope', 'aspect'
    keys = 'Year', 'Month', 'Day', 'NDVI', 'Tavg', 'Precip', 'ETr', 'PminusEtr', 'NLCD_class', 'taw'
    with open(output, 'w') as wfile:
        wfile.write('{}\n'.format(','.join(keys)))

        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):

            st = time.time()

            ndvi_data = get_kcb(mask_path, ndvi, day)
            precip_data = get_prism(mask_path, prism, day, variable="precip")
            tmin_data = get_prism(mask_path, prism, day, variable="min_temp")
            tmax_data = get_prism(mask_path, prism, day, variable="max_temp")
            tavg = tmin_data + tmax_data / 2
            # Finds the penman image.
            etrs_data = get_penman(mask_path, penman, day, variable="etrs")
            p_minus_etr = precip_data - etrs_data

            # modified here, too. took out dem, slope, aspect... added taw
            data = array((ndvi_data, tavg, precip_data, etrs_data, p_minus_etr, nlcd, taw)).T
            save_daily_pts(wfile, day, data) # save_daily_pts2 is missing. We have save_daily_pts_old and save_daily_pts

            runtime = time.time() - st

            print('Time for day = {}'.format(runtime))

        runtime_full = time.time() - st_begin

    print('Time to save entire period = {}'.format(runtime_full))


if __name__ == '__main__':
    start = datetime(2013, 12, 1)
    end = datetime(2013, 12, 31)

    root = os.path.join('/Volumes', 'Seagate Expansion Drive', 'ETRM_Inputs')
    output = os.path.join(root, 'NDVI_pts_out', 'NDVI_2013_dec_mo.csv')

    run(root, output, start, end)

# =================================== EOF =========================
