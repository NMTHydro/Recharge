# ===============================================================================
# Copyright 2018 Daniel Cadol
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
The purpose of this module is to generate PyRANA (and ETRM) compatible mask files
from a provided shape file location.

this module provides (1) function -- make_mask.

dancadol 16 July 2018
"""

import os

from numpy import array, asarray, zeros_like
from numpy.ma import masked_where, nomask
from osgeo import gdal
from subprocess import call



def make_mask():
    rasterize = 'gdal_rasterize -a Mask -ts 2272 2525 -tr 250 250 -te 114757 3471163 682757 4102413 -ot "Byte" ' \
                '-l Sevilleta_Shrub_point F:/ETRM_Inputs/NDVI_oldPts/Sevilleta_Shrub_point.shp ' \
                'F:/ETRM_Inputs/Masks/Sevilleta_Shrub_point.tif'
    call(rasterize)
