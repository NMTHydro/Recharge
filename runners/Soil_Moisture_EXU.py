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


"""This is the code that I used to process antecedent soil moisture"""
import csv
import numpy as np
import matplotlib.pyplot as plt

#First group, runoff gauge 11 and rain gauge 90
r_years = []
r_months = []
r_days = []
# r_dur = []
r_dep = []
# with open('H:\\Observations\\Soil_Moisture\\runoff_10.csv') as csvDataFile:
# with open('H:\\Observations\\East_4\\runoff_10.csv') as csvDataFile:
with open('C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 3\\unit source\\runoff112.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        # r_months.append(int(row[0]))
        # r_days.append(int(row[1]))
        # r_years.append(int(row[2]))
        # r_dur.append(int(row[3]))
        # r_dep.append(float(row[4]))
        r_months.append(int(row[1]))
        r_days.append(int(row[2]))
        r_years.append(int(row[3]))
        r_dep.append(float(row[4]))

#read rain data
p_years = []
p_months = []
p_days = []
p_dur = []
p_dep = []
'''head for 2 first grade watershed'''
# with open('H:\\Observations\\Soil_Moisture\\rain_31.csv') as csvDataFile:
'''head for east 4'''
# with open('H:\\Observations\\East_4\\precip_70.csv') as csvDataFile:
with open('C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 3\\unit source\\rain82.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        # p_months.append(int(row[0]))
        # p_days.append(int(row[1]))
        # p_years.append(int(row[2]))
        # p_dur.append(int(row[3]))
        # p_dep.append(float(row[4]))
        p_months.append(int(row[1]))
        p_days.append(int(row[2]))
        p_years.append(int(row[3]))
        p_dur.append(int(row[4]))
        p_dep.append(float(row[5]))
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
"""Stack data on daily basis"""
r_obs_years = []
r_obs_months = []
r_obs_days = []
# r_obs_duration = []
r_obs_depth = []
cdepth = float(r_dep[0])
# cduration = float(r_dur[0])
for i in range(len(r_years)-1):
    if r_years[i+1] == r_years[i] and r_months[i+1] == r_months[i] and r_days[i+1] == r_days[i]:
        cdepth = cdepth + float(r_dep[i+1])
        # cduration = cduration + float(r_dur[i + 1])
    else:
        r_obs_depth.append(cdepth)#depth in daily time interval
        # r_obs_duration.append(cduration)#duration in daily time interval
        cdepth = float(r_dep[i+1])
        # cduration = float(r_dur[i + 1])
        r_obs_years.append(r_years[i])
        r_obs_months.append(r_months[i])
        r_obs_days.append(r_days[i])
#precip
p_obs_years = []
p_obs_months = []
p_obs_days = []
p_obs_duration = []
p_obs_depth = []

cdepth = float(p_dep[0])
cduration = float(p_dur[0])

#sum up the depth and duration  for every day
for i in range(len(p_years)-1):
    if p_years[i+1] == p_years[i] and p_months[i+1] == p_months[i] and p_days[i+1] == p_days[i]:
        cdepth = cdepth + float(p_dep[i+1])
        cduration = cduration + float(p_dur[i + 1])
    else:
        p_obs_depth.append(cdepth)#depth in daily time interval
        p_obs_duration.append(cduration)#duration in daily time interval
        cdepth = float(p_dep[i+1])
        cduration = float(p_dur[i + 1])
        p_obs_years.append(p_years[i])
        p_obs_months.append(p_months[i])
        p_obs_days.append(p_days[i])

# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
"""Insert 0s to complete dataset"""
# read data from ETRM
years = []
months = []
days = []
#doesn't matter which file, as long as it is PRISM. Since this is for entrie time series
with open('H:\\Observations\\Precip_Anal_2\\Data\\70mm.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# set up time for depth
import jdcal
r_time = []
p_time = []
f_time = []
for i in range(len(r_obs_years)):
    a = sum(jdcal.gcal2jd(r_obs_years[i], r_obs_months[i],r_obs_days[i]))
    r_time.append(a)
for i in range(len(p_obs_years)):
    b = sum(jdcal.gcal2jd(p_obs_years[i], p_obs_months[i],p_obs_days[i]))
    p_time.append(b)
for i in range(len(years)):
    c = sum(jdcal.gcal2jd(years[i], months[i],days[i]))
    f_time.append(c)

# find indices
r_ind = [i for i, item in enumerate(f_time) if item in r_time]
p_ind = [i for i, item in enumerate(f_time) if item in p_time]
# fit 0s
p_obs_depth_f = [0] * len(f_time)
p_obs_duration_f = [0] * len(f_time)
r_obs_depth_f = [0] * len(f_time)
# r_obs_duration_f = [0] * len(f_time)
for i in range(len(p_ind)):
    p_obs_depth_f[p_ind[i]] = p_obs_depth[i]
    p_obs_duration_f[p_ind[i]] = p_obs_duration[i]
for i in range(len(r_ind)):
    r_obs_depth_f[r_ind[i]] = r_obs_depth[i]
    # r_obs_duration_f[r_ind[i]] = r_obs_duration[i]

# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
plt.plot(f_time,p_obs_depth_f,'r.-',label = "Precipitation")
plt.plot(f_time,r_obs_depth_f,'b.-',label = "Runoff")
plt.title("Precipitation and Runoff at r4 and p31")
plt.ylabel("Depth in mm")
plt.xlabel("Julian Days")
plt.legend(loc='upper left')
plt.rc('font', size=20)  # controls default text sizes
plt.rc('axes', titlesize=24, labelsize=20)  # fontsize of the axes title
plt.rc('xtick', labelsize=18)  # fontsize of the tick labels
plt.rc('ytick', labelsize=18)  # fontsize of the tick labels
plt.rc('legend', fontsize=18)  # legend fontsize
plt.rc('figure', titlesize=18)  # fontsize of the figure title
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
"""Calculate Intensity"""
# r_inten = [dep/dur for dep,dur in zip(r_obs_depth, r_obs_duration)]
p_inten = [dep/dur for dep,dur in zip(p_obs_depth, p_obs_duration)]
# fit 0s
p_inten_f = [0] * len(f_time)
for i in range(len(p_ind)):
    p_inten_f[p_ind[i]] = p_inten[i]

# ----------------------------------------------------------------------
# set up time for depth
import jdcal
# r_i_time = []
p_i_time = []

# for i in range(len(r_obs_depth)):
#     if r_obs_depth[i] > 0:
#         a = sum(jdcal.gcal2jd(r_obs_years[i], r_obs_months[i], r_obs_days[i]))
#         r_i_time.append(a)

for i in range(len(p_obs_depth)):
    if p_obs_duration[i] > 0:
        b = sum(jdcal.gcal2jd(p_obs_years[i], p_obs_months[i],p_obs_days[i]))
        p_i_time.append(b)
#------------------------------------------------------------------------
p_inten_n = [i*10 for i in p_inten_f]
# plot intensity
plt.plot(f_time,p_inten_n,'r*-',label = "Precipitation Intensity")
plt.plot(f_time,r_obs_depth_f,'b*-',label = "Runoff")
plt.title("Precipitation Intensity and Runoff at r4 and p31")
plt.ylabel("Depth in mm/Intensity in mm/min")
plt.xlabel("Julian Days")
plt.legend(loc='upper right')
plt.rc('font', size=20)  # controls default text sizes
plt.rc('axes', titlesize=24, labelsize=20)  # fontsize of the axes title
plt.rc('xtick', labelsize=18)  # fon tsize of the tick labels
plt.rc('ytick', labelsize=18)  # fontsize of the tick labels
plt.rc('legend', fontsize=18)  # legend fontsize
plt.rc('figure', titlesize=18)  # fontsize of the figure title

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#bin the data based on antecedent rainfall

# create antecedent rainfall condition
antecedent = []
for i in range(len(p_obs_depth_f)-8):
    antecedent.append(sum(p_obs_depth_f[i:i+7]))
#specify the bin
bin = [0,5,10,20,50,130]
depth = r_obs_depth_f[7:-1]
duration = p_inten_f[7:-1]
scatter = p_obs_depth_f[7:-1]
binsize = len(bin) - 1
bindepth = [[] for x in xrange(binsize)]
binduration = [[] for x in xrange(binsize)]

binscatter= [[] for x in xrange(binsize)]
for i in range(binsize):
    ind1 = [k for k, v in enumerate(antecedent) if v >= bin[i]]
    ind2 = [k for k, v in enumerate(antecedent) if v < bin[i+1]]
    ind = list(set(ind1) & set(ind2))
    for j in range(len(ind)):
        bindepth[i].append(depth[ind[j]])
        binduration[i].append(duration[ind[j]])
        binscatter[i].append(scatter[ind[j]])
        # label name
        lbln = "Bin: " + str(bin[i + 1])

plt.scatter(binduration[4], bindepth[4], label=bin[5],s=binscatter[4])
plt.scatter(binduration[3], bindepth[3], label=bin[4],s=binscatter[3])
plt.scatter(binduration[2], bindepth[2], label=bin[3],s=binscatter[2])
plt.scatter(binduration[1], bindepth[1], label=bin[2],s=binscatter[1])
plt.scatter(binduration[0], bindepth[0], label=bin[1],s=binscatter[0])

plt.scatter(binduration[4], bindepth[4], label=bin[5])
plt.scatter(binduration[3], bindepth[3], label=bin[4])
plt.scatter(binduration[2], bindepth[2], label=bin[3])
plt.scatter(binduration[1], bindepth[1], label=bin[2])
plt.scatter(binduration[0], bindepth[0], label=bin[1])







plt.title("Color coded in antecedent rainfall intensity at 11,90")
plt.xlabel("Precipitation Intensity in mm/min")
plt.ylabel("Runoff Depth in mm")
plt.legend(loc='upper right')
plt.rc('font', size=20)  # controls default text sizes
plt.rc('axes', titlesize=24, labelsize=20)  # fontsize of the axes title
plt.rc('xtick', labelsize=18)  # fontsize of the tick labels
plt.rc('ytick', labelsize=18)  # fontsize of the tick labels
plt.rc('legend', fontsize=18)  # legend fontsize
plt.rc('figure', titlesize=18)  # fontsize of the figure title


# import csv
#
# rows = zip(p_inten_f[7:-1], r_obs_depth_f[7:-1], antecedent, p_obs_depth_f[7:-1])
# csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Spring2018\\HYD 592\\R_bin.csv"
#
# #Assuming res is a flat list
# with open(csvfile, "w") as output:
#     writer = csv.writer(output)
#     for val in rows:
#         writer.writerow(val)

import csv

rows = zip(p_inten_f, r_obs_depth_f, p_obs_depth_f)
csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 3\\unit source\\IRP.csv"

#Assuming res is a flat list
with open(csvfile, "w") as output:
    writer = csv.writer(output)
    for val in rows:
        writer.writerow(val)

# --------------------------------------------------------------------------------
# ================================================================================
# --------------------------------------------------------------------------------
a = 7
antecedent = []
for i in range(len(p_obs_depth_f)-a-1):
    antecedent.append(sum(p_obs_depth_f[i:i+a]))

"""Split precip and runoff to monsoon or not monsoon"""
#variables for monsoon season
monsoon_years = []
monsoon_months = []
monsoon_days = []
monsoon_depth_p = []
monsoon_duration_p = []
monsoon_inten = []
monsoon_depth_r = []
# monsoon_ante = []
#variables for non-monsoon season
other_years = []
other_months = []
other_days = []
other_depth_p = []
other_duration_p = []
other_inten = []
other_depth_r = []
# other_ante = []
a = 0
# for i in range(7,len(years)-1,1):
for i in range(a,len(years) - 1,1):
    if months[i] == 6 or months[i] == 7 or months[i] == 8 or months[i] == 9:
        monsoon_years.append(years[i])
        monsoon_months.append(months[i])
        monsoon_days.append(days[i])
        monsoon_depth_p.append(p_obs_depth_f[i])
        monsoon_duration_p.append(p_obs_duration_f[i])
        monsoon_inten.append(p_inten_f[i])
        monsoon_depth_r.append(r_obs_depth_f[i])
        # monsoon_ante.append(antecedent[i-a])
    else:
        other_years.append(years[i])
        other_months.append(months[i])
        other_days.append(days[i])
        other_depth_p.append(p_obs_depth_f[i])
        other_duration_p.append(p_obs_duration_f[i])
        other_inten.append(p_inten_f[i])
        other_depth_r.append(r_obs_depth_f[i])
        # other_ante.append(antecedent[i-a])

import csv

# rows = zip(monsoon_depth_p,monsoon_inten,monsoon_depth_r,monsoon_ante)
# rows = zip(monsoon_depth_p,monsoon_inten,monsoon_depth_r,monsoon_duration_p,monsoon_ante)
# rows = zip(p_monsoon_years,p_monsoon_months,p_monsoon_days,p_monsoon_depth)
# csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Spring2018\\HYD 592\\Data1_g{n}.csv".format(n = a)
rows = zip(monsoon_depth_p,monsoon_inten,monsoon_depth_r)
csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 3\\unit source\\Data1_g{n}.csv".format(n = a)

#Assuming res is a flat list
with open(csvfile, "w") as output:
    writer = csv.writer(output)
    for val in rows:
        writer.writerow(val)

# rows = zip(other_depth_p,other_inten,other_depth_r,other_ante)
# rows = zip(other_depth_p,other_inten,other_depth_r,other_duration_p,other_ante)
#rows = zip(p_other_years,p_other_months,p_other_days,p_other_depth)
# csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Spring2018\\HYD 592\\Data2_g{n}.csv".format(n = a)
rows = zip(other_depth_p,other_inten,other_depth_r)
csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Summer2018\\Chapter 3\\unit source\\Data2_g{n}.csv".format(n = a)

#Assuming res is a flat list
with open(csvfile, "w") as output:
    writer = csv.writer(output)
    for val in rows:
        writer.writerow(val)

#------------------------------------------------------------
#------------------------------------------------------------
# for various antecedent conditions for PRISM
import csv
#specify the antecedent days

#PRISM for the rear data
years = []
months = []
days = []
depth = []
# with open('C:\\Users\\Esther\\Desktop\\NMTer-Spring2018\\MATH 582\\Term Project\\Data\\31.csv') as csvDataFile:
with open('H:\\Observations\\Precip_Anal_2\\data\\70mm.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        years.append(int(row[2]))
        months.append(int(row[0]))
        days.append(int(row[1]))
        depth.append(float(row[3]))

# calculate the individual depth
ind_depth = [depth[0]]
for i in range(len(depth)-1):
    pd = depth[i + 1] - depth[i]
    ind_depth.append(pd)
a = 7

# create antecedent rainfall condition
antecedent = []
for i in range(len(ind_depth)-a-1):
    antecedent.append(sum(ind_depth[i:i+a]))

#variables for monsoon season
p_monsoon_years = []
p_monsoon_months = []
p_monsoon_days = []
p_monsoon_depth = []
p_monsoon_ante = []

#variables for non-monsoon season
p_other_years = []
p_other_months = []
p_other_days = []
p_other_depth = []
p_other_ante = []

#calculate separate depth
for i in range(a,len(years)-1,1): #here is a because python starts at 0
    if months[i] == 6 or months[i] == 7 or months[i] == 8 or months[i] == 9:
        p_monsoon_years.append(int(years[i]))
        p_monsoon_months.append(int(months[i]))
        p_monsoon_days.append(int(days[i]))
        p_monsoon_depth.append(float(ind_depth[i]))
        p_monsoon_ante.append(antecedent[i - a])
    else:
        p_other_years.append(int(years[i]))
        p_other_months.append(int(months[i]))
        p_other_days.append(int(days[i]))
        p_other_depth.append(float(ind_depth[i]))
        p_other_ante.append(antecedent[i - a])

rows = zip(p_monsoon_years,p_monsoon_months,p_monsoon_days,p_monsoon_depth,p_monsoon_ante)
csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Spring2018\\HYD 592\\monsoon_ante{n}.csv".format(n = a)
#Assuming res is a flat list
with open(csvfile, "w") as output:
    writer = csv.writer(output)
    for val in rows:
        writer.writerow(val)
rows = zip(p_other_years,p_other_months,p_other_days,p_other_depth,p_other_ante)
csvfile = "C:\\Users\\Esther\\Desktop\\NMTer-Spring2018\\HYD 592\\other_ante{n}.csv".format(n = a)
#Assuming res is a flat list
with open(csvfile, "w") as output:
    writer = csv.writer(output)
    for val in rows:
        writer.writerow(val)

