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
from datetime import datetime
# ============= standard library imports ========================

sitename = 'Wjs'
# if applicable
cum_days = '7'

var = 'ETa'#'ETa' # 'RZSM'

# # Vcp
# taw = '200'
# # Seg
# taw = '325'
# # Mpj
# taw = '500'
# Wjs
taw = '900'

# triggers a specific daterange for plotting
date_range = True
#
# # Ses range
# start_date = datetime(2008, 9, 2)
# end_date = datetime(2012, 12, 30)

# # Seg range
# start_date = datetime(2008, 9, 2)
# end_date = datetime(2012, 12, 30)

# # Mpj range
# start_date = datetime(2008, 7, 21)
# end_date = datetime(2012, 12, 30)

# Wjs range
start_date = datetime(2007, 8, 16)
end_date = datetime(2012, 12, 20)

# # Vcp range
# start_date = datetime(2010, 9, 16)
# end_date = datetime(2012, 12, 20)

# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/mpj/calibration_output_II/mpj_7day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/mpj/calibration_output_II/mpj_non_cum_rzsm'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/mpj/'

# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/seg/calibration_output_II/seg_1day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/seg/calibration_output_II/seg_7day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/seg/calibration_output_II/seg_non_cum_rzsm'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/seg/'

# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/ses/calibration_output_II/ses_7day_eta_cum'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/ses/calibration_output_II/ses_non_cum_rzsm'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/ses/'

# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/wjs/calibration_output_II/wjs_cum_eta_1day'
root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/wjs/' #calibration_output_II/wjs_cum_eta_7day'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/wjs/calibration_output_II/wjs_non_cum_rzsm'
# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_mocl
# del_outputs/wjs/'


# root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_III/wjs/'

# combined_timeseries_file = 'cum_eta_model_df_{}_cum1.csv'
# combined_timeseries_file = 'rzsm_model_df_{}.csv'
combined_timeseries_file = 'taw_{}_dataset.csv'




combined_timeseries_file = combined_timeseries_file.format(taw)

combined_timeseries_path = os.path.join(root, combined_timeseries_file)
combined_df = pd.read_csv(combined_timeseries_path, parse_dates=True, index_col=0, header=0)
print combined_df.iloc[:, 0]

# clip timesereis to daterange
if date_range:
    combined_df = combined_df.loc[(combined_df.index >= start_date) & (combined_df.index <= end_date)]


prism = combined_df['prism_values'].cumsum().tolist()
site_precip = combined_df['amf_precip_values'].cumsum().tolist()
# site_precip_dates = pd.to_datetime(combined_df['amf_precip_dates']).tolist()
etrm_et = combined_df['average_vals_eta'].cumsum().tolist()
amf_et = combined_df['amf_eta_values'].cumsum().tolist()
etrm_ro = combined_df['average_vals_ro'].cumsum().tolist()
etrm_infil = combined_df['average_vals_infil'].cumsum().tolist()
jpl_eta = combined_df['jpl_values'].cumsum().tolist()

# TODO - GET PM Ref ET

if var == 'RZSM':
    amf_rzsm = combined_df['nrml_depth_avg_sm'].cumsum().tolist()
    etrm_rzsm = combined_df['average_vals_rzsm'].cumsum().tolist()

fig, ax = plt.subplots()
ax.plot(combined_df.index.values, etrm_et, color='black', label='ETRM ETa')
ax.plot_date(combined_df.index.values, etrm_et, fillstyle='none', color='black')

ax.plot(combined_df.index.values, jpl_eta, color='red', label='JPL ETa')
ax.plot_date(combined_df.index.values, jpl_eta, fillstyle='none', color='red')

ax.plot(combined_df.index.values, prism, color='blue', label='PRISM')
ax.plot_date(combined_df.index.values, prism, fillstyle='none', color='blue')

# Note, amf_cum is filled with akima interpolation
ax.plot(combined_df.index.values, amf_et, color='green', label='AMF ETa')
ax.plot_date(combined_df.index.values, amf_et, fillstyle='none', color='green')


ax.plot(combined_df.index.values, site_precip, color='orange', label='AMF Precip')
ax.plot_date(combined_df.index.values, site_precip, fillstyle='none', color='orange')

ax.set_title('Cumulative ETa and Precip Site:{} ETRM TAW:{}'.format(sitename, taw))
ax.set_ylabel('ETa or Precip in mm H20')
ax.set_xlabel('Date')

plt.legend(loc='lower right')

plt.grid(True)
plt.show()

fig2, ax2 = plt.subplots()

ax2.plot(combined_df.index.values, etrm_infil, color='purple', label='ETRM Infil')
ax.plot_date(combined_df.index.values, etrm_infil, fillstyle='none', color='purple')

ax2.plot(combined_df.index.values, etrm_ro, color='brown', label='ETRM Runoff')
ax2.plot_date(combined_df.index.values,etrm_ro, fillstyle='none', color='brown')

ax2.set_title('Cumulative Runoff and Infiltration Site:{} ETRM TAW:{}'.format(sitename, taw))
ax2.set_ylabel('Infiltration or Runoff in mm H20')
ax2.set_xlabel('Date')
plt.legend(loc='upper left')

plt.grid(True)
plt.show()
