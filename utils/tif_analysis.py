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

input_path = 'C:\Users\David\Documents\Recharge\Thesis\Figures\maps'
sand_tif = 'infil_index_clipped.tif'

geo = get_geo(input_path)
infil = convert_raster_to_array(input_path, sand_tif)

pct_ct = where(0.1 < infil, ones(infil.shape), zeros(infil.shape))

print 'shape = {}'.format(infil.shape)
print 'count infil = {}'.format(count_nonzero(pct_ct))
# ==========================  EOF  ==============================================
