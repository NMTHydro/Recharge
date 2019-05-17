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
from datetime import date
import yaml
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
# ============= standard library imports ========================
from utils.JPL_statistical_validation.eta_dataset_plotter import get_prism_results, get_jpl_results, get_etrm_results,\
    ec_data_processor
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import x_y_extract, raster_extract

"""This script analyzes residuals between Ameriflux and ETa models"""

def histogram_residuals(residuals, title=None, coloring='blue'):

    residuals = np.asarray(residuals)

    residuals = residuals[~np.isnan(residuals)]
    print 'mean residuals', np.mean(residuals)
    print 'mean 1st std dev', np.std(residuals)
    print 'mode residuals', stats.mode(residuals)

    # TODO - what's this issue now?!?!?
    residuals = residuals[(residuals > -100) & (residuals < 100)]

    print 'plotting Histogram'
    fig1, ax1 = plt.subplots()
    ax1.hist(residuals, bins=100, color='{}'.format(coloring))
    ax1.set_title('{}'.format(title))
    plt.savefig('/Volumes/Seagate_Blue/ameriflux_aoi_workfolder/error_analysis_output/{}.png'.format(title))

def ameriflux_residuals(df_data=None, dict_data=None, shapefile=None, taw=None, geo_info=None, location_name=None):

    # unpack the datasets
    ameriflux_data = df_data

    jpl_data, etrm_data = dict_data

    ### ====== GET AMeriflux data you want =====

    ameriflux_values = ameriflux_data.mmh20
    ameriflux_dates = ameriflux_data.date

    ### ===== EXTRACT JPL values from the tif =====
    feature_dictionary = x_y_extract(shapefile)

    print "feature dictionary", feature_dictionary

    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

    jpl_dates = jpl_data['dates']
    jpl_etas = jpl_data['etas']

    jpl_vals = []
    for eta_path in jpl_etas:

        # EXTRACT JPL point value from the raster
        eta_val = raster_extract(eta_path, x, y)
        jpl_vals.append(eta_val)

    # ===== EXTRACT ETRM from npy files =====
    etrm_tuple = etrm_dict[taw]

    date_objs = etrm_tuple[1]
    print 'date objs \n', date_objs
    etrm_eta_files = etrm_tuple[0]

    etrm_vals = []
    for eta_path in etrm_eta_files:

        # EXTRACT ETRM point value from the raster
        eta_arr = np.load(eta_path)
        eta_val = geospatial_array_extract(geo_info, eta_arr, (x, y))
        etrm_vals.append(eta_val)

    #  ===== Calculate Residuals between Ameriflux (Obs) and JPL (modeled) ========

    # we only want the JPL values that correspond with Ameriflux observations

    dates_in_common = []
    jpl_values_in_common = []
    ameriflux_values_in_common = []

    for aflux_date, a_val in zip(ameriflux_dates, ameriflux_values):
        for jpl_date, jpl_val in zip(jpl_dates, jpl_vals):

            if aflux_date == jpl_date:
                dates_in_common.append(aflux_date)
                jpl_values_in_common.append(jpl_val)
                ameriflux_values_in_common.append(a_val)

    # for the dates and values in common, we take a look at the residuals
    jpl_flux_residuals = []
    for flux_val, jpl_val in zip(ameriflux_values_in_common, jpl_values_in_common):

        # residual is (obs - modeled) / (fraction_error * obs) -> Jan says the error on Ameriflux is 30%
        jpl_flux_resid = (flux_val - jpl_val) / (0.3 * flux_val)
        jpl_flux_residuals.append(jpl_flux_resid)

    # make a histogram
    histogram_residuals(jpl_flux_residuals,
                        title='JPL_Ameriflux_Residuals_30error_{}'.format(location_name),
                        coloring='red')

    #  ===== Calculate Residuals between Ameriflux (Obs) and ETRM (modeled) ========

    etrm_values_in_common = []
    amf_vals_in_common = []


    for aflux_date, a_val in zip(ameriflux_dates, ameriflux_values):
        for etrm_date, etrm_val in zip(date_objs, etrm_vals):

            if aflux_date == etrm_date:
                etrm_values_in_common.append(etrm_val)
                amf_vals_in_common.append(a_val)

    etrm_flux_residuals = []
    for flux_val, etrm_val, in zip( amf_vals_in_common, etrm_values_in_common):

        # residual is (obs - modeled) / (fraction_error * obs) -> Jan says the error on Ameriflux is 30%
        etrm_flux_resid = (flux_val - etrm_val) / (0.3 * flux_val)
        etrm_flux_residuals.append(etrm_flux_resid)

    # make a histogram
    histogram_residuals(etrm_flux_residuals,
                        title='ETRM_Ameriflux_Residuals_30error_{}_{}'.format(location_name, taw),
                        coloring='green')


if __name__ == "__main__":

    # # shapefile
    # shape_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/' \
    #              'optimization_results_april_8/point_extract.shp'
    # # Ameriflux
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'

    shape_path_lst = ['/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcm_point_extract.shp',
                      '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp',
                      '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mjs_point_extract.shp',
                      '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Sg_point_extract.shp',
                      '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Ss_point_extract.shp',
                      '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcp_point_extract.shp',
                      '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcs_point_extract.shp']

    # todo - make sure Mjs is the same as Wjs (I think it is...)
    amf_path_list = ['/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv',
                     '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv',
                     '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Wjs_BASE_HH_7-5.csv',
                     '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Seg_BASE_HH_8-5.csv',
                     '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Ses_BASE_HH_8-5.csv',
                     '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcp_BASE_HH_6-5.csv',
                     '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcs_BASE_HH_3-5.csv']

    for shape, amf in zip(shape_path_lst, amf_path_list):

        # get geo-info path to handle importing numpy files
        geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'
        with open(geo_info_path, mode='r') as geofile:
            geo_dict = yaml.load(geofile)

        jpl_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'

        # dict with keys 'dates' for date objs and 'etas' for filepaths
        jpl_data_dict = get_jpl_results(jpl_path)

        # ETRM
        etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results'
        # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
        etrm_dict = get_etrm_results(etrm_path)


        # get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path
        daily_cum_ameriflux = ec_data_processor(amf)

        # Get the location name
        loc_string = amf.split('/')[-1]
        # print 'loc string ', loc_string
        loc_name = loc_string.split('_')[1]
        print 'loc name {}'.format(loc_name)

        ameriflux_residuals(df_data=(daily_cum_ameriflux), dict_data=(jpl_data_dict, etrm_dict), shapefile=shape,
                            taw='225', geo_info=geo_dict, location_name=loc_name)