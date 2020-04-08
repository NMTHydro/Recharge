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



def make_mask(shape_path, raster_out_path):
    rasterize = 'gdal_rasterize -a Mask -ts 2272 2525 -tr 250 250 -te 114757 3471163 682757 4102413 -ot "Byte" ' \
                '-l Sevilleta_Shrub_point F:/ETRM_Inputs/NDVI_oldPts/Sevilleta_Shrub_point.shp ' \
                'F:/ETRM_Inputs/Masks/Sevilleta_Shrub_point.tif'
    call(rasterize)

    # gdal_rasterize -a Mask -ts 2272 2525 -tr 250 250 -te 114757 3471163 682757 4102413 -ot "Byte" -l SaltBasin "C:/Users/Mike/PyRANA/HUCs & Model Bounds/SaltBasin.shp" F:/ETRM_inputs/Mask_Alternatives/SaltBasinNM.tif
    # gdal_rasterize -a Mask -ts 2272 2525 -tr 250 250 -te 114757 3471163 682757 4102413 -ot "Byte" -l NorthernSaltBasinMerged C:/Users/Mike/PyRANA/SaltBasin/NorthernSaltBasinMerged.shp F:/ETRM_inputs/Mask_Alternatives/NorthernSaltBasinNM.tif

    in_shp = shape_path # e.g. F:/ETRM_Inputs/NDVI_oldPts/Sevilleta_Shrub_point.shp
    out_ras = raster_out_path # e.g. F:/ETRM_Inputs/Masks/Sevilleta_Shrub_point.tif
    raster_name = 'arb_mask' # e.g., Sevilleta_Shrub_point
    x_min = 114757
    y_min = 3471163
    x_max = 682757
    y_max = 4102413
    cols = 2272
    rows = 2525
    cell_size = 250
    resample_method = 'near'
    raster = 'gdal_rasterize  -a Mask -te {b} {c} {d} {e} ' \
             '-ts {f} {g} -tr {h} {h} -l {i} {j} {k}'.format(b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                                             h=cell_size, i=raster_name, j=in_shp, k=out_ras)
    call(raster)
    # warp
    # warp = 'gdalwarp -overwrite  -s_srs EPSG:{a} -te {b} {c} {d} {e} ' \
    #        '-tr {f} {f} -r {g} -of GTiff {h} {i}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max,
    #                                                      f=rcell_size, g=resample_method, h=temp, i=out_raster)
    # call(warp)