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
from recharge.pixel_coord_finder import coord_getter
from runners.distributed_daily import dist_daily_run

def daily_tifmaker(taw_modification, date_range, dates, inputs_path, outputs_path, modified_taw_root):
    """Takes taw from model, modifies one taw, leaves one control taw, runs model twice and produces two sets of daily
    tifs. One set is perhaps key_day_month_year.tif(*x) the other key_day_month_year_mod.tif(*x).
    """

    etrm = Processes(date_range, inputs_path, outputs_path, write_freq='daily')
    etrm.set_save_dates(dates)
    etrm.run()

    etrm_mod = Processes(date_range, inputs_path, outputs_path, mod_output_root=modified_taw_root, write_freq='daily', taw_mod_switch=True)
    etrm_mod.modify_taw(taw_modification, return_taw=True)
    etrm_mod.set_save_dates(dates)
    etrm_mod.run()



def tif_retreival():
    """Based on the datetime_list goes and gets the filenames of the tifs that were generated in daily_tifmaker"""

# save dates is new.
def taw_writer(tif, date_range, save_dates, input_root, output_root, taw_modification, root, output, start, end):
    """Goal here is to plot the original masked taw and two modified versions of taw
    to a csv for each pixel in masked domain

    Additionally this will take in the tiffs from tiff_retreival and put in the values for each pixel to the
    right of the corresponding taw value.

    """

    mask_path = os.path.join(root, 'Mask')
    mask_arr = get_mask(mask_path)

    northing, easting = coord_getter(os.path.join(mask_path, 'zuni_1.tif'))

    # modified taw taken from function in processes class...
    etrm_new = Processes(date_range, input_root, output_root)
    # set_save_dates_function in processes calls set_save_dates in Raster_Manager() which takes the dates you want printed.
    etrm_new.set_save_dates(save_dates)
    #etrm_new.run()

    taw_new = etrm_new.modify_taw(taw_modification, return_taw=True)
    taw_new = remake_array(mask_path, taw_new)

    # unmodified taw taken from function in Processes class...
    etrm_unmod = Processes(date_range, input_root, output_root)
    print "etrm taw shape ---->>> ", etrm_unmod.get_taw().shape
    taw_unmod = etrm_unmod.get_taw()
    taw_unmod = remake_array(mask_path, taw_unmod)

    # original taw (taw) and modified mask taw (taw_new_masked)
    taw_name = 'taw_mod_4_21_10_0.tif'
    statics_to_save = os.path.join(root, 'statics')
    taw = convert_raster_to_array(statics_to_save, taw_name, 1)
    print taw.shape
    taw_new_masked = taw * taw_modification

    # pull out tif from today's folder (might want to change that.)
    todays_date = datetime.today().strftime("%Y_%m_%d")
    tif_path = os.path.join(outputs_path, 'ETRM_Results_{}'.format(todays_date))
    tif_array = convert_raster_to_array(tif_path, tif)

    # all the taw shapes are correct...
    print 'taw shape', taw.shape
    print 'taw_new shape', taw_new.shape
    print 'taw_new_masked shape', taw_new_masked.shape
    print 'taw unmodified from processes', taw_unmod.shape
    print 'tif array shape->', tif_array.shp

    keys = ('x', 'y', 'taw', 'taw_new_masked','taw_unmodified', 'taw_new')
    with open(output, 'w') as wfile:
        wfile.write('{}\n'.format(','.join(keys)))



        nrows, ncols = taw.shape
        for ri in xrange(nrows):
            for ci in xrange(ncols):
                mask_values = mask_arr[ri, ci]
                if mask_values:
                    #print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
                    items = ('{}'.format(easting[ri,ci]), '{}'.format(northing[ri,ci]), '{}'.format(taw[ri,ci]), '{}'.format(taw_new_masked[ri,ci]),'{}'.format(taw_unmod[ri,ci]), '{}'.format(taw_new[ri,ci]))
                    wfile.write('{}\n'.format(','.join(items)))



if __name__ == '__main__':





    inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')
    root = inputs_path
    # TODO need to get rid of a hardcoded output path.
    output = os.path.join(root, 'TAW_pts_out', 'TAW_xmas_test_2013.csv')

    #generate first set of dailies.
    dist_daily_run()

    # tifs should be a list or tuple.
    tifs = tif_retreival()

    # writes the big ol csv for each tif...
    # pause on this one do the first two for now...
    for tif in tifs:
        taw_writer(tif, (start, end), save_dates, inputs_path, outputs_path, taw_modification,
            root, output, start, end)
    # for results use the output tiff and base it on the path.

    #=====================================================

    # v...Scratch work that is still relevant...v

    #=====================================================
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


