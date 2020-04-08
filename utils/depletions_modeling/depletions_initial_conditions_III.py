import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

root = '/Users/Gabe/Downloads/thesis spreadies'
# sg_1k_1k = pd.read_csv(os.path.join(root,'we_depletions_sg_SWHC1000_INIDEP1000_timeseries.csv'), parse_dates=True)
# sg_600_600 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC600_INIDEP600_timeseries.csv'), parse_dates=True)
# sg_600_300 = pd.read_csv(os.path.join(root,'we_depletions_sg_SWHC600_INIDEP300_timeseries.csv'), parse_dates=True)
# sg_600_150 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC600_INIDEP150_timeseries.csv'), parse_dates=True)
#
# sg_300_300 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC300_INIDEP300_timeseries.csv'), parse_dates=True)
# sg_300_150 = pd.read_csv(os.path.join(root,'we_depletions_sg_SWHC300_INIDEP150_timeseries.csv'), parse_dates=True)
# sg_300_0 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC300_INIDEP0_timeseries.csv'), parse_dates=True)
#
# sg_150_150 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC150_INIDEP150_timeseries.csv'), parse_dates=True)
# sg_150_75 = pd.read_csv(os.path.join(root,'we_depletions_sg_SWHC150_INIDEP75_timeseries.csv'), parse_dates=True)
# sg_150_0 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC150_INIDEP0_timeseries.csv'), parse_dates=True)
#
# print sg_1k_1k.head()
#
# vcm_600_600 = pd.read_csv(os.path.join(root,'we_depletions_vcm_SWHC600_INIDEP600_timeseries.csv'), parse_dates=True)
# vcm_600_300 = pd.read_csv(os.path.join(root,'we_depletions_vcm_SWHC600_INIDEP300_timeseries.csv'), parse_dates=True)
# vcm_600_150 = pd.read_csv(os.path.join(root,'we_depletions_vcm_SWHC600_INIDEP150_timeseries.csv'), parse_dates=True)

# vcm_300_300 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC300_INIDEP300.csv'), parse_dates=True)
# vcm_300_150 = pd.read_csv(os.path.join(root,'ext_we_depletions_vcm_SWHC300_INIDEP150.csv'), parse_dates=True)
# vcm_300_0 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC300_INIDEP0.csv'), parse_dates=True)

# plt.plot([1,2,3], [3, 5,7])
# plt.show()


vcm_600_600 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC600_INIDEP600.csv'), parse_dates=True)
vcm_600_300 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC600_INIDEP300.csv'), parse_dates=True)
vcm_600_000 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC600_INIDEP0.csv'), parse_dates=True)


vcm_300_300 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC300_INIDEP300.csv'), parse_dates=True)
vcm_300_150 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC300_INIDEP150.csv'), parse_dates=True)
vcm_300_000 = pd.read_csv(os.path.join(root, 'ext_we_depletions_vcm_SWHC300_INIDEP0.csv'), parse_dates=True)


sg_600_600 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC600_INIDEP600.csv'), parse_dates=True)
sg_600_300 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC600_INIDEP300.csv'), parse_dates=True)
sg_600_000 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC600_INIDEP0.csv'), parse_dates=True)


sg_300_300 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC300_INIDEP300.csv'), parse_dates=True)
sg_300_150 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC300_INIDEP150.csv'), parse_dates=True)
sg_300_000 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC300_INIDEP0.csv'), parse_dates=True)


sg_150_150 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC150_INIDEP150.csv'), parse_dates=True)
sg_150_075 = pd.read_csv(os.path.join(root,'ext_we_depletions_sg_SWHC150_INIDEP75.csv'), parse_dates=True)
sg_150_000 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC150_INIDEP0.csv'), parse_dates=True)

sg_50_050 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC50_INIDEP50.csv'), parse_dates=True)
sg_50_025 = pd.read_csv(os.path.join(root,'ext_we_depletions_sg_SWHC50_INIDEP25.csv'), parse_dates=True)
sg_50_000 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC50_INIDEP0.csv'), parse_dates=True)

vcm_150_150 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC150_INIDEP150.csv'), parse_dates=True)
vcm_150_075 = pd.read_csv(os.path.join(root,'ext_we_depletions_sg_SWHC150_INIDEP75.csv'), parse_dates=True)
vcm_150_000 = pd.read_csv(os.path.join(root, 'ext_we_depletions_sg_SWHC150_INIDEP0.csv'), parse_dates=True)


# # plt.plot([1,2,3], [3, 5,7])
# # plt.show()
#
# vcm_600_600 = pd.read_csv(os.path.join(root,'we_depletions_vcm_SWHC600_INIDEP600_timeseries.csv'), parse_dates=True)
# vcm_600_300 = pd.read_csv(os.path.join(root,'we_depletions_vcm_SWHC600_INIDEP300_timeseries.csv'), parse_dates=True)
# vcm_600_150 = pd.read_csv(os.path.join(root,'we_depletions_vcm_SWHC600_INIDEP150_timeseries.csv'), parse_dates=True)
#
# vcm_300_300 = pd.read_csv(os.path.join(root, 'we_depletions_vcm_SWHC300_INIDEP300_timeseries.csv'), parse_dates=True)
# vcm_300_150 = pd.read_csv(os.path.join(root,'we_depletions_vcm_SWHC300_INIDEP150_timeseries.csv'), parse_dates=True)
# vcm_300_0 = pd.read_csv(os.path.join(root, 'we_depletions_vcm_SWHC300_INIDEP0_timeseries.csv'), parse_dates=True)

# print(sg_600_600['date'])
#
# plt.plot(sg_600_150['date'], sg_600_150['depletion'], label='sg')
# # plt.grid()
# plt.legend()
# plt.show()
# # plt.savefig(os.path.join(root, 'testfig.png'))

years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')

### ===== SG 50 ======
fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False, sharex=True)

ax1.plot(pd.to_datetime(sg_50_000['date']), sg_50_000['depletion'], color='r', label='swhc_50_inidep_000', linewidth=5)
ax1.plot(pd.to_datetime(sg_50_025['date']), sg_50_025['depletion'], color='b', label='swhc_50_inidep_025', linewidth=3)
ax1.plot(pd.to_datetime(sg_50_050['date']), sg_50_050['depletion'], color='g', label='swhc_50_inidep_050', linewidth=1)
ax1.set_xlabel('Date')
ax1.set_ylabel('Depletion (mm)')
ax1.set_title('Depletion with Given SWHC and Initial Depletion - Sevilleta')
ax1.legend()
ax1.grid()
ax2.plot(pd.to_datetime(sg_50_000['date']), sg_50_000['recharge_ro'], color='r', label='swhc_50_inidep_000', linewidth=3)
ax2.plot(pd.to_datetime(sg_50_025['date']), sg_50_025['recharge_ro'], color='b', label='swhc_50_inidep_025', linewidth=2)
ax2.plot(pd.to_datetime(sg_50_050['date']), sg_50_050['recharge_ro'], color='g', label='swhc_50_inidep_050', linewidth=1)
ax2.set_xlabel('Date')
ax2.set_ylabel('Recharge (mm)')
ax2.legend()
ax2.grid()
ax2.set_title('Recharge with Given SWHC and Initial Depletion - Sevilleta')
plt.subplots_adjust(hspace=1)
plt.show()

### ===== vcm 150 ======

fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False, sharex=True)
ax1.plot(pd.to_datetime(vcm_150_000['date']), vcm_150_000['depletion'], color='r', label='swhc_150_inidep_000', linewidth=5)
ax1.plot(pd.to_datetime(vcm_150_075['date']), vcm_150_075['depletion'], color='b', label='swhc_150_inidep_075', linewidth=3)
ax1.plot(pd.to_datetime(vcm_150_150['date']), vcm_150_150['depletion'], color='g', label='swhc_600_inidep_150', linewidth=1)
ax1.set_title('Depletion with Given SWHC and Initial Depletion - Valles Caldera')
ax1.grid()
ax1.legend()
ax2.plot(pd.to_datetime(vcm_150_000['date']), vcm_150_000['recharge_ro'], color='r', label='swhc_150_inidep_000', linewidth=5)
ax2.plot(pd.to_datetime(vcm_150_075['date']), vcm_150_075['recharge_ro'], color='b', label='swhc_150_inidep_075', linewidth=3)
ax2.plot(pd.to_datetime(vcm_150_150['date']), vcm_150_150['recharge_ro'], color='g', label='swhc_600_inidep_150', linewidth=1)
ax2.set_title('Depletion with Given SWHC and Initial Depletion - Valles Caldera')
ax2.grid()
ax2.legend()
plt.subplots_adjust(hspace=1)
plt.show()


### ===== SG 600 ======
fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False, sharex=True)

ax1.plot(pd.to_datetime(sg_600_000['date']), sg_600_000['depletion'], color='r', label='swhc_600_inidep_000', linewidth=5)
ax1.plot(pd.to_datetime(sg_600_300['date']), sg_600_300['depletion'], color='b', label='swhc_600_inidep_300', linewidth=3)
ax1.plot(pd.to_datetime(sg_600_600['date']), sg_600_600['depletion'], color='g', label='swhc_600_inidep_600', linewidth=1)
ax1.set_xlabel('Date')
ax1.set_ylabel('Depletion (mm)')
ax1.set_title('Depletion with Given SWHC and Initial Depletion - Sevilleta')
ax1.legend()
ax1.grid()
ax2.plot(pd.to_datetime(sg_600_000['date']), sg_600_000['recharge_ro'], color='r', label='swhc_600_inidep_000', linewidth=3)
ax2.plot(pd.to_datetime(sg_600_300['date']), sg_600_300['recharge_ro'], color='b', label='swhc_600_inidep_300', linewidth=2)
ax2.plot(pd.to_datetime(sg_600_600['date']), sg_600_600['recharge_ro'], color='g', label='swhc_600_inidep_600', linewidth=1)
ax2.set_xlabel('Date')
ax2.set_ylabel('Recharge (mm)')
ax2.legend()
ax2.grid()
ax2.set_title('Recharge with Given SWHC and Initial Depletion - Sevilleta')
plt.subplots_adjust(hspace=1)
plt.show()

### ===== SG 300 ======
fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False, sharex=True)
ax1.plot(pd.to_datetime(sg_300_000['date']), sg_300_000['depletion'], color='r', label='swhc_300_inidep_0', linewidth=5)
ax1.plot(pd.to_datetime(sg_300_150['date']), sg_300_150['depletion'], color='b', label='swhc_300_inidep_150', linewidth=3)
ax1.plot(pd.to_datetime(sg_300_300['date']), sg_300_300['depletion'], color='g', label='swhc_300_inidep_300', linewidth=1)
ax1.set_xlabel('Date')
ax1.set_ylabel('Depletion (mm)')
ax1.set_title('Depletion with Given SWHC and Initial Depletion - Sevilleta')
ax1.legend()
ax1.grid()
ax2.plot(pd.to_datetime(sg_300_000['date']), sg_300_000['recharge_ro'], color='r', label='swhc_300_inidep_0', linewidth=3)
ax2.plot(pd.to_datetime(sg_300_150['date']), sg_300_150['recharge_ro'], color='b', label='swhc_300_inidep_150', linewidth=2)
ax2.plot(pd.to_datetime(sg_300_300['date']), sg_300_300['recharge_ro'], color='g', label='swhc_300_inidep_300', linewidth=1)
ax2.set_xlabel('Date')
ax2.set_ylabel('Recharge (mm)')
ax2.legend()
ax2.grid()
ax2.set_title('Recharge with Given SWHC and Initial Depletion - Sevilleta')
plt.subplots_adjust(hspace=1)
plt.show()

### ===== vcm 150 ======
fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False, sharex=True)
ax1.plot(pd.to_datetime(sg_150_000['date']), sg_150_000['depletion'], color='r', label='swhc_150_inidep_000', linewidth=5)
ax1.plot(pd.to_datetime(sg_150_075['date']), sg_150_075['depletion'], color='b', label='swhc_150_inidep_075', linewidth=3)
ax1.plot(pd.to_datetime(sg_150_150['date']), sg_150_150['depletion'], color='g', label='swhc_150_inidep_150', linewidth=1)
ax1.set_xlabel('Date')
ax1.set_ylabel('Depletion (mm)')
ax1.set_title('Depletion with Given SWHC and Initial Depletion - Sevilleta')
ax1.legend()
ax1.grid()
ax2.plot(pd.to_datetime(sg_150_000['date']), sg_150_000['recharge_ro'], color='r', label='swhc_150_inidep_000', linewidth=3)
ax2.plot(pd.to_datetime(sg_150_075['date']), sg_150_075['recharge_ro'], color='b', label='swhc_150_inidep_075', linewidth=2)
ax2.plot(pd.to_datetime(sg_150_150['date']), sg_150_150['recharge_ro'], color='g', label='swhc_150_inidep_150', linewidth=1)
ax2.set_xlabel('Date')
ax2.set_ylabel('Recharge (mm)')
ax2.legend()
ax2.grid()
ax2.set_title('Recharge with Given SWHC and Initial Depletion - Sevilleta')
plt.subplots_adjust(hspace=1)
plt.show()


# print('plotting the new one')
# plt.plot(pd.to_datetime(sg_150_0['date']), sg_150_0['depletion'], color='red', label='swhc_150_inidep_0', linewidth=5)
# plt.plot(pd.to_datetime(sg_150_75['date']), sg_150_75['depletion'], color='blue', label='swhc_150_inidep_75', linewidth=3)
# plt.plot(pd.to_datetime(sg_150_150['date']), sg_150_150['depletion'], color='green', label='swhc_150_inidep_150', linewidth=1)
# plt.title('Depletion with Given SWHC and Initial Depletion')
# plt.xlabel('Date')
# plt.ylabel('Depletion (mm)')
# plt.grid()
# plt.legend()
# plt.show()

### ===== VCM 600 ======
fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False, sharex=True)
ax1.plot(pd.to_datetime(vcm_600_000['date']), vcm_600_000['depletion'], color='r', label='swhc_600_inidep_0', linewidth=5)
ax1.plot(pd.to_datetime(vcm_600_300['date']), vcm_600_300['depletion'], color='b', label='swhc_600_inidep_300', linewidth=3)
ax1.plot(pd.to_datetime(vcm_600_300['date']), vcm_600_600['depletion'], color='g', label='swhc_600_inidep_600', linewidth=1)
ax1.set_title('Depletion with Given SWHC and Initial Depletion - Valles Caldera')
ax1.grid()
ax1.legend()

ax2.plot(pd.to_datetime(vcm_600_000['date']), vcm_600_000['recharge_ro'], color='r', label='swhc_600_inidep_0', linewidth=5)
ax2.plot(pd.to_datetime(vcm_600_300['date']), vcm_600_300['recharge_ro'], color='b', label='swhc_600_inidep_300', linewidth=3)
ax2.plot(pd.to_datetime(vcm_600_600['date']), vcm_600_600['recharge_ro'], color='g', label='swhc_600_inidep_600', linewidth=1)
ax2.set_title('Depletion with Given SWHC and Initial Depletion - Valles Caldera')
ax2.grid()
ax2.legend()

plt.show()

### ===== VCM 300 ======
fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False, sharex=True)
ax1.plot(pd.to_datetime(vcm_300_000['date']), vcm_300_000['depletion'], color='red', label='swhc_300_inidep_0', linewidth=5)
ax1.plot(pd.to_datetime(vcm_300_150['date']), vcm_300_150['depletion'], color='blue', label='swhc_300_inidep_150', linewidth=3)
ax1.plot(pd.to_datetime(vcm_300_300['date']), vcm_300_300['depletion'], color='green', label='swhc_300_inidep_300', linewidth=1)
ax1.set_title('Depletion with Given SWHC and Initial Depletion - Valles Caldera')
ax1.grid()
ax1.legend()

ax2.plot(pd.to_datetime(vcm_300_000['date']), vcm_300_000['recharge_ro'], color='red', label='swhc_300_inidep_0', linewidth=5)
ax2.plot(pd.to_datetime(vcm_300_150['date']), vcm_300_150['recharge_ro'], color='blue', label='swhc_300_inidep_150', linewidth=3)
ax2.plot(pd.to_datetime(vcm_300_300['date']), vcm_300_300['recharge_ro'], color='green', label='swhc_300_inidep_300', linewidth=1)
ax2.set_title('Depletion with Given SWHC and Initial Depletion - Valles Caldera')
ax2.grid()
ax2.legend()

plt.show()


# fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4, sharey=True)
#
# ax0.xaxis.set_major_formatter(years_fmt)
# ax0.xaxis.set_major_locator(years)
# ax0.xaxis.set_minor_locator(months)
# ax0.plot(pd.to_datetime(sg_600_150['date']), sg_600_150['depletion'])
# ax0.set_title('Sg SWHC: 600, In. Dep: 150')
# ax0.set_ylabel('SWD (mm)')
#
# ax1.xaxis.set_major_formatter(years_fmt)
# ax1.xaxis.set_major_locator(years)
# ax1.xaxis.set_minor_locator(months)
# ax1.plot(pd.to_datetime(sg_600_300['date']), sg_600_300['depletion'])
# ax1.set_title('Sg SWHC: 600, In. Dep: 300')
# ax1.set_ylabel('SWD (mm)')
#
# ax2.xaxis.set_major_formatter(years_fmt)
# ax2.xaxis.set_major_locator(years)
# ax2.xaxis.set_minor_locator(months)
# ax2.plot(pd.to_datetime(sg_600_600['date']), sg_600_600['depletion'])
# ax2.set_title('Sg SWHC: 600, In. Dep: 600')
# ax2.set_ylabel('SWD (mm)')
#
# ax3.xaxis.set_major_formatter(years_fmt)
# ax3.xaxis.set_major_locator(years)
# ax3.xaxis.set_minor_locator(months)
# ax3.plot(pd.to_datetime(sg_1k_1k['date']), sg_1k_1k['depletion'])
# ax3.set_title('Sg SWHC: 1,000, In. Dep: 1,000')
# ax3.set_ylabel('SWD (mm)')

# # fig.autofmt_xdate()
# # plt.xlabel('Date')
# # plt.title('Soil Water Depletions at Sg Fluxtower with Initial Condition')
# plt.grid()
# plt.subplots_adjust(hspace=1)
# plt.show()


# fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, sharey=True)
#
# print type(vcm_600_150['date'][0])
#
# ax0.plot(pd.to_datetime(vcm_600_150['date']), vcm_600_150['depletion'])
# ax0.xaxis.set_major_locator(years)
# ax0.xaxis.set_major_formatter(years_fmt)
# ax0.xaxis.set_minor_locator(months)
# ax0.set_title('Vcm SWHC: 600, In. Dep: 150')
# ax0.set_ylabel('SWD (mm)')
# ax1.plot(pd.to_datetime(vcm_600_300['date']), vcm_600_300['depletion'])
# ax1.xaxis.set_major_locator(years)
# ax1.xaxis.set_major_formatter(years_fmt)
# ax1.xaxis.set_minor_locator(months)
# ax1.set_title('Vcm SWHC: 600, In. Dep: 300')
# ax1.set_ylabel('SWD (mm)')
# ax2.plot(pd.to_datetime(vcm_600_600['date']), vcm_600_600['depletion'])
# ax2.xaxis.set_major_locator(years)
# ax2.xaxis.set_major_formatter(years_fmt)
# ax2.xaxis.set_minor_locator(months)
# ax2.set_title('Vcm SWHC: 600, In. Dep: 600')
# ax2.set_ylabel('SWD (mm)')
#
# # fig.autofmt_xdate()
# plt.grid()
# # plt.xlabel('Date')
# # plt.title('Soil Water Depletions at Vcm Fluxtower with Initial Condition')
# plt.subplots_adjust(hspace=1)
# plt.show()
