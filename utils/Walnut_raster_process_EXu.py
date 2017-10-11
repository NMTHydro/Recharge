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

"""
The purpose of this module is to study soil properties of desired region.

The first section haven't been cleaned, yet.

First section: Modis data processing for NM/Walnut Gulch: .shp tp .tiff
Second section: Soil Physical Properties Processing
                    - Source: .tiff generated from SoilDataViewer
                    - Operation: merge 2 parts of SSURGO .tiffs
                                 manually get noData mask
                                 clip STATSGO based on noData mask
                                 merge SSURGO and STATSGO

EXu 13 SEP 2017
"""

import os, fnmatch
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





###############################################################################################################################
# Second Section
root = 'H:\\NewMexico\\DirectSoilData\\'
prop = 'gcmBD3rdbar'

def merge_operator_1(root, prop):
    """
    Checks if the date is specified for writing output and calls the write and tabulation methods.

    :param root: The main path of all data/folders storaging .tiff files
    :param prop: The specific soil property:
                    - gcmBD3rdbar: Bulk Density at field capacity (1/3 bar) in g/cm^3
                    - OrgMatter: organic matter expressed in % of weight of soil material d <= 2 mm
                    - percClay: % Clay content
                    - percSand: % Sand content
                    - percSilt: % Silt content
                    - umsKsat: saturation K in um/s
                    - WC3rdbar: water content at field capacity (1/3 bar) in volumetric percentage
    after finish this function, manually get noData method and operate the 2nd part of the function.
    """
    ssurgo = 'SU_average_weighted\\'
    statsgo = 'ST_average_weighted\\'
    #original files used to convert to standard noData value
    file_a = root + ssurgo + 'SSURGO_'+prop+'_5cm_Raster_1.tif'
    file_b = root + ssurgo + 'SSURGO_'+prop+'_5cm_Raster_2.tif'
    file_c = root + statsgo + 'STATSGO_'+prop+'_5cm_Raster.tif'
    #actual .tiff that are used to operate merging
    tiff_a = root + ssurgo + 'SSURGO_'+prop+'_5cm_Raster_1_n.tif'
    tiff_b = root + ssurgo + 'SSURGO_'+prop+'_5cm_Raster_2_n.tif'
    tiff_o = root + ssurgo + 'SSURGO_'+prop+'_5cm_Raster_New_n.tif'
    tiff_c = root + statsgo + 'STATSGO_'+prop+'_5cm_Raster_n.tif'
    #reset noData value
    warp1 = 'gdalwarp -dstnodata -9999 {a} {b}'.format(a=file_a, b=tiff_a)
    warp2 = 'gdalwarp -dstnodata -9999 {a} {b}'.format(a = file_b, b = tiff_b)
    warp3 = 'gdalwarp -dstnodata -9999 {a} {b}'.format(a=file_c, b=tiff_c)
    call(warp1)
    call(warp2)
    call(warp3)
    print('Done processes with resetting noData value of property {}'.format(prop))
    #merge ssurgo
    os.system('python D:\Anaconda2\Scripts\gdal_merge.py -n -9999 -a_nodata -9999  -of GTiff -o {a} {b} {c}'.format(a= tiff_o, b= tiff_a, c= tiff_b))
    print('Done processes with merging SSURGO of property {}'.format(prop))

    #here manually extract noData masks for each properties

projection = 26913  # NAD83 UTM Zone 12 North
x_min = 114757
y_min = 3471163
x_max = 682757
y_max = 4102413
cols = 2272
rows = 2525
resample_method = 'near'
cell_size = 250
root = 'H:\\NewMexico\\DirectSoilData\\'
prop = 'gcmBD3rdbar'

def merge_operator_2(prop):
    statsgo = 'ST_average_weighted\\'
    #mask = root + 'noData\\' + prop + '.shp'
    tiff_c = root + statsgo + 'STATSGO_' + prop + '_5cm_Raster_n.tif'
    tiff_cc = root + statsgo + 'STATSGO_' + prop + '_5cm_Raster_cut.tif'
    trans_0 = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
              ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                               h=resample_method, j=tiff_c, k=tiff_cc)
    call(trans_0)
    #trans_00 = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
               #' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                                #h=resample_method, j=mask, k=mask_c)
    #call(trans_00)
    #clip = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -cutline {i} {j} {k}'.format(a=projection, i=mask_c,
                                                                                             #j=tiff_cc, k=tiff_d)
    #call(clip)


def merge_operator_3(prop):
    #clip STATSGO
    ssurgo = 'SU_average_weighted\\'
    #statsgo = 'ST_average_weighted\\'
    statsgo = 'Clipped_nobuffer\\'



    #tiff_d = root + statsgo + 'Clipped_' + prop + '_5cm_Raster.tif'
    tiff_e = root + statsgo + 'Clipped_' + prop + '_5cm_Raster_cut.tif'
    tiff_o = root + ssurgo + 'SSURGO_' + prop + '_5cm_Raster_New_n.tif'
    tiff_oe = root + ssurgo + 'SSURGO_' + prop + '_5cm_Raster_New_cut.tif'

    #even the clip line doesn't work, warp before merge
    #trans_1 = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
         # ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                           #h=resample_method, j=tiff_d, k=tiff_e)
    #call(trans_1)
    trans_2 = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
          ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                           h=resample_method, j=tiff_o, k=tiff_oe)
    call(trans_2)
    #merge SSURGO and STATSGO
    merge = 'Merge_New\\'
    tiff_n = root + merge + 'Merged_' + prop + '_5cm_Raster_n.tif'

    os.system(
        'python D:\Anaconda2\Scripts\gdal_merge.py -n -9999 -a_nodata -9999  -of GTiff -o {a} {b} {c}'.format(a=tiff_n,
                                                                                                              b=tiff_oe,
                                                                                                              c=tiff_e))
    #clip to fit the model
    tiff = root + merge + 'Merged_' + prop + '_5cm_Raster.tif'
    fin = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                            h=resample_method, j=tiff_n, k=tiff)
    call(fin)




prop = 'gcmBD3rdbar'
raster_merge(prop)
prop = 'OrgMatter'
raster_merge(prop)
prop = 'percClay'
raster_merge(prop)
prop = 'percSand'
raster_merge(prop)
prop = 'percSilt'
raster_merge(prop)
prop = 'umsKsat'
raster_merge(prop)
prop = 'WC3rdbar'
raster_merge(prop)





import os, fnmatch
from subprocess import call


root = 'H:\\NewMexico\\DirectSoilData\\'
prop = 'gcmBD3rdbar'
def raster_merge(prop):
    ssurgo = 'SU_average_weighted\\'
    statsgo = 'ST_average_weighted\\'
    merge = 'Merge_Fin\\'

    a = root + statsgo + 'STATSGO_' + prop + '_5cm_Raster_n.tif'
    b = root + ssurgo + 'SSURGO_' + prop + '_5cm_Raster_New_n.tif'
    #C: / Users / Esther / Desktop / Merged_percSand_5cm_Raster_New_te.tif
    #C:\Users\Esther\Desktop\STATSGO_percSand_5cm_Raster_cut.tif
    #C:\Users\Esther\Desktop\SSURGO_percSand_5cm_Raster_New_n.tif
    #tiff_n = 'C:/Users/Esther/Desktop/Merged_percSand_5cm_Raster_New_te.tif'
    #tiff = 'C:/Users/Esther/Desktop/Merged_percSand_5cm_Raster_New_tet.tif'
    tiff_n = root + merge + 'Merged_' + prop + '_5cm_Raster_n.tif'
    tiff = root + merge + 'Merged_' + prop + '_5cm_Raster.tif'
    os.system(
        'python D:\Anaconda2\Scripts\gdal_merge.py -n -9999 -a_nodata -9999 -of GTiff -o {a} {b} {c}'.format(a = tiff_n, b = a, c = b))
    # clip to fit the model
    fin = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
      ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                       h='near', j=tiff_n, k=tiff)
    call(fin)
