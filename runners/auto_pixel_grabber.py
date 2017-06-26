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

#from recharge.raster_tools import convert_raster_to_array
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
            label = sel[-19:]

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

        print pixel

        tuple_list_sort = sorted(tuple_list, key = lambda tup: tup[0])
        tuple_list_sort = sorted(tuple_list_sort, key = lambda tup: tup[0][-1])
        #yay

        df_mod = pd.DataFrame(tuple_list_sort)

        print 'df', df_mod

        mod[pixel] = df_mod

    for pixel, tuple_list in obs_dict.items():

        print pixel
        tuple_list_sort = sorted(tuple_list, key=lambda tup: tup[0])
        #tuple_list_sort = sorted(tuple_list_sort, key=lambda tup: tup[0][-1])
        # yay

        df_obs = pd.DataFrame(tuple_list_sort)

        print 'df obs', df_obs

        obs[pixel] = df_obs

        #obs_list.append(obs)

    #print 'obs list', obs_list
    print 'obs', obs

    for pixel, dat_f in mod.items():

        frame = pd.concat([dat_f, obs[pixel]])

        together_frame[pixel] = frame

    print together_frame
    return together_frame


def run():

    print 'my hairy butt'

    # get pixel shapefile
    pixel_file = "/Users/Gabe/Desktop/pixel_masks/pixel_point_0.shp"

    #=====Get observations from somewhere.=======
    obs_dir = "/Users/Gabe/Desktop/rzsm_observations"
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


if __name__ == "__main__":
    run()


#==========================================
"""
takes a pixel mask, or a list of pixel masks

takes model output rasters

grabs the pixels corresponding to the mask that are in the rasters

puts the pixels into a dataframe and or nested dict.

***** Changes should be made to soil_moisture_mapper also *****

"""



#++++++=========== Saved Changes June 24, 2017 bc of switch to GDAL based Design

# def pathlist_make(pixel_dir):
#     """
#
#     :param pixel_dir:
#     :return:
#
#     gets the directory where the pixel rasters are and returns a list of the full file paths for each
#     raster in the directory
#     """
#     # grab the files in the directory
#     for files in os.walk(pixel_dir, topdown=True):
#         for name in files:
#             file_list = name
#
#     # remove the non-tiff files
#     for file in file_list:
#         if not file.endswith('.tif'):
#             file_list.remove(file)
#     print 'file list', file_list
#     path_list = [os.path.join(pixel_dir, item) for item in file_list]
#     print 'path list', path_list
#
#     return path_list
#
# def location_grab(directory_list):
#     """
#     uses the list of file directories constructed by pathlist_make(), turns the .tif into an array.
#     Gets the location(s?) of the non-zero value of the array.
#     Returns a dict of array locations.
#     In the case of the obs and model results, merely returns a dict of file name and path for later use.
#
#     :return:
#     """
#     location_dict = {}
#
#     # gonna look like {pixel_00: location, pixel_01:location}
#     if 'pixel_rast' in directory_list[0]:
#         for item in directory_list:
#             array = convert_raster_to_array(item)
#             item_list = item.split('.')
#             print 'item_list', item_list
#             sel = item_list[0]
#             label = sel[-13:]
#             # label is the title for the dict
#
#             # print 'array', array
#             # print'shape of the array', array.shape
#
#             location = np.where(array == 1)
#             print 'location', location
#             #add the label and location to the dict
#             location_dict[label] = location
#
#         print 'location dict', location_dict
#         return location_dict
#
#     elif 'rzsm_u_' in directory_list[0]:
#         for item in directory_list:
#             item_list = item.split('.')
#             sel = item_list[0]
#             label = sel[-19:]
#
#             location_dict[label] = item
#
#         #print 'rzsm obs location dict', location_dict
#         return location_dict
#
#     elif 'rzsm_' in directory_list[0]:
#         for item in directory_list:
#             item_list = item.split('.')
#             sel = item_list[0]
#             label = sel[-18:]
#
#             location_dict[label] = item
#
#         #print 'rzsm simulation location dict', location_dict
#         return location_dict
#
# def array_converter(dict_of_paths):
#     """
#     :param dict_of_paths:
#     :return:
#
#     Takes the paths for files that need to be converted into arrays.
#     The arrays are stored in a dict with the same keys as the dict of paths.
#     """
#     array_dict = {}
#     for name, path in dict_of_paths.items():
#         array = convert_raster_to_array(path)
#         array_dict[name] = array
#
#     print 'array dict! ', array_dict
#     return array_dict
#
# def value_packer(pixel, obs, model):
#     """
#     Gets the model array and
#     :param pixel:
#     :param obs:
#     :param model:
#     :return:
#     """
#     # master = {}
#     # for each pixel location
#
#         # for each obs value
#             # get value at location (HOW?)
#             # store value master[obskey] = value
#
#         # for each model value
#             # get value at location
#             # store value master[modelskey] = value
#
#     # return master
#
#     master = {}
#
#     for pixel, location in pixel.items():
#
#         # for observ, obs_arr in obs.items():
#         #
#         #     print obs_arr.shape
#         #
#         #     master[pixel][observ] = obs_arr[location]
#
#         for mod, mod_arr in model.items():
#
#             master[mod] = mod_arr[location]
#
#     return master
#
#
# def run():
#
#     pixel_dir = "/Users/Gabe/Desktop/pixel_masks"
#
#     #=====Get observations from somewhere.=======
#     obs_dir = "/Users/Gabe/Desktop/rzsm_observations"
#     obs_directory_list = pathlist_make(obs_dir)
#     obs_dir_dict = location_grab(obs_directory_list)
#
#     #=====Get modeled results from somewhere.====
#     model_dir = "/Users/Gabe/Desktop/modeled_rzsm"
#     model_dir_list = pathlist_make(model_dir)
#     model_dir_dict = location_grab(model_dir_list)
#
#     #===Get the obs and modeled results stored in a dict of arrays.====
#     #==================================================================
#     #==== Obs Arrays =======
#     obs_arr_dict = array_converter(obs_dir_dict)
#     #==== Modeled Arrays ===
#     model_arr_dict = array_converter(model_dir_dict)
#
#     #===== Make a location dict for the array locations of data you need
#     pixel_directory_list = pathlist_make(pixel_dir)
#     location_dict = location_grab(pixel_directory_list)
#
#     #use location dict to grab the right values from the Observations and Model Results
#     #store the values you get in a good format in a pixel by pixel dataframe.
#     master_dict = value_packer(location_dict, obs_arr_dict, model_arr_dict)
#     # TODO fix master dict for
#
#     print 'master dictionary', master_dict
#
#
#
#
# if __name__ == "__main__":
#     run()
#
#     #one_to_one_plotter()


#======= Save of 'formatter()' func June 25, 2017 =======
# def formatter(obs, model):
#
#     print 'len mod', len(model['rzsm_13_06_2004_000'])
#     iterate = len(model['rzsm_13_06_2004_000'])
#     obs_pixel_dict = {}
#     mod_pixel_dict = {}
#     obs_dict_list = []
#     mod_dict_list = []
#     count_1 = 0
#     count_2 = 0
#     key_dict = {}
#     a_dict = {}
#
#     # for i in range(iterate):
#     #     key_dict = {}
#     #     a_dict = {}
#
#     for key, item in obs.items():
#
#         print 'key', key
#         print 'item', item
#
#         #obs_pixel_dict = {'pixel_{}'.format(count_1):{key:item}}
#         key_dict[key] = item
#         ins_obs = key_dict
#
#         print 'ins obs', ins_obs
#
#         obs_pixel_dict['pixel_{}'.format(count_1)] = ins_obs
#
#         obs_dict_list.append(obs_pixel_dict)
#
#     count_1 += 1
#     # TODO - ^^^ Fix below to be like above ^^^^
#     # TODO - Need {pixel_0:{rzsm:{0: value, 1: value, 2: value} - You're going about it wrong.
#     # TODO - idea -> Instead of fucking around with dictionaries, go to DF and manipulate the DF.
#     for a, b in model.items():
#
#         #model_pixel_dict = {'pixel_{}'.format(count_2):{a:b}}
#
#         ins_mod = a_dict[key] = b
#
#         mod_pixel_dict['pixel_{}'.format(count_1)] = ins_mod
#
#         mod_dict_list.append(mod_pixel_dict)
#
#     count_2 += 1
#
#     print 'obs dict list', obs_dict_list
#
#     print 'mod_dict_list', mod_dict_list