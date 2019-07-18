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
import matplotlib.pyplot as plt
from utils.ameriflux_swhc_calibration.eta_dataset_plotter import get_etrm_results, get_jpl_results, get_prism_results, ec_data_processor_precip
from utils.ameriflux_swhc_calibration.ameriflux_etrm_cum_swhc_calibration import get_taw_list
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import raster_extract, x_y_extract

# ===== Precip Time Series =====

# PRISM - format = 'precip_YYYYjjj.tif' where jjj is three digit day of year
# prism_path = '/Volumes/Seagate_Blue/ameriflux_aoi/PRISM/precip/800m_std_all'
prism_path = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_inputs/mpj_aoi/PRISM/precip/800m_std_all'
# dict with keys 'dates' for date objs and 'precips' for filepaths
prism_dict = get_prism_results(prism_path)

# Ameriflux
ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'

# get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path
daily_cum_ameriflux, daily_cum_site_precip = ec_data_processor_precip(ameriflux_path)

ameriflux_eta_values = daily_cum_ameriflux.mmh20
ameriflux_precip_values = daily_cum_site_precip.P
ameriflux_dates = daily_cum_ameriflux.date
ameriflux_precip_dates = daily_cum_site_precip.date


amf_df = pd.DataFrame({'amf_eta_values': ameriflux_eta_values, 'amf_precip_values': ameriflux_precip_values,
                       'amf_dates': ameriflux_dates, 'amf_precip_dates': ameriflux_precip_dates})
# TODO - will this cause issues for the precip values?
amf_df.set_index('amf_dates', inplace=True)




shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp'

# get the x and y from the shapefile in order to extract
# ... from rasters raster_extract() and geospatial arrays geospatial_array_extract()
feature_dictionary = x_y_extract(shape_path)
# Use the feature dictionary to extract data from the rasters.
for feature, tup in feature_dictionary.iteritems():
    # Get the X and Y coords from the dictionary and unpack them
    x, y = tup
    print x, y

print 'ameriflux dates', ameriflux_dates

print 'processing prism'
# ====== select precip from prism ====
prism_precip = prism_dict['precips']
prism_dates = prism_dict['dates']

# GET the PRISM VALUES from the .tif
prism_values = []
for prism_rast in prism_precip:
    prism_val = raster_extract(prism_rast, x, y)
    prism_values.append(prism_val)

prism_df = pd.DataFrame({'prism_values': prism_values, 'prism_dates':prism_dates})


# # join the dataframes
# combined_df = prism_df.join(amf_df, how='outer')

# amf_df.rename(columns={amf_df.columns[0]: 'date_string'}, inplace=True)
# amf_df['dt'] = pd.to_datetime(amf_df.iloc[:, 0])
# print 'amf dt ', amf_df['dt']
# amf_df.set_index('dt', drop=False, inplace=True)
# amf_df.drop(['date_string'], axis=1, inplace=True)


prism = prism_df['prism_values'].tolist()
site_precip = amf_df['amf_precip_values'].tolist()
# site_precip_dates = pd.to_datetime(combined_df['amf_precip_dates']).tolist()
# etrm_et = combined_df['etrm_values'].tolist()
# amf_et = amf_df['amf_eta_values'].tolist()
# data_date = amf_df['dt'].tolist()

# print 'site precip dates \n', site_precip_dates

# data_date = [d.to_pydatetime() for d in data_date]


plt.plot(prism_dates, prism, color='blue')
plt.plot(ameriflux_precip_dates, site_precip, color='orange')
plt.show()