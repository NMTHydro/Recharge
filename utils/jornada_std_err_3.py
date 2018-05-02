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
    intersection = set(l1) & set(l2)
    return intersection

def formatter(df_dict):

    # get each date out as a list and put in the dictionary

    df_dates = {}
    for key, value in df_dict.iteritems():
        # print "value", value
        list_o_rings = []
        # list_o_swc_30 = []
        # list_o_swc_90 = []
        # list_o_swc_110 = []
        # list_o_swc_130 = []
        for i in value:
            date_lst = list(i['date'])
            jsm_30 = list(i['swc_30cm'])
            jsm_60 = list(i['swc_60cm'])
            jsm_90 = list(i['swc_90cm'])
            jsm_110 = list(i['swc_110cm'])
            jsm_130 = list(i['swc_130cm'])
            ring = (date_lst, jsm_30, jsm_60, jsm_90, jsm_110, jsm_130)
            list_o_rings.append(ring)
        # print "key -> {}, len(list_o_rings) -> {}".format(key, len(list_o_rings))
        df_dates[key] = list_o_rings

    # print "df dates", df_dates

    # we now have a dictionary of series of dates sorted by which pixel they came from.

    # next we need to do a couple of things in order to get the list of "good dates" we need
    # 1.) We need to check each groupings "." points together and pile that on into a list which we turn into a set.

    # put the dates sans '.' in here
    huge_list = []
    for key, value in df_dates.iteritems():
        for i in value:
            for da, a, b, c, d, e in zip(i[0], i[1], i[2], i[3], i[4], i[5]):
                # print 'test abcde {}{}{}{}{}'.format(a, b, c, d, e)
                if "." not in [a, b, c, d, e]:
                    huge_list.append(da)

    # 2.) once we get that initial set (huge list) we try and get the intersection of the huge list with
                    #  unmodified lists

    intersection_dates = {}
    for key, value in df_dates.iteritems():
        # this can be a list that stores the intersected lists, the final one being the final intersection.
        intersection_storage = []
        for num in range(len(value)):

            if num == 0:
                print "A"
                unmod_list = value[num][0]
                # compare this one to the huge list
                int = intersect(unmod_list, huge_list)
                intersection_storage.append(int)

            elif num > 0:
                print "B, C ..."
                unmod_list = value[num][0]
                # compare these ones to the previous intersection storage
                int = intersect(unmod_list, intersection_storage[num-1])
                intersection_storage.append(int)

            elif num == len(value):
                print "END"
                unmod_list = value[num+1][0] # todo figure out what the hell I'm doing wrong here.
                # compare to the last intersection storage
                int = intersect(unmod_list, intersection_storage[-1])
                intersection_storage.append(int)

        intersection_dates[key] = intersection_storage[-1]
        print "how long is the first intersection storage ? {}".format(len(intersection_storage[0]))
        print "how long is the last intersection storage ? {}".format(len(intersection_storage[-1]))
    # print "intersection dates dictionary", intersection_dates

    # the intersection dictionary contains the most 'parsimonious' selection of dates for a given pixel

    # 3.) now we will use this parsimonious list of dates to filter out our original data from the top

    # grab the df dict
    date_formated_dict = []
    for key, value in df_dates.iteritems():
        print "==========="
        print "KEY ", key
        tim = intersection_dates[key]
        list_o_rings = []
        for i in value:
            # set up empty lists to be filled with good values.
            date_lst = []
            jsm_30 = []
            jsm_60 = []
            jsm_90 = []
            jsm_110 = []
            jsm_130 = []
            for da, a, b, c, d, e in zip(i[0], i[1], i[2], i[3], i[4], i[5]):
                # print 'da xxxx', da
                # print 'a', a
                if da in tim:
                    date_lst.append(da)
                    jsm_30.append(a)
                    jsm_60.append(b)
                    jsm_90.append(c)
                    jsm_110.append(d)
                    jsm_130.append(e)
            print len(date_lst)
            print len(jsm_30)
            print len(jsm_60)
            print len(jsm_90)
            print len(jsm_110)
            print len(jsm_130)
            ring = (date_lst, jsm_30, jsm_60, jsm_90, jsm_110, jsm_130)
            # print "ring {}".format(ring)
            list_o_rings.append(ring)
        #     print key
        # print "listo", type(list_o_rings)
        # print "listo [0]", list_o_rings[0]
        # print "key", key
        print "==========="
        # # todo - fix problem here
        # todo also key 11, 12, 3, 4 ... What the ever loving fuck?
        # date_formated_dict[key] = list_o_rings
        #
        # print "show the date formatted dict", date_formated_dict
        #
        # # todo - pull each pixels data together into a dataframe.
        #
        # # pop the dataframes out to disk or keep working with em to get std error of the mean.





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

    # print "another look", df_dict['000']

    pix_dictionary = formatter(df_dict)







if __name__ == "__main__":

    # Before we find the standard error, we need to parse through the original file and remove any missing entries such
    #  that if data are missing for one location in the Jornada we throw out the missing data and all corresponding data
    #  in the time series.

    parse_data()


