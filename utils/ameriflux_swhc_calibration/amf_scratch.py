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
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import x_y_extract, raster_extract
from utils.ameriflux_swhc_calibration.eta_dataset_plotter import daily_time_parse, ec_data_processor_precip


ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'

amf_test, precip_df = ec_data_processor_precip(ameriflux_path)

plt.plot(precip_df.date, precip_df.P, color='red')
plt.show()


amf_df = pd.read_csv(ameriflux_path, header=2)

amf_df = amf_df[amf_df['P'] != -9999]

precip = amf_df['P']

time = amf_df['TIMESTAMP_START'].apply(lambda b: dt.strptime(str(b), '%Y%m%d%H%M'))


halfhour_data = pd.DataFrame({'timeseries': time, 'P': precip}) # took out precip. no good vals? 'P': P

# set the timeseries column to the index so groupby function can group by year and month of the index.
halfhour_data = halfhour_data.set_index(pd.DatetimeIndex(halfhour_data['timeseries']))

daily_cum_data = halfhour_data.groupby([lambda x: x.year, lambda x: x.month, lambda x: x.day]).sum()

# # get each day in the timeseries. there are duplicates from the groupby function, so use set() to get rid of
# #  duplicates
daily_cum_time = daily_time_parse(time)
#
# # # testing
# # daily_cum_data.to_csv('/Users/dcadol/Desktop/daily_cumulative_df.csv')
#
# format daily_cum_data to have datetimes
daily_cum_data['date'] = daily_cum_time

print daily_cum_data

# plt.plot(time, precip)
# plt.show()
#
plt.plot(daily_cum_data.date, daily_cum_data.P)
plt.show()