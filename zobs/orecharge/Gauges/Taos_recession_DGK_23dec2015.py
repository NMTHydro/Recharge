# David Ketchum 18 DEC 2015
# Find gauge recession at R. Pueblo de Taos
# dgketchum@gmail.com
from __future__ import division
import datetime
import string
from dateutil import rrule
from matplotlib import pyplot as plt
from scipy.ndimage import filters
from scipy.signal import gaussian
import math
import os
import pandas as pd
import numpy as np

# Bring in snow from SNOTEL site
folder = 'C:\\Users\\David\\Documents\\Recharge\\Point_data\\Taos'
os.chdir(folder)
select_csv = "Taos_Snow_2010_2013.csv"
fid = open(select_csv)
lines = fid.readlines()[1:]
fid.close()
rows = [line.split(',') for line in lines]
snow_date = []
snow_recs = []
for line in rows:
    snow_date.append(datetime.datetime.strptime(line[1], '%m/%d/%Y'))  # date
    snow_recs.append([float(line[3]) * 24.5])  # snow
print("Snow Data points: " + str(len(snow_recs)))
snow_start = snow_date[0]
snow_end = snow_date[-1]

# Read in gauge (from R. Pueblo de Taos USGS gauge 8269000), and precip records clipped from PRISM
folder = 'C:\\Users\David\\Documents\\Recharge\\Gauges\\Complete_Taos_q_ppt_HF_csv'
os.chdir(folder)
select_csv = "8269000_date_q_ppt.csv"
fid = open(select_csv)
lines = fid.readlines()[0:]
fid.close()
rows = [line.split(',') for line in lines]
recs = []
for line in rows:
    recs.append([datetime.datetime.strptime(line[0], '%Y/%m/%d %H:%M'),  # date
    float(line[1]), float(line[2])])
print("Gauge Data points: " + str(len(recs)))
recs = np.array(recs)

# Select gauge and precip records during available snow data time series
# fill in  high-frequency data with that day's snow value
# create array of all data [date, q, ppt, snow]
# There is probably a better way to do this, I dislike so many lists in my code
snow_hf = []
days = []
qq = []
pptt = []
s_date = [element.strftime('%m/%d/%Y') for element in snow_date]
for element in recs[:, 0]:
    dday = element.strftime('%m/%d/%Y')
    if element >= snow_start:
        pos = s_date.index(dday)
        snow_apnd = snow_recs[pos]
        snow_hf.append(snow_apnd)
        days.append(element)
        pos = days.index(element)
        qq.append(recs[pos, 1])
        pptt.append(recs[pos, 2])
qq = np.array(qq)
pptt = np.array(pptt)
days = np.array(days)
snow_hf = np.array(snow_hf)
data = np.column_stack((days, qq, pptt, snow_hf))

data_short = data[:, :]
# Plot array of concurrent data [q, ppt, snow] for inspection
# def make_patch_spines_invisible(ax):
#     ax.set_frame_on(True)
#     ax.patch.set_visible(False)
#     for sp in ax.spines.values():
#         sp.set_visible(False)
# fig, host = plt.subplots()
# fig.subplots_adjust(right=0.75)
# par1 = host.twinx()
# # par2 = host.twinx()
# # par2.spines["right"].set_position(("axes", 1.1))
# make_patch_spines_invisible(par2)
# # par2.spines["right"].set_visible(True)
# p1, = host.plot(data_short[:, 0], data_short[:, 1], "Purple", label="Discharge")
# p2, = par1.plot(data_short[:, 0], data_short[:, 2], "g", label="Precipitation")
# # p3, = par2.plot(data_short[:, 0], data_short[:, 3], "b", label="Snow Water Equivalent")
# # host.set_xlim()
# # host.set_ylim()
# # par1.set_ylim()
# # par2.set_ylim(2400, 0)
# host.set_xlabel("Date")
# host.set_ylabel("Cubic Feet per Second")
# par1.set_ylabel("Precipitation Total for Watershed [m^3]")
# # par2.set_ylabel("Snow Water Equivalent on Ground [mm]")
# host.yaxis.label.set_color(p1.get_color())
# par1.yaxis.label.set_color(p2.get_color())
# # par2.yaxis.label.set_color(p3.get_color())
# tkw = dict(size=4, width=1.5)
# host.tick_params(axis='y', colors=p1.get_color(), **tkw)
# par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
# # par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
# host.tick_params(axis='x', **tkw)
# lines = [p1, p2] #, p3]
# host.legend(lines, [l.get_label() for l in lines], loc=2)
# plt.show()

# Create time delay to find hydrograph recession, starting the midnight after the assumed 17:00 previous day's
# precipitation event, excluding wintertime (i.e. when snow is on the ground), create new array of
# data consisting of these "recession periods"

# This still needs to be constrained by time of day, i.e., the afternoon periods should be cut #

# First pull just the data with zero snowpack and non-rain days (I wish we had hourly precip!)
ds = data[:, 3]
no_snow = ds == 0.0
dr = data[:, 2]
no_rain = dr == 0.0
mask = np.logical_and(no_snow, no_rain)
elig_data = data[mask]
df = pd.DataFrame(elig_data[:, :], columns=['date', 'discharge', 'precipitation', 'snow'])

# The following data are very noisy, try smoothing it out, pandas has lots of options to
# experiment with
ser = pd.Series(df['discharge'])
roll = pd.rolling_mean(ser, 300)
hamming = pd.rolling_window(ser, 1000, 'hamming')
df['hamming'] = hamming
df['rolling'] = roll

# Plot smoothed data for inspection
# fig, ax = plt.subplots(1, figsize=(15, 5))
# ax.plot(df['date'], df['hamming'], 'g', label='Hamming Discharge (cfs) Window = 1000')
# ax.plot(df['date'], df['rolling'], 'r', label='Rolling Mean  Discharge (cfs) Window= 300')
# ax.plot(df['date'], df['discharge'], 'b', label='Measured Discharge (cfs)', alpha=0.3)
# ax.set_ylabel('Discharge (cfs)', color='k')
# ax.set_xlabel('Date')
# # plt.ylim(0.0, 1.0)
# for tl in ax.get_yticklabels():
#     tl.set_color('b')
# plt.title('Summer Hydrograph')
# plt.legend()
# plt.show()

# Then find days where the hydrograph is receding, i.e. dq/dt < 0, build in a delay to avoid local maxima
# mark recession domain with 'recession' parameter
df['dqdt'] = np.nan
df['recession'] = np.nan
dq_dt = 0.0
next_q = df.iloc[1, 4]
next_t = df.iloc[1, 0]
len_recs = df.shape[0]
for i in range(0, df.shape[0]):
    delta_t = next_t - df.iloc[i, 0]
    del_t = delta_t.total_seconds()
    if delta_t > datetime.timedelta(0, 1800):
        del_q = 0.0  # if del_q is zero, dqdt  won't be recorded
        print("Long gap between records, passing... " + '{0}'.format(delta_t))
        pass
    elif del_t == 0.0:
        del_q = 0.0  # if del_q is zero, dqdt won't be recorded
        print("Delta time is zero, this should be the end of the records....")
        break
    else:
        next_t = df.iloc[i + 2, 0]
        del_q = df.iloc[i, 4] - next_q
        next_q = df.iloc[i, 4]

        delay_dqdt = dq_dt  # Here we have a delay of only one timestep, this could be lengthened, or
        dq_dt = del_q/del_t  # a dependency on the time of day could be imposed, we should talk about this
        if delay_dqdt < 0.0:
            df.loc[i, 'dqdt'] = dq_dt
            df.loc[i, 'recession'] = df.iloc[i, 4]

# Create bins to aggregate dq/dt values across Q domain
q_min = 0.45000000
q_max = 1.500000000
interval = 0.02500000
length = (q_max-q_min)/interval                                                # q_list will be bin ranges
q_list = [[x, x + interval] for x in np.linspace(q_min, q_max, int(length))]  # q_list leaves gaps in the domain,
num_list = [x for x in range(0, len(q_list))]                                # I didn't take the time
bins = {key: value for (key, value) in zip(num_list, q_list)}               # to figure out how to fix it

# There is probably a better way to set up the placement of dqdt values
# in their respective bins, but the problem is having a structure
# of numeric dqdt values getting placed like so, without reverting to many lists,
# and thus losing the flexibility to adjust bins:
#    A B C D E F
#  0 x x x x x
#  1 x x     x
#  2 x x     x
#  3 x

# I ended up building a dataframe of NaN values to be replaced by dqdt values
# because the advantage of pandas--presumably--is that it can deal with NaN values in a
# structure of mixed data types
# There must be a bin tool in pandas, I know at least the histograms have a bin parameter
df_cols = pd.DataFrame.from_dict(bins)
a = np.empty((df.shape[0], df_cols.shape[1]))
a[:] = np.nan
df_a = pd.DataFrame(a, columns=bins)
frames = [df_cols, df_a]
df_nan = pd.concat(frames)
df_bins = pd.DataFrame(df_nan)
# first two rows of df are the bin ranges
for i in range(2, df.shape[0]):
    dqdt = df.iloc[i, 6]  # dqdt values are in col 6 of the original df
    # So we know that if there is a non-NaN dqdt,  we need to write that value
    # to the appropriate Q range
    if math.isnan(dqdt) is False:
        qq = df.iloc[i, 1]
        xx = 0              # Hopefully this counts correctly, I don't know a lot about zip
        for j, k in zip(df_bins.iloc[0, :], df_bins.iloc[1, :]):
            low = j
            high = k
            if low < qq <= high:
                df_bins.set_value(i, xx, dqdt)
            xx += 1
print("Created bins")

# This following is set-up to get ready to plot the bins, it could use some work probably
q_bin = []
mean_bin = []
std_up = []
std_down = []
std_bin = []
for column in df_bins:
    mean = df_bins[column].iloc[2:].mean()
    if math.isnan(mean) is False:
        q_class = (df_bins[column].iloc[0] + df_bins[column].iloc[1]) / 2
        q_error = df_bins[column].iloc[1] - df_bins[column].iloc[0]
        stddev = df_bins[column].iloc[2:].std()
        q_bin.append(q_class)
        mean_bin.append(mean)
        std_bin.append(stddev)
        std_up.append(mean + stddev)
        std_down.append(mean - stddev)
q_bin = np.array(q_bin)
mean_bin = np.array(mean_bin)
std_down = np.array(std_down)
std_up = np.array(std_up)
std_bin = np.array(std_bin)
bin_data = np.column_stack((q_bin, mean_bin, std_bin, std_up, std_down))
df_bin_short = pd.DataFrame(bin_data, columns=['q_bin', 'mean_bin', 'std_bin', 'std_up', 'std_down'])

# Plot "binned" data
plt.figure(1, figsize=(6, 4))
plt.plot(df_bin_short['q_bin'], -df_bin_short['mean_bin'], 'b-', label="mean recession at discharge rate")
plt.errorbar(df_bin_short['q_bin'], -df_bin_short['mean_bin'], fmt='ro',
             label="Mean Domain Lateral, Standard Deviation Vertical",
             xerr=q_error, yerr=df_bin_short['std_bin'], ecolor='black')
plt.xlabel('Q')
plt.ylabel('-dQ/dt')
plt.legend(loc='upper right')
plt.show()

# Plot histogram of binned data
freq = pd.DataFrame(df_bins.count())
freq = freq.transpose()
q_ser = ((df_bins.iloc[0, :] + df_bins.iloc[1, :]) / 2)
q_ser = q_ser.transpose()
hist_list = freq.append(q_ser, ignore_index=True)
ax = hist_list.plot(kind='bar', legend=None, xticks=np.linspace(0.0, 1.5, 15),
               title='Frequency Histogram for Discharge Bins')
ax.set_xlable('Discharge [cfs]')

# Plot no-rain, no-snow data, and derivatives
# fig, ax1 = plt.subplots(1, figsize=(15, 5))
# ax1.plot(df['date'], df['hamming'], 'b', label='Discharge (cfs)')
# ax1.plot(df['date'], df['recession'], 'g*', label='Discharge (cfs)')
# ax1.set_ylabel('Discharge (cfs)', color='k')
# ax1.set_xlabel('Date')
# plt.ylim(0.5, 1.6)
# plt.legend()
# for tl in ax1.get_yticklabels():
#     tl.set_color('b')
# ax2 = ax1.twinx()
# ax2.plot(df['date'], -df['dqdt'], 'r+', label='dQ/dt (cfs/sec)')
# ax2.set_ylabel('-dQ/dt', color='k')
# plt.ylim(-2.0e-7, 5.0e-7)
# for t2 in ax2.get_yticklabels():
#     t2.set_color('r')
# for t2 in ax2.get_xticklabels():
#     t2.set_color('k')
# plt.title('Title Here')
# plt.legend()
# plt.show()

# Plot ALL data, 3 axes
# def make_patch_spines_invisible(ax):
#     ax.set_frame_on(True)
#     ax.patch.set_visible(False)
#     for sp in ax.spines.values():
#         sp.set_visible(False)
# fig, host = plt.subplots()
# fig.subplots_adjust(right=0.75)
# par1 = host.twinx()
# par2 = host.twinx()
# par2.spines["right"].set_position(("axes", 1.1))
# make_patch_spines_invisible(par2)
# # par2.spines["right"].set_visible(True)
# p1, = host.plot(recs[:, 0], recs[:, 1], "Purple", label="Discharge")
# p2, = par1.plot(recs[:, 0], recs[:, 2], "g", label="Precipitation")
# p3, = par2.plot(snow_date, snow_recs, "b", label="Snow Water Equivalent")
# # host.set_xlim(0, 2)
# # host.set_ylim(0, 2)
# # par1.set_ylim(0, 4)
# par2.set_ylim(1000, 0)
# host.set_xlabel("Date")
# host.set_ylabel("Cubic Feet per Second")
# par1.set_ylabel("Precipitation Total for Watershed [m^3]")
# par2.set_ylabel("Snow Water Equivalent on Ground [mm]")
# host.yaxis.label.set_color(p1.get_color())
# par1.yaxis.label.set_color(p2.get_color())
# par2.yaxis.label.set_color(p3.get_color())
# tkw = dict(size=4, width=1.5)
# host.tick_params(axis='y', colors=p1.get_color(), **tkw)
# par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
# par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
# host.tick_params(axis='x', **tkw)
# lines = [p1, p2, p3]
# host.legend(lines, [l.get_label() for l in lines], loc=2)
# plt.show()

# Plot array of concurrent data (during snow years) [q, ppt, snow]
# def make_patch_spines_invisible(ax):
#     ax.set_frame_on(True)
#     ax.patch.set_visible(False)
#     for sp in ax.spines.values():
#         sp.set_visible(False)
# fig, host = plt.subplots()
# fig.subplots_adjust(right=0.75)
# par1 = host.twinx()
# par2 = host.twinx()
# par2.spines["right"].set_position(("axes", 1.1))
# make_patch_spines_invisible(par2)
# par2.spines["right"].set_visible(True)
# p1, = host.plot(data[:, 0], data[:, 1], "Purple", label="Discharge")
# p2, = par1.plot(data[:, 0], data[:, 2], "g", label="Precipitation")
# p3, = par2.plot(data[:, 0], data[:, 3], "b", label="Snow Water Equivalent")
# # host.set_xlim()
# # host.set_ylim()
# # par1.set_ylim()
# par2.set_ylim(2400, 0)
# host.set_xlabel("Date")
# host.set_ylabel("Cubic Feet per Second")
# par1.set_ylabel("Precipitation Total for Watershed [m^3]")
# par2.set_ylabel("Snow Water Equivalent on Ground [mm]")
# host.yaxis.label.set_color(p1.get_color())
# par1.yaxis.label.set_color(p2.get_color())
# par2.yaxis.label.set_color(p3.get_color())
# tkw = dict(size=4, width=1.5)
# host.tick_params(axis='y', colors=p1.get_color(), **tkw)
# par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
# par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
# host.tick_params(axis='x', **tkw)
# lines = [p1, p2, p3]
# host.legend(lines, [l.get_label() for l in lines], loc=2)
# plt.show()

