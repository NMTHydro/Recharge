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
import os
import pandas as pd
import numpy as np
import datetime
from matplotlib import pyplot as plt

# ============= local library imports ===========================
def intersect(l1, l2):
    intersection = l1 & l2
    return intersection

def formatter(df_dict):
    """

    :param df_dict: a dict of data frames with the keys from '000' to '012', 13 keys total
    :return:
    """

    for key, value in df_dict.iteritems():

        print("key \n {}".format(key))

        good_dates = []
        values = []
        good_dfs = []
        good_vals = []
        for df in value:
            date = df['date'] #pd.to_datetime(df['date'])
            j_30 = df['swc_30cm']
            j_60 = df['swc_60cm']
            j_90 = df['swc_90cm']
            j_110 = df['swc_110cm']
            j_130 = df['swc_130cm']

            vals = (date, j_30, j_60, j_90, j_110, j_130)
            values.append(vals)

        for i in values:
            for date, a, b, c, d, e in zip(i[0], i[1], i[2], i[3], i[4], i[5]):
                if "." not in [a, b, c, d, e]:
                    good_dates.append(date)
                # good_dates.append(date)

        print("good dates {} pixel {}, length {}".format(good_dates, key, len(good_dates)))

        # turn good dates into a series to delete the repetitions
        good_dates = set(good_dates)

        # need to test the intersection of all dates with the dates in values
        # for i in values:
        good_dates = intersect(good_dates, set(values[0][0]))

        # gooder_dates = []
        # for i, j in zip(values[0], good_dates):
        #     for day, gday in i, j:
        #         if day not in j:



        print("good dates as a set", good_dates)
        print("length of set", len(good_dates))

        print("length of values", len(values))
        for i in values:
            g_dates = []
            g_a = []
            g_b = []
            g_c = []
            g_d = []
            g_e = []
            for date, a, b, c, d, e in zip(i[0], i[1], i[2], i[3], i[4], i[5]):
                if date in good_dates:
                    g_dates.append(date)
                    g_a.append(a)
                    g_b.append(b)
                    g_c.append(c)
                    g_d.append(d)
                    g_e.append(e)

            good_vals.append((g_dates, g_a, g_b, g_c, g_d, g_e))

            print("===")
            print(len(g_dates))
            print(len(g_a))
            print(len(g_b))
            print(len(g_c))
            print(len(g_d))
            print(len(g_e))
            print("====")

        print("good values", len(good_vals))

        for i in good_vals:
            print("****")
            print(len(i[0]))
            print(len(i[1]))
            print(len(i[2]))
            print(len(i[3]))
            print(len(i[3]))
            print(len(i[3]))
            print("***")


            # data = {'date': good_vals[0], 'j_30': i[1], 'j_60': i[2], 'j_90': i[3], 'j_110': i[4], 'j_130': i[5]}
            # #     # good_df = pd.DataFrame(data=data, columns=['date', 'j_30', 'j_60', 'j_90', 'j_110', 'j_130'])
            # #     # good_dfs.append(good_df)





            # else:
            #     #for date, a, b, c, d, e in zip(i[0], i[1], i[2], i[3], i[4], i[5]):
            #     # data = {'date': i[0], 'j_30': i[1], 'j_60': i[2], 'j_90': i[3], 'j_110': i[4], 'j_130': i[5]}
            #     # good_df = pd.DataFrame(data=data, columns=['date', 'j_30', 'j_60', 'j_90', 'j_110', 'j_130'])
            #     # good_dfs.append(good_df)
            #     for dt, a, b, c, d, e in zip(i[0], i[1], i[2], i[3], i[4], i[5]):
            #         g_dates.append(dt)
            #         g_a.append(a)
            #         g_b.append(b)
            #         g_c.append(c)
            #         g_d.append(d)
            #         g_e.append(e)
            # good_vals.append((g_dates, g_a, g_b, g_c, g_d, g_e))


        # print "the good vals", good_vals
        # count = 0
        # for gtuple in good_vals:
        #     print "\n {} \n".format(count)
        #     for dates, a, b, c, d, e in zip(gtuple[0], gtuple[1], gtuple[2], gtuple[3], gtuple[4], gtuple[5]):
        #         print "lendates", len(dates)
        #         print "len a", len(a)
        #     count += 1


        # print "The good DFs ", good_dfs
        #
        # for i in good_dfs:
        #     print "length of good df is {}".format(len(i))







def parse_data():
    """"""
    # ====== Jornada =======
    # path to the jornada data
    path = "/Users/Gabe/Desktop/33_37_ETRM_aoi_project/Jornada_012002_transect_soil_water_content_data/" \
           "Jornada_012002_transect_soil_water_content_data.csv"  # This version has data that goes up through 2015

    df = pd.read_csv(path, header=72)  # I have no idea why it works on 72 but whatever.

    # print df

    relate_dict = {"000": ["C01", "C02"], "001": ["C03", "C04", "C05", "C06", "C07", "C08", "C09"],
                   "002": ["C10", "C11"],
                   "003": ["C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21"],
                   "004": ["C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29"],
                   "005": ["C31", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39"],
                   "006": ["C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48"],
                   "007": ["C51", "C52", "C53", "C54", "C55", "C56", "C57"],
                   "008": ["C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66"],
                   "009": ["C67", "C68", "C69", "C70"], "010": ["C71", "C72", "C73", "C74", "C75"],
                   "011": ["C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84"],
                   "012": ["C85", "C86", "C87", "C88", "C89"]}

    df_dict = {}
    for key, value in relate_dict.iteritems():
        loc_list = []
        for loc in value:

            df_jornada = df[df['location'] == loc]

            # print "df jornada for loc {} in pixel {} \n {}".format(loc, key, df_jornada)

            loc_list.append(df_jornada)

        df_dict[key] = loc_list

    print("another look", df_dict['000'])

    pix_dictionary = formatter(df_dict)







if __name__ == "__main__":

    # Before we find the standard error, we need to parse through the original file and remove any missing entries such
    #  that if data are missing for one location in the Jornada we throw out the missing data and all corresponding data
    #  in the time series.

    parse_data()


    # # this outputs a csv of the running avg(depth_average) and standard error of the mean for each pixel.
    # find_std_error()

    #
    # # process the missing data out of the df dicts
    # p_000 = pd.merge(df_dict['000'][0], df_dict['000'][1], on='date')
    #
    # print "p000", p_000
    #
    # p_000 = p_000[p_000.swc_30cm != "."]
    # p_000 = p_000[p_000.swc_60cm != "."]
    # p_000 = p_000[p_000.swc_90cm != "."]
    # p_000 = p_000[p_000.swc_110cm != "."]
    # p_000 = p_000[p_000.swc_130cm != "."]
    #
    # print "editt"