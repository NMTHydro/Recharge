import datetime
from dateutil import rrule
from matplotlib import pyplot as plt
import os
import numpy as np

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
    float(line[1]), float(line[2])])  # discharge
print("Data points: " + str(len(recs)))
all_recs = np.array(recs)

# Bring in snow

folder = 'C:\\Users\\David\\Documents\\Recharge\\Point_data\\Taos'
os.chdir(folder)
select_csv = "Taos_Snow_2010_2013.csv"
fid = open(select_csv)
lines = fid.readlines()[1:]
fid.close()
rows = [line.split(',') for line in lines]
recs = []
for line in rows:
    recs.append([datetime.datetime.strptime(line[1], '%m/%d/%Y'),  # date
    float(line[3])])  # discharge
print("Data points: " + str(len(recs)))
snow = np.array(recs)
snow_dates = snow[:, 0]
snow_in = snow[:, 1]
in_mm = 25.4
snow_mm = np.multiply(snow_in, in_mm)
snow_mm = np.array(snow_mm, dtype=float)


# def make_patch_spines_invisible(ax):

fig, ax = plt.subplots()
ax.set_frame_on(True)
ax.patch.set_visible(False)
for sp in ax.spines.values():
    sp.set_visible(False)
fig, host = plt.subplots()
fig.subplots_adjust(right=0.75)
par1 = host.twinx()
par2 = host.twinx()
par2.spines["right"].set_position(("axes", 1.2))
# make_patch_spines_invisible(par2)
par2.spines["right"].set_visible(True)
p1, = host.plot(all_recs[:, 0], all_recs[:, 1], "Purple", label="Discharge")
p2, = par1.plot(all_recs[:, 0], all_recs[:, 2], "g", label="Precipitation")
p3, = par2.plot(snow[:, 0], snow[:, 1], "b", label="Snow Water Equivalent")
# host.set_xlim(0, 2)
# host.set_ylim(0, 2)
# par1.set_ylim(0, 4)
par2.set_ylim(70, 0)
host.set_xlabel("Date")
host.set_ylabel("Cubic Feet per Second")
par1.set_ylabel("Precipitation Total for Watershed [m^3]")
par2.set_ylabel("[mm]")
host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
par2.yaxis.label.set_color(p3.get_color())
tkw = dict(size=4, width=1.5)
host.tick_params(axis='y', colors=p1.get_color(), **tkw)
par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
host.tick_params(axis='x', **tkw)
lines = [p1, p2, p3]
host.legend(lines, [l.get_label() for l in lines], loc=2)
plt.show()


# fig, ax1 = plt.subplots(1, figsize=(15, 5))
# ax1.plot(all_recs[:, 0], all_recs[:, 1], '-r', label='Discharge (cfs)')
# ax1.set_ylabel('Discharge (cfs)',  color='r')
# ax1.set_xlabel('Time')
# plt.legend()
# # plt.ylim(0.0,1.2)
# for tl in ax1.get_yticklabels():
#     tl.set_color('r')
# ax2 = ax1.twinx()
# ax2.plot(all_recs[:, 0], all_recs[:, 2], '-g', label='Watershed Rainfall (daily, cubic meters)')
# ax2.set_ylabel('Precipitation', color='g')
# # plt.ylim(0.0, 1.0)
# for tl in ax2.get_yticklabels():
#     tl.set_color('g')
# for tl in ax2.get_xticklabels():
#     tl.set_color('k')
# plt.legend()
# plt.title('Pueblo de Taos River Discharge vs Watershed Rainfall')
# plt.show()


