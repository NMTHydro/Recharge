# ===============================================================================
# Copyright 2017 EXu
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
# ==============================================================================
import os, fnmatch
import gdal
from subprocess import call


#folder path and variables for Walnut
input_folder = 'G:\\Walnut\\RealData\\'
output_folder = 'G:\\Walnut\\WalnutData\\'
projection = 26912  # NAD83 UTM Zone 13 North
x_min = 576863
y_min = 3501109
x_max = 637613
y_max = 3519609
cols = 2430
rows = 740
cell_size = 25
resample_method = 'average'
rscale = 10
rcols = cols/rscale
rrows = rows/rscale
rcell_size = cell_size * rscale


# #folder path and variables for New Mexico
# input_folder = 'G:\\ETRM_inputs\\SoilsData\\NM_Extracted\\Merged\\'
# output_folder = 'G:\\ETRM_inputs\\SoilsData\\NM_Extracted\\Merged\\'
# projection = 26912  # NAD83 UTM Zone 12 North
# x_min = 114757
# y_min = 3471163
# x_max = 682757
# y_max = 4102413
# cols = 22720
# rows = 25250
# cell_size = 25
# resample_method = 'average'
# rcols = cols/10
# rrows = rows/10
# rcell_size = cell_size*10


os.chdir(input_folder)
def find_format(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            yield file_

for shapefile in find_format(input_folder, '*.shp'):
    FOLDER, shp_name = os.path.split(shapefile)
    raster_name, extent = os.path.splitext(shp_name)

    in_shp = os.path.join(input_folder, shp_name)
    temp = os.path.join(output_folder, 'temp.tif')
    # out_shp = os.path.join(output_folder, shp_name) # add reprojection later
    out_raster = os.path.join(output_folder, '{a}.tif').format(a=raster_name)


    # rasterize
    raster = 'gdal_rasterize  -a SdvOutpu_1 -te {b} {c} {d} {e} -ts {f} {g} -tr {h} {h} -l {i} {j} {k}'.format(b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                                                                                               i=raster_name, j=in_shp, k=temp, h=cell_size)
    call(raster)
# warp
    warp = 'gdalwarp -overwrite  -s_srs EPSG:{a} -te {b} {c} {d} {e} -tr {f} {f} -r {g} -of GTiff {h} {i}'.format(a=projection, b=x_min, c=y_min, d=x_max,
                                                                            e=y_max, f=rcell_size, g = resample_method,
                                                                            h=temp, i=out_raster)
    call(warp)

