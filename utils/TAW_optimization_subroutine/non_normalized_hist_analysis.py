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
from matplotlib import pyplot as plt
# Future Warning told me to do this
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# ============= standard library imports ========================
from utils.TAW_optimization_subroutine.calculate_delta_chi import pull_series_jpl, pull_series, pull_series_eeflux, numpy_to_geotiff, get_obs_arr_jpl, get_model_arr
from utils.pixel_time_series_extractor import raster_extract

def geospatial_array_extract(geo_info, arr, x_y):
    """
    This function is for extracting a particular point value from a geospatial array stored as a .npy file. the
    geographic metadata is stored in a dictionary that can be from a .yml file as in clculate_delta_chi.py or some
    other form depending on need.
    :param geo_info: a dictionary with 'geotransform' in the gdal format
    :param arr: 2d numpy array
    :param x_y: (x, y) as a tuple containing geographic coordinates
    :return: A number or some other value from the point specified by the coordinates.
    """

    # unpack x and y coordinates
    x, y = x_y

    # get georefference info to eventually calculate the offset:
    transform = geo_info['geotransform']
    # print 'transform', transform
    xOrigin = transform[0]
    yOrigin = transform[3]
    # print 'x, y origin', xOrigin, yOrigin
    width_of_pixel = transform[1]
    height_of_pixel = transform[5]

    # print 'height and width', height_of_pixel, width_of_pixel

    # get the offsets so you can read the data from the correct position in the array.
    x_offset = int((x - xOrigin) / width_of_pixel)
    y_offset = int((y - yOrigin) / height_of_pixel)

    # print 'offsets', x_offset, y_offset

    value = arr[y_offset, x_offset]

    # print "VALUE {}".format(value)
    return value

def main(data_dir, temp_rss_path, geo_info, x_y):
    """"""

    # get the dates and the locations of all of the data from the data directory
    with open(data_dir, 'r') as yam:
        # load() returns a dict. load_all() returns a yaml object. Usefull if many subfiles are embedded.
        data_dict = yaml.load(yam)

    # Extract the dates and taw values from the data dictionary
    obs_dates, taw_vals = pull_series_jpl(data_dict)
    print 'obs dates \n', obs_dates

    obs = data_dict['obs']

    # pull out the geo info and save it in a dictionary (we can use numpy_to_geotiff function to convert these values to geotiffs,
    with open(geo_info, mode='r') as geofile:
        geo_dict = yaml.load(geofile)

    rss_daily_values = []
    rss_time_series = []
    print 'extracting values'
    for resid_date in obs_dates:



        taw = 1925

        # these you can use to generate a time series analysis of the root squared error.
        temp_name = '{}_{}_{}_{}.npy'.format(taw, resid_date.year, resid_date.month, resid_date.day)

        # get the array from the temp folder
        temp_arr = np.load(os.path.join(temp_rss_path, temp_name))

        # extract the value you want from the raster
        temp_value = geospatial_array_extract(geo_dict, temp_arr, x_y)

        rss_daily_values.append(temp_value)

        # # get the ETRM modeled array that matches the observation.
        # model_arr = get_model_arr(model_results, resid_date)
        #
        # model_value = geospatial_array_extract(geo_dict, model_arr, x_y)
        # etrm_daily_values.append(model_value)

        rss_time_series.append(resid_date)

    # # deal with Nan values and convert to numpy arr
    # rss_daily_values = np.asarray(rss_daily_values)
    #
    # rss_daily_values = np.nan_to_num(rss_daily_values)
    #
    # rss_daily_values = rss_daily_values.tolist()

    rss_daily_values_cleaned = []
    rss_time_series_cleaned = []
    for resid, date in zip(rss_daily_values, rss_time_series):
        if resid > -50:
            rss_daily_values_cleaned.append(resid)
            rss_time_series_cleaned.append(date)

    print 'plotting'
    fig, ax = plt.subplots()
    ax.plot_date(rss_time_series_cleaned, rss_daily_values_cleaned, fillstyle='none', color='blue')
    ax.set_title('Daily Residuals between ETRM and JPL')
    ax.set_ylabel('(non-normalized residual / 0.15*obs) of ETa 1925')
    ax.set_xlabel('Time')

    plt.show()

    # Now Make a histogram of all of the values...
    print 'plotting Histogram'
    fig1, ax1 = plt.subplots()
    ax1.hist(rss_daily_values_cleaned, bins=30, color='green')
    ax1.set_title('ETRM and JPL non_normalized residual / 0.15*obs of eta 1925 taw')
    plt.show()


if __name__ == '__main__':

    data_locations_dir = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/get_data_output_jpl.yml'

    # temp_rss_path = '/Users/dcadol/Desktop/desktop_taw_optimization_temp'
    temp_rss_path = '/Volumes/Seagate_Blue/normalized_residuals'

    geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'

    # x = -11681571.66
    # y = 4261647.835

    # x = 464210.572
    # y = 3950111.228

    # x = 484933.768
    # y = 3946983.0
    #
    # # pixel 1 (the second pixel in the Sangre de Cristo Range)
    # x = 438375.118
    # y = 3990305.028

    # Northern most pixel on flat grassland
    x = 480622.768
    y = 3949786.084

    # # near the northern most pixel
    # x= 481082.524
    # y = 3948795.715

    # utm_coords
    x_y = (x, y)

    main(data_locations_dir, temp_rss_path, geo_info_path, x_y)