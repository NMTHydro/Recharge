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
from dynamic_raster_finder import get_kcb, get_penman, get_prism
from raster_tools import convert_raster_to_array, apply_mask, save_daily_pts
import time


def run(root, output_root):

    startday = datetime(2000, 1, 1)
    endday = datetime(2013, 12, 31)

    mask_path = os.path.join(root, 'Mask')

    # etrm = Processes(date_range, mask_path,
    #                  output_root= output_root,
    #                  polygons= os.path.join(root, 'Blank_Geo'),
    #                  static_inputs= os.path.join(root, 'statics'),
    #                  initial_inputs=os.path.join(root, 'initialize'))
    statics_to_save = os.path.join (root,'NDVI_statics')
    ndvi = os.path.join(root, 'NDVI', 'NDVI_std_all')
    prism = os.path.join(root, 'PRISM')
    penman = os.path.join(root, 'PM_RAD')
    nlcd_name = 'nlcd_nm_utm13.tif'
    dem_name = 'NMbuffer_DEM_UTM13_250m.tif'
    aspect_name = 'NMbuffer_DEMAspect_UTM13_250m.tif'
    slope_name = 'NMbuffer_DEMSlope_UTM13_250m.tif'
    filename = os.path.join(root, 'NDVI_pts_out','NDVI_2000_2013.csv')

    nlcd = apply_mask(mask_path, convert_raster_to_array(statics_to_save, nlcd_name, 1))
    dem = apply_mask(mask_path, convert_raster_to_array(statics_to_save, dem_name, 1))
    slope = apply_mask(mask_path, convert_raster_to_array(statics_to_save, slope_name, 1))
    aspect = apply_mask(mask_path, convert_raster_to_array(statics_to_save, aspect_name, 1))

    cnt = 0
    if cnt == 0:
        with open(filename, "a") as wfile:
            wfile.write(
                '{},{},{},{},{},{},{},{},{},{},{},{} \n'.format('Year', 'Month', 'Day', 'NDVI', 'Tavg', 'Precip', 'ETr',
                                                                'PminusEtr', 'NLCD_class', 'Elev', 'Slope', 'Aspect'))
        cnt = 1

    st_begin = time.time()

    for day in rrule.rrule(rrule.DAILY, dtstart=startday, until=endday):

        st = time.time()


        ndvi_data = get_kcb(mask_path, ndvi, day)
        precip_data = get_prism(mask_path, prism, day, variable="precip")
        tmin_data = get_prism(mask_path, prism, day, variable="min_temp")
        tmax_data = get_prism(mask_path, prism, day, variable="max_temp")
        tavg = tmin_data + tmax_data / 2
        etrs_data = get_penman(mask_path, penman, day, variable="etrs")
        p_minus_etr = precip_data - etrs_data

        save_daily_pts(filename, day, ndvi_data, tavg, precip_data, etrs_data, p_minus_etr, nlcd, dem, slope, aspect)

        runtime = time.time() - st

        print('Time for day = {}'.format(runtime))

    runtime_full = time.time() - st_begin

    print('Time to save entire period = {}'.format(runtime_full))



if __name__ == '__main__':
    run('F:\\ETRM_Inputs',
        'F:\\ETRM_Results')
