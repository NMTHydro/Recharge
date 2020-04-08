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
from utils.ameriflux_swhc_calibration.eta_dataset_plotter import get_etrm_results,\
    ec_data_processor
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import x_y_extract

def daily_time_filter(date_lst, value_lst, mo_day_tpl):
    """
    filters a daily time series based on ((start mo, start day),(end mo, end day))
    :param date_lst: list of date objects
    :param value_lst: list of values corresponding to date objects in time series
    :param mo_day_tpl: ((start mo, start day),(end mo, end day)) where tuples contain date objects
    :return: filtered list of date objects and values
    """
    filtered_dates = []
    filtered_values = []
    for d, v in zip(date_lst, value_lst):

        yr = d.year

        start_d = date(yr, mo_day_tpl[0][0], mo_day_tpl[0][1])
        end_d = date(yr, mo_day_tpl[1][0], mo_day_tpl[1][1])

        if (d > start_d) and (d < end_d):
            filtered_dates.append(d)
            filtered_values.append(v)

    return filtered_dates, filtered_values

def get_taw_list(etrm_dict):
    """

    :param etrm_dict:
    :return:
    """
    taw_lst = []
    for key in etrm_dict.keys():
        taw_lst.append(int(key))

    taw_lst = sorted(taw_lst)
    return taw_lst

def taw_optimize_1d(parameter_lst, chi_dict, outpath, name, num_obs, name_extension='noncum', swhc_vals=None, swhc_method=None):
    """
    Make a detailed optimization summary and output to yml file. Save a plot of the chi square vs swhc and display plot
    :param parameter_lst:
    :param chi_dict:
    :param outpath:
    :param name:
    :param num_obs:
    :return:
    """


    print 'optimizing'


    chimin_dict = {}

    chi_list = []
    for param in parameter_lst:
        print 'param {}'.format(param)
        print 'chi dictionary {}'.format(chi_dict['{}'.format(param)])
        chi_list.append(chi_dict['{}'.format(param)])

    chi_min = chi_list[0]
    for chi, param in zip(chi_list, parameter_lst):

        if chi < chi_min:
            chi_min = chi

    delta_chi = chi_min + 3.841459

    print 'min chi square is', chi_min

    chimin_dict['optimum_chi'] = chi_min
    chimin_dict['param_lst'] = parameter_lst
    chimin_dict['chi_lst'] = chi_list
    chimin_dict['delta_chi'] = delta_chi
    chimin_dict['number_of_observations'] = num_obs

    print 'making chi min output'
    chimin_output = os.path.join(outpath, '{}_chimin_{}.yml'.format(name, name_extension))
    with open(chimin_output, 'w') as wfile:
        yaml.dump(chimin_dict, wfile)

    # get the index of the minimum value in the chi list for plotting
    chimin_indx = chi_list.index(min(chi_list))



    print 'plotting'
    fig = plt.figure(figsize=(12, 5))# TODO - Adjust Y lim for RZSM
    ax1 = plt.subplot(111)
    # print type(chi_list)
    # print type(parameter_lst)
    print chi_list
    print parameter_lst
    ax1.scatter(parameter_lst, chi_list, color='blue', label='Chi Square')
    ax1.scatter(parameter_lst[chimin_indx], chi_list[chimin_indx], color='red')
    ax1.axvline(x=parameter_lst[chimin_indx], color='red', label='SWHC of Min. Chi Square')
    # ax1.axvline(y=min(chi_list), color='r', linestyle='-', label='Minimum Chi Squared')
    #ax.axhline(y=delta_chi, color='r', linestyle='-', label='95% ci line')
    ax1.axvline(x=swhc_vals[0], color='green', label='SWHC ' + swhc_method[0])
    ax1.axvline(x=swhc_vals[1], color='purple', label='SWHC ' + swhc_method[1])
    ax1.axvline(x=swhc_vals[2], color='black', label='SWHC ' + swhc_method[2])
    ax1.axvline(x=swhc_vals[3], color='orange', label='SWHC ' + swhc_method[3])
    ax1.axvline(x=swhc_vals[4], color='brown', label='SWHC ' + swhc_method[4])
    # plt.xticks(wjs_taws, wjs_method, rotation='vertical')
    ax1.set_title('Chi Square against SWHC for Ameriflux Site {}'.format(name))
    ax1.set_ylabel('Chi Square')
    ax1.set_xlabel('Soil Water Holding Capacity (mm)')
    ax1.set_facecolor('xkcd:light grey')
    # ax1.set_aspect(1)# only feasible for 14 day
    # plt.ylim(0, 8000) # for 1 day
    plt.ylim(0, 1500) # for 7 day
    # plt.ylim(0, 450) # for 14_day
    # plt.ylim(0, 760000) # for rzsm
    plt.xlim(0, 925)
    ax1.grid(True)
    ax1.minorticks_on()
    ax1.legend(loc='lower right')

    fig_output_path = os.path.join(outpath, '{}_chiplot_{}.png'.format(name, name_extension))
    plt.savefig(fig_output_path)
    plt.show()

    return chimin_dict

def etrm_value_extraction(x_y, param, model_dictionary, geo_info):
    """"""
    # Unpack the coordinates
    x, y = x_y

    model_files = model_dictionary['{}'.format(param)][0]
    print 'these are the model files \n', model_files
    # # these will be different from obs_dates_lst in the case of cumulative_mode = True
    # model_dates = model_dictionary['{}'.format(param)][1]
    model_vals = []
    print 'extracting for param {}'.format(param)
    for model_path in model_files:
        # EXTRACT ETRM point value from the raster
        model_arr = np.load(model_path)
        val = geospatial_array_extract(geo_info, model_arr, (x, y))
        model_vals.append(val)

    return model_vals

def get_chisquare_dict(model_dictionary, parameter_lst, error, outpath, name, cum_mode=False, geo_info=None,
                       x_y=None, rzsm=False, name_extension=None, cum_value=None, sitename=None):
    """
    Make a dict of the sum of squared normalized residuals indexed by parameter value.
    :param obs_dates_lst:
    :param obs_values_lst:
    :param model_dictionary: dictionary of etrm results
    :param parameter_lst: the list of TAWs
    :param geo_info:
    :param x_y:
    :param error:
    :param outpath:
    :param name:
    :return:
    """

    # track the degrees of freedom
    n = 0

    # for storing the chi square of each parameter value
    chi_dict = {}

    # hold on to the normalized residuals
    resid_dict = {}

    # track degrees of freedom
    dof_dict = {}

    for param in parameter_lst:

        # extract the model values based on the model_dictionary which is etrm files corresponding to ameriflux
        #  observation dates.

        if rzsm:
            model_vals = model_dictionary['{}'.format(param)][0]

        elif not cum_mode:
            model_vals = etrm_value_extraction(x_y, param, model_dictionary, geo_info)

        else:
            model_vals = model_dictionary['{}'.format(param)][0]

        # get the observed values from the optimization dictionary
        obs_values_lst = model_dictionary['{}'.format(param)][2]

        # the dates in common are stored at index 1 in the optimization dict tuple
        obs_dates_lst = model_dictionary['{}'.format(param)][1]

        # old version of how it was done. For safekeeping
        # model_files = model_dictionary['{}'.format(param)][0]
        # # these will be different from obs_dates_lst in the case of cumulative_mode = True
        # model_dates = model_dictionary['{}'.format(param)][1]
        # model_vals = []
        # print 'extracting for param {}'.format(param)
        # for model_path in model_files:
        #     # EXTRACT ETRM point value from the raster
        #     model_arr = np.load(model_path)
        #     val = geospatial_array_extract(geo_info, model_arr, (x, y))
        #     model_vals.append(val)
        #
        # # calculate the normalized residual
        # resid_lst = []
        # chisquare_resid = 0
        # print 'taking residuals for {}'.format(param)

        # calcualte the normalized residual
        resid_lst = []
        chisquare_resid = 0
        print 'taking residuals for {}'.format(param)
        print 'the lenght of the obs values list {}'.format(len(obs_values_lst))
        print 'the lenght of the model values list {}'.format(len(model_vals))

        for obs_val, mod_val in zip(obs_values_lst, model_vals):

            # === Switch to additive error assumption if observation is lower than a certain threshold ===

            if cum_mode:
                if cum_value == 7:
                    if obs_val > 2.0:
                        residual_value = (obs_val - mod_val) / (error * obs_val)
                    else:
                        residual_value = (obs_val - mod_val) / 2.0
                elif cum_value == 14:
                    if obs_val > 4.0:
                        residual_value = (obs_val - mod_val) / (error * obs_val)
                    else:
                        residual_value = (obs_val - mod_val) / 4.0

                elif cum_value == 1:
                    if obs_val > 1.0:
                        residual_value = (obs_val - mod_val) / (error * obs_val)
                    else:
                        residual_value = (obs_val - mod_val) / 1.0
            else:
                # Normailization
                # [n0 + ((value - mi) * (n1 - n0)) / (ma - mi) where n1=1 and n0 = 0 value, mi and ma are tdr values with uncertainty
                # (error + error) / (error + error)

                residual_value = (obs_val - mod_val) / error
                # if obs_val < 0.05:
                #     residual_value = (obs_val - mod_val) / 0.05
                # if sitename == 'wjs':
                #
                #     # shallow_flight = 80.0
                #     # middle_flight = 170.0
                #     # deep_flight = 200.0
                #     #
                #     # tdr_uncertainty = 0.015
                #     #
                #     # smoisture_uncertainty = (tdr_uncertainty * (shallow_flight + middle_flight + deep_flight)) / (shallow_flight + middle_flight + deep_flight)
                #     #
                #     # # smoisture_avg = ((shallow * shallow_flight) + (mid * middle_flight) + (deep * deep_flight)) / \
                #     # #                 (shallow_flight + middle_flight + deep_flight)
                #
                #     residual_value = (obs_val - mod_val) / error
                #
                # elif sitename == 'ses' or sitename == 'seg':
                #
                #     shallow_flight = 80.0
                #     middle_flight = 170.0
                #     deep_flight = 300.0
                #
                #     residual_value = (obs_val - mod_val) / 0.015
                #
                # elif sitename == 'mpj':
                #
                #     shallow_flight = 80.0
                #     middle_flight = 70.0
                #     deep_flight = 200.0
                #
                #     residual_value = (obs_val - mod_val) / 0.015
                #
                # elif sitename == 'vcp' or sitename == 'vcs':
                #
                #     shallow_flight = 80.0
                #     middle_flight = 170.0
                #     deep_flight = 300.0
                #
                #     residual_value = (obs_val - mod_val) / 0.015




            resid_lst.append(residual_value)
            # accrete the squared normalized residual to the chi square value
            chisquare_resid += residual_value ** 2

            # for every observation there is one more degree of freedom
            n += 1

        # store a timeseries of residuals indexed by parameters
        resid_dict['{}'.format(param)] = (obs_dates_lst, resid_lst)

        # store the chi square value indexed by parameter value
        chi_dict['{}'.format(param)] = chisquare_resid

        # store the degrees of freedom for each param (should not change)
        dof_dict['{}'.format(param)] = n

    # output the resid dict to a yml
    print 'output residuals'
    resid_storage_path = os.path.join(outpath, '{}_resid_{}.yml'.format(name, name_extension))
    with open(resid_storage_path, 'w') as wfile:
        yaml.dump(resid_dict, wfile)

    return chi_dict, dof_dict

def make_optimization_dict(etrm_dict, obs_values, obs_dates):
    """
    Since get_etrm_results gets us an etrm dict with only values corresponding to observations, we have to make sure
    that the observations that we use in the optimization also correspond to the ETRM values
    :param etrm_dict:
    :param obs_values:
    :param obs_dates:
    :return:
    """

    opt_dict = {}

    # value = (sorted files, sorted dates)
    for key, value in etrm_dict.iteritems():
        # print 'key', key
        # print 'value', value

        etrm_files = value[0]
        etrm_dates = value[1]

        corr_obs = []

        # for etrm_f, etrm_d, obs_val, obs_date in zip(etrm_files, etrm_dates, obs_values, obs_dates):

        for obs_val, obs_date in zip(obs_values, obs_dates):

            if obs_date in etrm_dates:
                corr_obs.append(obs_val)

        # the optimization dictionary is the same as the ETRM dictionary but with the corresponding observations attached
        opt_dict[key] = (etrm_files, etrm_dates, corr_obs)

    return opt_dict



if __name__ == "__main__":

    # 1)
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Seg_BASE_HH_8-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'
    amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Wjs_BASE_HH_7-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Ses_BASE_HH_8-5.csv'
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcp_BASE_HH_6-5.csv'

    # Vcs does not have growing season overlap with ETRM
    # amf = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcs_BASE_HH_3-5.csv'

    # 2)
    amf_name = 'US-Mpj'
    # get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path

    daily_cum_ameriflux = ec_data_processor(amf)

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


    ameriflux_dates, ameriflux_eta_values = daily_time_filter(ameriflux_dates, ameriflux_eta_values, growing_season)

    print 'len ameriflux_eta_values', len(ameriflux_eta_values)
    print 'len ameriflux dates', len(ameriflux_dates)

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

        etrm_dict = get_etrm_results(etrm_path, observation_dates=ameriflux_dates)

        with open(os.path.join(etrm_dict_path, '{}.yml'.format(amf_name)), 'w') as wfile:
            yaml.dump(etrm_dict, wfile)



    # Manufacture the list of TAWs from the etrm dict
    taw_list = get_taw_list(etrm_dict)

    # create a new dictionary called the optimization dictionary that will be the same as the ETRM dictionary but
    # contain only ameriflux eta values that correspond to the days and observations that ETRM and Ameriflux have in common.
    opt_dict = make_optimization_dict(etrm_dict, ameriflux_eta_values, ameriflux_dates)

    # print 'opt dict 325\n', opt_dict['325']

    # Geo info
    # DONT need to change unless you change the study area
    geo_info_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder/geo_info_ameriflux.yml'
    with open(geo_info_path, mode='r') as geofile:
        geo_dict = yaml.load(geofile)


    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Sg_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcm_point_extract.shp'
    shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mjs_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Ss_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcp_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcs_point_extract.shp'

    feature_dictionary = x_y_extract(shape_path)

    print "feature dictionary", feature_dictionary

    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary
        x_y = tup

    estimated_observational_error = 0.3

    print 'opt_dict\n', opt_dict
    chi_dictionary, dof_dict = get_chisquare_dict(model_dictionary=opt_dict, parameter_lst=taw_list,
                                                  geo_info=geo_dict, x_y=x_y,
                                                  error=estimated_observational_error,
                                                  outpath=etrm_dict_path, name=amf_name)

    # get the number of observations out
    dof = dof_dict['{}'.format(taw_list[0])]

    print 'generating chimin dictionary'
    chimin_dict = taw_optimize_1d(parameter_lst=taw_list, chi_dict=chi_dictionary, outpath=etrm_dict_path, name=amf_name, num_obs=dof)

    print 'chi min dictionary \n', chimin_dict

