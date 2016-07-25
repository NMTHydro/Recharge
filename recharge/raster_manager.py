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
The purpose of this module is to calculate recharge over a defined geographic area.

this module provides (1) function -- run_distributed_ETRM.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""

from osgeo import gdal
from numpy import array, ones, maximum


class ManageRasters:

    def __init__(self):
        pass

    def convert_raster_to_array(self, raster=None, input_raster_path=None,
                                filename=None, minimum_value=None, band=1):

        # Read in static data as arrays
        if not raster:
            raster = self._open_raster(input_path=input_raster_path, filename=filename)
        ras = array(raster.GetRasterBand(band).ReadAsArray(), dtype=float)
        if minimum_value:
            min_val = ones(ras.shape) * minimum_value
            ras = maximum(ras, min_val)
        return ras

    def _open_raster(self, input_path, filename):
        ras_open = gdal.Open('{a}\\{b}'.format(a=input_path, b=filename))
        return ras_open


# ============= EOF =============================================