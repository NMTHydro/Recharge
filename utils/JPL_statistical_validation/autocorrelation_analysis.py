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
import pandas as pd
from datetime import datetime as dt
from datetime import date
import yaml
import numpy as np
from matplotlib import pyplot as plt
# ============= standard library imports ========================
from utils.JPL_statistical_validation.eta_dataset_plotter import get_prism_results, get_jpl_results, get_etrm_results,\
    ec_data_processor
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import x_y_extract, raster_extract

""" This script will perform autocorrelation analysis of JPL, ETRM and Ameriflux EC time series"""

def autocorrelate(list_of_values, shift_interger, linspace_range, title_string):

    vals_arr = np.asarray(list_of_values)

    shifted = (vals_arr[:-shift_interger], vals_arr[shift_interger:])
    slope, intercept = np.polyfit(shifted[0], shifted[1], 1)
    x = np.linspace(0, linspace_range, 50)
    y = x * slope + intercept

    # 1 day lag corr coeff
    corr = np.corrcoef(shifted[0], shifted[1])[0, 1]
    print 'corr coeff for {} day shift:'.format(shift_interger), corr

    fig, ax = plt.subplots()
    ax.set_title('autocorrelation plot for shift {} dataset {} corr coef = {}'.format(shift_interger, title_string, corr))
    ax.scatter(shifted[0], shifted[1])
    ax.set_xlabel('i - {}'.format(shift_interger))
    ax.set_ylabel('i')
    ax.plot(x, y)
    plt.show()

def autocorrelation_analysis(df_data=None, dict_data=None, shapefile=None, taw=None, geo_info=None):

    ameriflux_data = df_data

    jpl_data, etrm_data = dict_data

    start_date = date(2011, 5, 10)
    end_date = date(2011, 8, 14)

    ### =========== Ameriflux Autocorrelation Analysis =================

    ameriflux_values = ameriflux_data.mmh20
    ameriflux_dates = ameriflux_data.date

    time_period = []
    time_period_vals = []
    for val, d in zip(ameriflux_values, ameriflux_dates):

        print d
        print d > start_date
        print d < end_date

        if d > start_date and d < end_date:
            time_period.append(d)
            time_period_vals.append(val)


    # 1 day
    autocorrelate(time_period_vals, 1, 5, 'ameriflux summer 2011')


    # 2 day

    autocorrelate(time_period_vals, 2, 5, 'ameriflux summer 2011')

    # todo - comprehensive autocorrelogram


    ### =========== JPL Autocorrelation Analysis ========

    feature_dictionary = x_y_extract(shapefile)

    print "feature dictionary", feature_dictionary

    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

    jpl_dates = jpl_data['dates']
    jpl_etas = jpl_data['etas']


    jpl_time_period = []
    jpl_time_period_vals = []

    for eta_path, d in zip(jpl_etas, jpl_dates):
        if d > start_date and d < end_date:
            print d
            jpl_time_period.append(d)

            # EXTRACT JPL point value from the raster
            eta_val = raster_extract(eta_path, x, y)
            jpl_time_period_vals.append(eta_val)


    # print 'jple time period', jpl_time_period
    # plt.plot(jpl_time_period, jpl_time_period_vals, color='red')
    # plt.plot_date(jpl_time_period, jpl_time_period_vals, fillstyle=None, color='red')
    # plt.show()

    # == Autocorrelation ==

    # 1 day

    autocorrelate(jpl_time_period_vals, 1, 6, 'jpl summer 2011')

    # 2 day

    autocorrelate(jpl_time_period_vals, 2, 6, 'jpl summer 2011')

    # todo - comprehensive autocorrelogram


    ### ================== ETRM Autocorrelation Analysis ==================

    etrm_tuple = etrm_dict[taw]

    date_objs = etrm_tuple[1]
    print 'date objs \n', date_objs
    etrm_eta_files = etrm_tuple[0]

    etrm_time_period = []
    etrm_time_period_vals = []

    for eta_path, d in zip(etrm_eta_files, date_objs):
        # print 'd', d
        # print 'd type', type(d)
        if d > start_date and d < end_date:
            print d
            etrm_time_period.append(d)

            # EXTRACT ETRM point value from the raster
            eta_arr = np.load(eta_path)
            eta_val = geospatial_array_extract(geo_info, eta_arr, (x, y))
            etrm_time_period_vals.append(eta_val)

    # == Autocorrelation ==

    # 1 day
    autocorrelate(etrm_time_period_vals, 1, 6, 'etrm')

    # 2 day
    autocorrelate(etrm_time_period_vals, 2, 6, 'etrm')

    # todo - comprehensive autocorrelogram



if __name__ == "__main__":

    # shapefile
    shape_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/' \
                 'optimization_results_april_8/point_extract.shp'

    # get geo-info path to handle importing numpy files
    geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'
    with open(geo_info_path, mode='r') as geofile:
        geo_dict = yaml.load(geofile)

    jpl_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'

    # dict with keys 'dates' for date objs and 'etas' for filepaths
    jpl_data_dict = get_jpl_results(jpl_path)

    # ETRM
    etrm_path = '/Volumes/Seagate_Blue/taw_optimization_etrm_outputs_april_8_N_Central_nm_2m/etrm_results'
    # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
    etrm_dict = get_etrm_results(etrm_path)

    # Ameriflux
    ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'

    # get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path
    daily_cum_ameriflux = ec_data_processor(ameriflux_path)

    autocorrelation_analysis(df_data=(daily_cum_ameriflux), dict_data=(jpl_data_dict, etrm_dict),
                             shapefile=shape_path, taw='1925', geo_info=geo_dict)
