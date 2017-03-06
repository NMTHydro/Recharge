import datetime
from dateutil import rrule
from matplotlib import pyplot as plt
import os
import numpy as np

# Bring in snow

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
print "Data points: " + str(len(snow_recs))
snow_start = snow_date[0]
snow_end = snow_date[-1]

# Bring in guage and precip records

folder = 'C:\\Users\David\\Documents\\Recharge\\Gauges\\Complete_q_ppt_HF_csv'
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
print "Data points: " + str(len(recs))
recs = np.array(recs)

# Select gauge and precip records during available snow data time series
# create nparray of all data [date, q, ppt, snow]
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

# Create time delay to find hydrograph recession, starting the midnight after the 17:00 previous day's
# precipitation event, excluding wintertime (i.e. when snow is on the ground), create new array of
# data consistiing of these "recession periods"
for element in data:


# Plot ALL data

# def make_patch_spines_invisible(ax):
#     ax.set_frame_on(True)
#     ax.patch.set_visible(False)
#     for sp in ax.spines.values():
#         sp.set_visible(False)
# fig, host = plt.subplots()
# fig.subplots_adjust(right=0.75)
# par1 = host.twinx()
# par2 = host.twinx()
# par2.spines["right"].set_position(("axes", 1.2))
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
# par2.set_ylabel("[mm]")
# host.yaxis.label.set_color(p1.get_color())
# par1.yaxis.label.set_color(p2.get_color())
# par2.yaxis.label.set_color(p3.get_color())
# tkw = dict(size=4, width=1.5)
# host.tick_params(axis='y', colors=p1.get_color(), **tkw)
# par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
# # par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
# host.tick_params(axis='x', **tkw)
# lines = [p1, p2, p3]
# host.legend(lines, [l.get_label() for l in lines], loc=2)
# plt.show()



# Plot array of concurrent data [q, ppt, snow]
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

