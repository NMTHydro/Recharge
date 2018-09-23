# ===============================================================================
# Copyright 2016 gabe-parrish
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

# ============= standard library imports ========================
import os
import pandas as pd
import numpy as np
import datetime
from matplotlib import pyplot as plt
from datetime import datetime

# ============= local library imports ===========================

# =================================== run() exclusive functions =============================================

def plot_depths(dates, d30, d60, d90, d110, d130, name, tdate, rzsm, taw, pixel):
    """"""

    figure_title = "rzsm_5_depths_{}_TAW_{}_pixel_{}".format(name, taw, pixel)

    fig = plt.figure()
    fig.suptitle("Soil moisture at different depths for {} at TAW = {} corr to pixel {}".format(name, taw, pixel), fontsize=12, fontweight='bold')
    plt.rcParams['axes.grid'] = True

    p30 = fig.add_subplot(511)
    p30.set_title("30cm depth", fontsize=10, fontweight='bold')
    # p30.set_xlabel('date', fontsize=8)
    p30.set_ylabel('swc')
    p30.plot(dates, d30, linewidth=1)
    p30.plot(tdate, rzsm, linewidth=1)
    p30.plot_date(dates, d30, marker='o', markersize=2)

    p60 = fig.add_subplot(512)
    p60.set_title("60cm depth", fontsize=10, fontweight='bold')
    # p60.set_xlabel('date', fontsize=8)
    p60.set_ylabel('swc')
    p60.plot(dates, d60, linewidth=1)
    p60.plot(tdate, rzsm, linewidth=1)
    p60.plot_date(dates, d60, marker='o', markersize=2)

    p90 = fig.add_subplot(513)
    p90.set_title("90cm depth", fontsize=10, fontweight='bold')
    # p90.set_xlabel('date', fontsize=8)
    p90.set_ylabel('swc')
    p90.plot(dates, d90, linewidth=1)
    p90.plot(tdate, rzsm, linewidth=1)
    p90.plot_date(dates, d90, marker='o', markersize=2)


    p110 = fig.add_subplot(514)
    p110.set_title("110cm depth", fontsize=10, fontweight='bold')
    # p110.set_xlabel('date', fontsize=8)
    p110.set_ylabel('swc')
    p110.plot(dates, d110, linewidth=1)
    p110.plot(tdate, rzsm, linewidth=1)
    p110.plot_date(dates, d110, marker='o', markersize=2)
    # p110.grid()

    p130 = fig.add_subplot(515)
    p130.set_title("130cm depth", fontsize=10, fontweight='bold')
    # p130.set_xlabel('date', fontsize=8)
    p130.set_ylabel('swc')
    p130.plot(dates, d130, linewidth=1)
    p130.plot(tdate, rzsm, linewidth=1)
    p130.plot_date(dates, d130, marker='o', markersize=2)
    # p130.grid()

    # plt.tight_layout()
    # plt.subplots_adjust(top=0.89)
    plt.subplots_adjust(hspace=.5)


    # plt.show()

    plt.savefig("/Users/Gabe/Desktop/juliet_stuff/jornada_plot_output/{}.pdf".format(figure_title))

    plt.close(fig)

def make_set(df):
    """"""

    location_list = []
    locations = df['location']

    for i in locations:
        # print "location", i
        if i.startswith("C"):
            location_list.append(i)

    location_set = set(location_list)
    # print "the location set", location_set

    ## for str in ["DRY", "WET", "STD"]:
    ##     location_set.remove(str)

    return location_set

def build_jornada_etrm():
    """"""
    relate_dict = {"000": ["C01", "C02"], "001": ["C03", "C04", "C05", "C06", "C07", "C08", "C09"],
                   "002": ["C10", "C11"], "003": ["C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21"],
                   "004": ["C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29"],
                   "005": ["C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39"],
                   "006": ["C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48"],
                   "007": ["C51", "C52", "C53", "C54", "C55", "C56", "C57"],
                   "008": ["C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66"],
                   "009": ["C67", "C68", "C69", "C70"], "010": ["C71", "C72", "C73", "C74", "C75"],
                   "011": ["C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84"],
                   "012": ["C85", "C86", "C87", "C88", "C89"]}
    jornada_etrm = {}
    for key, value in relate_dict.iteritems():
        if len(value)>0:
            for k in value:
                jornada_etrm[k] = key

    # print "the jornada etrm", jornada_etrm
    return jornada_etrm

def nrml_rzsm(data, df_long):
    """
     Normalize the volumetric soil water content into a RZSM by taking the Min - Max and normalizing on a scale of zero
    to one.

    :param data: A shorter dataset we need to normalize to min and max in order to plot.
    :param df_long: A longer dataset that contains a lower min and higher max than the dataset we end up plotting
    :return: normalized dataset
    """

    print('length of data', len(data))

    print('length of data long', len(df_long))

    # convert from strings to float
    data = [float(i) for i in data]
    data_long = [float(i) for i in df_long]

    # Get min and max from a longer dataset
    ma = max(data_long)
    print("ma", ma)
    mi = min(data_long)
    print("mi", mi)

    # normalized scale
    n0 = 0
    n1 = 1

    # create a new normalized dataset
    nrml_data = [n0 + (value - mi)/(ma - mi) for value in data]
    print("lenght of normalized data", len(nrml_data))

    return nrml_data


def run():
    """
    Get the Jornada data and for each gauge, plot a subplot for a different depth,
    i.e for three depths its a three subplot plot.
    :return:
    """

    # TODO - Make an output text file that records the diff between min and max soil water content for each trans. loc.

    #====== Tracker =======
    # # path to a tracker file
    # tracker_path = "/Users/Gabe/Desktop/juliet_stuff/March_2018_model_runs/taw_295/etrm_tracker_000.csv"

    # # get the main dataframe
    # df_tracker = pd.read_csv(tracker_path)
    # # print "df_tracker\n", df_tracker

    # # we need to get rzsm and dates
    # tdate = pd.to_datetime(df_tracker['Date'])
    # # print 'tdate\n', tdate
    # rzsm = df_tracker['rzsm']
    # # print 'rzsm\n', rzsm

    #====== Jornada =======
    # path to the jornada data
    path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
           "Jornada_012002_transect_soil_water_content_data.csv" # This version has data that goes up through 2015


    df = pd.read_csv(path, header=72) # I have no idea why it works on 72 but whatever.

    # print "the df \n", df
    # print "df['Date'] \n", df['date']

    # filter out missing data "."
    df = df[df['swc_30cm'] != "."] #, 'swc_60cm', 'swc_110cm', 'swc_130cm'
    df = df[df['swc_60cm'] != "."]
    df = df[df['swc_90cm'] != "."]
    df = df[df['swc_110cm'] != "."]
    df = df[df['swc_130cm'] != "."]

    # # Cut off extraneous dates we don't need...
    df_long = df[df.index > 15000] # 32000 <- use for plotting
    df = df[df.index > 32000]

    # +=+=+=+=+=+= Automatic Plotter mode +=+=+=+=+=+=

    # set TAW
    taw = 115

    # set tracker path
    tracker_path = "/Users/Gabe/Desktop/juliet_stuff/March_2018_model_runs/taw_{}".format(taw)

    # print tracker_path
    tracker_path_dict = {}
    for path, directories, files in os.walk(tracker_path):
        for i in files:
            # print "file -> ", i
            if len(i) == 20:
                name = i[13:-4]
            else:
                name = i[13:-9]
            # print "name", name

            csv_path = os.path.join(path, i)
            tracker_path_dict[name] = csv_path

    print("tracker path dictionary \n", tracker_path_dict['001'])

    # Build the jornada ETRM dictionary relating every transect measurement point to a ETRM pixel.
    jornada_etrm = build_jornada_etrm() #location_set, tracker_path_dict

    # TODO - MIN MAX output function

    # create a file at a place

    min_max_path = "/Users/Gabe/Desktop/juliet_stuff/March_2018_model_runs/min_max.txt"

    with open(min_max_path, "w") as created_file:
        created_file.write("\n -------------- \n MIN and MAX volumetric soil moisture for Jornada neutron probe data"
                           " \n -------------- \n")

    # within the loop open the file in append mode (a)

    for key, value in jornada_etrm.iteritems():
        print("key -> ", key)
        print("value -> ", value)

        #===== TRACKER ======
        df_tracker = pd.read_csv(tracker_path_dict[value])

        # we need to get rzsm and dates
        tdate = pd.to_datetime(df_tracker['Date'])
        # print 'tdate\n', tdate
        rzsm = df_tracker['rzsm']
        # print 'rzsm\n', rzsm

        pixel = value

        # ===== Jornada ========

        jornada_var = df[df['location'] == key]

        # a long version of the jornada dataset to get a more accurate min and max from the whole dataset to perform
        # the normalization with
        jornada_var_long = df_long[df_long['location'] == key]


        # ===== Append min and max to min_max.txt ========

        # write out the key and value, key = probe, value = pixel
        with open(min_max_path, 'a') as append_file:
            append_file.write(" \n ====== \n probe {} / pixel {} \n====== \n".format(key, value))

        # deal with all the separate depths and report them separately
        list_of_codes = ['swc_30cm', 'swc_60cm', 'swc_90cm', 'swc_110cm', 'swc_130cm']

        for code in list_of_codes:
            jor_var_long = jornada_var_long[code]

            jor_var_long = [float(i) for i in jor_var_long]

            # Get min and max from a longer dataset
            ma = max(jor_var_long)
            mi = min(jor_var_long)

            diff = ma - mi

            # write the min and max underneath a code in the min_max.txt code

            with open(min_max_path, 'a') as append_file:
                append_file.write("\n ****** \n depth: {} \n min: {} \n max: {} "
                                  "\n diff btwn max and min: {} \n \n".format(code, ma, mi, diff))

        # ===== Depths ========

        # 30 cm depth
        j_30 = np.array(nrml_rzsm(jornada_var['swc_30cm'], jornada_var_long['swc_30cm']))
        # convert to a float
        # j_30 = j_30.astype(np.float)

        # 60cm
        j_60 = np.array(nrml_rzsm(jornada_var['swc_60cm'], jornada_var_long['swc_60cm']))
        # j_60 = j_60.astype(np.float)

        # 90cm
        j_90 = np.array(nrml_rzsm(jornada_var['swc_90cm'], jornada_var_long['swc_90cm']))
        # print "here is j_90 -> {}".format(j_90)
        # j_90 = j_90.astype(np.float)

        # 110cm
        j_110 = np.array(nrml_rzsm(jornada_var['swc_110cm'], jornada_var_long['swc_110cm']))
        # j_110 = j_110.astype(np.float)

        # 130cm
        j_130 = np.array(nrml_rzsm(jornada_var['swc_130cm'], jornada_var_long['swc_130cm']))
        # j_130 = j_130.astype(np.float)

        # get the date...
        j_date = pd.to_datetime(jornada_var['date'])

        j_name = key

        plot_depths(j_date, j_30, j_60, j_90, j_110, j_130, j_name, tdate, rzsm, taw, pixel)

        # todo - write a function that builds the jornada_etrm dict you are using for plotting

        # todo - give plot_depths some alternative MODES that allow a comparison with all five depths or just with
        # 30 cm

        # todo - make another plotting function that plots all the associated jornada and etrm pixels together
        # cumulatively on the same figure..

        # todo - make a script that does all the TAWs plotted cummulatively...

# =================================== find_error() exclusive functions =============================================

def nrml_rzsm_for_error(data):
    """
     Normalize the volumetric soil water content into a RZSM by taking the Min - Max and normalizing on a scale of zero
    to one.

    :return: normalized dataset
    """

    print('length of data', len(data))

    print("DATA", data)

    # Get min and max from a long dataset
    ma = max(data)
    print("ma", ma)
    mi = min(data)
    print("mi", mi)

    # normalized scale
    n0 = 0
    n1 = 1

    # create a new normalized dataset
    nrml_data = [n0 + ((value - mi) * (n1 - n0)) / (ma - mi) for value in data]
    print("lenght of normalized data", len(nrml_data))
    print("actual normal data array", nrml_data)

    return nrml_data

def float_data(data):
    data = [float(i) for i in data]
    return data

def depth_average(j_30, j_60, j_90, j_110, j_130):
    """

    :param j_30: time series of 30m vol soil moisture data
    :param j_60: time series of 60m vol soil moisture data
    :param j_90: time series of 90m vol soil moisture data
    :param j_110: time series of 110m vol soil moisture data
    :param j_130: time series of 130m vol soil moisture data
    :return: depth averaged vol soil moisture to be normalized.
    """
    javg_lst = []
    for j3, j6, j9, j11, j13 in zip(j_30, j_60, j_90, j_110, j_130):
        # multiply each probe measurement by a depth weighting term and get the average of all depth weighted values
        # 30cm(0-45), 60cm(45-75), 90cm(75-100), 110cm(100-120), 130cm(120-150) <- Depth weighting of the probes

        print("values {} {} {} {} {}".format(j3, j6, j9, j11, j13))

        # print "numerator", ((j3 * float(45/150)) + (j6 * float(30/150)) + (j9 * float(25/150)) + (j11 * float(20/150)) + (j13 * float(30/150)))
        #
        # print "numerator mod", ((j3) + (j6 ) + (j9) + (j11) + ( j13))
        # print "numerator mod 2", (
        # (j3 * (45)) + (j6 * (30 )) + (j9 * (25)) + (j11 * (20)) + (
        # j13 * float(30)))
        # TODO - Clean this up and make sure d_avg is correct.
        d_avg = ((j3 * (45)) + (j6 * (30)) + (j9 * (25)) + (j11 * (20)) + (j13 * (30))) / 150.0

        # j_avg = ((j3 * float(45/150)) + (j6 * float(30/150)) + (j9 * float(25/150)) + (j11 * float(20/150)) +
        #          (j13 * float(30/150))) / 5.0
        javg_lst.append(d_avg)

    print("j avg list", javg_lst)

    return javg_lst


def find_error():
    """
    1.) depth average all the jornada data
    2.) Convert the soil moisture values into a relative soil moisture condition
    3.) On a per_pixel basis: Get the average, and std deviation and variability
    4.) print that to a textfile or something.
    :return:
    """

    # ====== Jornada =======
    # path to the jornada data
    path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
           "Jornada_012002_transect_soil_water_content_data.csv"  # This version has data that goes up through 2015

    df = pd.read_csv(path, header=72)  # I have no idea why it works on 72 but whatever.

    # print "the df \n", df
    # print "df['Date'] \n", df['date']

    # filter out missing data "."
    df = df[df['swc_30cm'] != "."]  # , 'swc_60cm', 'swc_110cm', 'swc_130cm'
    df = df[df['swc_60cm'] != "."]
    df = df[df['swc_90cm'] != "."]
    df = df[df['swc_110cm'] != "."]
    df = df[df['swc_130cm'] != "."]

    # # Cut off extraneous dates we don't need...
    df_long = df[df.index > 15000]  # 32000 <- use for plotting
    df = df[df.index > 32000]

    # dictionary that relates each pixel to the correct jornada stations.
    relate_dict = {"000": ["C01", "C02"], "001": ["C03", "C04", "C05", "C06", "C07", "C08", "C09"],
                   "002": ["C10", "C11"], "003": ["C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21"],
                   "004": ["C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29"],
                   "005": ["C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39"],
                   "006": ["C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48"],
                   "007": ["C51", "C52", "C53", "C54", "C55", "C56", "C57"],
                   "008": ["C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66"],
                   "009": ["C67", "C68", "C69", "C70"], "010": ["C71", "C72", "C73", "C74", "C75"],
                   "011": ["C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84"],
                   "012": ["C85", "C86", "C87", "C88", "C89"]}

    # dictionary that relates each jornada station to the correct pixel.
    jornada_etrm = build_jornada_etrm()

    # loop through the jornada_etrm dictionary to get the proper Jornada data locations while tracking the ETRM pixel.
    avg_normal_dictionary = {}
    for key, value in jornada_etrm.iteritems():
        # print "key -> ", key
        # print "value -> ", value

        # ===== Jornada ========

        jornada_var = df[df['location'] == key]

        # a long version of the jornada dataset to get a more accurate min and max from the whole dataset to perform
        # the normalization with
        jornada_var_long = df_long[df_long['location'] == key]

        # you only want to use the long jornada var...
        # print "Jornada VAR", jornada_var_long

        # ===== Depths (FIND ERROR) <- Don't normalize the data yet ========

        # 30 cm depth
        j_30 = float_data(jornada_var_long['swc_30cm'])
        # convert to a float
        # j_30 = j_30.astype(np.float)

        # 60cm
        j_60 = float_data(jornada_var_long['swc_60cm'])
        # j_60 = j_60.astype(np.float)

        # 90cm
        j_90 = float_data(jornada_var_long['swc_90cm'])
        # print "here is j_90 -> {}".format(j_90)
        # j_90 = j_90.astype(np.float)

        # 110cm
        j_110 = float_data(jornada_var_long['swc_110cm'])
        # j_110 = j_110.astype(np.float)

        # 130cm
        j_130 = float_data(jornada_var_long['swc_130cm'])
        # j_130 = j_130.astype(np.float)

        # # get the date...
        # j_date = pd.to_datetime(jornada_var['date'])

        j_name = key

        # depth average
        j_avg = depth_average(j_30, j_60, j_90, j_110, j_130)

        # normalize
        jornada_avg_nrml = nrml_rzsm_for_error(j_avg)

        # print "length of the depth avg {}".format(len(jornada_avg_nrml))

        # add the normalized depth averaged value for each location into a new dictionary:
        avg_normal_dictionary[key] = jornada_avg_nrml

    # now we need to go through the relate dict to get the sigma, variability and average for each ETRM pixel
    # print "relate dict \n {}".format(relate_dict)
    # print "average_normal_dict \n {}".format(avg_normal_dictionary)

    related_stats_dict = {}
    for key, value in relate_dict.iteritems():
        if len(value) > 0:
            _loc_dict = {}
            for loc in value:
                # the depth averaged, normalized, time series for a given location
                avg_nrml = np.array(avg_normal_dictionary[loc])
                # the location average
                loc_avg = np.average(avg_nrml)
                # print "location {}'s average -> {}".format(loc, loc_avg)
                # the location variance
                loc_var = np.var(avg_nrml)
                # print "location {}'s variance -> {}".format(loc, loc_var)
                # the location std dev
                loc_std = np.std(avg_nrml)
                # print "location {}'s std deviatin -> {}".format(loc, loc_std)
                stats = (loc_avg, loc_var, loc_std)

                _loc_dict[loc] = stats

            related_stats_dict[key] = _loc_dict

    print("updated related statistics dictionary \n {}".format(related_stats_dict))


    ### find the Standard error of the mean for each pixel
    std_err_dict = {}
    for key, value in related_stats_dict.iteritems():
        print("pixel {}".format(key))

        # start a count to count the tubes in a given pixel.
        num_tubes = 0
        # ned to capture the averages
        tube_avgs = []
        for k, v in value.iteritems():

            # add the average into the list
            tube_avgs.append(v[0])

            # count the tube
            num_tubes += 1

        # take the standard deviation of the tube averages
        tube_avgs = np.array(tube_avgs)
        tube_std = np.std(tube_avgs)

        # std error of the mean

        sem = tube_std/(float(num_tubes) ** (1/2))

        # add to dictionary
        std_err_dict[key] = sem


    ### find the average of averages for each pixel
    avg_of_avgs = {}
    for key, value in related_stats_dict.iteritems():

        # start a count to count the tubes in a given pixel.
        num_tubes = 0
        # ned to capture the averages
        tube_avgs = []

        for k, v in value.iteritems():
            # add the average into the list
            tube_avgs.append(v[0])

            # count the tube
            num_tubes += 1

        # add up the tube averages

        sum_avgs = np.array(tube_avgs)
        sum_avgs = np.sum(sum_avgs)


        # divide by the number of tubes

        avg_avg = sum_avgs/float(num_tubes)

        # add to dictionary

        avg_of_avgs[key] = avg_avg



    # +=+=+=+=+=+=+=+=+=+=+=+= AGGREGATE and OUTPUT +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

    # create a file at a place

    stats_output_path = "/Users/Gabe/Desktop/juliet_stuff/March_2018_model_runs/stats_output_250m.txt"

    with open(stats_output_path, "w") as created_file:
        created_file.write("\n ------------------------------------- \n "
                           "AVG, VARIANCE and STD DEV for Jornada neutron probe data"
                           " \n ------------------------------------- \n")

    for key, value in related_stats_dict.iteritems():

        with open(stats_output_path, 'a') as append_file:
            append_file.write("\n \n \n ****** \n STATS for PIXEL {} \n ******  \n \n ".format(key))


        for k, v in value.iteritems():
            with open(stats_output_path, 'a') as append_file:
                append_file.write("\n \n === \n LOCATION {} \n ===  \n \
                 \n time_depth_average {} \n variance_depth_average {} \n"
                                  " std_dev_depth_average {} ".format(k, v[0], v[1], v[2]))

    with open(stats_output_path, "a") as append_file:
        append_file.write("\n \n \n ----------------------------------------------"
                          " \n Standard Error of the Mean per ETRM Pixel "
                          "\n ---------------------------------------------- \n")

    for key, value in std_err_dict.iteritems():

        with open(stats_output_path, 'a') as append_file:
            append_file.write("\n \n ****** \n STD ERR for PIXEL {} is -> {} \n ******  \n \n ".format(key, value))

    with open(stats_output_path, "a") as append_file:
        append_file.write("\n \n \n ----------------------------------------------"
                          " \n Average of Averages for each pixel"
                          "\n ---------------------------------------------- \n")

    for key, value in avg_of_avgs.iteritems():

        with open(stats_output_path, 'a') as append_file:
            append_file.write("\n \n ****** \n AVG of AVGs for PIXEL {} is -> {} \n ******  \n \n ".format(key, value))

# =================================== storage_plot() exclusive functions =============================================
def plot_storage(total_storage, taw, dates, j_name, mi, ma, tdate, rzsm, pixel, etrm_taw):
    """"""
    # fig, ax = plt.subplots(figsize=(6,6))
    #
    # print "fig {}".format(fig)
    # print "ax {}".format(ax)
    rel_storage = [(storage-mi)/taw for storage in total_storage]
    # for storage in total_storage:
    #     storage/taw

    figure_title = "Relative Storage_location-{}_taw-{}_pixel-{}".format(j_name, etrm_taw, pixel)

    fig = plt.figure()
    # fig.suptitle("Soil moisture at different depths for {} at TAW = {} corr to pixel {}".format(name, taw, pixel), fontsize=12, fontweight='bold')
    plt.rcParams['axes.grid'] = True

    aa = fig.add_subplot(111)
    aa.set_title("Root Zone Water Fraction for a total 150 cm depth: location-{}, "
                 "taw-{}, pixel- {}".format(j_name, etrm_taw, pixel), fontsize=10, fontweight='bold')
    aa.set_xlabel('date', fontsize=12)
    aa.set_ylabel('RZWF', fontsize = 12) #= (storage - minimum storage)/(max storage - min storage)
    aa.plot(dates, rel_storage, linewidth=2)
    aa.plot(tdate, rzsm, linewidth=2)
    aa.plot_date(dates, rel_storage, marker='o', markersize=4)

    # change the axes
    plt.xlim(datetime.strptime("01/01/2000", "%m/%d/%Y"), datetime.strptime("01/01/2012", "%m/%d/%Y"))

    plt.tight_layout()
    # plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=.7, wspace=0.2, hspace=0.2)
    # plt.subplots_adjust(top=.85)

    # plt.show()

    plt.savefig("/Users/Gabe/Desktop/juliet_stuff/jornada_plot_output/{}.pdf".format(figure_title))

    plt.close(fig)

def calc_storage(j_30, j_60, j_90, j_110, j_130):
    """

    :param j_30:
    :param j_60:
    :param j_90:
    :param j_110:
    :param j_130:
    :return:
    """
    j_storage_lst = []
    for j3, j6, j9, j11, j13 in zip(j_30, j_60, j_90, j_110, j_130):
        # multiply each probe vol soil moisture measurement by a depth
        # 30cm(0-45), 60cm(45-75), 90cm(75-100), 110cm(100-120), 130cm(120-150) <- Depth weighting of the probes
        storage = ((j3 * (45)) + (j6 * (30)) + (j9 * (25)) + (j11 * (20)) + (j13 * (30)))
        j_storage_lst.append(storage)

    # print "values {} {} {} {} {}".format(j3, j6, j9, j11, j13)

    # print "list of storage -> {}".format(j_storage_lst)

    return j_storage_lst


def storage_plot():
    """
    1.) storage in each layer [theta * depth o' layer] <- time series
    2.) Add up storages to get TOTAL STORAGE <- time series
    3.) Get max and min of TOTAL STORAGE time series --> Max-Min = TAW
    4.) Plot storage/TAW over time for each location
    5.) Plot TAW over distance along transect
    :return:
    """
    # ====== Jornada =======
    # path to the jornada data
    path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
           "Jornada_012002_transect_soil_water_content_data.csv"  # This version has data that goes up through 2015

    df = pd.read_csv(path, header=72)  # I have no idea why it works on 72 but whatever.

    # print "the df \n", df
    # print "df['Date'] \n", df['date']

    # filter out missing data "."
    df = df[df['swc_30cm'] != "."]  # , 'swc_60cm', 'swc_110cm', 'swc_130cm'
    df = df[df['swc_60cm'] != "."]
    df = df[df['swc_90cm'] != "."]
    df = df[df['swc_110cm'] != "."]
    df = df[df['swc_130cm'] != "."]

    # # Cut off extraneous dates we don't need...
    df_long = df[df.index > 15000]  # 32000 <- use for plotting
    df = df[df.index > 32000]

    # +=+=+=+=+=+= Automatic Plotter mode +=+=+=+=+=+=

    # set TAW
    etrm_taw = 70

    # set tracker path
    tracker_path = "/Users/Gabe/Desktop/juliet_stuff/March_2018_model_runs/taw_{}".format(etrm_taw)

    # print tracker_path
    tracker_path_dict = {}
    for path, directories, files in os.walk(tracker_path):
        for i in files:
            # print "file -> ", i
            if len(i) == 20:
                name = i[13:-4]
            else:
                name = i[13:-9]
            # print "name", name

            csv_path = os.path.join(path, i)
            tracker_path_dict[name] = csv_path

    # dictionary that relates each jornada station to the correct pixel.
    jornada_etrm = build_jornada_etrm()

    # loop through the jornada_etrm dictionary to get the proper Jornada data locations while tracking the ETRM pixel.
    storage_taw_dict = {}
    for key, value in jornada_etrm.iteritems():
        # print "key -> ", key
        # print "value -> ", value

        # ===== Jornada ========

        jornada_var = df[df['location'] == key]

        # a long version of the jornada dataset to get a more accurate min and max from the whole dataset to perform
        # the normalization with
        jornada_var_long = df_long[df_long['location'] == key]

        # you only want to use the long jornada var...
        # print "Jornada VAR", jornada_var_long

        # ===== TRACKER ======
        df_tracker = pd.read_csv(tracker_path_dict[value])

        # we need to get rzsm and dates
        tdate = pd.to_datetime(df_tracker['Date'])
        # print 'tdate\n', tdate
        rzsm = df_tracker['rzsm']
        # print 'rzsm\n', rzsm

        pixel = value

        # ===== Depths (plot storage) ========

        # 30 cm depth
        j_30 = float_data(jornada_var_long['swc_30cm'])
        # 60cm
        j_60 = float_data(jornada_var_long['swc_60cm'])
        # 90cm
        j_90 = float_data(jornada_var_long['swc_90cm'])
        # 110cm
        j_110 = float_data(jornada_var_long['swc_110cm'])
        # 130cm
        j_130 = float_data(jornada_var_long['swc_130cm'])

        # get the date...
        j_date = pd.to_datetime(jornada_var_long['date'])

        j_name = key

        # time series of storage
        total_storage = calc_storage(j_30, j_60, j_90, j_110, j_130)

        # get the TAW
        # minimum
        mi = min(total_storage)
        print("this is the min {}".format(mi))
        # maximum
        ma = max(total_storage)
        print("this is the max {}".format(ma))
        taw = ma - mi

        print("This is the TAW {}".format(taw))

        # storage_taw_dict[key] = (total_storage, taw)

        plot_storage(total_storage, taw, j_date, j_name, mi, ma, tdate, rzsm, pixel, etrm_taw)


    # print "total storage and taw dictionary -> {}".format(storage_taw_dict)

# ========================= storage_plot_mod() exclusive functions =============================

def plot_storage_simple(dates, storage, storage_name, loc):

    figure_title = "Storage for location - {} for assumed Storage Depth - {}".format(loc, storage_name)

    fig = plt.figure()
    # fig.suptitle("Soil moisture at different depths for {} at TAW = {} corr to pixel {}".format(name, taw, pixel), fontsize=12, fontweight='bold')
    plt.rcParams['axes.grid'] = True

    aa = fig.add_subplot(111)
    aa.set_title(figure_title, fontsize=10, fontweight='bold')
    aa.set_xlabel('date', fontsize=12)
    aa.set_ylabel('Storage cm', fontsize=12)  # = (storage - minimum storage)/(max storage - min storage)
    aa.plot(dates, storage, linewidth=2)
    aa.plot_date(dates, storage, marker='o', markersize=4)

    # # change the axes
    # plt.xlim(datetime.strptime("01/01/2000", "%m/%d/%Y"), datetime.strptime("01/01/2012", "%m/%d/%Y"))

    plt.tight_layout()
    # plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=.7, wspace=0.2, hspace=0.2)
    # plt.subplots_adjust(top=.85)
    plt.show()

def calc_storage_mod(swc):
    """

    :param swc:
    :return:
    """

    depths = ('30', '60', '90', '110', '130')

    depth_vals = {}
    for d in depths:
        moisture_depth = swc['swc_{}cm'.format(d)]
        depth_vals[d] = moisture_depth

    # print "Depth vals dict \n {}".format(depth_vals)

    lifts = (45.0, 30.0, 25.0, 20.0, 25.0)

    # get 30 cm storage
    stor_30 = np.array(float_data(depth_vals['30'])) * lifts[0]

    # get 60cm storage
    stor_60 = 0
    for i in range(0, 2):
        stor_60 += np.array(float_data(depth_vals[depths[i]])) * lifts[i]

    # get 90 cm storage
    stor_90 = 0
    for i in range(0, 3):
        stor_90 += np.array(float_data(depth_vals[depths[i]])) * lifts[i]

    # get 110 cm storage
    stor_110 = 0
    for i in range(0, 4):
        stor_110 += np.array(float_data(depth_vals[depths[i]])) * lifts[i]

    # get 130 cm storage
    stor_130 = 0
    for i in range(0, 5):
        stor_130 += np.array(float_data(depth_vals[depths[i]])) * lifts[i]

    return [stor_30, stor_60, stor_90, stor_110, stor_130]


def storage_plot_mod():
    """

    :return:
    """
    # ====== Jornada =======
    # path to the jornada data
    path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
           "Jornada_012002_transect_soil_water_content_data.csv"  # This version has data that goes up through 2015

    df = pd.read_csv(path, header=72)  # I have no idea why it works on 72 but whatever.

    # print "the df \n", df
    # print "df['Date'] \n", df['date']

    # filter out missing data "."
    df = df[df['swc_30cm'] != "."]  # , 'swc_60cm', 'swc_110cm', 'swc_130cm'
    df = df[df['swc_60cm'] != "."]
    df = df[df['swc_90cm'] != "."]
    df = df[df['swc_110cm'] != "."]
    df = df[df['swc_130cm'] != "."]

    # # Cut off extraneous dates we don't need...
    df_long = df[df.index > 15000]  # 32000 <- use for plotting
    df = df[df.index > 32000]

    for i in range(1, 90):
        key = "C{:02d}".format(i)
        # print "Key {}".format(key)

        swc = df_long[df_long['location'] == key]
        print("SWC \n", swc)

        # get five sets of storages from the swc measurements for each tube...
        storages = calc_storage_mod(swc)
        storage_names = ['stor_30', 'stor_60', 'stor_90', 'stor_110', 'stor_130']

        # to plot, link up the storages with the dates...
        dates = pd.to_datetime(swc['date'])

        for storage, name in zip(storages, storage_names):

            plot_storage_simple(dates, storage, name, key)

        # TODO 1) Set up to plot all three storages on the same plot

        # TODO 2) Set up to plot ETrF alongside the storages...(seems like it could be involved).





# # =================================== find_std_error() exclusive functions =============================================
#
# def nrml_rzsm_for_error(data):
#     """
#      Normalize the volumetric soil water content into a RZSM by taking the Min - Max and normalizing on a scale of zero
#     to one.
#
#     :return: normalized dataset
#     """
#
#     # print 'length of data', len(data)
#     #
#     # print "DATA", data
#
#     # Get min and max from a long dataset
#     ma = max(data)
#     # print "ma", ma
#     mi = min(data)
#     # print "mi", mi
#
#     # normalized scale
#     n0 = 0
#     n1 = 1
#
#     # create a new normalized dataset
#     nrml_data = [n0 + ((value - mi) * (n1 - n0)) / (ma - mi) for value in data]
#     # print "lenght of normalized data", len(nrml_data)
#     # print "actual normal data array", nrml_data
#
#     return nrml_data
#
# def float_data(data):
#     data = [float(i) for i in data]
#     return data
#
# def depth_average(j_30, j_60, j_90, j_110, j_130):
#     """
#
#     :param j_30: time series of 30m vol soil moisture data
#     :param j_60: time series of 60m vol soil moisture data
#     :param j_90: time series of 90m vol soil moisture data
#     :param j_110: time series of 110m vol soil moisture data
#     :param j_130: time series of 130m vol soil moisture data
#     :return: depth averaged vol soil moisture to be normalized.
#     """
#     javg_lst = []
#     for j3, j6, j9, j11, j13 in zip(j_30, j_60, j_90, j_110, j_130):
#         # multiply each probe measurement by a depth weighting term and get the average of all depth weighted values
#         # 30cm(0-45), 60cm(45-75), 90cm(75-100), 110cm(100-120), 130cm(120-150) <- Depth weighting of the probes
#
#         # print "values {} {} {} {} {}".format(j3, j6, j9, j11, j13)
#
#         # print "numerator", ((j3 * float(45/150)) + (j6 * float(30/150)) + (j9 * float(25/150)) + (j11 * float(20/150)) + (j13 * float(30/150)))
#         #
#         # print "numerator mod", ((j3) + (j6 ) + (j9) + (j11) + ( j13))
#         # print "numerator mod 2", (
#         # (j3 * (45)) + (j6 * (30 )) + (j9 * (25)) + (j11 * (20)) + (
#         # j13 * float(30)))
#         # TODO - Clean this up and make sure d_avg is correct.
#         d_avg = ((j3 * (45)) + (j6 * (30)) + (j9 * (25)) + (j11 * (20)) + (j13 * (30))) / 150.0
#
#         # j_avg = ((j3 * float(45/150)) + (j6 * float(30/150)) + (j9 * float(25/150)) + (j11 * float(20/150)) +
#         #          (j13 * float(30/150))) / 5.0
#         javg_lst.append(d_avg)
#
#     # print "j avg list", javg_lst
#
#     return javg_lst
#
#
# def find_std_error():
#     """
#     1.) depth average all the jornada data
#     2.) Convert the soil moisture values into a relative soil moisture condition
#     3.) On a per_pixel basis: Get the average, and std deviation and variability
#     4.) print that to a csv
#     :return:
#     """
#
#     # TODO - Write a routine to format the dataframe into
#
#     # ====== Jornada =======
#     # path to the jornada data
#     path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
#            "Jornada_012002_transect_soil_water_content_data.csv"  # This version has data that goes up through 2015
#
#     df = pd.read_csv(path, header=72)  # I have no idea why it works on 72 but whatever.
#
#     # print "the df \n", df
#     # print "df['Date'] \n", df['date']
#
#     # filter out missing data "."
#     df = df[df.swc_30cm != "."]  # , 'swc_60cm', 'swc_110cm', 'swc_130cm' | df.swc_60cm | df.swc_90cm | df.swc_110cm | df.swc_130cm
#     df = df[df.swc_60cm != "."]
#     df = df[df.swc_90cm != "."]
#     df = df[df.swc_110cm != "."]
#     df = df[df.swc_130cm != "."]
#
#     # # Cut off extraneous dates we don't need...
#     df_long = df[df.index > 15000]  # 32000 <- use for plotting
#     # df = df[df.index > 32000]
#     # df_long = df_long[df_long.index < 15250]
#
#     # testing to see why the datasets at each location are different lengths...
#
#     testpath = "/Users/Gabe/Desktop/test_water_content_data.csv"
#
#     df_long.to_csv(testpath)
#
#     # dictionary that relates each pixel to the correct jornada stations.
#     relate_dict = {"000": ["C01", "C02"], "001": ["C03", "C04", "C05", "C06", "C07", "C08", "C09"],
#                    "002": ["C10", "C11"], "003": ["C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21"],
#                    "004": ["C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29"],
#                    "005": ["C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39"],
#                    "006": ["C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48"],
#                    "007": ["C51", "C52", "C53", "C54", "C55", "C56", "C57"],
#                    "008": ["C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66"],
#                    "009": ["C67", "C68", "C69", "C70"], "010": ["C71", "C72", "C73", "C74", "C75"],
#                    "011": ["C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84"],
#                    "012": ["C85", "C86", "C87", "C88", "C89"]}
#
#     # dictionary that relates each jornada station to the correct pixel.
#     jornada_etrm = build_jornada_etrm()
#
#     # loop through the jornada_etrm dictionary to get the proper Jornada data locations while tracking the ETRM pixel.
#     avg_normal_dictionary = {}
#     for key, value in jornada_etrm.iteritems():
#         # print "key -> ", key
#         # print "value -> ", value
#
#         # ===== Jornada ========
#
#         jornada_var = df[df['location'] == key]
#
#         # a long version of the jornada dataset to get a more accurate min and max from the whole dataset to perform
#         # the normalization with
#         jornada_var_long = df_long[df_long['location'] == key]
#
#         print "length jornada var long {}, key {}".format(len(jornada_var_long), key)
#
#         # you only want to use the long jornada var...
#         # print "Jornada VAR", jornada_var_long
#
#         # ===== Depths (FIND ERROR) <- Don't normalize the data yet ========
#
#         # 30 cm depth
#         j_30 = float_data(jornada_var_long['swc_30cm'])
#         print "len j_30", len(j_30)
#         # convert to a float
#         # j_30 = j_30.astype(np.float)
#
#         # 60cm
#         j_60 = float_data(jornada_var_long['swc_60cm'])
#         print "len j_60", len(j_60)
#         # j_60 = j_60.astype(np.float)
#
#         # 90cm
#         j_90 = float_data(jornada_var_long['swc_90cm'])
#         print "len j_90", len(j_90)
#         # print "here is j_90 -> {}".format(j_90)
#         # j_90 = j_90.astype(np.float)
#
#         # 110cm
#         j_110 = float_data(jornada_var_long['swc_110cm'])
#         print "len j_110", len(j_110)
#         # j_110 = j_110.astype(np.float)
#
#         # 130cm
#         j_130 = float_data(jornada_var_long['swc_130cm'])
#         print "len j_130", len(j_130)
#         # j_130 = j_130.astype(np.float)
#
#         # get the date...
#         j_date = pd.to_datetime(jornada_var['date'])
#
#         # print "THE DATE \n {}".format(j_date)
#
#         # depth average
#         j_avg = depth_average(j_30, j_60, j_90, j_110, j_130)
#
#         # normalize
#         jornada_avg_nrml = nrml_rzsm_for_error(j_avg)
#
#         # print "length of the depth avg {}".format(len(jornada_avg_nrml))
#
#         # add the normalized depth averaged value for each location into a new dictionary:
#         avg_normal_dictionary[key] = jornada_avg_nrml
#
#         avg_normal_dictionary['date'] = j_date
#
#     # now we need to go through the relate dict to get the sigma, variability and average for each ETRM pixel
#     # print "relate dict \n {}".format(relate_dict)
#     # print "average_normal_dict \n {}".format(avg_normal_dictionary)
#
#
#
#     depth_avg_time_series = {}
#     for key, value in relate_dict.iteritems():
#         if len(value) > 0:
#             _loc_dict = {}
#             for loc in value:
#                 # the depth averaged, normalized, time series for a given location
#                 avg_nrml = np.array(avg_normal_dictionary[loc])
#
#                 # add the time series to a dictionary
#                 _loc_dict[loc] = avg_nrml
#
#             depth_avg_time_series[key] = _loc_dict
#
#     # print "updated related statistics dictionary \n {}".format(depth_avg_time_series)
#     #
#     #
#     # ### find the Standard error of the mean for each pixel
#
#     std_error_d = {}
#     # key_lst = []
#     sum_lst = []
#     for key, value in depth_avg_time_series.iteritems():
#
#         # print "key", key
#         #
#         # print "value", value
#
#         arr_lst = []
#
#         for k, v in value.iteritems():
#             if len(arr_lst) == 0:
#                 print "k first", k
#                 print 'v first', v
#                 print "first time!"
#                 arr_lst = v
#                 print "length first time {}".format(len(arr_lst))
#             else:
#                 print "k", k
#                 print "v", v
#                 print "len v", len(v)
#                 prev_list = arr_lst
#                 arr_lst = v + prev_list
#
#         print "summed list for key {} and list is \n {}".format(key, arr_lst)
#         std_error_d[key] = arr_lst
#
#     print "final sum dictionary {}".format(std_error_d)
#
#
#
#
#     #
#     # ### find the average of averages for each pixel
#
#
#
#     # +=+=+=+=+=+=+=+=+=+=+=+= AGGREGATE and OUTPUT +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=



if __name__ == "__main__":

    # # this will generate depth plots of ETRM and Jornada data and rzsm theta estimates
    # run()

    # # this outputs a text_file indicating the uncertainty of the RZSM for each pixel.
    # find_error()

    # # this will output plots of the relative storage for the Jornada tubes.
    # storage_plot()

    # this will output plots of the storage for the Jornada tubes at different storage levels
    storage_plot_mod()

    # # this outputs a csv of the running avg(depth_average) and standard error of the mean for each pixel.
    # find_std_error()