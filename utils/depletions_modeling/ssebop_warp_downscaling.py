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

import gdal
import os
from gdalconst import *
from subprocess import call

""""
### Example ETRM georefference info ###
ETRM precip
extent:114757.0000000000000000,3471163.0000000000000000 : 682757.0000000000000000,4102413.0000000000000000
pixel size: 250,-250
dim: X: 2272 Y: 2525 Bands: 1

### Example gdalwarp command for transforming SSEBop to ETRM grid and resampling ###
gdalwarp -overwrite -s_srs EPSG:4326 -t_srs EPSG:26913 -r near
-ts 2272 2525 -te 114757.0 3471163.0
682757.0 4102413.0
-of GTiff "/Users/Gabe/Desktop/NM_DEM_slope/SSEBop/SSEBOP_Geotiff/ ssebop_2003_8.tif" "/Volumes/Seagate Expansion
 Drive/SSEBop_research/ssebop_2003_8_warp_nn_nad83.tif"
"""

def warp(initial_projection, final_projection, resampling_method, dimx, dimy, xmin, ymin, xmax,
         ymax, input_path, output_path):
    """

    :param initial_projection:
    :param final_projection:
    :param resampling_method:
    :param dimx:
    :param dimy:
    :param xmin:
    :param ymin:
    :param xmax:
    :param ymax:
    :param input_path:
    :param output_path:
    :return:
    """
    print resampling_method
    warpcommand = "gdalwarp -overwrite -s_srs {} -t_srs {} -r {} -ts {} {} -te {} {} {} {} -of GTiff {} {}".format(initial_projection, final_projection, resampling_method, dimx, dimy, xmin, ymin, xmax, ymax, input_path, output_path)
    print 'warp command', warpcommand

    # Actually starts the warp.
    call(warpcommand, shell=True)

def run():
    """
    Based on user-specified dimensions, extent, projection and resampling method, this script will warp andresample all
     geotiff files in a given directory.
    :return:
    """
    root_path = "/Users/Gabe/Desktop/NM_DEM_slope/SSEBop/SSEBOP_Geotiff"
    output_root = "/Users/Gabe/Desktop/NM_DEM_slope/SSEBop/SSEBOP_Geotiff_warped"
    initial_projection = 'EPSG:4326'
    final_projection = 'EPSG:26913'
    resampling_method = 'near'
    dimx = 2272
    dimy = 2525
    xmin = 114757.0
    ymin = 3471163.0
    xmax = 682757.0
    ymax = 4102413.0

    # we 'walk' through each file in the directory and warp it to our user defined specifications...
    walk_obj = os.walk(root_path)
    for path, subdir, files in walk_obj:
        for file in files:
            header = file.split('.')[0]
            newfilename = "{}{}".format(header, "_warped.tif")
            input_path = os.path.join(path, file)
            output_path = os.path.join(output_root, newfilename)
            warp(initial_projection, final_projection, resampling_method, dimx, dimy, xmin,
                 ymin, xmax,ymax, input_path, output_path)


if __name__== "__main__":
    run()
