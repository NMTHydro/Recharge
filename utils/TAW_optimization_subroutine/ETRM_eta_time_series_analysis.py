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
# ============= standard library imports ========================
from utils.TAW_optimization_subroutine.calculate_delta_chi import pull_series_jpl, pull_series, pull_series_eeflux, numpy_to_geotiff, get_obs_arr_jpl, get_model_arr
from utils.pixel_time_series_extractor import raster_extract
from utils.TAW_optimization_subroutine.residuals_timeseries_analysis import geospatial_array_extract


def main(data_dir, etrm_data_dir, temp_rss_path, geo_info, x_y):
    """"""

    # get the dates and the locations of all of the data from the data directory
    with open(data_dir, 'r') as yam:
        # load() returns a dict. load_all() returns a yaml object. Usefull if many subfiles are embedded.
        data_dict = yaml.load(yam)

    # pull out the geo info and save it in a dictionary (we can use numpy_to_geotiff function to convert these values to geotiffs,
    with open(geo_info, mode='r') as geofile:
        geo_dict = yaml.load(geofile)

    obs = data_dict['obs']

    # Extract the dates and taw values from the data dictionary
    obs_dates, taw_vals = pull_series_jpl(data_dict)

    etrm_eta = []
    obs_eta = []
    taw = 475
    print 'extracting'
    for date in obs_dates:

        obs_arr = get_obs_arr_jpl(obs, date)
        obs_value = geospatial_array_extract(geo_dict, obs_arr, x_y)
        obs_eta.append(obs_value)

        etrm_name = 'ETRM_daily_eta_taw_{}_{}_{}_{}.npy'.format(taw, date.year, date.month, date.day)
        model_arr = np.load(os.path.join(etrm_data_dir, etrm_name))
        model_value = geospatial_array_extract(geo_dict, model_arr, x_y)
        etrm_eta.append(model_value)

    print 'plotting'
    fig, ax = plt.subplots()
    ax.plot_date(obs_dates, etrm_eta, fillstyle='none', color='blue')
    ax.plot_date(obs_dates, obs_eta, fillstyle='none', color='red')
    ax.set_title('Daily ETRM and JPL ETa in mm')
    ax.set_ylabel('Daily ETa in mm')
    ax.set_xlabel('Date')

    plt.show()

if __name__ == '__main__':

    data_locations_dir = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/get_data_output_jpl.yml'

    etrm_data_directory = '/Volumes/Seagate_Blue/ETRM_espanola_aoi_binary000/190308_16_55/numpy_arrays'

    temp_rss_path = '/Users/dcadol/Desktop/desktop_taw_optimization_temp'

    geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'

    # x = -11681571.66
    # y = 4261647.835

    # x = 464210.572
    # y = 3950111.228

    # x = 484933.768
    # y = 3946983.

    # pixel 1 (the second pixel in the Sangre de Cristo Range)
    x = 438375.118
    y = 3990305.028

    # utm_coords
    x_y = (x, y)

    main(data_locations_dir, etrm_data_directory, temp_rss_path, geo_info_path, x_y)