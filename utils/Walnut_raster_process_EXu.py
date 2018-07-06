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
projection = 26912  # NAD83 UTM Zone 12 North
x_min = 576863
y_min = 3501109
x_max = 637613
y_max = 3519609
cols = 2430
rows = 740
cell_size = 250
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

#Walnut Gulch Soil Properties rasters merge
'''The files in Walnut Gulch are originally set noData Value of -9999
    The Projection is 26912 NAD83 Zone12'''
root = 'H:\\Walnut\\'

projection = 26912  # NAD83 UTM Zone 12 North
x_min = 576863
y_min = 3501109
x_max = 637613
y_max = 3519609
cols = 2430
rows = 740
cell_size = 250
resample_method = 'near'

def Walnut_Raster_Op(root,prop):
    #folders
    input_folder = 'WalnutExtractedNew\\'
    output_folder = 'WalnutSoilProperties\\'
    #first convert cut both SU and S to the same grid
    file_ua = root + input_folder + 'SU_'+prop+'.tif'
    file_ub = root + input_folder + 'SU_'+prop+'_cut.tif'
    file_ta = root + input_folder + 'ST_'+prop+'.tif'
    file_tb = root + input_folder + 'ST_'+prop+'_cut.tif'
    warp_u = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -tr {i} {i}\n' \
             ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max,
                                              h=resample_method, i=cell_size,j=file_ua, k=file_ub)
    call(warp_u)
    warp_t = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -tr {i} {i}\n' \
             ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max,
                                              h=resample_method, i = cell_size, j=file_ta, k=file_tb)
    call(warp_t)
    #Then, merge them
    tiff_m = root + output_folder + 'Merged_' + prop + '_m.tif'
    os.system(
        'python D:\Anaconda2\Scripts\gdal_merge.py -n -9999 -a_nodata -9999  -of GTiff -o {a} {b} {c}'.format(a=tiff_m,
                                                                                                              b=file_tb,
                                                                                                              c=file_ub))
    #Warp to standardized
    tiff = root + output_folder + 'Merged_' + prop + '.tif'
    warp_f = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -tr {i} {i}\n' \
             ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max,
                                              h=resample_method, i = cell_size, j=tiff_m, k=tiff)
    call(warp_f)


#runner

prop = 'gcmBD3rdbar'
Walnut_Raster_Op(root,prop)
prop = 'OrgMatter'
Walnut_Raster_Op(root,prop)
prop = 'percClay'
Walnut_Raster_Op(root,prop)
prop = 'percSand'
Walnut_Raster_Op(root,prop)
prop = 'percSilt'
Walnut_Raster_Op(root,prop)
prop = 'umsKsat'
Walnut_Raster_Op(root,prop)
prop = 'WC3rdbar'
Walnut_Raster_Op(root,prop)


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

projection = 26913  # NAD83 UTM Zone 13 North
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



    ######
    #Walnut Gulch




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


#=============================================
#Walnut
import os, fnmatch
from subprocess import call

input_folder = 'G:\\ETRM_inputs_Walnut\\PM_RAD_New'
projection = 26912  # NAD83 UTM Zone 12 North
x_min = 576863
y_min = 3501109
x_max = 637613
y_max = 3519609
cols = 243
rows = 74
resample_method = 'near'
x_min_n = 576863+250
y_min_n = 3501109+500
#x_min_n = 577113
#y_min_n = 3501609

cols_n = 243-1
rows_n = 74-2
def find_format(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            yield file_
input_folder = 'G:\\ETRM_inputs_Walnut\\PM_RAD_New\\'
files = os.listdir(input_folder)
for it in files:
    in_folder = input_folder+it
    in_folder = 'G:\\ETRM_inputs_Walnut\\PM2000\\'
    os.chdir(in_folder)
    for raster in find_format(in_folder, '*.tif'):
        FOLDER,r_name = os.path.split(raster)
        tiff = r_name
        temp = "temp.tif"
        reprojection = 'gdalwarp -overwrite -s_srs EPSG:4326 -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
         ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                       h=resample_method, j=tiff, k=temp)
        call(reprojection)
        cut = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
         ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                       h=resample_method, j=temp, k=tiff)
        call(cut)


#=============================================
#NDVI
import os, fnmatch
from subprocess import call
from recharge.raster_tools import convert_raster_to_array
from recharge.raster_tools import convert_array_to_raster
from recharge.raster_tools import get_raster_geo_attributes
input_folder = 'G:\\ETRM_inputs_Walnut\\NDVI\\NDVI_Real\\'
files = os.listdir(input_folder)
root = "G:\\ETRM_inputs_Walnut\\PM_RAD\\PM2000\\"
for it in files:
    in_folder = input_folder+it+"\\"
    os.chdir(in_folder)
    for raster in find_format(in_folder, '*.tif'):
        FOLDER,r_name = os.path.split(raster)
        tiff = r_name
        temp = "temp.tif"
        cut = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
         ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                       h=resample_method, j=tiff, k=temp)
        call(cut)
        ndvi = convert_raster_to_array(in_folder, temp)
        arr = ndvi*0.0001

        geo = get_raster_geo_attributes(root)
        output_path = in_folder+tiff

        convert_array_to_raster(output_path, arr, geo, output_band=1)

###=========================
#Prism


#=============================================
#Walnut
import os, fnmatch
from subprocess import call

input_folder = 'G:\\ETRM_inputs_Walnut\\PM_RAD_New'
projection = 26912  # NAD83 UTM Zone 12 North
x_min = 576863
y_min = 3501109
x_max = 637613
y_max = 3519609
cols = 243
rows = 74
resample_method = 'near'
x_min_n = 576863+250
y_min_n = 3501109+500
cols_n = 243-1
rows_n = 74-2
def find_format(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            yield file_

# input_folder = 'G:\\NMTECH_PRISM_UTM\\Walnut_Gulch\\ppt\\'
# input_folder = 'G:\\NMTECH_PRISM_UTM\\Walnut_Gulch\\tmax\\'
input_folder = 'G:\\NMTECH_PRISM_UTM\\Walnut_Gulch\\tmin\\'
# output_folder = 'G:\\ETRM_inputs_Walnut\\PRISM\\precip\\800m_std_all\\'
# output_folder = 'G:\\ETRM_inputs_Walnut\\PRISM\\Temp\\Maximum_standard\\'
output_folder = 'G:\\ETRM_inputs_Walnut\\PRISM\\Temp\\Minimum_standard\\'
files = os.listdir(input_folder)
for it in files:
    in_folder = input_folder+it+"\\"
    # in_folder = input_folder
    out_folder = output_folder+it+"\\"
    # out_folder = output_folder +"2000\\"
    os.chdir(in_folder)
    for raster in find_format(in_folder, '*.tif'):
        FOLDER,r_name = os.path.split(raster)
        tiff = r_name
        temp = "temp.tif"
        cut = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
         ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                       h=resample_method, j=tiff, k=temp)
        call(cut)
        # tiff_n = out_folder+"Walnut_precip_" + r_name[-12:-4]+".tiff"
        # warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
        #     ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
        #                                    h=resample_method, j=temp, k=tiff_n)
        # call(warp)

        # tiff_n = out_folder + "Walnut_MaxTemp_" + r_name[-12:-4] + ".tiff"
        # warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
        #    ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
        #                                     h=resample_method, j=temp, k=tiff_n)
        # call(warp)

        tiff_n = out_folder + "Walnut_MinTemp_" + r_name[-12:-4] + ".tiff"
        warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
            ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                        h=resample_method, j=temp, k=tiff_n)
        call(warp)



#------------------------------
#For statics
in_t = "H:\\WGEW\\ETRM_inputs\\statics\\Merge_TAW150cm_utm.tif"
out_t = "H:\\WGEW\\ETRM_inputs\\statics\\taw_Walnut_SoilDatabase.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h=resample_method, j=in_t, k=out_t)
call(warp)
taw= convert_raster_to_array("H:\\WGEW\\ETRM_inputs\\statics\\", "taw_Walnut_SoilDatabase.tif")
taw = 15*taw
dr = taw/2
geo = get_raster_geo_attributes("H:\\WGEW\\ETRM_inputs\\statics\\geo")
output_path1 = "H:\\WGEW\\ETRM_inputs\\statics\\taw_Walnut_mm.tif"
output_path2 = "H:\\WGEW\\ETRM_inputs\\statics\\dr_half_taw_mm.tif"
arr1 = taw
arr2 = dr
convert_array_to_raster(output_path1, arr1, geo, output_band=1)
convert_array_to_raster(output_path2, arr2, geo, output_band=1)

#tew===================
in_t = "H:\\WGEW\\ETRM_inputs\\statics\\Merge_fc_cmwater_10cm_utm.tif"
out_t = "H:\\WGEW\\ETRM_inputs\\statics\\fc_Walnut_SoilDatabase.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h=resample_method, j=in_t, k=out_t)
call(warp)
in_t = "H:\\WGEW\\ETRM_inputs\\statics\\Merge_wp_cmwater_10cm_utm.tif"
out_t = "H:\\WGEW\\ETRM_inputs\\statics\\wp_Walnut_SoilDatabase.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h=resample_method, j=in_t, k=out_t)
call(warp)
fc= convert_raster_to_array("H:\\WGEW\\ETRM_inputs\\statics\\", "fc_Walnut_SoilDatabase.tif")
wp= convert_raster_to_array("H:\\WGEW\\ETRM_inputs\\statics\\", "wp_Walnut_SoilDatabase.tif")
tew = (fc -0.5*wp)*100
de = tew/2
geo = get_raster_geo_attributes("H:\\WGEW\\ETRM_inputs\\statics\\geo")
output_path1 = "H:\\WGEW\\ETRM_inputs\\statics\\tew_Walnut_mm.tif"
output_path2 = "H:\\WGEW\\ETRM_inputs\\statics\\de_half_tew_mm.tif"
arr1 = tew
arr2 = de
convert_array_to_raster(output_path1, arr1, geo, output_band=1)
convert_array_to_raster(output_path2, arr2, geo, output_band=1)

in_t = "H:\\Walnut\\WalnutData\\Merge_percSand_5cm_utm.tif"
out_t = "H:\\WGEW\\ETRM_inputs\\statics\\percSand.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h=resample_method, j=in_t, k=out_t)
call(warp)
in_t = "H:\\Walnut\\WalnutData\\Merge_percClay_5cm_utm.tif"
out_t = "H:\\WGEW\\ETRM_inputs\\statics\\percClay.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h=resample_method, j=in_t, k=out_t)
call(warp)

sand= convert_raster_to_array("H:\\WGEW\\ETRM_inputs\\statics\\", "percSand.tif")
clay= convert_raster_to_array("H:\\WGEW\\ETRM_inputs\\statics\\", "percClay.tif")

idx_s_80 = sand>80
idx_c_50 = clay>50
rew = 8 + 0.08*clay

rew[idx_s_80] = 20-0.15*sand[idx_s_80]
rew[idx_c_50] = 11 - 0.06*clay[idx_c_50]
drew= rew/2
geo = get_raster_geo_attributes("H:\\WGEW\\ETRM_inputs\\statics\\geo")
output_path1 = "H:\\WGEW\\ETRM_inputs\\statics\\rew_Walnut_mm.tif"
output_path2 = "H:\\WGEW\\ETRM_inputs\\statics\\drew_half_rew_mm.tif"
arr1 = rew
arr2 = drew
convert_array_to_raster(output_path1, arr1, geo, output_band=1)
convert_array_to_raster(output_path2, arr2, geo, output_band=1)

















#-----------------------------------------------
#quaternary and mask
input_folder = 'G:\\ETRM_inputs_Walnut\\statics\\'
name = "quat_deps_0.tif"
inp = "G:\\ETRM_inputs_Walnut\\statics\\geo"
qua = convert_raster_to_array(input_folder, name)
arr = qua * 0
geo = get_raster_geo_attributes(inp)
output_path = input_folder + "quat_deps_0.tif"
convert_array_to_raster(output_path, arr, geo, output_band=1)
import numpy as np
output_path = 'G:\\ETRM_inputs_Walnut\\Mask\\mask_Walnut.tif'
arr = np.ones((geo['rows'],geo['cols']))
convert_array_to_raster(output_path, arr, geo, output_band=1)

#NLCD
#Set 30 m nearest sampling
resample_method = "near"
in_t = "H:\\WGEW\\nlcd_2006_landcover_2011_edition_2014_10_10\\nlcd_2006_landcover_2011_edition_2014_10_10.img"
out_t = "H:\\WGEW\\NLCD_Walnut_30.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:5070 -t_srs EPSG:26912 -te 576863 3501109 637613 3519619 -ts 2025 617\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h=resample_method, j=in_t, k=out_t)
call(warp)
nlcd = convert_raster_to_array("H:\\WGEW\\", "NLCD_Walnut_30.tif")
from collections import Counter
count_nlcd = Counter(nlcd.flatten())
idx_open_water = nlcd == 11 #17
idx_21 = nlcd == 21
idx_22 = nlcd == 22
idx_23 = nlcd == 23
idx_24 = nlcd == 24
idx_urban = idx_21+idx_22+idx_23+idx_24 #13
idx_barren = nlcd == 31 #16
idx_evergreen_forest = nlcd == 42 #2
idx_mixed_forest = nlcd == 43 #5
idx_shrub = nlcd == 52 #7
idx_grassland = nlcd == 71 #10
idx_81 = nlcd == 81
idx_82 = nlcd == 82
idx_crop = idx_81 + idx_82 #12
idx_90 = nlcd == 90
idx_95 = nlcd == 95
idx_wetland = idx_90 + idx_95 #17

vegetation_height=np.ones((617,2025))
root_depth=np.ones((617,2025))

vegetation_height[idx_open_water] = 0
root_depth[idx_open_water] = 1.3
vegetation_height[idx_urban] = 0
root_depth[idx_urban] = 0.001
vegetation_height[idx_barren] = (0.05+0.8)/2
root_depth[idx_barren] = 1.0
vegetation_height[idx_evergreen_forest] = 30.0
root_depth[idx_evergreen_forest] = 2.5
vegetation_height[idx_mixed_forest] = 20
root_depth[idx_mixed_forest] = 2.0
vegetation_height[idx_shrub] = 1.0
root_depth[idx_shrub] = 1.0
vegetation_height[idx_grassland] = (0.05+0.8)/2
root_depth[idx_grassland] = 0.5
vegetation_height[idx_crop] = (0.0+0.8)/2
root_depth[idx_crop] = 0.7
vegetation_height[idx_wetland] = (0.05+1.0)/2
root_depth[idx_wetland] = 1.0

geo = get_raster_geo_attributes("H:\\WGEW\\geo")
output_path1 = "H:\\WGEW\\plnt_hgt.tif"
output_path2 = "H:\\WGEW\\root_depth.tif"
arr1 = vegetation_height
arr2 = root_depth
convert_array_to_raster(output_path1, arr1, geo, output_band=1)
convert_array_to_raster(output_path2, arr2, geo, output_band=1)
in_t = "H:\\WGEW\\plnt_hgt.tif"
out_t = "H:\\WGEW\\plnt_hgt_250.tif"

warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h="average", j=in_t, k=out_t)
call(warp)
in_t = "H:\\WGEW\\root_depth.tif"
out_t = "H:\\WGEW\\root_depth_250.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h="average", j=in_t, k=out_t)
call(warp)


in_t = "H:\\Walnut\\Ksat.tif"
out_t = "H:\\WGEW\\Ksat_calculated_ums.tif"
warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h}  -multi {j} {k}'.format(a=projection, b=x_min_n, c=y_min_n, d=x_max, e=y_max, f=cols_n, g=rows_n,
                                            h="average", j=in_t, k=out_t)
call(warp)
gdalwarp -overwrite -s_srs EPSG:26912 -t_srs EPSG:26912 -te 577113 3501609 637613 3519609
-te 577113 3501609 637613 3519609 -tr 250 250
gdalwarp -overwrite -s_srs EPSG:26912 -te 577113 3501609 637613 3519609 -tr 250 250 -r max -of GTiff
#rasterize example to make mask
-te 114757 3471163 682757 4102413 -tr 250 250
#first step
gdal_rasterize -a id -te 577113 3501609 637613 3519609 -tr 1.0 1.0 -l r81 "G:/Observations/Precipitation/PRISM gauge/r81.shp" G:/Observations/Precipitation/81.tif


#-------------------------------------------------------------------
#-------------------------------------------------------------------
#-------------------------------------------------------------------
#New Mexico Initialize de dr drew

import os
from subprocess import call
from recharge.raster_tools import convert_raster_to_array
from recharge.raster_tools import convert_array_to_raster
from recharge.raster_tools import get_raster_geo_attributes

#dr
taw= convert_raster_to_array("H:\\ETRM_inputs\\statics\\", "taw_mod_4_21_10_0.tif")
dr = taw/2
geo = get_raster_geo_attributes("H:\\ETRM_inputs\\Blank_Geo")
output_path = "G:\\NewMexico\\dr_half_taw_mm.tif"
arr = dr
convert_array_to_raster(output_path, arr, geo, output_band=1)

#de===================
tew = convert_raster_to_array("H:\\ETRM_inputs\\statics\\", "tew_250_15apr.tif")
de = tew/2
geo = get_raster_geo_attributes("H:\\ETRM_inputs\\Blank_Geo")
output_path = "G:\\NewMexico\\de_half_tew_mm.tif"
arr = de
convert_array_to_raster(output_path, arr, geo, output_band=1)

#drew===================
rew = convert_raster_to_array("H:\\ETRM_inputs\\statics\\", "rew_22SEPT16.tif")
drew = rew/2
geo = get_raster_geo_attributes("H:\\ETRM_inputs\\Blank_Geo")
output_path = "G:\\NewMexico\\drew_half_rew_mm.tif"
arr = drew
convert_array_to_raster(output_path, arr, geo, output_band=1)

#===============================================================================
# process New Mexico rasters for thesis Chapter 2
root = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\NM rasters\\"
type = "eta"
#others like etrs,eta, infil, precip, ro
name0 = root + "tot_" + type + "_2000.tif"
name1 = root + "tot_" + type + "_2001.tif"
name2 = root + "tot_" + type + "_2002.tif"
name3 = root + "tot_" + type + "_2003.tif"
name4 = root + "tot_" + type + "_2004.tif"
name5 = root + "tot_" + type + "_2005.tif"
name6 = root + "tot_" + type + "_2006.tif"
name7 = root + "tot_" + type + "_2007.tif"
name8 = root + "tot_" + type + "_2008.tif"
name9 = root + "tot_" + type + "_2009.tif"
name10 = root + "tot_" + type + "_2010.tif"
name11 = root + "tot_" + type + "_2011.tif"
name12 = root + "tot_" + type + "_2012.tif"
name13 = root + "tot_" + type + "_2013.tif"
#------------------------------------------
yr0 = convert_raster_to_array(name0)
yr1 = convert_raster_to_array(name1)
yr2 = convert_raster_to_array(name2)
yr3 = convert_raster_to_array(name3)
yr4 = convert_raster_to_array(name4)
yr5 = convert_raster_to_array(name5)
yr6 = convert_raster_to_array(name6)
yr7 = convert_raster_to_array(name7)
yr8 = convert_raster_to_array(name8)
yr9 = convert_raster_to_array(name9)
yr10 = convert_raster_to_array(name10)
yr11 = convert_raster_to_array(name11)
yr12 = convert_raster_to_array(name12)
yr13 = convert_raster_to_array(name13)

total = (yr0+yr1+yr2+yr3+yr4+yr5+yr6+yr7+yr8+yr9+yr10+yr11+yr12+yr13)/14
geo = get_raster_geo_attributes("H:\\ETRM_inputs\\Blank_Geo")
output_path = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\"+type+".tif"
arr = total
convert_array_to_raster(output_path, arr, geo, output_band=1)

precip = convert_raster_to_array("C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\precip.tif")
ro = convert_raster_to_array("C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\ro.tif")
etrs = convert_raster_to_array("C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\etrs.tif")
infil = convert_raster_to_array("C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\infil.tif")
eta = convert_raster_to_array("C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\eta.tif")

geo = get_raster_geo_attributes("H:\\ETRM_inputs\\Blank_Geo")

output_path1 = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\ro_precent.tif"
output_path2 = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\etrs_precent.tif"
output_path3 = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\infil_precent.tif"
output_path4 = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 2\\eta_precent.tif"

arr1 =  precip * 0
arr1[precip > 0] = 100 * ro[precip > 0]/precip[precip > 0]
arr2 =  precip * 0
arr2[precip > 0] = 100 * etrs[precip > 0]/precip[precip > 0]
arr3 =  precip * 0
arr3[precip > 0] = 100 * infil[precip > 0]/precip[precip > 0]
arr4 =  precip * 0
arr4[precip > 0] = 100 * eta[precip > 0]/precip[precip > 0]

convert_array_to_raster(output_path1, arr1, geo, output_band=1)
convert_array_to_raster(output_path2, arr2, geo, output_band=1)
convert_array_to_raster(output_path3, arr3, geo, output_band=1)
convert_array_to_raster(output_path4, arr4, geo, output_band=1)