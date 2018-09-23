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
import os

#from etrm.raster_tools import convert_raster_to_array
from collections import defaultdict

import numpy as np
import pandas as pd

from osgeo import gdal, ogr
import struct

# ============= local library imports ===========================

def pathlist_make(pixel_dir):
    """

    :param pixel_dir:
    :return:

    gets the directory where the pixel rasters are and returns a list of the full file paths for each
    raster in the directory
    """

    # grab the files in the directory
    for files in os.walk(pixel_dir, topdown=True):
        for name in files:
            file_list = name

    # remove the non-tiff files
    for file in file_list:
        if not file.endswith('.tif'):
            file_list.remove(file)
    #print 'file list', file_list
    path_list = [os.path.join(pixel_dir, item) for item in file_list]
    #print 'path list', path_list

    return path_list

def dict_maker(directory_list):
    """
    uses the list of file directories constructed by pathlist_make(),
    In the case of the obs and model results, merely returns a dict of file name and path for later use.

    :return:
    """
    location_dict = {}

    # cut out lines here

    if 'rzsm_u_' in directory_list[0]:
        for item in directory_list:
            item_list = item.split('.')
            sel = item_list[0]
            label = sel[-20:]

            location_dict[label] = item

        #print 'rzsm obs location dict', location_dict
        return location_dict

    elif 'rzsm_' in directory_list[0]:
        for item in directory_list:
            item_list = item.split('.')
            sel = item_list[0]
            label = sel[-19:] # TODO - we need format to be rzsm_dd_mm_yyy_###

            location_dict[label] = item

        #print 'rzsm simulation location dict', location_dict
        return location_dict

def shape_ext_func(pixel, dict, key, item):
    """
    ====== Credit for this code comes from
    ====https://gis.stackexchange.com/questions/46893/getting-pixel-value-of-gdal-raster-under-ogr-point-without-numpy
    accessed on June 24, 2017
    :param pixel:
    :param dict:
    :param key:
    :param item:
    :return:
    """

    src_ds = gdal.Open(dict[key])
    gt = src_ds.GetGeoTransform()
    rb = src_ds.GetRasterBand(1)

    ds = ogr.Open(pixel)
    lyr = ds.GetLayer()
    pix_value_list = []
    count = 0
    pix_value_dict = {}
    for feat in lyr:
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()  # coord in map units

        # Convert from map to pixel coordinates.
        # Only works for geotransforms with no rotation.
        px = int((mx - gt[0]) / gt[1])  # x pixel
        py = int((my - gt[3]) / gt[5])  # y pixel

        structval = rb.ReadRaster(px, py, 1, 1,
                                  buf_type=gdal.GDT_Float32)  # Assumes 16 bit int aka 'short', buf_type=gdal.GDT_UInt16

        intval = struct.unpack('f', structval)  # use the 'short' format code (2 bytes) not int (4 bytes)
        #print 'intval', intval[0]  # intval is a tuple, length=1 as we only asked for 1 pixel value
        pix_value_list.append(intval[0])
        pix_value_dict[count] = intval[0]
        count += 1
    #return pix_value_dict
    return pix_value_list


def value_extract(pixel_file, obs_dir_dict, model_dir_dict):
    """
    :param pixel_file:
    :param obs_dir_dict:
    :param model_dir_dict:
    :return:
    """
    obs_value_dict = {}
    model_value_dict = {}
    for key, item in obs_dir_dict.items():

        observations = shape_ext_func(pixel_file, obs_dir_dict, key, item)
        obs_value_dict[key] = observations
    #print 'obs_value Dictionary', obs_value_dict

    for a, b in model_dir_dict.items():
        results = shape_ext_func(pixel_file, model_dir_dict, a, b)
        model_value_dict[a] = results
    #print 'model_value Dictionary', model_value_dict
    return obs_value_dict, model_value_dict

def dict_combine(list):

    """
    This function came from-
    https://stackoverflow.com/questions/20072870/combining-two-dictionaries-into-one-with-the-same-keys
    :param list:
    :return:
    """

    result = {}
    for dic in list:
        for key in (result.viewkeys() | dic.keys()):
            if key in dic:
                result.setdefault(key, []).append(dic[key])
    return result


def formatter(obs, model):
    combined_list = []
    obs_value_list = []
    mod_value_list = []
    for key, item in obs.items():

        #print 'key', key
        #print 'item', item
        count_1 = 0
        obs_dict = {}
        for value in item:
            obs_dict['pixel_{}'.format(count_1)] = (key, item[count_1]) # used to be tuple
            count_1 += 1
        obs_value_list.append(obs_dict)

    final_obs = dict_combine(obs_value_list)

    #print 'final obs', final_obs

    for a, b in model.items():

        count_2 = 0
        mod_dict = {}
        for value in b:
            mod_dict['pixel_{}'.format(count_2)] = (a, b[count_2])
            count_2 += 1
        mod_value_list.append(mod_dict)

    final_mod = dict_combine(mod_value_list)

    #print 'final model ', final_mod

    #combined_list.append(final_mod)
    #combined_list.append(final_obs)

    #print 'combined list', combined_list
    return final_mod, final_obs


def frameit(mod_dict, obs_dict):
    """
    takes list of
    :param list:
    :return:
    """

    mod_list = []
    obs_list = []
    obs = {}
    mod = {}
    together_frame = {}

    for pixel, tuple_list in mod_dict.items():

        print(pixel)

        tuple_list_sort = sorted(tuple_list, key = lambda tup: tup[0])
        tuple_list_sort = sorted(tuple_list_sort, key = lambda tup: tup[0][-1])
        #yay

        df_mod = pd.DataFrame(tuple_list_sort)

        #print 'df', df_mod

        rev_dfmod = df_mod.iloc[::-1]

        mod[pixel] = rev_dfmod

    for pixel, tuple_list in obs_dict.items():

        print(pixel)
        tuple_list_sort = sorted(tuple_list, key=lambda tup: tup[0])
        #tuple_list_sort = sorted(tuple_list_sort, key=lambda tup: tup[0][-1])
        # yay

        df_obs = pd.DataFrame(tuple_list_sort)

        #print 'df obs', df_obs

        #=== HERE I reverse the order bc of how my plotting program is set up.
        rev_dfobs = df_obs.iloc[::-1]

        obs[pixel] = rev_dfobs

        #obs_list.append(obs)

    #print 'obs list', obs_list
    #print 'obs', obs

    for pixel, dat_f in mod.items():

        frame = pd.concat([dat_f, obs[pixel]])

        together_frame[pixel] = frame

    print('together frame', together_frame)
    return together_frame

def xml_write(frame_dict):
    """
    Takes a dataframe and writes to excel. This is the main output of this script.
    The output xml is used by a plotting script.
    """

    for pixel in frame_dict.keys():

        #print 'pixel contents -----', frame_dict[pixel]

        pd.DataFrame.to_csv(frame_dict[pixel], '/Users/Gabe/Desktop/RZSM_analysis/pixels_6/{}.csv'.format(pixel), index=False, header=None)


def run():
    """
    takes a pixel mask, or a list of pixel masks

    takes model output rasters

    grabs the pixels corresponding to the mask that are in the rasters

    puts the pixels into a dataframe and or nested dict.

    ***** Changes should be made to soil_moisture_mapper also *****

    """

    print('my hairy butt')

    # get pixel shapefile
    pixel_file = "/Users/Gabe/Desktop/pixel_masks/pixel_shapefile.shp"

    #=====Get observations from somewhere.=======
    obs_dir = "/Users/Gabe/Desktop/rzsm_observations_updated"
    obs_directory_list = pathlist_make(obs_dir)
    obs_dir_dict = dict_maker(obs_directory_list)

    #=====Get modeled results from somewhere.====
    model_dir = "/Users/Gabe/Desktop/modeled_rzsm"
    model_dir_list = pathlist_make(model_dir)
    model_dir_dict = dict_maker(model_dir_list)
    #print 'model dir dict', model_dir_dict

    obs_value_dict, model_value_dict = value_extract(pixel_file, obs_dir_dict, model_dir_dict)

    final_mod, final_obs = formatter(obs_value_dict, model_value_dict) # should return a list of pixel by pixel dataframes

    frame_dict = frameit(final_mod, final_obs)



    # TODO - func to write frames to xml and save so pixel_plotter can work w em.

    xml_write(frame_dict)


if __name__ == "__main__":
    run()