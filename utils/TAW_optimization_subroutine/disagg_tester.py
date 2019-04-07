# ===============================================================================
# Copyright 2019 Jan Hendrickx and Gabriel Parrish
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
import os
import yaml
import numpy as np
import gdal
from gdalconst import GDT_Float32
# ============= standard library imports ========================

def write_raster(array, geotransform, output_path, output_filename, dimensions, projection, flip_arr=False):
    """
    Write raster outputs a Geotiff to a specified location.

    :param array: an array to be printed as a raster
    :param geotransform: a list of intergers containing information about the size and resolution of the raster
    :param output_path: path where you want to output the raster.
    :param output_filename:
    :param dimensions: x and y dimensions of the raster as a tuple
    :param projection: geographic projection string
    :param datatype: NA
    :return: NA
    """
    filename = os.path.join(output_path, output_filename)
    print 'writing to location {}'.format(filename)

    driver = gdal.GetDriverByName('GTiff')
    # path, cols, rows, bandnumber, data type (if not specified, as below, the default is GDT_Byte)
    output_dataset = driver.Create(filename, dimensions[0], dimensions[1], 1, GDT_Float32)

    # we write TO the output band
    output_band = output_dataset.GetRasterBand(1)

    if flip_arr:
        array = np.flipud(array)
        print 'shape of transpose', array.shape
    # we don't need to do an offset
    output_band.WriteArray(array, 0, 0)

    print 'done writing.'

    # set the geotransform in order to georefference the image
    output_dataset.SetGeoTransform(geotransform)
    # set the projection
    output_dataset.SetProjection(projection)

def numpy_to_geotiff(array, geo_info, output_path, output_name):
    """"""

    trans = geo_info['geotransform']

    dim = geo_info['dimensions']
    proj = geo_info['projection']

    print'transform', trans
    print 'dimensions', dim
    print 'projections', proj

    write_raster(array, geotransform=trans, output_path=output_path, output_filename=output_name,
                 dimensions=dim, projection=proj)

def geotiff_output(taw_vals, rss_arrs, geo_info, namekey, outpath):
    """"""
    for arr, taw_val in zip(rss_arrs, taw_vals):
        outname = '{}_image_taw_{}.tif'.format(namekey, taw_val)
        numpy_to_geotiff(arr, geo_info, outpath, outname)

def optimize_taw_disaggregate(rss_path, output_path, geo_info, big_arr=False, test_mode=False, hair_trigger=False):
    """

    :param rss_path:
    :param output_path:
    :param geo_info:
    :param big_arr:
    :param test_mode:
    :param hair_trigger: if the error reduction ever falls below specified threshold we take the correspondig TAW.
    If false, we take TAW beyond which every error reduction is below the specified threshold.
    :return:
    """

    if test_mode:

        test_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/taw_calibration_disaggregated/grassland_test.csv'

        with open(test_path, 'r') as rfile:

            taw_vals = []
            rss_vals = []

            for line in rfile:
                taw_rss = line.split(',')
                taw = int(taw_rss[0])
                rss = float(taw_rss[1])

                taw_vals.append(taw)
                rss_vals.append(rss)

        # get the average daily rss in mm
        rss_vals_avg_daily = [((rss / 11.0) / 365.0) for rss in rss_vals]

        print 'the rss avg daily error \n', rss_vals_avg_daily

        error_reduced_lst = []
        for i in range(len(rss_vals_avg_daily)):
            # print 'i', i
            if i == 0:
                error_reduced_lst.append('')

            elif i > 0:
                # calculate the error reduced by each taw step
                error_reduced = rss_vals_avg_daily[i] - rss_vals_avg_daily[i-1]
                error_reduced_lst.append(error_reduced)

            # elif i == len(rss_vals_avg_daily)
        print 'the error reduced list \n', error_reduced_lst

        # set the first value of the list to the second value
        error_reduced_lst[0] = error_reduced_lst[1]
        print 'the error reduced list \n', error_reduced_lst

        # round the values to the 2nd decimal place
        error_reduced_lst= [round(i, 2) for i in error_reduced_lst]

        # # select the TAW after which error reduced is no longer greater than 0.01
        # for taw, reduced_error in zip(taw_vals, error_reduced_lst):
        #     print 'taw {}, re {}'.format(taw, reduced_error)
        indx_lst = []
        for i, re in enumerate(error_reduced_lst):
            if abs(re) <= 0.01:
                indx_lst.append(i)

        print 'the index list\n', indx_lst
        consecutives = []
        for i in range(len(indx_lst)+1):

            if i > 0 and i < (len(indx_lst)-1):
                print i
                if indx_lst[i + 1] == indx_lst[i] + 1:
                    consecutives.append(indx_lst[i])
            elif i == len(indx_lst)-1:
                if indx_lst[i] -1 == indx_lst[i-1]:
                    consecutives.append(indx_lst[i-1])
                    consecutives.append(indx_lst[i])

        print 'consecutives \n', consecutives

        # take the first index after which the reduced error is consistently less than or equal to 0.01

        target_index = consecutives[0]

        # taw at the target index is the optimum taw

        optimum_taw = taw_vals[target_index]

        print 'optimum taw', optimum_taw

    else:
        print 'running'
        # open rss dict from yml file for testing
        with open(rss_path, 'r') as rfile:
            rss = yaml.load(rfile)

        print 'optimizing taw'
        # get taw, rss arrays out.
        taw_vals = rss['taw']
        rss_arrs = rss['rss']

        # # slice the array for testing so you can see it change or not...
        # rss_arrs = [rss[200:220, 200:220] for rss in rss_arrs]


        print 'len of rss arrs', len(rss_arrs)

        # get the average daily rss in mm for an 11 year time period todo - these outputs look strange
        rss_vals_avg_daily = [((rss / 11.0) / 365.0) for rss in rss_arrs]

        # output average daily rss as images for better visualization
        geotiff_output(taw_vals, rss_vals_avg_daily, geo_info, namekey='daily_rss', outpath=output_path)

        print 'the rss avg daily error \n', len(rss_vals_avg_daily)

        error_reduced_lst = []
        for i in range(len(rss_vals_avg_daily)):
            print 'i', i
            if i == 0:
                error_reduced_lst.append('')

            elif i > 0:
                # calculate the error reduced by each taw step todo - these should be positive if error is DECREASING
                error_reduced = rss_vals_avg_daily[i] - rss_vals_avg_daily[i - 1]
                error_reduced_lst.append(error_reduced)

            # elif i == len(rss_vals_avg_daily)
        print 'the error reduced list \n', error_reduced_lst

        # set the first value of the list to the second value
        error_reduced_lst[0] = error_reduced_lst[1]

        print 'the error reduced list \n', error_reduced_lst

        # output ERROR_REDUCED as images
        geotiff_output(taw_vals, error_reduced_lst, geo_info, namekey='error_reduced', outpath=output_path)

        # make all errors positive by taking the absolute value todo - what are the implications of taking the absolute value? It may mess up the algorithm
        error_reduced_lst = [np.absolute(i) for i in error_reduced_lst]

        # output ERROR_REDUCED as images
        geotiff_output(taw_vals, error_reduced_lst, geo_info, namekey='error_reduced_positive', outpath=output_path)

        # round the values to the 2nd decimal place FOR AN ARRAY
        error_reduced_lst = [np.round(i, 2) for i in error_reduced_lst]

        # output ERROR_REDUCED as images
        geotiff_output(taw_vals, error_reduced_lst, geo_info, namekey='error_reduced_positive_rounded', outpath=output_path)

        # # select the TAW after which error reduced is no longer greater than 0.01

        # prepare to store three dimensional arrays with dstack
        value_shape = rss_arrs[0].shape
        three_d_shape = (value_shape[0], value_shape[1], 0)

        # for storing the boolean for the expression: rss value < 0.01
        # todo - should this be np.zeros or is np.empty better?
        # reduced_error_tab = np.zeros(three_d_shape, dtype=bool)
        reduced_error_tab = np.empty(three_d_shape)

        # for storing the minimum taw
        taw_tab = np.empty(three_d_shape)


        smaller_than_list = []
        for taw, error_array in zip(taw_vals, error_reduced_lst):

            print 'checking rss for taw: {}'.format(taw)

            # make each taw into an array so we can index it
            taw_arr = np.full(error_array.shape, taw, dtype='float64')

            # # we only want to store values that are less than or equal to 0.01 when rounded (rounding handled earlier)
            # smaller_than = error_array <= 0.01

            # get the boolean where error array is less than 0.05
            smaller_than = error_array <= 0.05
            # print'smaller than array \n', smaller_than

            # we append the smaller_than array as an int for testing
            smaller_than_list.append(smaller_than.astype(int))

            # append the smaller than array to reduced error tab with dstack
            reduced_error_tab = np.dstack((reduced_error_tab, smaller_than))

            # append the taw array to a 3d array
            taw_tab = np.dstack((taw_tab, taw_arr))

        # print '3d array True for error values less than or equal to 0.01 otherwise, False \n', reduced_error_tab
        geotiff_output(taw_vals, smaller_than_list, geo_info, namekey='smaller_than', outpath=output_path)

        # 1) go through the 3d array of true false from start to finish, extract true/false as list along 3rd dimension
        # 2) go through that list and get the indices of the true values
        # 3) get the indices that are consecutive
        # 4) take the first of the consecutive indices and grab the corresponding TAW.
        # 5) put the TAW back in a 2d array where it belongs.

        # This will hold the optimized TAW (2d array)
        optimum_taw_disagg = np.zeros(rss_arrs[0].shape)

        # iterate through the 3d array
        cols, rows, vals = reduced_error_tab.shape
        # print 'cols {}, rows {}, vals {}'.format(cols, rows, vals)
        for i in range(cols):
            for j in range(rows):

                true_indices = []
                taw_lst = []

                for k in range(vals):
                    taw = taw_tab[i, j, k]
                    # print 'taw is ', taw
                    taw_lst.append(taw)
                    if reduced_error_tab[i, j, k]:
                        true_indices.append(k)

                # print 'true indices {} for ({},{})'.format(true_indices, i, j)

                # based on optional setting take the taw value based on the first instance that the error reduction falls below the threshold
                if hair_trigger:
                    try:
                        target_index = true_indices[0]
                    except IndexError:
                        # otherwise go with the max TAW
                        target_index = -1

                else:
                    consecutives = []
                    for ti in range(len(true_indices) + 1):

                        # for i in range(len(indx_lst) + 1):
                        #
                        #     if i > 0 and i < (len(indx_lst) - 1):
                        #         print i
                        #         if indx_lst[i + 1] == indx_lst[i] + 1:
                        #             consecutives.append(indx_lst[i])
                        #     elif i == len(indx_lst) - 1:
                        #         if indx_lst[i] - 1 == indx_lst[i - 1]:
                        #             consecutives.append(indx_lst[i - 1])
                        #             consecutives.append(indx_lst[i])

                        # The problem is likely right here...
                        if ti > 0 and ti < (len(true_indices) - 1):
                            if true_indices[ti + 1] == true_indices[ti] + 1:
                                consecutives.append(true_indices[ti])
                        elif ti == len(true_indices) - 1:
                            if true_indices[ti] - 1 == true_indices[ti - 1]:
                                consecutives.append(true_indices[ti - 1])
                                consecutives.append(true_indices[ti])

                    # print 'consecutives \n', consecutives

                    # take the first index after which the reduced error is consistently less than or equal to 0.01
                    try:
                        target_index = consecutives[0]
                    except IndexError:
                        # otherwise go with the maximum TAW
                        target_index = -1

                # # taw at the target index is the optimum taw
                # print 'target index {}'.format(target_index)
                # print 'Taw list is {} \n and we select taw {} using the target index'.format(taw_lst, taw_lst[target_index])

                optimum_taw = taw_lst[target_index]
                # when we have the taw value put it back in the 2d array
                optimum_taw_disagg[i, j] = optimum_taw

                # with open(os.path.join(output_path, 'index.txt'), 'a') as wfile:
                #     wfile.write('{},{} modified'.format(i, j))
                #
                # print 'optimum_taw disagg array\n', optimum_taw_disagg

    # # todo - output the rasters
    numpy_to_geotiff(optimum_taw_disagg, geo_info, output_path, output_name='optimized_taw_disagg.tif')

test_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/taw_calibration_disaggregated/rss.yml'
geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'
output_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/disagg_test_folder'

# pull out the geo info
with open(geo_info_path, mode='r') as geofile:
    geo_dict = yaml.load(geofile)

optimize_taw_disaggregate(rss_path=test_path, output_path=output_path, geo_info=geo_dict, big_arr=False,
                          test_mode=False, hair_trigger=True)