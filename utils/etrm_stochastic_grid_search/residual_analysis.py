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
from datetime import datetime
# ============= standard library imports ========================
from utils.TAW_optimization_subroutine.timeseries_processor import accumulator

sitename = 'Wjs'
# if applicable
cum_days = '7'

# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/mpj/calibration_output/mpj_7day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/mpj/calibration_output/mpj_rzsm'

# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/seg/calibration_output/seg_7day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/seg/calibration_output/seg_rzsm'

# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/ses/calibration_output/ses_7day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/ses/calibration_output/ses_rzsm'

root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/wjs/calibration_output/wjs_7day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/wjs/calibration_output/wjs_rzsm'


chimin_path = os.path.join(root, 'US-{}_chimin_cum_eta_{}.yml'.format(sitename, cum_days))
resid_path = os.path.join(root, 'US-{}_resid_cum_eta_{}.yml'.format(sitename, cum_days))
combined_timeseries_file = 'cum_eta_model_df_{}_cum7.csv'

# chimin_path = os.path.join(root, 'US-{}_chimin_non_cum_rzsm.yml'.format(sitename))
# resid_path = os.path.join(root, 'US-{}_resid_non_cum_rzsm.yml'.format(sitename))
# combined_timeseries_file = 'rzsm_model_df_{}.csv'


var = 'ETa'#'ETa' # 'RZSM'
taw = '600'

# starting TAW value
begin_taw = 25
# ending TAW value
end_taw = 925
# grid search step size. Each ETRM run will increase the uniform TAW of the RZSW holding capacity by this many mm.
taw_step = 25
taw_list = []
optimization_dict = {}
for i in range(0, ((end_taw - begin_taw) / taw_step)):
    if i == 0:
        current_taw = begin_taw
    else:
        current_taw += taw_step

    taw_list.append(current_taw)


with open(chimin_path, 'r') as rfile:
    chimin_dict = yaml.load(rfile)
with open(resid_path, 'r') as rfile:
    resid_dict = yaml.load(rfile)


print 'residual dict \n', resid_dict
resid_tseries = resid_dict[taw][0]
resid_vals = resid_dict[taw][1]
resid_tseries = [datetime.strptime(str(i)[0:10], '%Y-%m-%d') for i in resid_tseries]


# sort t series greatest to least and keep timeseries there.
resid_sorted = sorted(zip(resid_vals, resid_tseries))

# TODO - Grab the PRISM data for the large values on either end of resid_sorted for the pixel...

combined_timeseries_file = combined_timeseries_file.format(taw)

combined_timeseries_path = os.path.join(root, combined_timeseries_file)
combined_df = pd.read_csv(combined_timeseries_path, parse_dates=True, index_col=0, header=0)



prism = combined_df['prism_values']


resid_large = resid_sorted[0:4] + resid_sorted[-4:]

# plt.plot(combined_df.index.values, prism)
# plt.plot(combined_df.index.values, combined_df['amf_eta_values'])
# plt.plot(combined_df.index.values, combined_df['average_vals_eta'])
# plt.show()

resid_dates = []
resid_vals = []
for resid_tup in resid_large:

    val, dt = resid_tup

    # print 'dt {}'.format(dt)

    # datetime.datetime(dt)
    resid_dates.append(dt)
    resid_vals.append(val)

df_datelist = [i for i in combined_df.index]

high_outlier_indices = []
for i, d in enumerate(df_datelist):

    # print d.year, d.month, d.day

    for res_tup in resid_large:
        res_val, res_d = res_tup

        if (res_d.year, res_d.month, res_d.day) == (d.year, d.month, d.day):
            # print 'resday', (res_d.year, res_d.month, res_d.day), 'dday', (d.year, d.month, d.day)
        # if res_d == d:
            high_outlier_indices.append(i)

print high_outlier_indices


prism = combined_df['prism_values'].tolist()
site_precip = combined_df['amf_precip_values'].tolist()
# site_precip_dates = pd.to_datetime(combined_df['amf_precip_dates']).tolist()
etrm_et = combined_df['average_vals_eta'].tolist()
amf_et = combined_df['amf_eta_values'].tolist()

if var == 'RZSM':
    amf_rzsm = combined_df['nrml_depth_avg_sm'].tolist()
    etrm_rzsm = combined_df['average_vals_rzsm'].tolist()
    etrm_ro = combined_df['average_vals_ro'].tolist()


data_date = df_datelist

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


ax1 = plt.subplot(411)
ax1.set_title('Largest Normalized Residuals in Timeseires')
ax1.set_xlabel('Date')
ax1.set_ylabel('Residual {}'.format(var))
plt.scatter(resid_dates, resid_vals)
plt.grid()

# plt.setp(ax1.get_xticklabels(), fontsize=6)
if var == 'ETa':
    ax2 = plt.subplot(412, sharex=ax1)
    ax2.set_title('Ameriflux {} and ETRM {}'.format(sitename, var))
    ax2.set_xlabel('Date')
    ax2.set_ylabel('ETa in mm')
    plt.plot(data_date, etrm_et, color='black', label='ETRM')
    plt.plot_date(data_date, etrm_et, color='black', fillstyle='none')
    plt.plot(data_date, amf_et, color='green', label='AMF')
    plt.plot_date(data_date, amf_et, color='green', fillstyle='none')
    plt.grid()
    plt.legend(loc=(1.01, 0.5))
    # # make these tick labels invisible
    # plt.setp(ax2.get_xticklabels(), visible=False)

elif var == 'RZSM':
    ax2 = plt.subplot(412, sharex=ax1)
    ax2.set_title('Ameriflux {} and ETRM {}'.format(sitename, var))
    ax2.set_xlabel('Date')
    ax2.set_ylabel('RZSM Fraction')
    plt.plot(data_date, etrm_rzsm, color='red', label='ETRM')
    plt.plot_date(data_date, etrm_rzsm, color='red', fillstyle='none', label=None)
    plt.plot(data_date, amf_rzsm, color='purple', label='AMF')
    plt.plot_date(data_date, amf_rzsm, color='purple', fillstyle='none', label=None)
    plt.grid()
    plt.legend(loc=(1.01, 0.5))


# share x and y
ax3 = plt.subplot(413, sharex=ax1)
ax3.set_title('PRISM and Site {} Precipitation'.format(sitename))
ax3.set_xlabel('Date')
ax3.set_ylabel(('Precipitation in mm'))
plt.plot(data_date, prism, color='blue', label='PRISM')
plt.plot_date(data_date, prism, color='blue', fillstyle='none')
plt.plot(data_date, site_precip, color='orange', label='AMF')
plt.plot_date(data_date, site_precip, color='orange', fillstyle='none')
plt.grid()
plt.legend(loc=(1.01, 0.5))


if var == 'RZSM':
    # ax4 = plt.subplot(414, sharex=ax1)
    # ax4.set_title('ETRM {} Runoff'.format(sitename))
    # ax4.set_xlabel('Date')
    # ax4.set_ylabel('ETRM Runoff in mm')
    # plt.plot(data_date, etrm_ro, color='brown', label='Runoff')
    # plt.plot_date(data_date, etrm_ro, color='brown', fillstyle='none')
    # plt.grid()
    # plt.legend(loc=(1.01, 0.5))
    # =====
    ax4 = plt.subplot(414, sharex=ax1)
    ax4.set_title('Ameriflux {} and ETRM {}'.format(sitename, var))
    ax4.set_xlabel('Date')
    ax4.set_ylabel('ETa in mm')
    plt.plot(data_date, etrm_et, color='black', label='ETRM')
    plt.plot_date(data_date, etrm_et, color='black', fillstyle='none')
    plt.plot(data_date, amf_et, color='green', label='AMF')
    plt.plot_date(data_date, amf_et, color='green', fillstyle='none')
    plt.grid()
    plt.legend(loc=(1.01, 0.5))

plt.subplots_adjust(hspace=.75) # left, right, bottom, top, wspace, hspace
plt.show()



# ================== PLOTTING INFILTRATION ==================
etrm_infil = combined_df['average_vals_infil'].tolist()

ax1 = plt.subplot(311)
ax1.set_title('infil_timeseries')
ax1.set_xlabel('Date')
ax1.set_ylabel('infiltration {} TAW'.format(var, taw))
plt.plot(data_date, etrm_infil, color='black', label='ETRM')
plt.plot_date(data_date, etrm_infil, color='black', fillstyle='none')
plt.grid()


ax2 = plt.subplot(312, sharex=ax1)
ax2.set_title('Ameriflux {} and ETRM {}'.format(sitename, var))
ax2.set_xlabel('Date')
ax2.set_ylabel('ETa in mm')
plt.plot(data_date, etrm_et, color='black', label='ETRM')
plt.plot_date(data_date, etrm_et, color='black', fillstyle='none')
plt.plot(data_date, amf_et, color='green', label='AMF')
plt.plot_date(data_date, amf_et, color='green', fillstyle='none')
plt.grid()
plt.legend(loc=(1.01, 0.5))


ax3 = plt.subplot(313, sharex=ax1)
ax3.set_title('PRISM and Site {} Precipitation'.format(sitename))
ax3.set_xlabel('Date')
ax3.set_ylabel(('Precipitation in mm'))
plt.plot(data_date, prism, color='blue', label='PRISM')
plt.plot_date(data_date, prism, color='blue', fillstyle='none')
plt.plot(data_date, site_precip, color='orange', label='AMF')
plt.plot_date(data_date, site_precip, color='orange', fillstyle='none')
plt.grid()
plt.legend(loc=(1.01, 0.5))

plt.subplots_adjust(hspace=.75)
plt.show()