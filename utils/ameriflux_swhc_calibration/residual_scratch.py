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
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import datetime
# ============= standard library imports ========================
from utils.TAW_optimization_subroutine.timeseries_processor import accumulator


root = '/Volumes/Seagate_Blue/taw_optimization_work_folder/ceff_06'

chimin_path = os.path.join(root, 'US-Mpj_chimin_noncum.yml')

resid_path = os.path.join(root, 'US-Mpj_resid.yml')

taw_lst = [25, 125, 225, 325, 425, 525, 625, 725, 825, 925, 1025,
           1125, 1225, 1325, 1425, 1525, 1625, 1725, 1825, 1925] # ceff_06 doesn't have [2025]

cumulative = False
cum_int = 3
taw = '425'

with open(chimin_path, 'r') as rfile:
    chimin_dict = yaml.load(rfile)
with open(resid_path, 'r') as rfile:
    resid_dict = yaml.load(rfile)


print 'residual dict \n', resid_dict


resid_tseries = resid_dict[taw][0]
resid_vals = resid_dict[taw][1]

# sort t series greatest to least and keep timeseries there.

resid_sorted = sorted(zip(resid_vals, resid_tseries))

# TODO - Grab the PRISM data for the large values on either end of resid_sorted for the pixel...

# combined_timeseries_path = '/Users/dcadol/Desktop/academic_docs_II/combined_timeseries_Mpj_taw425_prismTZ.csv'
combined_timeseries_path = '/Users/dcadol/Desktop/academic_docs_II/combined_timeseries_Mpj_taw425_plus19hrs.csv'
combined_df = pd.read_csv(combined_timeseries_path, header=0)
combined_df.rename(columns={combined_df.columns[0]: 'date_string'}, inplace=True)
combined_df['dt'] = pd.to_datetime(combined_df.iloc[:, 0])
combined_df.set_index('dt', drop=False, inplace=True)
combined_df.drop(['date_string'], axis=1, inplace=True)

if cumulative:
    combined_df = accumulator(time_df=combined_df, time_unit='days', cum_int=cum_int)

print 'combined_df \n', combined_df

prism = combined_df['prism_values']

# print 'prism \n', prism

resid_large = resid_sorted[0:10] + resid_sorted[-11:]

print 'eight largest residuals ', resid_large


# plt.plot(combined_df.index.values, prism)
# plt.plot(combined_df.index.values, combined_df['amf_eta_values'])
# plt.plot(combined_df.index.values, combined_df['etrm_values'])
# plt.show()

resid_dates = []
resid_vals = []
for resid_tup in resid_large:

    val, dt = resid_tup

    # print 'dt {}'.format(dt)

    # datetime.datetime(dt)
    resid_dates.append(dt)
    resid_vals.append(val)

df_datelist = combined_df['dt'].tolist()

high_outlier_indices = []
for i, d in enumerate(df_datelist):

    # print d.year, d.month, d.day

    for res_tup in resid_large:
        res_val, res_d = res_tup

        # print res_d.year, res_d.month, res_d.day
        if (res_d.year, res_d.month, res_d.day) == (d.year, d.month, d.day):
            # print 'resday', (res_d.year, res_d.month, res_d.day), 'dday', (d.year, d.month, d.day)
        # if res_d == d:
            high_outlier_indices.append(i)

print high_outlier_indices

# site_precip_dates = []
# for precip_date in combined_df['amf_precip_dates']:
#
#     print precip_date
#     print type(precip_date)
#     # year = int(precip_date.split('-')[0])
#     # month = int(precip_date.split('-')[1])
#     # day = int(precip_date.split('-')[2])
#
#     # precip_dt = datetime.datetime(year, month, day)
#     #
#     # site_precip_dates.append(precip_dt)



prism = combined_df['prism_values'].tolist()
site_precip = combined_df['amf_precip_values'].tolist()
# site_precip_dates = pd.to_datetime(combined_df['amf_precip_dates']).tolist()
etrm_et = combined_df['etrm_values'].tolist()
amf_et = combined_df['amf_eta_values'].tolist()
data_date = combined_df['dt'].tolist()

# print 'site precip dates \n', site_precip_dates

data_date = [d.to_pydatetime() for d in data_date]

high_outlier_prism = []
high_outlier_etrm = []
high_outlier_amf = []
high_outlier_dates = []

for oi in high_outlier_indices:

    precip_outlier = prism[oi]
    etrm_et_outlier = etrm_et[oi]
    amf_et_outlier = amf_et[oi]
    outlier_date = data_date[oi]

    high_outlier_prism.append(precip_outlier)
    high_outlier_etrm.append(etrm_et_outlier)
    high_outlier_amf.append(amf_et_outlier)
    high_outlier_dates.append(outlier_date)


# # TODO - How can I plot a given number of days before and after the event?
print len(data_date)
print len(site_precip)
print 'bothlens'

# for i, dd_precip in enumerate(zip(data_date, site_precip)):
#
#     dd, precip = dd_precip
#     print 'index {}'.format(i)
#     print 'dd: {}'.format(dd)
#     print 'precip: {}'.format(precip)

ax1 = plt.subplot(311)
plt.scatter(resid_dates, resid_vals)
# plt.setp(ax1.get_xticklabels(), fontsize=6)

ax2 = plt.subplot(312, sharex=ax1)
plt.plot(data_date, etrm_et, color='black')
plt.plot(data_date, amf_et, color='green')
# # make these tick labels invisible
# plt.setp(ax2.get_xticklabels(), visible=False)

# share x and y
ax3 = plt.subplot(313, sharex=ax1)
plt.plot(data_date, prism, color='blue')
plt.plot(data_date, site_precip, color='orange')
# plt.xlim(0.01, 5.0)

plt.title('plus19')

plt.show()

