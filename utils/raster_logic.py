# ===============================================================================
# Copyright 2016 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance
# with the License.
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

# =================================IMPORTS=======================================
from osgeo import gdal
from numpy import array, where, count_nonzero, ones, zeros
import os

from recharge.raster_tools import convert_raster_to_array
from recharge.raster_tools import get_raster_geo_attributes as get_geo

input_path = 'E:\\'
sand_tif = 'combo_pct_sand.tif'
clay_tif = 'combo_pct_clay.tif'
out_name = 'rew_22SEPT16.tif'

geo = get_geo(input_path)
sand = convert_raster_to_array(input_path, sand_tif)
clay = convert_raster_to_array(input_path, clay_tif)

rew = 8 + 0.08 * clay
rew = where(sand > 80.0, 20.0 - 0.15 * sand, rew)
rew = where(clay > 50, 11 - 0.06 * clay, rew)


driver = gdal.GetDriverByName('GTiff')
out_data_set = driver.Create(os.path.join(input_path, out_name), geo['cols'], geo['rows'],
                             geo['bands'], geo['data_type'])
out_data_set.SetGeoTransform(geo['geotransform'])
out_data_set.SetProjection(geo['projection'])
output_band = out_data_set.GetRasterBand(1)
output_band.WriteArray(rew, 0, 0)


if __name__ == '__main__':
    pass

# ==========================  EOF  ==============================================
