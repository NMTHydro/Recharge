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
def nrml_rzsm_for_error(data):
    """
     Normalize the volumetric soil water content into a RZSM by taking the Min - Max and normalizing on a scale of zero
    to one.

    :return: normalized dataset
    """

    # print 'length of data', len(data)
    #
    # print "DATA", data

    # Get min and max from a long dataset
    ma = max(data)
    # print "ma", ma
    mi = min(data)
    # print "mi", mi

    # normalized scale
    n0 = 0
    n1 = 1

    # create a new normalized dataset
    nrml_data = [n0 + ((value - mi) * (n1 - n0)) / (ma - mi) for value in data]
    # print "lenght of normalized data", len(nrml_data)
    # print "actual normal data array", nrml_data

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

        # print "values {} {} {} {} {}".format(j3, j6, j9, j11, j13)

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

    # print "j avg list", javg_lst

    return javg_lst

def find_std_error():
    """
    1.) depth average all the jornada data
    2.) Convert the soil moisture values into a relative soil moisture condition
    3.) On a per_pixel basis: Get the average, and std deviation and variability
    4.) print that to a csv
    :return:
    """

    # TODO - Write a routine to format the dataframe into

    # ====== Jornada =======
    # path to the jornada data
    path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
           "Jornada_012002_transect_soil_water_content_data.csv"  # This version has data that goes up through 2015

    df = pd.read_csv(path, header=72)  # I have no idea why it works on 72 but whatever.

    # print "the df \n", df
    # print "df['Date'] \n", df['date']

    # filter out missing data "."
    df = df[df.swc_30cm != "."]  # , 'swc_60cm', 'swc_110cm', 'swc_130cm' | df.swc_60cm | df.swc_90cm | df.swc_110cm | df.swc_130cm
    df = df[df.swc_60cm != "."]
    df = df[df.swc_90cm != "."]
    df = df[df.swc_110cm != "."]
    df = df[df.swc_130cm != "."]

    # # Cut off extraneous dates we don't need...
    df_long = df[df.index > 15000]  # 32000 <- use for plotting
    # df = df[df.index > 32000]
    # df_long = df_long[df_long.index < 15250]

    # testing to see why the datasets at each location are different lengths...

    testpath = "/Users/Gabe/Desktop/test_water_content_data.csv"

    df_long.to_csv(testpath)

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

        # print "length jornada var long {}, key {}".format(len(jornada_var_long), key)

        # you only want to use the long jornada var...
        # print "Jornada VAR", jornada_var_long

        # ===== Depths (FIND ERROR) <- Don't normalize the data yet ========

        # 30 cm depth
        j_30 = float_data(jornada_var_long['swc_30cm'])
        print "len j_30", len(j_30)
        # convert to a float
        # j_30 = j_30.astype(np.float)

        # 60cm
        j_60 = float_data(jornada_var_long['swc_60cm'])
        print "len j_60", len(j_60)
        # j_60 = j_60.astype(np.float)

        # 90cm
        j_90 = float_data(jornada_var_long['swc_90cm'])
        print "len j_90", len(j_90)
        # print "here is j_90 -> {}".format(j_90)
        # j_90 = j_90.astype(np.float)

        # 110cm
        j_110 = float_data(jornada_var_long['swc_110cm'])
        print "len j_110", len(j_110)
        # j_110 = j_110.astype(np.float)

        # 130cm
        j_130 = float_data(jornada_var_long['swc_130cm'])
        print "len j_130", len(j_130)
        # j_130 = j_130.astype(np.float)

        # get the date...
        j_date = pd.to_datetime(jornada_var['date'])

        # print "THE DATE \n {}".format(j_date)

        # depth average
        j_avg = depth_average(j_30, j_60, j_90, j_110, j_130)

        # normalize
        jornada_avg_nrml = nrml_rzsm_for_error(j_avg)

        # print "length of the depth avg {}".format(len(jornada_avg_nrml))

        # add the normalized depth averaged value for each location into a new dictionary:
        avg_normal_dictionary[key] = jornada_avg_nrml

        avg_normal_dictionary['date'] = j_date

    # now we need to go through the relate dict to get the sigma, variability and average for each ETRM pixel
    # print "relate dict \n {}".format(relate_dict)
    # print "average_normal_dict \n {}".format(avg_normal_dictionary)



    depth_avg_time_series = {}
    for key, value in relate_dict.iteritems():
        if len(value) > 0:
            _loc_dict = {}
            for loc in value:
                # the depth averaged, normalized, time series for a given location
                avg_nrml = np.array(avg_normal_dictionary[loc])

                # add the time series to a dictionary
                _loc_dict[loc] = avg_nrml

            depth_avg_time_series[key] = _loc_dict

    # print "updated related statistics dictionary \n {}".format(depth_avg_time_series)
    #
    #
    # ### find the Standard error of the mean for each pixel

    std_error_d = {}
    # key_lst = []
    sum_lst = []
    for key, value in depth_avg_time_series.iteritems():

        # print "key", key
        #
        # print "value", value

        arr_lst = []

        for k, v in value.iteritems():
            if len(arr_lst) == 0:
                print "k first", k
                print 'v first', v
                print "first time!"
                arr_lst = v
                print "length first time {}".format(len(arr_lst))
            else:
                print "k", k
                print "v", v
                print "len v", len(v)
                prev_list = arr_lst
                arr_lst = v + prev_list

        print "summed list for key {} and list is \n {}".format(key, arr_lst)
        std_error_d[key] = arr_lst

    print "final sum dictionary {}".format(std_error_d)




    #
    # ### find the average of averages for each pixel



    # +=+=+=+=+=+=+=+=+=+=+=+= AGGREGATE and OUTPUT +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

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

# ======================== PARSING ==============================================================
def parse_data():
    """"""
    # ====== Jornada =======
    # path to the jornada data
    path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
           "Jornada_012002_transect_soil_water_content_data.csv"  # This version has data that goes up through 2015

    df = pd.read_csv(path, header=72)  # I have no idea why it works on 72 but whatever.

    # print df

    # filter out missing data "."
    df = df[df.swc_30cm != "."]  # , 'swc_60cm', 'swc_110cm', 'swc_130cm'
    df = df[df.swc_60cm != "."]
    df = df[df.swc_90cm != "."]
    df = df[df.swc_110cm != "."]
    df = df[df.swc_130cm != "."]

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

    # need to do a depth average first,

    avg_normal_dictionary = {}
    for key, value in jornada_etrm.iteritems():
        # print "key -> ", key
        # print "value -> ", value

        # ===== Jornada ========

        jornada_var = df[df['location'] == key]

        # a long version of the jornada dataset to get a more accurate min and max from the whole dataset to perform
        # the normalization with
        jornada_var_long = df[df['location'] == key]

        # print "length jornada var long {}, key {}".format(len(jornada_var_long), key)

        # you only want to use the long jornada var...
        # print "Jornada VAR", jornada_var_long

        # ===== Depths (FIND ERROR) <- Don't normalize the data yet ========

        # 30 cm depth
        j_30 = float_data(jornada_var_long['swc_30cm'])
        # print "len j_30", len(j_30)
        # convert to a float
        # j_30 = j_30.astype(np.float)

        # 60cm
        j_60 = float_data(jornada_var_long['swc_60cm'])
        # print "len j_60", len(j_60)
        # j_60 = j_60.astype(np.float)

        # 90cm
        j_90 = float_data(jornada_var_long['swc_90cm'])
        # print "len j_90", len(j_90)
        # print "here is j_90 -> {}".format(j_90)
        # j_90 = j_90.astype(np.float)

        # 110cm
        j_110 = float_data(jornada_var_long['swc_110cm'])
        # print "len j_110", len(j_110)
        # j_110 = j_110.astype(np.float)

        # 130cm
        j_130 = float_data(jornada_var_long['swc_130cm'])
        # print "len j_130", len(j_130)
        # j_130 = j_130.astype(np.float)

        # get the date...
        j_date = pd.to_datetime(jornada_var['date'])

        # print "THE DATE \n {}".format(j_date)
        # depth average
        j_avg = depth_average(j_30, j_60, j_90, j_110, j_130)

        j_avg_normal = (nrml_rzsm_for_error(j_avg), j_date)

        # add the normalized depth averaged value for each location into a new dictionary:
        avg_normal_dictionary[key] = j_avg_normal

        # add the date to the dictionary?

    # # as a reminder this is the dictionary that has been normalized
    # print "avg normal dictionary", avg_normal_dictionary

    # make a list of dataframes
    df_list = []
    for key, value in avg_normal_dictionary.iteritems():

        _df = pd.DataFrame(data={key: value[0], 'date': value[1]}, columns=[key, 'date'])

        df_list.append(_df)

    # print "DF list {}".format(df_list)

    # join the dataframes by the 'date' column. only matching rows will be kept

    df_merge_list = []
    df_merge = None
    for i in range(len(df_list)):
        print "i", i

        if i == 0:
            print "first merge"
            _df_interim = pd.merge(df_list[i], df_list[i + 1], on='date')
            # df_merge_list.append(_df_interim)
            df_merge = _df_interim
            del _df_interim
        elif i > 0 : # and i < (len(df_list) -1)
            print 'do the second merge'
            # _df_interim = pd.merge(df_merge_list[i-1], df_list[i], on='date')
            _df_interim = pd.merge(df_merge, df_list[i], on='date')
            # df_merge_list.append(_df_interim)
            df_merge = _df_interim
            del _df_interim
        # else:
        #     print 'merge backwards'
        #     _df_interim = pd.merge(df_merge_list[i - 1], df_list[i], on='date')
        #     df_merge_list.append(_df_interim)

    print "This is the final merged dataframe {}".format(df_merge_list[-1])


if __name__ == "__main__":

    # Before we find the standard error, we need to parse through the original file and remove any missing entries such
    #  that if data are missing for one location in the Jornada we throw out the missing data and all corresponding data
    #  in the time series.

    parse_data()


    # # this outputs a csv of the running avg(depth_average) and standard error of the mean for each pixel.
    # find_std_error()