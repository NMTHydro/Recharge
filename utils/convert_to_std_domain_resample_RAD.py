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
import os, fnmatch
import gdal
from subprocess import call

def find_rasters(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            print("here's your files -> ", file_)
            yield file_
            print("file yielded")



def folderwarp(input_folder, output_folder, resample_method_one):

    # input_folder = '/Volumes/SeagateExpansionDrive/ETRM_inputs/PM_RAD/PM2012' # C:\Recharge_GIS\land_use_land_cover /PM2000
    # output_folder = '/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/PM_RAD/PM2012' # C:\Recharge_GIS\OSG_Data
    # extent ='/Users/Gabe/Desktop/33_37_ETRM_aoi_project/created_layers/big_aoi_nad83_z13n.shp' #'/Users/Gabe/Desktop/33_37_ETRM_aoi_project/created_layers/p033r037_7dt20010613_z13_30_nad83z13_nn_crop_nad83.tif' # F:\\Reference_shape\\NM_poly500mbuf\\NM_poly500mbuf.shp

    os.chdir(input_folder)

    # metadata of Landsat file.
    projection = 26913  # NAD83 UTM Zone 13 North
    x_min = 279225  #114757
    y_min = 3585165 # 3471163
    x_max = 435225 # 682757
    y_max = 3705165 #4102413
    cols = 5200 # 2272
    rows = 4000 # 2525
    # resample_method_one = 'cubic'
    # resample_method_two = 'mode'
    cell_size = 30 #250

    for raster in find_rasters(input_folder, '*.tif'):
        FOLDER, raster_name = os.path.split(raster)

        print("folder", FOLDER)

        print("raster name", raster_name)


        in_raster = os.path.join(input_folder, raster_name)
        print("in raster", in_raster)
        temp = os.path.join(output_folder, 'temp.tif')
        out_raster = os.path.join(output_folder, raster_name)
        print("out raster", out_raster)

        #warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g} -r {h} -cutline {i} -crop_to_cutline -multi -srcnodata "-3.40282346639e+038" -dstnodata -999 {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows, h=resample_method_one, i=extent, j=in_raster, k=out_raster) # k = temp
        warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g} -r {h} -multi -srcnodata "-3.40282346639e+038" -dstnodata -999 {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows, h=resample_method_one, j=in_raster, k=out_raster) # k = temp

        print("WARP ({})".format(warp))

        call(warp, shell=True)

        # warp2 = 'gdalwarp -overwrite  -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -tr {f} {f} \n' \
        #         ' -r {g} -multi -srcnodata -999 -dstnodata -999 {h} {i}'.format(a=projection, b=x_min, c=y_min, d=x_max,
        #                                                                         e=y_max, f=cell_size, g=cell_size,
        #                                                                         h=temp, i=out_raster)
        # call(warp2)

        print("Done processing {}".format(out_raster))

def run_rad():
    """Warps all the files in all the subfolders for Gadget Radiation budget"""

    base_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/PM_RAD"
    output_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/PM_RAD"
    resample_method = "cubic"

    for path, directory, file in os.walk(base_path, topdown=False):

        for i in directory:
            if i.startswith("rad"):
                input_folder = os.path.join(base_path, i)
                output_folder = os.path.join(output_path, i)
                os.mkdir(output_folder)
                folderwarp(input_folder, output_folder, resample_method)

def run_PRISM():
    """Warps all the files in all the subfolders for PRISM precip model input"""

    base_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/PRISM/Precip/800m_std_all"
    output_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/PRISM/Precip/800m_std_all"
    resample_method = "cubic"

    folderwarp(base_path, output_path, resample_method)

def run_statics():
    """ Warps all the files in the statics folder of ETRM_inputs"""

    base_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/statics"
    output_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/statics_temp"
    resample_method = "near"

    folderwarp(base_path, output_path, resample_method)

def run_maxtemp():
    """ warps all the files in the Maximum Prism Temp folder"""

    base_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/PRISM/Temp/Maximum"
    output_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/Prism/Temp/Maximum_standard"
    resample_method = "cubic"

    folderwarp(base_path, output_path, resample_method)

def run_mintemp():
    """Warps all files in Minimum Prism Temp Folder"""
    base_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/PRISM/Temp/Minimum"
    output_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/Prism/Temp/Minimum_standard"
    resample_method = "cubic"

    folderwarp(base_path, output_path, resample_method)

def run_ndvi():
    """ Warps all files from NDVI/NDVI folder"""

    base_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/NDVI/NDVI"
    output_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/NDVI/NDVI"
    resample_method = "cubic"

    for path, directory, file in os.walk(base_path, topdown=False):

        for i in directory:
            input_folder = os.path.join(base_path, i)
            output_folder = os.path.join(output_path, i)
            os.mkdir(output_folder)
            folderwarp(input_folder, output_folder, resample_method)

def run_initialize():
    """ Warps all the initial de dr and drew rasters"""

    base_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/initialize"
    output_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/initialize"
    resample_method = "near"

    folderwarp(base_path, output_path, resample_method)

if __name__ == "__main__":

    # runs code for PM radiation
    #run_rad()

    # runs code for PRISM files
    # run_PRISM()

    # runs code for static files
    # run_statics()

    # runs code for max_temp
    #run_maxtemp()

    # runs code for min temp
    # run_mintemp()

    # runs code for NDVI
    # run_ndvi()

    # runs code for initialize
    run_initialize()