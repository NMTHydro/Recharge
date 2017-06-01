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

import pandas as pd
import numpy as np
import yaml

from app.config import Config
from app.paths import paths
from recharge.etrm_processes import Processes


from utils.pixel_coord_finder import coord_getter


from recharge.raster_tools import tiff_framer, get_mask, convert_array_to_raster, remake_array, get_raster_geo_attributes, apply_mask

# ============= local library imports ===========================

def get_dates(config_path):
    ""
    # read each yml section.

    with open(config_path, 'r') as rfile:
        try:
            yaml_thing = yaml.load(rfile)
                # print key, value
        except:
            print 'exception'
    #print "yaml thing", yaml_thing


    # pull out save dates list

    save_dates = yaml_thing['save_dates']

    # TODO - store in dict where keys are 000, 001, respectively
    # TODO - return the dict

    return save_dates

def get_file_date(filename):
    """
    Gets the date off the filename

    :param filename:
    :return:
    """
    #print 'getting file date'

    # remove.tif
    filename = filename.split('.')

    filename = filename[-2]

    #print 'filename sans tiff', filename

    filename = filename.split('_')

    #print 'filename', filename

    if len(filename)> 3:
        filtered_file = filename
        filename[-1]
        filedate = '{}_{}_{}'.format(filename[-3],filename[-2], filename[-1])
        #print 'filedate', filedate

    return filedate

def tiff_pathmaker(tiff_root):
    """
    inside a given directory
                #for files starting with 'de_'
                # get the dates of files and paths of files
                # store dates as keys and paths as values in a date_dict
                # store the date_dict in de dict
    # for files starting with 'dr_'
            # get the dates of files and paths of files
            # store the dates as keys and paths as values in date dict
            # store the date_dict in dr dict
        # for files starting with 'drew_'
            # get the dates of files and paths of files
            #store the dates as keys and paths as values in date dict
            #store the date_dict in drew_dicth

        # store de, dr and drew_dicts in a directory dict

    # return directory dict"""
    d = {}
    de_date_dict_list = []
    dr_date_dict_list = []
    drew_date_dict_list = []
    #de = {}
    # for each directory in tiff_root
    #print 'is this happening???'
    #print tiff_root
    n = 0
    for roots, dirs, files in os.walk(tiff_root, topdown=True):

        # TODO - build the nested dict
        print "roots", roots

        #roots = '00{}'.format(n)

        #print 'roots split', roots



        #d[roots] = {}

        #print dirs



        #de[]
        #===================================================
        for name in files:
            reldir = os.path.relpath(roots, tiff_root)
            relfile= os.path.join(reldir, name)
            if name.startswith('de_') and len(name.split('_')) > 3:

                file_date = get_file_date(name)
                #date values = '{}: {}'.format()
                date_dict = {'{}'.format(file_date): '{}'.format(os.path.join(tiff_root, relfile))}
                #d['dict{}'.format(n)]['de_dict'] = date_dict

                #print 'date dict', date_dict
                de_date_dict_list.append(date_dict)

                d['de'] = de_date_dict_list

            elif name.startswith('dr_') and len(name.split('_')) > 3:

                file_date = get_file_date(name)
                date_dict = {'{}'.format(file_date): '{}'.format(os.path.join(tiff_root, relfile))}

                dr_date_dict_list.append(date_dict)

                d['dr'] = dr_date_dict_list

            elif name.startswith('drew_') and len(name.split('_')) > 3:
                file_date = get_file_date(name)
                date_dict = {'{}'.format(file_date): '{}'.format(os.path.join(tiff_root, relfile))}

                drew_date_dict_list.append(date_dict)

                d['drew'] = drew_date_dict_list


    print 'de date dict list', de_date_dict_list
    print 'len of date dict list {}'.format(len(de_date_dict_list))
    print 'len dr date dict list', len(dr_date_dict_list)
    print 'len drew date dic list', len(drew_date_dict_list)

    print 'd', d

    return d


def framer_func(mask_path, tiff_paths, dates):

        # dates_list = make a dates list from dates dict

        # for subdirectory/taw_run in tiff_paths
            # pull out dr, de, drew paths matching given date in dates list

            # taw_date_dict = put list of new paths in a new subdirectory dict keys 001, 002 etc.

            # put taw_date_dict in date_taw_dict where keys are the corresponding date from date list

        # for date_dict in date_taw_dict
            # for taw_run in date_dict
                # tiff_list = list of paths stored inside.


                #tiff_frame = tiff_framer(mask_path, tiff_list)

                # tiff_frame_dict = store each tiff_frame in a {date:{taw_run1:tiff_frame, taw_run2: tiff_frame,
        # taw_run3: tiff_frame}, date2:{taw_run1:tiff_frame, taw_run2: tiff_frame, taw_run3: tiff_frame}}


        # return tiff frame dict .... or it could be a list w a dict inside
        pass


#
# def taw_func(root):
#     """Function gets a masked UNIFORM taw"""
#     #TODO- maybe just use dict_setup code to read in taw and modify.
#     #TODO- make an initialize taw function.
#
#     mask_path = os.path.join(root, 'Mask')
#     mask_arr = get_mask(mask_path)
#
#     northing, easting = coord_getter(os.path.join(mask_path, 'unioned_raster_output.tif'))
#
#     home = os.path.expanduser('~')
#     cp1 = os.path.join(home, 'ETRM_CONFIG.yml')
#
#     # uniform taw
#     cfg = Config(path=cp1)
#     for i, runspec in enumerate(cfg.runspecs):
#         # runspec1 = cfg1.runspecs[0]
#         paths.build(runspec.input_root, runspec.output_root)
#         etrm = Processes(runspec)
#         print 'config uniform_taw------->', runspec.uniform_taw
#         taw_u = etrm.uniform_taw(runspec.uniform_taw)
#         print 'uniform_taw array', taw_new
#         taw_u = remake_array(mask_path, taw_new)
#
#
#         columns = ['x', 'y', 'taw_uniform']
#         x_list = []
#         y_list = []
#         taw_u_list = []
#         nrows, ncols = taw_u.shape
#         for ri in xrange(nrows):
#             for ci in xrange(ncols):
#                 mask_values = mask_arr[ri, ci]
#                 if mask_values:
#                     # print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
#                     x_list.append('{}'.format(easting[ri, ci]))
#                     y_list.append('{}'.format(northing[ri, ci]))
#                     taw_u_list.append('{}'.format(taw_u[ri, ci]))
#
#         taw_data_dict = {'x': x_list, 'y': y_list, 'taw_uniform': taw_u_list}
#         taw_df = pd.DataFrame(taw_data_dict, columns=columns)
#
#     taw_i_dict = {i: taw_df}
#
#     print 'taw dataframe', taw_df
#     return taw_i_dict
#    pass


def run():

    # indented
    #------PATHS-------
    hard_drive_path = os.path.join('/', 'Volumes', 'Seagate Expansion Drive')
    inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')
    mp = os.path.join(inputs_path, 'Mask')
    mask_path = os.path.join(mp, 'unioned_raster_output.tif')  # mp, 'zuni_1.tif'
    config_path = "/Users/Gabe/ETRM_CONFIG.yml"
    tiff_root = '/Users/Gabe/Desktop/saved_etrm_desktop_outputs'


    # -----DATES-----
    dates = get_dates(config_path)
    #print 'dates list', dates


    # ------ TIFF DIRECTORIES --------
    # a function to get all the tiff_directories we want.
    tiff_pathmaker(tiff_root)
    #print 'tiff paths', tiff_paths



    # ----TIFFS----

    #tiff_dict = framer_func(mask_path, tiff_paths, dates)
    #print tiff_dict



    # ------ TAWS ------

    #taw_frame_dict = taw_func(inputs_path)

    # ------ RZSM = 1- (D/TAW) -------
    #rzsm_mapper(taw_frame_dict, taw_frame_dict, inputs_path, mask_path)



if __name__ == '__main__':
    run()

#=====================================================================================================================
#=====================================================================================================================
#=====================================================================================================================
#=====================================================================================================================

    # def rzsm_mapper(depletions_dict, taw_dict, inputs_path, mask_path):


    # """Root Zone Soil Mapper, which takes two dataframe objects, depletions, taw and gets soil moiture using
    #     RZSM = 1- (D/TAW) for each pixel of the model. The RZSM will be converted to an array and refitted into
    #     a map using convert_array_to_raster()"""
    #
    #     #de = depletions.as_matrix(columns='de') # why won't this work?
    #
    #     de = depletions.ix[:, 2]
    #     de = de.values.tolist()[0:]
    #     de = np.array(de)
    #     print 'de shape', de.shape
    #     print 'de', de
    #
    #     dr = depletions.ix[:, 3]
    #     dr = dr.values.tolist()[0:]
    #     dr = np.array(dr)
    #     print'dr shape', dr.shape
    #
    #     drew = depletions.ix[:, 4]
    #     drew = drew.values.tolist()[0:]
    #     drew = np.array(drew)
    #     print'drew shape', drew.shape
    #
    #
    #     d = de + dr + drew
    #     print 'depletion ->', d
    #     print 'depletion shape', d.shape
    #
    #     # TODO - you don't need an array for this. scalar will work.
    #     ones = np.ones(d.shape) # was 32787 now 3056 because the mask size changed you dummy!
    #
    #     taw_unmod = taw.ix[:, 2]
    #     taw_unmod = taw_unmod.values.tolist()[0:]
    #
    #     taw_unmod = [float(value) for value in taw_unmod]
    #     # for value in taw_unmod:
    #     #     value = int(value)
    #
    #     taw_unmod = np.array(taw_unmod)
    #     print 'taw_unmod shape', taw_unmod.shape
    #     print 'taw_unmod', taw_unmod
    #     quotient = (d/taw_unmod)
    #     print 'Quotient', quotient
    #     unmod_soil_arr = ones - quotient
    #     print 'unmodified rzsm array', unmod_soil_arr
    #
    #     #print 'taw shape', taw_unmod.shape
    #
    #     taw_mod = taw.ix[:, 3]
    #     taw_mod = taw_mod.values.tolist()[0:]
    #     taw_mod = [float(value) for value in taw_mod]
    #     taw_mod = np.array(taw_mod)
    #     quotient = d/taw_mod
    #     mod_soil_arr = ones - quotient
    #
    #     print 'modified rzsm array', mod_soil_arr
    #
    #
    #     # ---- Get Arrays Back into shape! -----
    #
    #     #print 'paths.static_inputs',
    #     # should be able to get the paths thing to work.
    #     #geo_path = Paths()
    #     geo_path = os.path.join(inputs_path, 'statics')
    #     geo_thing = get_raster_geo_attributes(geo_path)
    #     print 'GEO THING', geo_thing
    #     print 'unmod shape', unmod_soil_arr.shape
    #     print unmod_soil_arr
    #     unmod_soil_arr = remake_array(os.path.dirname(mask_path), unmod_soil_arr)
    #     convert_array_to_raster('/Users/Gabe/Desktop/gdal_raster_output/newtestfile.tif', unmod_soil_arr, geo_thing)


    #=======

    # # TODO - based on the date list, make a function that formats the tiff list.
    # # be mindful that under the new ETRM we don't have multiple depletions....
    # tiff_list = ['de_27_12_2013.tif', 'dr_27_12_2013.tif', 'drew_27_12_2013.tif']
    # tiff_list = [os.path.join(tiff_root, i) for i in tiff_list]
    # tiff_frame = tiff_framer(mask_path, tiff_list)


    # ---- TAW ----------
    # TODO - needs to be a list of TAW's grabbed from the config file. Change taw_func...
    #taw_df, taw_data_dict = taw_func(inputs_path)

    # ----- Take Stock ----
    # tiff_frame.to_excel('/Users/Gabe/Desktop/tiff_frame.xls')
    # taw_df.to_excel('/Users/Gabe/Desktop/taw_df.xls')

    # ------ RZSM = 1- (D/TAW) -------
    # rzsm_mapper(tiff_frame, taw_df, inputs_path, mask_path)



    # def taw_func(root):
#     """Function gets a masked original taw and a masked modified taw"""
#     #TODO- maybe just use dict_setup code to read in taw and modify.
#     #TODO- make an initialize taw function.
#
#     mask_path = os.path.join(root, 'Mask')
#     mask_arr = get_mask(mask_path)
#
#     northing, easting = coord_getter(os.path.join(mask_path, 'unioned_raster_output.tif'))
#
#     home = os.path.expanduser('~')
#     #cp1 = os.path.join(home, 'ETRM_CONFIG_TAW.yml') # for a modified taw
#     cp1 = os.path.join(home, 'ETRM_CONFIG.yml')  # for an unmodified taw
#
#     # modified taw
#     cfg1 = Config(path=cp1)
#     runspec1 = cfg1.runspecs[0]
#     paths.build(runspec1.input_root, runspec1.output_root)
#     etrm_new = Processes(runspec1)
#     print 'config taw_mod------->', runspec1.taw_modification
#     taw_new = etrm_new.modify_taw(runspec1.taw_modification)
#     print 'new taw newwww', taw_new
#     taw_new = remake_array(mask_path, taw_new)
#
#     # unmodified taw
#
#     runspec2 = cfg1.runspecs[1]
#     etrm_unmod = Processes(runspec2)
#     print "etrm taw shape ---->>> ", etrm_unmod.get_taw().shape
#     taw_unmod = etrm_unmod.get_taw()
#     taw_unmod = remake_array(mask_path, taw_unmod)
#
#     columns = ['x', 'y', 'taw_unmodified', 'taw_new']
#     x_list = []
#     y_list = []
#     taw_unmodified_list = []
#     taw_new_list = []
#     nrows, ncols = taw_new.shape
#     for ri in xrange(nrows):
#         for ci in xrange(ncols):
#             mask_values = mask_arr[ri, ci]
#             if mask_values:
#                 # print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
#                 x_list.append('{}'.format(easting[ri, ci]))
#                 y_list.append('{}'.format(northing[ri, ci]))
#                 taw_unmodified_list.append('{}'.format(taw_unmod[ri, ci]))
#                 taw_new_list.append('{}'.format(taw_new[ri, ci]))
#
#     taw_data_dict = {'x': x_list, 'y': y_list, 'taw_unmodified': taw_unmodified_list, 'taw_new': taw_new_list}
#     taw_df = pd.DataFrame(taw_data_dict, columns=columns)
#
#     #print 'taw dataframe', taw_df
#     return taw_df, taw_data_dict
#
#
# def rzsm_mapper(depletions, taw, inputs_path, mask_path):
#     """Root Zone Soil Mapper, which takes two dataframe objects, depletions, taw and gets soil moiture using
#     RZSM = 1- (D/TAW) for each pixel of the model. The RZSM will be converted to an array and refitted into
#     a map using convert_array_to_raster()"""
#
#     #de = depletions.as_matrix(columns='de') # why won't this work?
#
#     de = depletions.ix[:, 2]
#     de = de.values.tolist()[0:]
#     de = np.array(de)
#     print 'de shape', de.shape
#     print 'de', de
#
#     dr = depletions.ix[:, 3]
#     dr = dr.values.tolist()[0:]
#     dr = np.array(dr)
#     print'dr shape', dr.shape
#
#     drew = depletions.ix[:, 4]
#     drew = drew.values.tolist()[0:]
#     drew = np.array(drew)
#     print'drew shape', drew.shape
#
#
#     d = de + dr + drew
#     print 'depletion ->', d
#     print 'depletion shape', d.shape
#
#     # TODO - you don't need an array for this. scalar will work.
#     ones = np.ones(d.shape) # was 32787 now 3056 because the mask size changed you dummy!
#
#     taw_unmod = taw.ix[:, 2]
#     taw_unmod = taw_unmod.values.tolist()[0:]
#
#     taw_unmod = [float(value) for value in taw_unmod]
#     # for value in taw_unmod:
#     #     value = int(value)
#
#     taw_unmod = np.array(taw_unmod)
#     print 'taw_unmod shape', taw_unmod.shape
#     print 'taw_unmod', taw_unmod
#     quotient = (d/taw_unmod)
#     print 'Quotient', quotient
#     unmod_soil_arr = ones - quotient
#     print 'unmodified rzsm array', unmod_soil_arr
#
#     #print 'taw shape', taw_unmod.shape
#
#     taw_mod = taw.ix[:, 3]
#     taw_mod = taw_mod.values.tolist()[0:]
#     taw_mod = [float(value) for value in taw_mod]
#     taw_mod = np.array(taw_mod)
#     quotient = d/taw_mod
#     mod_soil_arr = ones - quotient
#
#     print 'modified rzsm array', mod_soil_arr
#
#
#     # ---- Get Arrays Back into shape! -----
#
#     #print 'paths.static_inputs',
#     # should be able to get the paths thing to work.
#     #geo_path = Paths()
#     geo_path = os.path.join(inputs_path, 'statics')
#     geo_thing = get_raster_geo_attributes(geo_path)
#     print 'GEO THING', geo_thing
#     print 'unmod shape', unmod_soil_arr.shape
#     print unmod_soil_arr
#     unmod_soil_arr = remake_array(os.path.dirname(mask_path), unmod_soil_arr)
#     convert_array_to_raster('/Users/Gabe/Desktop/gdal_raster_output/newtestfile.tif', unmod_soil_arr, geo_thing)