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
from matplotlib import pyplot as plt
from datetime import date
import numpy as np
# ============= standard library imports ========================
from utils.ameriflux_swhc_calibration.eta_dataset_plotter import get_prism_results, get_jpl_results, get_etrm_results,\
    ec_data_processor
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import x_y_extract, raster_extract


if __name__ == "__main__":

    cumulative_mode = True
    cumulative_int = 3
    # 1)
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Seg_BASE_HH_8-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Wjs_BASE_HH_7-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Ses_BASE_HH_8-5.csv'
    amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcp_BASE_HH_6-5.csv'

    # Vcs does not have growing season overlap with ETRM
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcs_BASE_HH_3-5.csv'

    # 2)
    amf_name = 'US-Vcp'
    # get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path

    daily_cum_ameriflux = ec_data_processor(amf)

    # the date is stored in timeseries column so that column will need to be converted to date object.
    if cumulative_mode:
        ts = daily_cum_ameriflux.timeseries
        ts = ts.to_list()
        date_ts = [date(i.year, i.month, i.day) for i in ts]
        daily_cum_ameriflux['date'] = date_ts

    # Get the dates from the ameriflux analysis as a list.
    ameriflux_dates = daily_cum_ameriflux.date
    ameriflux_eta_values = daily_cum_ameriflux.mmh20
    ameriflux_dates = ameriflux_dates.to_list()
    ameriflux_eta_values = ameriflux_eta_values.to_list()

    # Modify Dates
    # 2.1) Specify the growing season
    start_grow_month = 5
    start_grow_day = 15

    end_grow_month = 9
    end_grow_day = 15
    growing_season = ((5, 15), (9, 15))

    # Note: if cumulative mode
    ameriflux_dates, ameriflux_eta_values = daily_time_filter(ameriflux_dates, ameriflux_eta_values, growing_season)



    # 2.5) Did you modify the date range of the ameriflux files from the last time you ran the script?
    date_mod = True


    # ETRM
    # 3)
    # etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results'
    etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results_ceff_06'
    # 4)
    etrm_dict_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder'

    if os.path.isfile(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name))) and not date_mod:
        print 'date mod is {}'.format(date_mod)
        print 'loading etrm dict from pre-existing yml file'
        # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
        with open(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name)), 'r') as rfile:
            etrm_dict = yaml.load(rfile)
    else:
        print 'the yml for the etrm data is {}'.format(os.path.isfile(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name))))
        print 'date mod is {}'.format(date_mod)
        print 'making the etrm yaml file for ameriflux date ranges'
        # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
        # cumulative mode will return all the dates between analysis_dates[0] and analysis_dates[-1]
        etrm_dict = get_etrm_results(etrm_path, analysis_dates=ameriflux_dates, cumulative_mode=cumulative_mode)

        with open(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name)), 'w') as wfile:
            yaml.dump(etrm_dict, wfile)


    # Manufacture the list of TAWs from the etrm dict
    taw_list = get_taw_list(etrm_dict)

    # Geo info
    # DONT need to change unless you change the study area
    geo_info_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder/geo_info_ameriflux.yml'
    with open(geo_info_path, mode='r') as geofile:
        geo_dict = yaml.load(geofile)


    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Sg_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcm_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mjs_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Ss_point_extract.shp'
    shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcp_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcs_point_extract.shp'

    feature_dictionary = x_y_extract(shape_path)

    print "feature dictionary", feature_dictionary

    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary
        x_y = tup

    estimated_observational_error = 0.3

    chi_dictionary, dof_dict = get_chisquare_dict(obs_dates_lst=ameriflux_dates, obs_values_lst=ameriflux_eta_values,
                                        model_dictionary=etrm_dict, parameter_lst=taw_list, geo_info=geo_dict,
                                        x_y=x_y, percent_error=estimated_observational_error, outpath=etrm_dict_path,
                                        name=amf_name)

    # get the number of observations out
    dof = dof_dict['{}'.format(taw_list[0])]

    print 'generating chimin dictionary'
    chimin_dict = taw_optimize_1d(parameter_lst=taw_list, chi_dict=chi_dictionary, outpath=etrm_dict_path, name=amf_name, num_obs=dof)

    print 'chi min dictionary \n', chimin_dict

