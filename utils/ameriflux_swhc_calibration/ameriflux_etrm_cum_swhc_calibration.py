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
import pandas as pd
from matplotlib import pyplot as plt
from datetime import date
import numpy as np
# ============= standard library imports ========================
from utils.ameriflux_swhc_calibration.eta_dataset_plotter import get_etrm_results, ec_data_processor
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import x_y_extract
from utils.TAW_optimization_subroutine.timeseries_processor import accumulator
from utils.ameriflux_swhc_calibration.ameriflux_etrm_swhc_calibration import get_taw_list, get_chisquare_dict,\
    taw_optimize_1d, daily_time_filter, etrm_value_extraction, make_optimization_dict



if __name__ == "__main__":

    """This script has essentially the same functionality as ameriflux_etrm_swhc_calibration.py except for this script
     calibrates cumulative ETa for a defined number of days/months"""

    cumulative_mode = True # todo - may not be necessary
    # options: 'days', 'weeks', 'months', 'years'
    calibration_unit = 'days'
    # indicates that you will calibrate to 3 day cumulative ETa values
    cumulative_int = 14

    # 1) choose the standardized ameriflux .csv dataset to calibrate to
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Seg_BASE_HH_10-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Wjs_BASE_HH_7-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Ses_BASE_HH_8-5.csv'
    amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcp_BASE_HH_6-5.csv'


    # 2) This name will pervade the naming of the output files.
    amf_name = 'US-Vcp'

    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Sg_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcm_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mjs_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Ss_point_extract.shp'
    shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcp_point_extract.shp'

    # get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path
    print 'processing ec data'
    daily_cum_ameriflux = ec_data_processor(amf)

    # # ALSO get cumulative amf ETa values in mm/day by initially getting thirty minute interval data
    # amf_30min = ec_data_processor(amf, daily=False)
    # Then accumulate that data based on the calibration unit and the cumulative interger specified

    # # must do a bit of reformatting todo - probably not necessary. We can do it from the optimization dictionary.
    # daily_cum_ameriflux = daily_cum_ameriflux.reset_index()
    # daily_cum_ameriflux['dt'] = pd.to_datetime(daily_cum_ameriflux.date)
    # daily_cum_ameriflux = daily_cum_ameriflux.set_index('dt')
    # # this is where we accumulate the daily amf values
    # amf_cum = accumulator(time_df=daily_cum_ameriflux, time_unit=calibration_unit, cum_int=cumulative_int)

    # === Now we have daily cumulative ameriflux we can use to get the corresponding daily ETRM values ===
    # once we have the etrm values extracted then we will convert those into a df and run accumulator() on them as well
    #  so that the dates are all equivalent.

    # Get the dates from the ameriflux analysis as a list.
    ameriflux_dates = daily_cum_ameriflux.date
    ameriflux_eta_values = daily_cum_ameriflux.mmh20
    ameriflux_dates = ameriflux_dates.to_list()
    ameriflux_eta_values = ameriflux_eta_values.to_list()

    # print 'len ameriflux_eta_values', len(ameriflux_eta_values)
    # print 'len ameriflux dates', len(ameriflux_dates)

    # Modify Dates
    # 2.1) Specify the growing season
    start_grow_month = 5
    start_grow_day = 15

    end_grow_month = 9
    end_grow_day = 15
    growing_season = ((5, 15), (9, 15))


    ameriflux_dates, ameriflux_eta_values = daily_time_filter(ameriflux_dates, ameriflux_eta_values, growing_season)

    print 'len ameriflux_eta_values', len(ameriflux_eta_values)
    print 'len ameriflux dates', len(ameriflux_dates)


    # 2.5) Did you modify the date range of the ameriflux files from the last time you ran the script
    # OR
    # are you using a different ameriflux tower and shapefil from the last time you ran the scipt?
    date_mod = True


    # ETRM
    # 3) Specify the path to where all of the output arrays for the grid search ETRM run are stored.
    # etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results'
    etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results_ceff_06'
    # 4)
    etrm_dict_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder'

    if os.path.isfile(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name))) and not date_mod:
        print 'date mod is {}'.format(date_mod)
        print 'loading ETRM dict from pre-existing yml file'
        # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
        with open(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name)), 'r') as rfile:
            etrm_dict = yaml.load(rfile)
    else:
        print 'the yml for the etrm data is {}'.format(os.path.isfile(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name))))
        print 'date mod is {}'.format(date_mod)
        print 'making the ETRM yaml file for ameriflux date ranges and retrieving daily ETRM results'
        # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
        # cumulative mode will return all the dates between analysis_dates[0] and analysis_dates[-1]
        print 'number of analysis dates', len(ameriflux_dates)
        etrm_dict = get_etrm_results(etrm_path, observation_dates=ameriflux_dates)

        with open(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name)), 'w') as wfile:
            yaml.dump(etrm_dict, wfile)


    print 'test values in etrm dict'
    print len(etrm_dict['325'][0])
    print len(etrm_dict['325'][1])


    # Manufacture the list of TAWs from the etrm dict
    taw_list = get_taw_list(etrm_dict)

    # create a new dictionary called the optimization dictionary that will be the same as the ETRM dictionary but
    # contain only ameriflux eta values that correspond to the days and observations that ETRM and Ameriflux have in common.
    opt_dict = make_optimization_dict(etrm_dict, ameriflux_eta_values, ameriflux_dates)

    # Geo info
    # DONT need to change unless you change the study area
    geo_info_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder/geo_info_ameriflux.yml'
    with open(geo_info_path, mode='r') as geofile:
        geo_dict = yaml.load(geofile)


    # feature dictionary is for getting the point locations from the point file.
    feature_dictionary = x_y_extract(shape_path)
    print "feature dictionary", feature_dictionary
    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary
        x_y = tup


    etrm_cum_dict = {}
    for param in taw_list:

        print 'accumulating etrm values for param {}'.format(param)
        print 'opt dict param', opt_dict['{}'.format(param)]

        model_vals = etrm_value_extraction(x_y=x_y, param=param, model_dictionary=opt_dict, geo_info=geo_dict)

        # once we have the model values for a given parameter, in place we should make a df datetimes|model_vals
        obs_dates = opt_dict['{}'.format(param)][1]
        obs_values = opt_dict['{}'.format(param)][2]

        # make into a dataframe and reformat so that DF has a datetime index
        model_df = pd.DataFrame({'time': obs_dates, 'model_values': model_vals, 'obs_values': obs_values},
                                columns=['time', 'model_values', 'obs_values'])

        model_df.to_csv('/Users/dcadol/Desktop/daily_model_df_{}.csv'.format(param))

        model_df['dt'] = pd.to_datetime(model_df.time)
        model_df = model_df.set_index('dt')

        cum_df = accumulator(time_df=model_df, time_unit='days', cum_int=cumulative_int)

        # get rid of the zero values
        cum_df = cum_df[cum_df['model_values'] != 0]
        cum_df = cum_df[cum_df['obs_values'] != 0]

        # testing -- output each param cumulative df as a .csv

        cum_df.to_csv('/Users/dcadol/Desktop/cum_model_df_{}.csv'.format(param))

        # extract the dates values from the dataframe and store in a dictionary
        cum_obs_vals = cum_df.obs_values
        cum_obs_vals = cum_obs_vals.to_list()

        cum_dates = cum_df.index
        cum_dates = cum_dates.to_list()
        # convert from datetime into date
        cum_dates = [date(cum_date.year, cum_date.month, cum_date.day) for cum_date in cum_dates]

        cum_model_vals = cum_df.model_values
        cum_model_vals = cum_model_vals.to_list()

        etrm_cum_dict['{}'.format(param)] = (cum_model_vals, cum_dates, cum_obs_vals)

    print 'etrm cum dict', etrm_cum_dict

    estimated_observational_error = 0.3
    chi_dictionary, dof_dict = get_chisquare_dict(model_dictionary=etrm_cum_dict, parameter_lst=taw_list,
                                                  geo_info=geo_dict, x_y=x_y,
                                                  percent_error=estimated_observational_error,
                                                  outpath=etrm_dict_path, name=amf_name, cum_mode=True)

    # get the number of observations out
    dof = dof_dict['{}'.format(taw_list[0])]

    print 'generating chimin dictionary'
    chimin_dict = taw_optimize_1d(parameter_lst=taw_list, chi_dict=chi_dictionary, outpath=etrm_dict_path,
                                  name=amf_name, num_obs=dof, name_extension='cum')

    print 'chi min dictionary \n', chimin_dict

