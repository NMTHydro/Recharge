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

# ============= local library imports ===========================

from datetime import datetime
from recharge.etrm_processes import Processes
import os
from recharge.raster_tools import convert_raster_to_array, apply_mask, save_daily_pts, remake_array, get_mask
from utils.pixel_coord_finder import coord_getter
from runners.distributed_daily import dist_daily_run
import pandas as pd
from pandas import DataFrame
from runners.config import Config

def tif_retreival(datetime_list):
    """Based on the datetime_list goes and gets the filenames of the tifs that were generated in daily_tifmaker"""
    return None

def taw_framer(root): # taw_modification takout test.
    """Only does the georefferenced taw dataframes"""

    mask_path = os.path.join(root, 'Mask')
    mask_arr = get_mask(mask_path)

    northing, easting = coord_getter(os.path.join(mask_path, 'zuni_1.tif'))

    home = os.path.expanduser('~')
    cp1 = os.path.join(home, 'ETRM_CONFIG.yml')
    cp2 = os.path.join(home, 'ETRM_CONFIG_TAW.yml')
    # modified taw taken from function in processes class...
    cfg1 = Config()
    cfg1.load(cp2)
    etrm_new = Processes(cfg1)
    # set_save_dates_function in processes calls set_save_dates in Raster_Manager() which takes the dates you want printed.
    etrm_new.set_save_dates(cfg1.save_dates)
    #etrm_new.run()

    taw_new = etrm_new.modify_taw(cfg1.taw_modification, return_taw=True)
    taw_new = remake_array(mask_path, taw_new)



    #unmodified taw taken from function in Processes class...
    cfg2 = Config()
    cfg2.load(cp1)
    etrm_unmod = Processes(cfg2)
    print "etrm taw shape ---->>> ", etrm_unmod.get_taw().shape
    taw_unmod = etrm_unmod.get_taw()
    taw_unmod = remake_array(mask_path, taw_unmod)


    # # original taw (taw) and modified mask taw (taw_new_masked)
    taw_modification = cfg2.taw_modification
    taw_name = 'taw_mod_4_21_10_0.tif'
    statics_to_save = os.path.join(root, 'statics') # TODO - does this do anything?
    taw = convert_raster_to_array(statics_to_save, taw_name, 1)
    print taw.shape
    taw_new_masked = taw * taw_modification

    # all the taw shapes are correct...
    print 'taw shape', taw.shape
    print 'taw_new shape', taw_new.shape
    print 'taw_new_masked shape', taw_new_masked.shape
    print 'taw unmodified from processes', taw_unmod.shape

    columns = ['x', 'y', 'taw', 'taw_new_masked','taw_unmodified', 'taw_new']
    x_list = []
    y_list = []
    taw_list = []
    taw_new_masked_list = []
    taw_unmodified_list = []
    taw_new_list = []
    nrows, ncols = taw.shape
    for ri in xrange(nrows):
        for ci in xrange(ncols):
            mask_values = mask_arr[ri, ci]
            if mask_values:
                #print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
                x_list.append('{}'.format(easting[ri,ci]))
                y_list.append('{}'.format(northing[ri,ci]))
                taw_list .append('{}'.format(taw[ri,ci]))
                taw_new_masked_list.append('{}'.format(taw_new_masked[ri,ci]))
                taw_unmodified_list.append('{}'.format(taw_unmod[ri,ci]))
                taw_new_list.append('{}'.format(taw_new[ri,ci]))

    taw_data_dict = {'x': x_list, 'y': y_list, 'taw': taw_list, 'taw_new_masked': taw_new_masked_list,
                 'taw_unmodified':taw_unmodified_list, 'taw_new': taw_new_list}
    taw_df = pd.DataFrame(taw_data_dict, columns=columns)

    print 'taw dataframe', taw_df
    return taw_df, taw_data_dict


def tiff_framer(mod_tif_list, unmod_tif_list, root, unmod_desktop_root, mod_desktop_root, test_root, test_tiff_list):
    """Does whichever georefferenced tiff dataframe"""

    home = os.path.expanduser('~')
    cp = os.path.join(home, 'ETRM_CONFIG_TAW.yml')
    cfg = Config()
    cfg.load(cp)
    taw_modification = cfg.taw_modification

    mask_path = os.path.join(root, 'Mask')
    mask_arr = get_mask(mask_path)

    # TODO - build the mask into the config object.
    northing, easting = coord_getter(os.path.join(mask_path, 'zuni_1.tif'))

    test_array_list = []
    for raster_file in test_tiff_list:
        strings = raster_file.split('/')
        #print strings
        raster_file = strings[6]
        #print 'raster_file',raster_file
        # TODO - Figure out why I get AttributeError: 'NoneType' object has no attribute 'GetRasterBand'
        # when we print rasters why don't they have band1 info in the metadata?
        #print 'test array'
        test_array_list.append(convert_raster_to_array(test_root, raster_file, band=1)) # removed the band, maybe it wanted band=...

    mod_array_list = []
    for raster_file in mod_tif_list:
        strings = raster_file.split('/')
        print strings
        raster_file = strings[8]
        #print 'mod array'
        mod_array_list.append(convert_raster_to_array(mod_desktop_root, raster_file, band=1))
    #
    unmod_array_list = []
    for raster_file in unmod_tif_list:
        strings = raster_file.split('/')
        print strings
        raster_file = strings[8]
        #print 'unmod array'
        unmod_array_list.append(convert_raster_to_array(unmod_desktop_root, raster_file, band=1))

    mod_cols = ['mod_de', 'mod_dr', 'mod_drew', 'mod_tot-eta', 'mod_tot-etrs']

    unmod_cols = ['de', 'dr', 'drew', 'tot-eta', 'tot-etrs']

    test_cols = ['x', 'y', 'test_eta', 'test_etrs']

    test_df_list = []
    test_dict_list = []
    for array in test_array_list:
        x_list = []
        y_list = []
        value_list = []
        nrows, ncols = test_array_list[0].shape
        for ri in xrange(nrows):
            for ci in xrange(ncols):
                mask_values = mask_arr[ri, ci]
                if mask_values:
                    # print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
                    x_list.append('{}'.format(easting[ri, ci]))
                    y_list.append('{}'.format(northing[ri, ci]))
                    value_list.append('{}'.format(array[ri, ci]))
                    #print 'mod value list {}'.format(value_list)
        test_dict_data = {'x': '{}'.format(x_list), 'y':'{}'.format(y_list),
                          'test_eta': '{}'.format(value_list), 'test_etrs':'{}'.format(value_list)}

        # This does not look right...
        test_dataframe = pd.DataFrame(test_dict_data, index=x_list,columns= test_cols,) # TODO - why do i need an index here?
        #print 'test dataframe', test_dataframe

    test_df_list.append(test_dataframe)


    mod_dict_list = []
    for array in mod_array_list:
        print array
        x_list = []
        y_list = []
        de_value_list = []
        dr_value_list = []
        drew_value_list = []
        toteta_value_list = []
        totetrs_value_list = []
        print 'array shape', mod_array_list[0].shape
        nrows, ncols = mod_array_list[0].shape
        for ri in xrange(nrows):
            for ci in xrange(ncols):
                mask_values = mask_arr[ri, ci]
                if mask_values:
                    # print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
                    #
                    x_list.append('{}'.format(easting[ri, ci]))
                    y_list.append('{}'.format(northing[ri, ci]))
                    #value_list.append('{}'.format(array[ri, ci]))
                    de_value_list.append('{}'.format(mod_array_list[0][ri,ci]))
                    dr_value_list.append('{}'.format(mod_array_list[1][ri,ci]))
                    drew_value_list.append('{}'.format(mod_array_list[2][ri, ci]))
                    toteta_value_list.append('{}'.format(mod_array_list[3][ri, ci]))
                    totetrs_value_list.append('{}'.format(mod_array_list[4][ri, ci]))
                    #print 'mod value list {}'.format(value_list)
        mod_dict_data = {'x': x_list, 'y': y_list, 'mod_de': de_value_list, 'mod_dr':dr_value_list,
                         'mod_drew': drew_value_list, 'mod_tot-eta': toteta_value_list, 'mod_tot-etrs': totetrs_value_list}
        print mod_dict_data
    mod_dict_list.append(mod_dict_data)

    #print 'mod dict list \n {}'.format(mod_dict_list)

    unmod_dict_list = []
    # TODO take loops out....
    x_list = []
    y_list = []
    x_list = []
    y_list = []
    de_value_list = []
    dr_value_list = []
    drew_value_list = []
    toteta_value_list = []
    totetrs_value_list = []
    nrows, ncols = unmod_array_list[0].shape
    for ri in xrange(nrows):
        for ci in xrange(ncols):
            mask_values = mask_arr[ri, ci]
            if mask_values:
                # print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
                x_list.append('{}'.format(easting[ri, ci]))
                y_list.append('{}'.format(northing[ri, ci]))
                #value_list.append('{}'.format(array[ri, ci]))
                de_value_list.append('{}'.format(unmod_array_list[0][ri, ci]))
                dr_value_list.append('{}'.format(unmod_array_list[1][ri, ci]))
                drew_value_list.append('{}'.format(unmod_array_list[2][ri, ci]))
                toteta_value_list.append('{}'.format(unmod_array_list[3][ri, ci]))
                totetrs_value_list.append('{}'.format(unmod_array_list[4][ri, ci]))
                #print 'unmod value list {}'.format(value_list)
    unmod_dict_data = {'x': x_list, 'y': y_list, 'de': de_value_list, 'dr': dr_value_list, 'drew': drew_value_list,
                       'tot-eta': toteta_value_list, 'tot-etrs': totetrs_value_list}
    #print 'unmod_dict_data {}'.format(unmod_dict_data)
    unmod_dict_list.append(unmod_dict_data)

    #print "unmod_dict_list \n {}".format(unmod_dict_list)



if __name__ == '__main__':

    #taw_modification = 1.15
    hard_drive_path = os.path.join('/Volumes', 'Seagate Expansion Drive')
    inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')

    # outputs_path = os.path.join(hard_drive_path, 'ETRM_Results')
    # modified_taw_path = os.path.join(hard_drive_path, 'ETRM_Results', 'TAW_mod_results')

    root = inputs_path
    mod_desktop_root = '/Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters'
    unmod_desktop_root = '/Users/Gabe/Desktop/ETRM_desktop_output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters'

    # test_root = '/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_03_08/daily_rasters'
    test_root = '/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_02_24/monthly_rasters'
    #output = os.path.join(root, 'TAW_pts_out', 'TAW_xmas_test_2013.csv')

    #taw_frame, taw_data_dict = taw_framer(root)

    # TODO build the tiff_retreival() function
    # mod_tiff_list, unmod_tif_list = tif_retreival()

    # for now... Just hardcode a list of tiff paths to test.
    # mod_tif_path = /Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/
    # unmod_tif_path = /Users/Gabe/Desktop/ETRM_desktop_output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/

    mod_tif_list = ['/Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/de_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/dr_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/drew_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/tot_eta_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/tot_etrs_30_12_2013.tif']

    unmod_tif_list = ['/Users/Gabe/Desktop/ETRM_destop_output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/de_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_desktop_output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/dr_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_desktop_output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/drew_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_desktop_output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/tot_eta_30_12_2013.tif',
                     '/Users/Gabe/Desktop/ETRM_desktop_output/ETRM_results/ETRM_Results_2017_03_14/daily_rasters/tot_etrs_30_12_2013.tif']

    # test_tif_list = ['/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_03_08/daily_rasters/tot_eta_27_12_2013.tif',
    #                  '/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_03_08/daily_rasters/tot_etrs_30_12_2013.tif']

    test_tif_list = ['/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_02_24/monthly_rasters/eta_7_2012.tif',
                     '/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_02_24/montly_rasters/etrs_7_2012.tif']


    tiff_framer(mod_tif_list, unmod_tif_list, root, mod_desktop_root, unmod_desktop_root, test_root, test_tif_list)



# def frame_joiner():
#     """Joins the output tiff dataframes and the TAW dataframes..."""
#
#     #save dates is new.
# def taw_writer(tif, date_range, save_dates, input_root, output_root, taw_modification, root, output, start, end):
#     """ Short term goal: Get this working again and don't forget to comment what the function inputs are this time.
#     Med term goal, Have this output instead of a csv, a pandas dataframe that is stored...
#     """
#
#     mask_path = os.path.join(root, 'Mask')
#     mask_arr = get_mask(mask_path)
#
#     northing, easting = coord_getter(os.path.join(mask_path, 'zuni_1.tif'))
#
#     # modified taw taken from function in processes class...
#     etrm_new = Processes(date_range, input_root, output_root)
#     # set_save_dates_function in processes calls set_save_dates in Raster_Manager() which takes the dates you want printed.
#     etrm_new.set_save_dates(save_dates)
#     #etrm_new.run()
#
#     taw_new = etrm_new.modify_taw(taw_modification, return_taw=True)
#     taw_new = remake_array(mask_path, taw_new)
#
#     # unmodified taw taken from function in Processes class...
#     etrm_unmod = Processes(date_range, input_root, output_root)
#     print "etrm taw shape ---->>> ", etrm_unmod.get_taw().shape
#     taw_unmod = etrm_unmod.get_taw()
#     taw_unmod = remake_array(mask_path, taw_unmod)
#
#     # original taw (taw) and modified mask taw (taw_new_masked)
#     taw_name = 'taw_mod_4_21_10_0.tif'
#     statics_to_save = os.path.join(root, 'statics')
#     taw = convert_raster_to_array(statics_to_save, taw_name, 1)
#     print taw.shape
#     taw_new_masked = taw * taw_modification
#
#     # pull out tif from today's folder (might want to change that.)
#     todays_date = datetime.today().strftime("%Y_%m_%d")
#     tif_path = os.path.join(outputs_path, 'ETRM_Results_{}'.format(todays_date))
#     tif_array = convert_raster_to_array(tif_path, tif)
#
#     # all the taw shapes are correct...
#     print 'taw shape', taw.shape
#     print 'taw_new shape', taw_new.shape
#     print 'taw_new_masked shape', taw_new_masked.shape
#     print 'taw unmodified from processes', taw_unmod.shape
#     print 'tif array shape->', tif_array.shp
#
#     keys = ('x', 'y', 'taw', 'taw_new_masked','taw_unmodified', 'taw_new')
#     with open(output, 'w') as wfile:
#         wfile.write('{}\n'.format(','.join(keys)))
#
#
#
#         nrows, ncols = taw.shape
#         for ri in xrange(nrows):
#             for ci in xrange(ncols):
#                 mask_values = mask_arr[ri, ci]
#                 if mask_values:
#                     #print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
#                     items = ('{}'.format(easting[ri,ci]), '{}'.format(northing[ri,ci]), '{}'.format(taw[ri,ci]), '{}'.format(taw_new_masked[ri,ci]),'{}'.format(taw_unmod[ri,ci]), '{}'.format(taw_new[ri,ci]))
#                     wfile.write('{}\n'.format(','.join(items)))


    #=====================================================

    # v...Scratch work that is still relevant...v


    #=====================================================

    # 5/15/17

# def run_pandastest(xmas_csv_path, taw_foil):
#     """Experimenting with pandas merge ability and read and write from csvs..."""
#
#     xmas = pd.read_csv(xmas_csv_path)
#
#     foil = pd.read_csv(taw_foil)
#
#     xmas = DataFrame(xmas)
#
#     foil = DataFrame(foil)
#
#     print 'y\n', foil['y']
#
#     print 'x\n', xmas['x']
#
#
#     merged = pd.merge(xmas, foil) # on='y' .... on='x' doesn't work
#
#     print 'merged', merged
#
#     merged.to_csv('/Users/Gabe/Desktop/merged_test.csv')
#     #leaves a weird column in there... and why does 'x' give a key error and not 'y' or 'taw'?
#
#
#
# if __name__ == '__main__':
#
#     xmas_csv_path = "/Users/Gabe/Desktop/TAW_xmas_test_2013.csv"
#
#     taw_foil = "/Users/Gabe/Desktop/taw_xmas_foil.csv"

    #run_pandastest(xmas_csv_path, taw_foil)
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # def run(date_range, input_root, output_root, taw_modification, root, output, start, end):
    #     """Approach here is to just cut out the taw array from the file and multiply that array by whatever
    #     the taw modification is and write that into the file."""
    #
    #     taw_name = 'taw_mod_4_21_10_0.tif'
    #     statics_to_save = os.path.join(root, 'statics')
    #
    #     mask_path = os.path.join(root, 'Mask')
    #
    #     taw_new_masked = convert_raster_to_array(statics_to_save, taw_name, 1)
    #
    #
    #     print "New masked TAW", taw_new_masked
    #
    #     print "New masked TAW shape", taw_new_masked.shape
    #
    #     taw_new_masked = taw_new_masked * taw_modification
    #
    #     print "TAW array multiplied by taw_modification", taw_new_masked
    #
    #     mask_arr = get_mask(mask_path)
    #
    #     keys = ('x', 'y', 'taw_new_masked')
    #
    #     with open(output, 'w') as wfile:
    #         wfile.write('{}\n'.format(','.join(keys)))
    #
    #         nrows, ncols = taw_new_masked.shape
    #         for ri in xrange(nrows):
    #             for ci in xrange(ncols):
    #                 mask_value = mask_arr[ri, ci]
    #                 if mask_value:
    #                     print ri, ci, taw_new_masked[ri, ci]
    #                     items = ('{}'.format(ri), '{}'.format(ci), '{}'.format(taw_new_masked[ri,ci]))
    #                     wfile.write('{}\n'.format(','.join(items)))
    #
    #     return
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # def run(date_range, input_root, output_root, taw_modification, root, output, start, end):
    #     """This plotted an updated taw by taking the modified taw array from processes and remaking the array."""
    #     etrm_new = Processes(date_range, input_root,output_root)
    #     taw_new = etrm_new.modify_taw(taw_modification, return_taw=True)
    #
    #     mask_path = os.path.join(root, 'Mask')
    #     print "New TAW", taw_new
    #
    #     print "New TAW shape", taw_new.shape
    #
    #     taw_new = remake_array(mask_path, taw_new)
    #
    #     print "Remade TAW shape", taw_new.shape
    #
    #     mask_arr = get_mask(mask_path)
    #
    #     keys = ('x', 'y', 'taw_new')
    #
    #     with open(output, 'w') as wfile:
    #         wfile.write('{}\n'.format(','.join(keys)))
    #
    #         nrows, ncols = taw_new.shape
    #         for ri in xrange(nrows):
    #             for ci in xrange(ncols):
    #                 mask_value = mask_arr[ri, ci]
    #                 if mask_value:
    #                     print ri, ci, taw_new[ri, ci]
    #                     items =  ('{}'.format(ri), '{}'.format(ci), '{}'.format(taw_new[ri,ci]))
    #                     wfile.write('{}\n'.format(','.join(items)))
    #
    #     return
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # def run(date_range, input_root, output_root, taw_modification, root, output, start, end):
    #    """This plotted the taw from the original tiff"""
    #
    #     taw_name = 'taw_mod_4_21_10_0.tif'
    #     statics_to_save = os.path.join(root, 'statics')
    #
    #     mask_path = os.path.join(root, 'Mask')
    #     taw = convert_raster_to_array(statics_to_save, taw_name, 1)
    #
    #     print "This is the original taw shape {}".format(taw.shape)  # 2525, 2272
    #
    #     # returns a boolean array. (True, False)
    #     mask_arr = get_mask(mask_path)
    #
    #     print 'mask arr', mask_arr, mask_arr.shape
    #     print 'taw', taw, taw.shape
    #
    #     print "This is the new taw shape {}".format(taw.shape)  # 2525, 2272
    #
    #
    #     keys = ('x', 'y', 'taw')
    #     with open(output, 'w') as wfile:
    #         print "your file is at this path: {}".format(output)
    #         print taw.shape
    #
    #         wfile.write('{}\n'.format(','.join(keys)))
    #
    #         nrows, ncols = taw.shape
    #         for ri in xrange(nrows):
    #             for ci in xrange(ncols):
    #                 # idx = ri*ncols + ci
    #                 mask_value = mask_arr[ri, ci]
    #                 # print 'rrrrr', mask_value
    #                 if mask_value:
    #                     #print ri, ci, taw[ri, ci]
    #                     wfile.write('{},{},{}\n'.format(ri, ci, taw[ri,ci]))
    #
    #                     # for row, item in enumerate(taw):
    #                     #
    #                     #     for col, value in enumerate(item):
    #                     #         print row, col, value
    #                     #         wfile.write('{}\n'.format(row, col, value))
    #                     # remake array()
    #
    #                     # currently 1-d


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Scrachwork save Monday 1:56 pm march 13:

        # def daily_tifmaker(taw_modification, date_range, dates, inputs_path, outputs_path, modified_taw_root):
        #     """Takes taw from model, modifies one taw, leaves one control taw, runs model twice and produces two sets of daily
        #     tifs. One set is perhaps key_day_month_year.tif(*x) the other key_day_month_year_mod.tif(*x).
        #     """
        #
        #     etrm = Processes(date_range, inputs_path, outputs_path, write_freq='daily')
        #     etrm.set_save_dates(dates)
        #     etrm.run()
        #
        #     etrm_mod = Processes(date_range, inputs_path, outputs_path, mod_output_root=modified_taw_root,
        #                          write_freq='daily', taw_mod_switch=True)
        #     etrm_mod.modify_taw(taw_modification, return_taw=True)
        #     etrm_mod.set_save_dates(dates)
        #     etrm_mod.run()
        #
        #
        # def tif_retreival():
        #     """Based on the datetime_list goes and gets the filenames of the tifs that were generated in daily_tifmaker"""
        #
        #
        # # save dates is new.
        # def taw_writer(tif, date_range, save_dates, input_root, output_root, taw_modification, root, output, start,
        #                end):
        #     """Goal here is to plot the original masked taw and two modified versions of taw
        #     to a csv for each pixel in masked domain
        #
        #     Additionally this will take in the tiffs from tiff_retreival and put in the values for each pixel to the
        #     right of the corresponding taw value.
        #
        #     """
        #
        #     mask_path = os.path.join(root, 'Mask')
        #     mask_arr = get_mask(mask_path)
        #
        #     northing, easting = coord_getter(os.path.join(mask_path, 'zuni_1.tif'))
        #
        #     # modified taw taken from function in processes class...
        #     etrm_new = Processes(date_range, input_root, output_root)
        #     # set_save_dates_function in processes calls set_save_dates in Raster_Manager() which takes the dates you want printed.
        #     etrm_new.set_save_dates(save_dates)
        #     # etrm_new.run()
        #
        #     taw_new = etrm_new.modify_taw(taw_modification, return_taw=True)
        #     taw_new = remake_array(mask_path, taw_new)
        #
        #     # unmodified taw taken from function in Processes class...
        #     etrm_unmod = Processes(date_range, input_root, output_root)
        #     print "etrm taw shape ---->>> ", etrm_unmod.get_taw().shape
        #     taw_unmod = etrm_unmod.get_taw()
        #     taw_unmod = remake_array(mask_path, taw_unmod)
        #
        #     # original taw (taw) and modified mask taw (taw_new_masked)
        #     taw_name = 'taw_mod_4_21_10_0.tif'
        #     statics_to_save = os.path.join(root, 'statics')
        #     taw = convert_raster_to_array(statics_to_save, taw_name, 1)
        #     print taw.shape
        #     taw_new_masked = taw * taw_modification
        #
        #     # pull out tif from today's folder (might want to change that.)
        #     todays_date = datetime.today().strftime("%Y_%m_%d")
        #     tif_path = os.path.join(outputs_path, 'ETRM_Results_{}'.format(todays_date))
        #     tif_array = convert_raster_to_array(tif_path, tif)
        #
        #     # all the taw shapes are correct...
        #     print 'taw shape', taw.shape
        #     print 'taw_new shape', taw_new.shape
        #     print 'taw_new_masked shape', taw_new_masked.shape
        #     print 'taw unmodified from processes', taw_unmod.shape
        #     print 'tif array shape->', tif_array.shp
        #
        #     keys = ('x', 'y', 'taw', 'taw_new_masked', 'taw_unmodified', 'taw_new')
        #     with open(output, 'w') as wfile:
        #         wfile.write('{}\n'.format(','.join(keys)))
        #
        #         nrows, ncols = taw.shape
        #         for ri in xrange(nrows):
        #             for ci in xrange(ncols):
        #                 mask_values = mask_arr[ri, ci]
        #                 if mask_values:
        #                     # print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
        #                     items = (
        #                     '{}'.format(easting[ri, ci]), '{}'.format(northing[ri, ci]), '{}'.format(taw[ri, ci]),
        #                     '{}'.format(taw_new_masked[ri, ci]), '{}'.format(taw_unmod[ri, ci]),
        #                     '{}'.format(taw_new[ri, ci]))
        #                     wfile.write('{}\n'.format(','.join(items)))
        #
        #
        # if __name__ == '__main__':
        #
        #     start_year = 2013
        #     start_month = 12
        #     start_day = 30
        #
        #     end_year = 2013
        #     end_month = 12
        #     end_day = 31
        #
        #     taw_modification = 1.15
        #
        #     hard_drive_path = os.path.join('/Volumes', 'Seagate Expansion Drive')
        #     inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')
        #     outputs_path = os.path.join(hard_drive_path, 'ETRM_Results')
        #     modified_taw_path = os.path.join(hard_drive_path, 'ETRM_Results', 'TAW_mod_results')
        #
        #     start = datetime(start_year, start_month, start_day)
        #     end = datetime(end_year, end_month, end_day)
        #
        #     root = inputs_path
        #     # TODO need to get rid of a hardcoded output path.
        #     output = os.path.join(root, 'TAW_pts_out', 'TAW_xmas_test_2013.csv')
        #
        #     save_dates = [datetime(2013, 12, 30), datetime(2013, 12, 31)]
        #     date_range = (start, end)
        #
        #     # generate the dailies.
        #     daily_tifmaker(taw_modification, date_range, save_dates, inputs_path, outputs_path, modified_taw_path)
        #
        #     # tifs should be a list or tuple.
        #     tifs = tif_retreival()
        #
        #     # writes the big ol csv for each tif...
        #     # pause on this one do the first two for now...
        #     for tif in tifs:
        #         taw_writer(tif, (start, end), save_dates, inputs_path, outputs_path, taw_modification,
        #                    root, output, start, end)


        # def daily_tifmaker(taw_modification, date_range, dates, inputs_path, outputs_path, modified_taw_root):
        #     """Takes taw from model, modifies one taw, leaves one control taw, runs model twice and produces two sets of daily
        #     tifs. One set is perhaps key_day_month_year.tif(*x) the other key_day_month_year_mod.tif(*x).
        #     """
        #
        #     etrm = Processes(date_range, inputs_path, outputs_path, write_freq='daily')
        #     etrm.set_save_dates(dates)
        #     etrm.run()
        #
        #     etrm_mod = Processes(date_range, inputs_path, outputs_path, mod_output_root=modified_taw_root, write_freq='daily', taw_mod_switch=True)
        #     etrm_mod.modify_taw(taw_modification, return_taw=True)
        #     etrm_mod.set_save_dates(dates)
        #     etrm_mod.run()