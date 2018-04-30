# ===============================================================================
# Copyright 2018 EXu
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
'''This is the script that I used to handle data processing
in Walnut Gulch'''
import csv
import numpy as np
import jdcal
import matplotlib.pyplot as plt

years = []
months = []
days = []
depth = []

obs_years = []
obs_months = []
obs_days = []

with open('G:\\Observations\\Precip_Anal\\FirstSet.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[3]))
        months.append(int(row[1]))
        days.append(int(row[2]))
        depth.append(row[4])
with open('G:\\Observations\\Precip_Anal\\SecondSet.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[3]))
        months.append(int(row[1]))
        days.append(int(row[2]))
        depth.append(row[4])
cum_depth = []
cdepth = float(depth[0])
for i in range(len(years)-1):
    if years[i+1] == years[i] and months[i+1] == months[i] and days[i+1] == days[i]:
        cdepth = cdepth + float(depth[i+1])
    else:
        cum_depth.append(cdepth)
        cdepth = float(depth[i+1])
        obs_years.append(years[i])
        obs_months.append(months[i])
        obs_days.append(days[i])

cd = np.cumsum(cum_depth)
X=[]
for i in range(len(obs_years)):
    b = sum(jdcal.gcal2jd(obs_years[i], obs_months[i], obs_days[i]))
    X.append(b)

years = []
months = []
days = []
depth = []

with open('G:\\Observations\\Precip_Anal\\acreft_all.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
        depth.append(float(row[3]))


myInt = (1.233*10**12)**(1/3)
newList = [x / myInt for x in depth]

y = []
for i in range(len(years)):
    a = sum(jdcal.gcal2jd(years[i], months[i],days[i]))
    y.append(a)

X = range(len(cd))
plt.plot(y,newList,label = "Observation for entire watershed")
plt.plot(X,cd,label = "PRISM for entire watershed")
plt.title('Precipitation Depth at All Gauges')
plt.ylabel('Cumulative Depth in mm')
plt.xlabel('Julian Day from 2/20/2000 to 12/31/2015')
plt.legend()
#cd - cum depth for obs
#newList - cum depth for PRISM
obs = []
for k in range(2000, 2016, 1):
    if k == 2000:
        a = [i for i, j in enumerate(obs_years) if j == k]
        diff = cd[max(a)]
        obs.append(diff)
    else:
        a = [i for i, j in enumerate(obs_years) if j == k]
        diff = cd[max(a)]-cd[min(a)-1]
        obs.append(diff)
 #cd[len(cd)-1] - sum(obs)

prism = []
for k in range(2000, 2016, 1):
    if k == 2000:
        a = [i for i, j in enumerate(years) if j == k]
        diff = newList[max(a)]
        prism.append(diff)
    else:
        a = [i for i, j in enumerate(years) if j == k]
        diff = newList[max(a)] - newList[min(a) - 1]
        prism.append(diff)
# newList[len(newList)-1] - sum(prism)
a = range(2000,2016,1)
b = [(x*1.0)/y for x, y in zip(prism, obs)]
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.bar(a,obs,label = "Precip Depth")
ax2.plot(a, b, 'r-', label = "Ratio")
ax1.set_xlabel('Year')
ax2.set_ylabel('PRISM/Gauge')
ax1.set_ylabel('Observed Annual Precipitation Depth in mm')
plt.title('All Watershed')
plt.legend()
plt.show()


#=====================================================================
#New separate files
"""Comparison between prism and their cloest gauges"""
import csv

obs_years = []
obs_months = []
obs_days = []
obs_depth = []

with open('G:\\Observations\\Precip_Anal\\o24.csv') as csvDataFile:
# with open('G:\\Observations\\Precip_Anal\\81.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        obs_years.append(int(row[3]))
        obs_months.append(int(row[1]))
        obs_days.append(int(row[2]))
        obs_depth.append(float(row[4]))
        # obs_years.append(int(row[2]))
        # obs_months.append(int(row[0]))
        # obs_days.append(int(row[1]))
        # obs_depth.append(float(row[3]))
import numpy as np
obs_cum_depth = np.cumsum(obs_depth)

years = []
months = []
days = []
depth = []

with open('G:\\Observations\\Precip_Anal\\24.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
        depth.append(float(row[3]))

import jdcal
x = []
y = []
for i in range(len(obs_years)):
    a = sum(jdcal.gcal2jd(obs_years[i], obs_months[i], obs_days[i]))
    x.append(a)
for i in range(len(years)):
    b = sum(jdcal.gcal2jd(years[i], months[i], days[i]))
    y.append(b)

import matplotlib.pyplot as plt
plt.plot(x,obs_cum_depth,label = "observation")
plt.plot(y,depth,label ="PRISM")
# plt.plot(x,obs_depth,label = "at the exact pixel")
# plt.plot(y,depth,label ="offset by 1")
plt.title('Near Rain Gauge 24')
plt.ylabel('Cumulative Depth in mm')
plt.xlabel('Julian Day from 2/20/2000 to 12/31/2015')
plt.rc('font', size=12)  # controls default text sizes
plt.rc('axes', titlesize=12, labelsize=12)  # fontsize of the axes title
plt.rc('xtick', labelsize=10)  # fontsize of the tick labels
plt.rc('ytick', labelsize=10)  # fontsize of the tick labels
plt.legend()

#calculate annual difference
obs = []
for k in range(2000, 2016, 1):
    if k == 2000:
        a = [i for i, j in enumerate(obs_years) if j == k]
        diff = obs_cum_depth[max(a)]
        obs.append(diff)
    else:
        a = [i for i, j in enumerate(obs_years) if j == k]
        diff = obs_cum_depth[max(a)]-obs_cum_depth[min(a)-1]
        obs.append(diff)
# obs_cum_depth[len(obs_cum_depth)-1] - sum(obs)

prism = []
for k in range(2000, 2016, 1):
    if k == 2000:
        a = [i for i, j in enumerate(years) if j == k]
        diff = depth[max(a)]
        prism.append(diff)
    else:
        a = [i for i, j in enumerate(years) if j == k]
        diff = depth[max(a)] - depth[min(a) - 1]
        prism.append(diff)
# depth[len(depth)-1] - sum(prism)
a = range(2000,2016,1)
b = [(x*1.0)/y for x, y in zip(prism, obs)]

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.bar(a,obs,label = "Precip Depth")
ax2.plot(a, b, 'r-', label = "Ratio")
ax1.set_xlabel('Year')
ax2.set_ylabel('PRISM/Gauge')
ax1.set_ylabel('Observed Annual Precipitation Depth in mm')
plt.title('Near gauge 24')
plt.legend()
plt.show()


#three places
P/O = [1.03,0.95,0.74,0.84,0.77,0.68,1.11,0.87,0.84,0.93,1.00,1.02,0.97,0.90,1.10,1.41]
#Entire


#===========================
import csv
import numpy as np
import jdcal
import matplotlib.pyplot as plt

'''ID Month Day Year Duration Depth'''

ID = []
years = []
months = []
days = []
duration=[]
depth = []

with open('G:\\Observations\\Precip_Anal_2\\East_Corner_4.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        ID.append(int(row[0]))
        months.append(int(row[1]))
        days.append(int(row[2]))
        years.append(int(row[3]))
        duration.append(row[4])
        depth.append(row[5])
obs_years = []
obs_months = []
obs_days = []
obs_id = []
obs_duration = []
cum_depth = []
cum_duration = []
cdepth = float(depth[0])
cduration = float(duration[0])
for i in range(len(years)-1):
    if years[i+1] == years[i] and months[i+1] == months[i] and days[i+1] == days[i]:
        cdepth = cdepth + float(depth[i+1])
        cduration = cduration + float(duration[i + 1])
    else:
        cum_depth.append(cdepth)
        cum_duration.append(cduration)
        cdepth = float(depth[i+1])
        cduration = float(duration[i + 1])
        obs_years.append(years[i])
        obs_months.append(months[i])
        obs_days.append(days[i])
        obs_id.append(ID[i])

gauge_number = 70
def sep_time_depth(gauge_number,obs_id,obs_years,obs_months,obs_days,cum_depth,cum_duration):
    ind = [i for i, j in enumerate(obs_id) if j == gauge_number]
    dep = []
    x = []
    dur = []
    for i in ind:
        dep.append(cum_depth[i])
        dur.append(cum_duration[i])
        t = sum(jdcal.gcal2jd(obs_years[i], obs_months[i], obs_days[i]))
        x.append(t)
    cd = np.cumsum(dep)
    return dep,dur,x,cd,ind
dep,dur,x,cd,ind = sep_time_depth(gauge_number,obs_id,obs_years,obs_months,obs_days,cum_depth,cum_duration)


years = []
months = []
days = []
depth = []

with open('G:\\Observations\\Precip_Anal_2\\Data\\70mm.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
        depth.append(float(row[3]))
y = []
for i in range(len(years)):
    a = sum(jdcal.gcal2jd(years[i], months[i],days[i]))
    y.append(a)

plt.bar(x,np.log(dur))
plt.title('Precipitation Density Distribution at Gauge 70')
plt.ylabel('Precipitation duration in minutes')
plt.xlabel('Julian Day from 2/20/2000 to 12/31/2015')
plt.legend()


plt.plot(x,cd,label = "Observation")
plt.plot(y,depth,label = "PRISM")
plt.title('Precipitation Depth at Gauge 70')
plt.ylabel('Cumulative Depth in mm')
plt.xlabel('Julian Day from 2/20/2000 to 12/31/2015')
plt.rc('font', size=12)  # controls default text sizes
plt.rc('axes', titlesize=12, labelsize=12)  # fontsize of the axes title
plt.rc('xtick', labelsize=10)  # fontsize of the tick labels
plt.rc('ytick', labelsize=10)  # fontsize of the tick labels
plt.legend()
#cd - cum depth for obs
#newList - cum depth for PRISM
obs = []
for k in range(2000, 2016, 1):
    if k == 2000:
        oyears = obs_years[min(ind):max(ind)+1]
        a = [i for i, j in enumerate(oyears) if j == k]
        diff = cd[max(a)]
        obs.append(diff)
    else:
        oyears = obs_years[min(ind):max(ind) + 1]
        a = [i for i, j in enumerate(oyears) if j == k]
        diff = cd[max(a)]-cd[min(a)-1]
        obs.append(diff)
# cd[len(cd)-1] - sum(obs)

prism = []
for k in range(2000, 2016, 1):
    if k == 2000:
        a = [i for i, j in enumerate(years) if j == k]
        diff = depth[max(a)]
        prism.append(diff)
    else:
        a = [i for i, j in enumerate(years) if j == k]
        diff = depth[max(a)] - depth[min(a) - 1]
        prism.append(diff)
# depth[len(depth)-1] - sum(prism)
a = range(2000,2016,1)
b = [(x*1.0)/y for x, y in zip(prism, obs)]
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.bar(a,obs,label = "Precip Depth")
ax2.plot(a, b, 'r-', label = "Ratio")
ax1.set_xlabel('Year')
ax2.set_ylabel('PRISM/Gauge')
ax1.set_ylabel('Observed Annual Precipitation Depth in mm')
plt.title('Gauge 70')
plt.legend()
plt.show()

#============================================================================
#============================================================================
#============================================================================
#============================================================================
#============================================================================
#============================================================================
#============================================================================

#PRISM vs Observation
#one far away -- 69
import csv
import numpy as np
import jdcal
import matplotlib.pyplot as plt

'''csv storage order: ID Month Day Year Duration Depth'''

ID = []
years = []
months = []
days = []
duration=[]
depth = []
#read observational files
with open('G:\\Observations\\Precip_Anal_2\\East_Corner_4.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        ID.append(int(row[0]))
        months.append(int(row[1]))
        days.append(int(row[2]))
        years.append(int(row[3]))
        duration.append(row[4])
        depth.append(row[5])
obs_years = []
obs_months = []
obs_days = []
obs_id = []
obs_duration = []
obs_depth = []
cdepth = float(depth[0])
cduration = float(duration[0])

#sum up the depth and duration  for every day
for i in range(len(years)-1):
    if years[i+1] == years[i] and months[i+1] == months[i] and days[i+1] == days[i]:
        cdepth = cdepth + float(depth[i+1])
        cduration = cduration + float(duration[i + 1])
    else:
        obs_depth.append(cdepth)#depth in daily time interval
        obs_duration.append(cduration)#duration in daily time interval
        cdepth = float(depth[i+1])
        cduration = float(duration[i + 1])
        obs_years.append(years[i])
        obs_months.append(months[i])
        obs_days.append(days[i])
        obs_id.append(ID[i])

#variables for monsoon season
monsoon_years = []
monsoon_months = []
monsoon_days = []
monsoon_id = []
monsoon_depth = []
monsoon_duration = []
#variables for non-monsoon season
other_years = []
other_months = []
other_days = []
other_id = []
other_depth = []
other_duration = []

for i in range(len(obs_years)):
    if obs_months[i] == 6 or obs_months[i] == 7 or obs_months[i] == 8 or obs_months[i] == 9:
        monsoon_years.append(obs_years[i])
        monsoon_months.append(obs_months[i])
        monsoon_days.append(obs_days[i])
        monsoon_id.append(obs_id[i])
        monsoon_depth.append(obs_depth[i])
        monsoon_duration.append(obs_duration[i])
    else:
        other_years.append(obs_years[i])
        other_months.append(obs_months[i])
        other_days.append(obs_days[i])
        other_id.append(obs_id[i])
        other_depth.append(obs_depth[i])
        other_duration.append(obs_duration[i])

"""fuction for take out precip depth and duration data from certain gauge in julian day"""
def sep_time_depth(gauge_number,obs_id,obs_years,obs_months,obs_days,cum_depth,cum_duration):
    ind = [i for i, j in enumerate(obs_id) if j == gauge_number]
    dep = []
    x = []
    dur = []
    for i in ind:
        dep.append(cum_depth[i])
        dur.append(cum_duration[i])
        t = sum(jdcal.gcal2jd(obs_years[i], obs_months[i], obs_days[i]))
        x.append(t)
    cd = np.cumsum(dep)
    return dep,dur,x,cd,ind

#for the gauge of
gauge_number = 70
#monsoon
m_dep,m_dur,m_time,m_cum_dep,m_ind = sep_time_depth(gauge_number =gauge_number,obs_id = monsoon_id,obs_years = monsoon_years,obs_months=monsoon_months,obs_days=monsoon_days,cum_depth=monsoon_depth,cum_duration=monsoon_duration)
#other time
o_dep,o_dur,o_time,o_cum_dep,o_ind = sep_time_depth(gauge_number,other_id,other_years,other_months,other_days,other_depth,other_duration)
#---------------------------------------------------------------------------------------------------
#PRISM for the rear data
years = []
months = []
days = []
depth = []

with open('C:\\Users\\Esther\\Desktop\\NMTer-Spring2018\\HYD 592\\90.csv') as csvDataFile:
# with open('G:\\Observations\\Precip_Anal_2\\Data\\70mm.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
        depth.append(float(row[3]))

# calculate the individual depth
ind_depth = []
for i in range(len(depth)-1):
    pd = depth[i + 1] - depth[i]
    ind_depth.append(pd)

#variables for monsoon season
p_monsoon_years = []
p_monsoon_months = []
p_monsoon_days = []
p_monsoon_depth = []

#variables for non-monsoon season
p_other_years = []
p_other_months = []
p_other_days = []
p_other_depth = []

#calculate separate depth
for i in range(len(years)-1):
    if months[i+1] == 6 or months[i+1] == 7 or months[i+1] == 8 or months[i+1] == 9:
        p_monsoon_years.append(int(years[i+1]))
        p_monsoon_months.append(int(months[i+1]))
        p_monsoon_days.append(int(days[i+1]))
        p_monsoon_depth.append(float(ind_depth[i]))
    else:
        p_other_years.append(int(years[i+1]))
        p_other_months.append(int(months[i+1]))
        p_other_days.append(int(days[i+1]))
        p_other_depth.append(float(ind_depth[i]))

#set up time frame
p_m_time = []
p_o_time = []
for i in range(len(p_monsoon_years)):
    a = sum(jdcal.gcal2jd(p_monsoon_years[i], p_monsoon_months[i],p_monsoon_days[i]))
    p_m_time.append(a)
for i in range(len(p_other_years)):
    b = sum(jdcal.gcal2jd(p_other_years[i], p_other_months[i],p_other_days[i]))
    p_o_time.append(b)

#corresponding relationship:
#m_dep/o_dep -- p_monsoon_depth/p_other_depth
#------------------------------------------------------------------------------
#for monsoon season
ms_indices = [i for i, item in enumerate(p_m_time) if item in set(m_time)]
p_m_dep = [p_monsoon_depth[int(i)] for i in ms_indices]
#cum
p_m_cum_dep = np.cumsum(p_m_dep)
#for other time
o_indices = [i for i, item in enumerate(p_o_time) if item in set(o_time)]
p_o_dep = [p_other_depth[int(i)] for i in o_indices]
#cum
p_o_cum_dep = np.cumsum(p_o_dep)

#---------------------------------------------------------------------------
#comparison for cum
plt.plot(m_time,m_cum_dep,label = "Gauge")
plt.plot(m_time,p_m_cum_dep,label = "PRISM")
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Cumulative Depth Comparison for monsoon season")
plt.legend()
#------------------------------------------------------------
plt.plot(o_time,o_cum_dep,label = "Gauge")
plt.plot(o_time,p_o_cum_dep,label = "PRISM")
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Cumulative Depth Comparison for usual time")
plt.legend()
#---------------------------------------------------------------------------
#comparison for separate
plt.scatter(m_dep,p_m_dep)
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Depth Comparison for monsoon season")
#------------------------------------------------------------
plt.scatter(o_dep,p_o_dep)
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Depth Comparison for other time")


#==========================================================================================
# one close -- 81
years = []
months = []
days= []
duration = []
depth = []

with open('G:\\Observations\\Precip_Anal_2\\Data\\81mmData.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
        depth.append(float(row[4]))
        duration.append(int(row[3]))
obs_years = []
obs_months = []
obs_days = []
obs_duration = []
obs_depth = []
cdepth = float(depth[0])
cduration = float(duration[0])

#sum up the depth and duration  for every day
for i in range(len(years)-1):
    if years[i+1] == years[i] and months[i+1] == months[i] and days[i+1] == days[i]:
        cdepth = cdepth + float(depth[i+1])
        cduration = cduration + float(duration[i + 1])
    else:
        obs_depth.append(cdepth)#depth in daily time interval
        obs_duration.append(cduration)#duration in daily time interval
        cdepth = float(depth[i+1])
        cduration = float(duration[i + 1])
        obs_years.append(years[i])
        obs_months.append(months[i])
        obs_days.append(days[i])
#variables for monsoon season
monsoon_years = []
monsoon_months = []
monsoon_days = []
monsoon_depth = []
monsoon_duration = []
#variables for non-monsoon season
other_years = []
other_months = []
other_days = []
other_depth = []
other_duration = []

for i in range(len(obs_years)):
    if obs_months[i] == 6 or obs_months[i] == 7 or obs_months[i] == 8 or obs_months[i] == 9:
        monsoon_years.append(obs_years[i])
        monsoon_months.append(obs_months[i])
        monsoon_days.append(obs_days[i])
        monsoon_depth.append(obs_depth[i])
        monsoon_duration.append(obs_duration[i])
    else:
        other_years.append(obs_years[i])
        other_months.append(obs_months[i])
        other_days.append(obs_days[i])
        other_depth.append(obs_depth[i])
        other_duration.append(obs_duration[i])

n_m_cum_dep = np.cumsum(monsoon_depth)
n_o_cum_dep = np.cumsum(other_depth)
n_m_time = []
for i in range(len(monsoon_years)):
    a = sum(jdcal.gcal2jd(monsoon_years[i], monsoon_months[i],monsoon_days[i]))
    n_m_time.append(a)
n_o_time = []
for i in range(len(other_years)):
    a = sum(jdcal.gcal2jd(other_years[i], other_months[i],other_days[i]))
    n_o_time.append(a)



# PRISM for the near data
years = []
months = []
days = []
depth = []

with open('G:\\Observations\\Precip_Anal\\81.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
        depth.append(float(row[3]))

# calculate the individual depth
ind_depth = []
for i in range(len(depth) - 1):
    pd = depth[i + 1] - depth[i]
    ind_depth.append(pd)

# variables for monsoon season
np_monsoon_years = []
np_monsoon_months = []
np_monsoon_days = []
np_monsoon_depth = []

# variables for non-monsoon season
np_other_years = []
np_other_months = []
np_other_days = []
np_other_depth = []

# calculate separate depth
for i in range(len(years) - 1):
    if months[i + 1] == 6 or months[i + 1] == 7 or months[i + 1] == 8 or months[i + 1] == 9:
        np_monsoon_years.append(int(years[i + 1]))
        np_monsoon_months.append(int(months[i + 1]))
        np_monsoon_days.append(int(days[i + 1]))
        np_monsoon_depth.append(float(ind_depth[i]))
    else:
        np_other_years.append(int(years[i + 1]))
        np_other_months.append(int(months[i + 1]))
        np_other_days.append(int(days[i + 1]))
        np_other_depth.append(float(ind_depth[i]))

# set up time frame
np_m_time = []
np_o_time = []
for i in range(len(np_monsoon_years)):
    a = sum(jdcal.gcal2jd(np_monsoon_years[i], np_monsoon_months[i], np_monsoon_days[i]))
    np_m_time.append(a)
for i in range(len(np_other_years)):
    b = sum(jdcal.gcal2jd(np_other_years[i], np_other_months[i], np_other_days[i]))
    np_o_time.append(b)

# corresponding relationship:
# m_dep/o_dep -- monsoon_depth/other_depth
# ------------------------------------------------------------------------------
# for monsoon season
ms_indices = [i for i, item in enumerate(np_m_time) if item in set(n_m_time)]
np_m_dep = [np_monsoon_depth[int(i)] for i in ms_indices]
# cum
np_m_cum_dep = np.cumsum(np_m_dep)
# for other time
o_indices = [i for i, item in enumerate(np_o_time) if item in set(n_o_time)]
np_o_dep = [np_other_depth[int(i)] for i in o_indices]
# cum
np_o_cum_dep = np.cumsum(np_o_dep)

#---------------------------------------------------------------------------
#comparison for cum
plt.plot(n_m_time,np_m_cum_dep,label = "PRISM")
plt.plot(n_m_time,n_m_cum_dep,label = "Gauge")
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Cumulative Depth Comparison for monsoon season at 81")
plt.legend()
#------------------------------------------------------------
plt.plot(n_o_time,np_o_cum_dep,label = "PRISM")
plt.plot(n_o_time,n_o_cum_dep,label = "Gauge")
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Cumulative Depth Comparison for usual time at 81")
plt.legend()
#---------------------------------------------------------------------------
#comparison for separate
plt.scatter(monsoon_depth,np_m_dep)
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Depth Comparison for monsoon season at 81")
#------------------------------------------------------------
plt.scatter(other_depth,np_o_dep)
plt.ylabel("PRISM")
plt.xlabel("Gauge")
plt.title("Depth Comparison for other time at 81")

#=============================================================
#=============================================================
#duration comparison
#rear gauge
#monsoon season
plt.scatter(m_dur,p_m_dep)
plt.ylabel("Depth in mm")
plt.xlabel("Duration in min")
plt.title("Intensity for monsoon season at Rear Location")
#------------------------------------------------------------
#other time
plt.scatter(o_dur,p_o_dep)
plt.ylabel("Depth in mm")
plt.xlabel("Duration in min")
plt.title("Intensity for other time at Rear Location")
#=============================
#near gauge
#monsoon season
plt.scatter(monsoon_duration,monsoon_depth)
plt.ylabel("Depth in mm")
plt.xlabel("Duration in min")
plt.title("Intensity for monsoon season at Near Location (81)")
#------------------------------------------------------------
#other time
plt.scatter(other_duration,other_depth)
plt.ylabel("Depth in mm")
plt.xlabel("Duration in min")
plt.title("Intensity for other time at Near Location (81)")

#================================================================
#----------------------------------------------------------------
#================================================================
#stochastic analysis in distribution
#=====================================================================
#These are the common dates that both gauge and PRISM collected data.
bins = np.linspace(0, 70,15)
plt.hist(m_dep,bins,alpha=0.5,label= "Gauge")
plt.hist(p_m_dep,bins,alpha=0.5,label= "PRISM")
plt.legend()
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for monsoon season at rear pixel (Gauge 69)")
#------------------------------------------------------------
bins = np.linspace(0, 50, 11)
plt.hist(o_dep,bins,alpha=0.5,label= "Gauge")
plt.hist(p_o_dep,bins,alpha=0.5,label= "PRISM")
plt.legend(loc='upper right')
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for other time at rear pixel (Gauge 69)")
plt.show()

#comparison for separate,near
bins = np.linspace(0,60,13)
plt.hist(monsoon_depth,bins,alpha=0.5,label= "Gauge")
plt.hist(np_m_dep,bins,alpha=0.5,label= "PRISM")
plt.legend()
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for monsoon season at near pixel (Gauge 81)")

#------------------------------------------------------------
bins = np.linspace(0, 50, 11)
plt.hist(other_depth,bins,alpha=0.5,label= "Gauge")
plt.hist(np_o_dep,bins,alpha=0.5,label= "PRISM")
plt.legend(loc='upper right')
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for other time at near pixel (Gauge 81)")
plt.show()
#=====================================================================
#for all PRISM data
bins = np.linspace(0, 70,15)
bins = np.linspace(5, 70,14)
plt.hist(m_dep,bins,alpha=0.5,label= "Gauge")
plt.hist(p_monsoon_depth,bins,alpha=0.5,label= "PRISM[All_data]")
plt.legend()
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for monsoon season at rear pixel (Gauge 69)")
#------------------------------------------------------------
bins = np.linspace(0, 50, 11)
bins = np.linspace(5, 50, 10)
plt.hist(o_dep,bins,alpha=0.5,label= "Gauge")
plt.hist(p_other_depth,bins,alpha=0.5,label= "PRISM[All_data]")
plt.legend(loc='upper right')
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for other time at rear pixel (Gauge 69)")
plt.show()

#comparison for separate,near
bins = np.linspace(0,60,13)
bins = np.linspace(5,60,12)
plt.hist(monsoon_depth,bins,alpha=0.5,label= "Gauge")
plt.hist(np_monsoon_depth,bins,alpha=0.5,label= "PRISM[All_data]")
plt.legend()
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for monsoon season at near pixel (Gauge 81)")

#------------------------------------------------------------
bins = np.linspace(0, 50, 11)
bins = np.linspace(5, 50, 10)
plt.hist(other_depth,bins,alpha=0.5,label= "Gauge")
plt.hist(np_other_depth,bins,alpha=0.5,label= "PRISM[All_data]")
plt.legend(loc='upper right')
plt.ylabel("Counts/Days")
plt.xlabel("Depth/mm")
plt.title("Depth Distribution for other time at near pixel (Gauge 81)")
plt.show()

#================================================================================
#================================================================================
#================================================================================
#================================================================================
#Intensity - bin my precip
import math
'''This is the function to find the closest ceil integer based on the bin base'''
def makebin(y,base = 5):
    def ceil(x, base=5):
        return int(base * math.ceil(float(x) / base))
    ymax = max(y)
    thebin = np.linspace(0, ceil(ymax, base), ceil(ymax, base) / base + 1)
    return thebin

"""This is the function to bin the data into several groups and plot them"""
def binmydata(bin, depth, duration,tlt):
    binsize = len(bin) - 1
    bindepth = [[] for x in xrange(binsize)]
    binduration = [[] for x in xrange(binsize)]

    for i in range(binsize):
        ind = np.where((depth < bin[i + 1]) & (depth >= bin[i]))
        ind = ind[0]
        for j in range(len(ind)):
            bindepth[i].append(depth[ind[j]])
            binduration[i].append(duration[ind[j]])

        # label name
        lbln = "Bin: " + str(bin69m[i + 1])
        plt.scatter(binduration[i], bindepth[i], label=lbln)

    plt.title(tlt)
    plt.ylabel("Precipitation Depth in mm")
    plt.xlabel("Duration in min")
    plt.legend(loc='lower right')
    plt.rc('font', size=20)  # controls default text sizes
    plt.rc('axes', titlesize=24, labelsize=20)  # fontsize of the axes title
    plt.rc('xtick', labelsize=18)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=18)  # fontsize of the tick labels
    plt.rc('legend', fontsize=18)  # legend fontsize
    plt.rc('figure', titlesize=18)  # fontsize of the figure title
#===================================================================
#Monsoon at 69
bin = makebin(m_dep,base = 5)
depth = m_dep
duration = m_dur
tlt = "Monsoon Season Intensity at 69"
binmydata(bin, depth, duration,tlt)
#Other time at 69
bin = makebin(o_dep,base = 5)
depth = o_dep
duration = o_dur
tlt = "Other Time Intensity at 69"
binmydata(bin, depth, duration,tlt)
#-------------------------------------------------------
#Monsoon at 81
bin = makebin(monsoon_depth,base = 5)
depth = monsoon_depth
duration = monsoon_duration
tlt = "Monsoon Season Intensity at 81"
binmydata(bin, depth, duration,tlt)
#Other time at 81
bin = makebin(other_depth,base = 5)
depth = other_depth
duration = other_duration
tlt = "Other Time Intensity at 81"
binmydata(bin, depth, duration,tlt)
#=======================================================================

