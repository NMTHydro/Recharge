# ===============================================================================
# Copyright 2018 gabe-parrish
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
from datetime import date, timedelta
import numpy as np
# ============= local library imports ===========================
from recharge.raster_tools import convert_raster_to_array, get_raster_geo_attributes
from utils.depletions_modeling.cumulative_depletions import write_raster

def add_year(datetime_date, years):
    """Don't really need this funtion but may come in useful later"""
    try:
        return datetime_date.replace(year = datetime_date.year + years)
    except ValueError:
        return datetime_date + (date(d.year + years, 1, 1) - date(datetime_date.year, 1, 1))


def all_time_ndvi_avg(ndvi_root, start_date, end_date, array_shape, representative_ndvi_file, output_folder):
    """"""

    # get the info needed to write the raster from the representative_ndvi_file
    ndvi_geo_attributes = get_raster_geo_attributes(representative_ndvi_file)

    array_shape = (ndvi_geo_attributes['rows'], ndvi_geo_attributes['cols'])

    print 'ndvi_geo \n', ndvi_geo_attributes

    num_years = end_date.year - start_date.year

    period_delta = end_date - start_date

    cumulative_ndvi = np.zeros(array_shape, dtype=float)
    count = 0
    for i in range(num_years+1):

        start_current_year = date(start_date.year + i, 01, 01)
        print 'accumulating for year starting: {}'.format(start_current_year)
        start_next_year = date(start_current_year.year + 1, 01, 01)
        year_folder_path = os.path.join(ndvi_root, '20{:02}'.format(i))

        year_delta = start_next_year - start_current_year

        for d in range(year_delta.days):

            ndvi_date = start_current_year + timedelta(days=d)

            ndvi_name = 'NDVI{}_{:02}_{:02}.tif'.format(ndvi_date.year, ndvi_date.month, ndvi_date.day)
            ndvi_path = os.path.join(year_folder_path, ndvi_name)

            ndvi_arr = convert_raster_to_array(ndvi_path)

            cumulative_ndvi += ndvi_arr
            count += 1

    print 'count', count
    print 'days', period_delta.days

    print 'averaging ndvi'
    average_ndvi = cumulative_ndvi/count

    print 'outputting NDVI to output folder {}'.format(output_folder)

    write_raster(average_ndvi, ndvi_geo_attributes['geotransform'], output_folder, 'all_time_avg_ndvi.tif',
                 array_shape, ndvi_geo_attributes['projection'])

if __name__ == "__main__":


    ndvi_root = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/NDVI/NDVI'

    start_date = date(2000, 01, 01)

    end_date = date(2013, 12, 31)

    # shape of ETRM array
    array_shape = (2525, 2272)

    representative_ndvi_file = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/NDVI/NDVI/2000'

    output_folder = '/Users/Gabe/Desktop/academic_docs/LandFire/NDVI_parameters'

    all_time_ndvi_avg(ndvi_root, start_date, end_date, array_shape, representative_ndvi_file, output_folder)