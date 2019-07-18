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
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# ============= standard library imports ========================
from utils.ameriflux_swhc_calibration.eta_dataset_plotter import get_etrm_results, get_jpl_results, get_prism_results, ec_data_processor_precip
from utils.ameriflux_swhc_calibration.ameriflux_etrm_cum_swhc_calibration import get_taw_list
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import raster_extract, x_y_extract

def dataset_processor(jpl_dict, prism_dict):
    """"""

    print 'processing jpl'
    # ====== select jpl from dict =====
    jpl_eta = jpl_dict['etas']
    jpl_dates = jpl_dict['dates']

    # GET the JPL VALUES from the .tif
    jpl_values = []
    for jpl_rast in jpl_eta:
        if jpl_rast.endswith('.tif'):
            jpl_val = raster_extract(jpl_rast, x, y)
            jpl_values.append(jpl_val)

    print 'processing prism'
    # ====== select precip from prism ====
    prism_precip = prism_dict['precips']
    prism_dates = prism_dict['dates']

    # GET the PRISM VALUES from the .tif
    prism_values = []
    for prism_rast in prism_precip:
        prism_val = raster_extract(prism_rast, x, y)
        prism_values.append(prism_val)


    return jpl_values, jpl_dates, prism_values, prism_dates

if __name__ == '__main__':

    print 'plotting Ameriflux, ETRM and JPL ETas to compare with cumulative PRISM for each growing season.'

    # intput parameters

    # ===== Point Info - UTM Shapefile) =====

    sitename = 'Mpj'

    # shapefile
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcp_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Ss_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mjs_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Sg_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcm_point_extract.shp'
    shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp'

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
    prism_path = '/Volumes/Seagate_Blue/ameriflux_aoi/PRISM/precip/800m_std_all'

    # dict with keys 'dates' for date objs and 'precips' for filepaths
    prism_dict = get_prism_results(prism_path)

    # ===== Observational ETa Time Series =====

    # JPL - format = 'YYYY.mm.dd.PTJPL.ET_daily_kg.MODISsin1km_etrm.tif' [using full ETRM dataset so you can plot
    # against Ameriflux that is outside of Study area]
    jpl_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'

    # dict with keys 'dates' for date objs and 'etas' for filepaths
    jpl_data_dict = get_jpl_results(jpl_path)

    # Ameriflux
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'
    ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Seg_BASE_HH_10-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Ses_BASE_HH_8-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcp_BASE_HH_6-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Wjs_BASE_HH_7-5.csv'

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
    amf_df.set_index('amf_dates', inplace=True)

    # ETRM - get it from the original output files
    # etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results'
    etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results_ceff_06'
    taw = '425'

    # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
    etrm_dict = get_etrm_results(etrm_path)

    # get geo-info path to handle importing numpy files
    # geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'
    geo_info_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder/geo_info_ameriflux.yml'
    with open(geo_info_path, mode='r') as geofile:
        geo_dict = yaml.load(geofile)



    # ====== select etrm dataset based on TAW =======
    etrm_eta_tup = etrm_dict[taw]

    etrm_eta = etrm_eta_tup[0]
    etrm_dates = etrm_eta_tup[1]

    # GET THE ETRM VALUES from the numpy array
    etrm_values = []
    for etrm_rast in etrm_eta:
        etrm_arr = np.load(etrm_rast)
        etrm_val = geospatial_array_extract(geo_dict, etrm_arr, (x, y))
        etrm_values.append(etrm_val)


    # process JPL and PRISM datasets [extract them from the .tif]
    jpl_values, jpl_dates, prism_values, prism_dates = dataset_processor(jpl_dict=jpl_data_dict, prism_dict=prism_dict)


    # ==================================================
    # ================ PHASE II ========================
    #===================================================


    # convert each timeseries to a dataframe

    jpl_df = pd.DataFrame({'jpl_values': jpl_values, 'jpl_dates': jpl_dates})
    prism_df = pd.DataFrame({'prism_values': prism_values, 'prism_dates':prism_dates})
    etrm_df = pd.DataFrame({'etrm_values': etrm_values, 'etrm_dates': etrm_dates})

    # make each dataframe have the date as the index
    jpl_df.set_index('jpl_dates', inplace=True)
    prism_df.set_index('prism_dates', inplace=True)
    etrm_df.set_index('etrm_dates', inplace=True)

    # join the dataframes
    combined_df = etrm_df.join(jpl_df, how='outer').join(prism_df, how='outer').join(amf_df, how='outer')

    # TODO - How do I get ETRM runoff (monthly into this dataset?)

    # output the file

    combined_df.to_csv('/Users/dcadol/Desktop/academic_docs_II/combined_timeseries_{}_taw{}_plus19hrs.csv'.format(sitename, taw))


