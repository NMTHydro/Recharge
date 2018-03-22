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

# ============= local library imports ===========================


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
    relate_dict = {"000":["C01", "C02"] ,"001": ["C03", "C04", "C05", "C06", "C07", "C08", "C09"],
                   "002":["C10", "C11"], "003":["C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21"],
                   "004":["C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29"],
                   "005":[] , "006":[], "007":[], "008":[] , "009":[], "010":[], "011":[],
                   "012":["C85", "C86", "C87", "C88", "C89"]}
    jornada_etrm = {}
    for key, value in relate_dict.iteritems():
        if len(value)>0:
            for k in value:
                jornada_etrm[k] = key

    print "the jornada etrm", jornada_etrm
    return jornada_etrm

def nrml_rzsm(data, df_long):
    """
     Normalize the volumetric soil water content into a RZSM by taking the Min - Max and normalizing on a scale of zero
    to one.

    :param data: A shorter dataset we need to normalize to min and max in order to plot.
    :param df_long: A longer dataset that contains a lower min and higher max than the dataset we end up plotting
    :return: normalized dataset
    """

    print 'length of data', len(data)

    print 'length of data long', len(df_long)

    # convert from strings to float
    data = [float(i) for i in data]
    data_long = [float(i) for i in df_long]

    # Get min and max from a longer dataset
    ma = max(data_long)
    print "ma", ma
    mi = min(data_long)
    print "mi", mi

    # normalized scale
    n0 = 0
    n1 = 1

    # create a new normalized dataset
    nrml_data = [n0 + (value - mi)/(ma - mi) for value in data]
    print "lenght of normalized data", len(nrml_data)

    return nrml_data

def run():
    """
    Get the Jornada data and for each gauge, plot a subplot for a different depth,
    i.e for three depths its a three subplot plot.
    :return:
    """

    # TODO - Make an output text file that records the diff between min and max soil water content for each trans. loc.

    #====== Tracker =======
    # path to a tracker file
    tracker_path = "/Users/Gabe/Desktop/juliet_stuff/March_2018_model_runs/taw_295/etrm_tracker_000.csv"

    # get the main dataframe
    df_tracker = pd.read_csv(tracker_path)
    # print "df_tracker\n", df_tracker

    # we need to get rzsm and dates
    tdate = pd.to_datetime(df_tracker['Date'])
    # print 'tdate\n', tdate
    rzsm = df_tracker['rzsm']
    # print 'rzsm\n', rzsm

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

    print "tracker path dictionary \n", tracker_path_dict['001']

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
        print "key -> ", key
        print "value -> ", value

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


if __name__ == "__main__":

    run()