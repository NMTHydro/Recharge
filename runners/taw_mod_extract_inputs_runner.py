# ===============================================================================
# Copyright 2016 gabe-parrish
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

# ============= standard library imports ========================
import os

# ============= local library imports ===========================

from datetime import datetime
from recharge.etrm_processes import Processes

from dateutil import rrule
import os
import time
from numpy import array

from recharge.dynamic_raster_finder import get_kcb, get_penman, get_prism
from recharge.raster_tools import convert_raster_to_array, apply_mask, save_daily_pts2


def run_model(date_range, input_root, output_root, taw_modification):
    etrm = Processes(date_range, input_root, output_root)
    etrm.modify_taw(taw_modification)
    etrm.run()



def run_extractor(root, output, start, end):

    mask_path = os.path.join(root, 'Mask')

    statics_to_save = os.path.join (root,'NDVI_statics')
    ndvi = os.path.join(root, 'NDVI', 'NDVI_std_all')
    prism = os.path.join(root, 'PRISM')
    penman = os.path.join(root, 'PM_RAD')

    nlcd_name = 'nlcd_nm_utm13.tif'
    dem_name = 'NMbuffer_DEM_UTM13_250m.tif'
    aspect_name = 'NMbuffer_DEMAspect_UTM13_250m.tif'
    slope_name = 'NMbuffer_DEMSlope_UTM13_250m.tif'

    nlcd = apply_mask(mask_path, convert_raster_to_array(statics_to_save, nlcd_name, 1))
    dem = apply_mask(mask_path, convert_raster_to_array(statics_to_save, dem_name, 1))
    slope = apply_mask(mask_path, convert_raster_to_array(statics_to_save, slope_name, 1))
    aspect = apply_mask(mask_path, convert_raster_to_array(statics_to_save, aspect_name, 1))

    st_begin = time.time()
    keys = 'Year', 'Month', 'Day', 'NDVI', 'Tavg', 'Precip', 'ETr', 'PminusEtr', 'NLCD_class', 'Elev', 'Slope', 'Aspect'
    with open(output, 'w') as wfile:
        wfile.write('{}\n'.format(','.join(keys)))

        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):

            st = time.time()

            ndvi_data = get_kcb(mask_path, ndvi, day)
            precip_data = get_prism(mask_path, prism, day, variable="precip")
            tmin_data = get_prism(mask_path, prism, day, variable="min_temp")
            tmax_data = get_prism(mask_path, prism, day, variable="max_temp")
            tavg = tmin_data + tmax_data / 2
            etrs_data = get_penman(mask_path, penman, day, variable="etrs")
            p_minus_etr = precip_data - etrs_data

            data = array(ndvi_data, tavg, precip_data, etrs_data, p_minus_etr, nlcd, dem, slope, aspect).T
            save_daily_pts2(wfile, day, data)

            runtime = time.time() - st

            print('Time for day = {}'.format(runtime))

        runtime_full = time.time() - st_begin

    print('Time to save entire period = {}'.format(runtime_full))


if __name__ == '__main__':

    ##### TAW runner #####

    start_year = 2013
    start_month = 12
    start_day = 1

    end_year = 2013
    end_month = 12
    end_day = 31

    taw_modification = .6

    hard_drive_path = os.path.join('/Volumes','Seagate Expansion Drive')
    inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')
    outputs_path = os.path.join(hard_drive_path, 'ETRM_Results')

    run_model((datetime(start_year, start_month, start_day),
         datetime(end_year, end_month, end_day)),
        inputs_path,
        outputs_path, taw_modification)


    ##### Extract ######
    start = datetime(2000, 1, 1)
    end = datetime(2013, 12, 31)

    root = inputs_path
    output = os.path.join(root, 'TAW_pts_out', 'TAW_12_2013.csv')

    run_extractor(root, output, start, end)

