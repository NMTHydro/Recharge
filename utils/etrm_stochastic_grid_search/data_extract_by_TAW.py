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
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
# ============= standard library imports ========================
from utils.ameriflux_swhc_calibration.eta_dataset_plotter import get_etrm_results, get_jpl_results, get_prism_results, ec_data_processor_precip
from utils.ameriflux_swhc_calibration.ameriflux_etrm_cum_swhc_calibration import get_taw_list
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import raster_extract, x_y_extract
from utils.ameriflux_swhc_calibration.eta_point_dataset_generator import dataset_processor



### TODO - Add code to extract all the necessary datasets for calibration and figure making to be saved to the same .csv

"""Get PRISM, Ameriflux ET, Ameriflux soil moisture, AMERIFLUX precip, GADGET refET AND all 4 ETRM datasets side 
by side for a given TAW and put em in the same csv for later reference."""


def convert_sm_to_rzsm(rzsm_df, sitename, nrml=True):
    """

    :param rzsm_df:
    :return:
    """

    shallow = rzsm_df['shall_swc_interp']
    mid = rzsm_df['mid_swc_interp']
    deep = rzsm_df['deep_swc_interp']

    if sitename == 'vcp' or sitename == 'vcm':

        shallow_flight = 80.0
        middle_flight = 170.0
        deep_flight = 300.0

        smoisture_avg = ((shallow * shallow_flight) + (mid * middle_flight) + (deep * deep_flight)) / \
                 (shallow_flight + middle_flight + deep_flight)

    elif sitename == 'wjs':

        shallow_flight = 80.0
        middle_flight = 170.0
        deep_flight = 200.0

        smoisture_avg = ((shallow * shallow_flight) + (mid * middle_flight) + (deep * deep_flight)) / \
                        (shallow_flight + middle_flight + deep_flight)

    elif sitename == 'mpj':

        shallow_flight = 80.0
        middle_flight = 70.0
        deep_flight = 200.0

        smoisture_avg = ((shallow * shallow_flight) + (mid * middle_flight) + (deep * deep_flight)) / \
                        (shallow_flight + middle_flight + deep_flight)

    elif sitename == 'ses' or sitename == 'seg':

        shallow_flight = 80.0
        middle_flight = 170.0
        deep_flight = 300.0

        smoisture_avg = ((shallow * shallow_flight) + (mid * middle_flight) + (deep * deep_flight)) / \
                        (shallow_flight + middle_flight + deep_flight)


    rzsm_df['depth_avg_sm'] = smoisture_avg

    print 'depth avg sm \n', smoisture_avg

    if nrml:
        # Get min and max from a long dataset
        ma = max(smoisture_avg.dropna())
        print "ma", ma
        mi = min(smoisture_avg.dropna())
        print "mi", mi

        # normalized scale
        n0 = 0
        n1 = 1

        # create a new normalized dataset
        nrml_data = [n0 + ((value - mi) * (n1 - n0)) / (ma - mi) for value in smoisture_avg]
        print 'nrml data arr \n', nrml_data
        # print "lenght of normalized data", len(nrml_data)
        # print "actual normal data array", nrml_data

        rzsm_df['nrml_depth_avg_sm'] = nrml_data

    return rzsm_df




if __name__ == '__main__':

    # # intput parameters
    #
    # # ===== Point Info - UTM Shapefile) =====
    #
    # sitename = 'seg'
    # sitename = 'ses'
    sitename = 'wjs'

    # shapefile
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcp_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Ss_point_extract.shp'
    shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mjs_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Sg_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcm_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp'

    # get the x and y from the shapefile in order to extract
    # ... from rasters raster_extract() and geospatial arrays geospatial_array_extract()
    feature_dictionary = x_y_extract(shape_path)
    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

    # ===== Precip Time Series =====

    # PRISM - format = 'precip_YYYYjjj.tif' where jjj is three digit day of year
    prism_path = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_inputs/{}_aoi/PRISM/precip/800m_std_all'.format(sitename)
    # prism_path = '/Volumes/Seagate_Blue/ameriflux_aoi/PRISM/precip/800m_std_all'
    # dict with keys 'dates' for date objs and 'precips' for filepaths
    prism_dict = get_prism_results(prism_path)

    # ===== Observational ETa Time Series =====

    # JPL - format = 'YYYY.mm.dd.PTJPL.ET_daily_kg.MODISsin1km_etrm.tif' [using full ETRM dataset so you can plot
    # against Ameriflux that is outside of Study area]
    jpl_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'

    # dict with keys 'dates' for date objs and 'etas' for filepaths
    jpl_data_dict = get_jpl_results(jpl_path)

    # process JPL and PRISM datasets [extract them from the .tif]
    jpl_values, jpl_dates, prism_values, prism_dates = dataset_processor(jpl_dict=jpl_data_dict, prism_dict=prism_dict, x=x, y=y)

    jpl_df = pd.DataFrame({'jpl_values': jpl_values, 'jpl_dates': jpl_dates})
    prism_df = pd.DataFrame({'prism_values': prism_values, 'prism_dates': prism_dates})

    # make each dataframe have the date as the index
    jpl_df.set_index('jpl_dates', inplace=True)
    prism_df.set_index('prism_dates', inplace=True)

    # Ameriflux
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Seg_BASE_HH_10-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Ses_BASE_HH_8-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcp_BASE_HH_6-5.csv'
    ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Wjs_BASE_HH_7-5.csv'

    # get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path
    # daily_cum_ameriflux = ec_data_processor(ameriflux_path)
    daily_cum_ameriflux, daily_cum_site_precip = ec_data_processor_precip(ameriflux_path)

    ameriflux_eta_values = daily_cum_ameriflux.mmh20
    ameriflux_precip_values = daily_cum_site_precip.P
    ameriflux_dates = daily_cum_ameriflux.date
    ameriflux_precip_dates = daily_cum_site_precip.date

    amf_df = pd.DataFrame({'amf_eta_values': ameriflux_eta_values, 'amf_precip_values': ameriflux_precip_values,
                           'amf_dates': ameriflux_dates, 'amf_precip_dates': ameriflux_precip_dates})
    # TODO - will this cause issues for the precip values?

    amf_df.loc[amf_df['amf_dates'].isnull(), 'amf_dates'] = amf_df['amf_precip_dates']
    amf_df.set_index('amf_dates', inplace=True)

    print 'output test amf df to check for defects'

    amf_df.to_csv('/Users/dcadol/Desktop/amf_testicle.csv')
    # ========================== GET RZSM data ===========================


    # rzsm_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/soil_moisture_data/amf_soil_moisture/US-Mpj_daily_SWC.csv'
    # rzsm_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/soil_moisture_data/amf_soil_moisture/US-Seg_daily_SWC.csv'
    # rzsm_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/soil_moisture_data/amf_soil_moisture/US-Ses_daily_SWC.csv'
    rzsm_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/soil_moisture_data/amf_soil_moisture/US-Wjs_daily_SWC.csv'
    # rzsm_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/soil_moisture_data/amf_soil_moisture/US-Vcp_daily_SWC.csv'
    rzsm_df = pd.read_csv(rzsm_path, header=3)

    date_col = rzsm_df['date']



    datetime_date_col = [datetime.strptime(i, '%m/%d/%y') for i in date_col]
    datetime_date_col = [date(i.year, i.month, i.day) for i in datetime_date_col]

    rzsm_df['date_dt'] = datetime_date_col
    rzsm_df['date_index'] = datetime_date_col

    rzsm_df.set_index('date_index', inplace=True)

    # inspired by the code in jornada_std_error.py
    rzsm_df = convert_sm_to_rzsm(rzsm_df, sitename, nrml=True)

    rzsm_df.to_csv('/Users/dcadol/Desktop/rzsm_df_test_{}.csv'.format(sitename))



    # # plt.plot(rzsm_df['date_dt'], rzsm_df['shall_swc_interp'], color='blue')
    # # plt.plot(rzsm_df['date_dt'], rzsm_df['mid_swc_interp'], color='green')
    # # plt.plot(rzsm_df['date_dt'], rzsm_df['deep_swc_interp'], color='red')
    # # plt.show()
    #
    # join the dataframes
    combined_df = jpl_df.join(prism_df, how='outer').join(amf_df, how='outer').join(rzsm_df, how='outer')
    #
    # # test
    # combined_df.to_csv('/Users/dcadol/Desktop/combined_dataset_test.csv')

    # # todo - make a ton of new files where you join each stochastic variable output [infil, rzsm, ro, eta] for a
    # # given TAW with all of these variables

    # # tESTING
    # combined_df_path = '/Users/dcadol/Desktop/combined_dataset_test.csv'
    #
    # combined_df = pd.read_csv(combined_df_path, parse_dates=True, index_col=0)

    print 'precip \n', combined_df['amf_precip_values']

    print combined_df.head()

    print combined_df.index.values
    #
    vars = ['infil', 'rzsm', 'ro', 'eta']

    # starting TAW value
    begin_taw = 25
    # ending TAW value
    end_taw = 925
    # grid search step size. Each ETRM run will increase the uniform TAW of the RZSW holding capacity by this many mm.
    taw_step = 25

    averaged_fmt = '{}_taw_{}_average.csv'

    averaged_etrm_path = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_III/{}/stochastic_csvs/averaged'.format(sitename)

    for i in range(0, ((end_taw - begin_taw) / taw_step)):
        if i == 0:
            current_taw = begin_taw
        else:
            current_taw += taw_step

        dfList = []
        for var in vars:

            etrm_csv_name = averaged_fmt.format(var, current_taw)
            etrm_csv_path = os.path.join(averaged_etrm_path, etrm_csv_name)

            etrm_df = pd.read_csv(etrm_csv_path, parse_dates=True, index_col=3)

            print etrm_df.head()
            print etrm_df.index.values

            dfList.append(etrm_df)

        reduced_df = reduce(lambda x, y: pd.merge(x, y, how='outer', left_index=True, right_index=True), dfList)

        big_df = reduced_df.merge(combined_df, how='outer', left_index=True, right_index=True)

        big_df.to_csv('/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_III/{}/taw_{}_dataset.csv'.format(sitename, current_taw))




