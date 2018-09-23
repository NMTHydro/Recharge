# ===============================================================================
# Copyright 2016 Juliet Ayertey
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

# ============= local library imports ===========================
import sys
import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame, Series
from datetime import datetime
import os
import fnmatch


# print "HELLO WORLD"

def find_dates(path, list_of_dates):
    """
    Say what this function does here:

    path - what is is and why
    list_of_dates - what it is and why
    """

    df = pd.read_csv(path)  # todo - change this "/Users/Gabe/Desktop/etrm_tracker_007-0000_juliet_output007.csv"
    # df = pd.DataFrame(path)

    keywords_mod = []
    for key in list_of_dates:
        key = key.split("/")

        key = "{}-{}-{}".format(key[2], key[0], key[1])

        # print "formatted key {}".format(key)

        keywords_mod.append(key)

    listMatchInd = []
    for i in range(len(df.index)):

        if any(x in df['Date'][i] for x in keywords_mod):
            # appends the index of the row corresponding to the date we want to a list.
            listMatchInd.append(i)

    out = df.ix[listMatchInd]

    return out


def tracker_iterator(main_path, list_of_dates):
    """explanation"""

    # for every tracker file, get the path.
    out_files = []
    for a, b, c in os.walk(main_path, topdown=False):


        for file in c:
            # print "file", file
            if file.startswith('etrm_tracker'):
                fullpath = os.path.join(a, file)
                out_files.append(fullpath)

    # print type(out_files)

    print(len(out_files)) # len outfiles - 16

    # dat = []
    # for path in out_files:
    #     y = find_dates(path, list_of_dates)
    #     # if any(x in df['Date'][i] for x in keywords_mod):
    #     dat.append(y)
    #
    # print "dat!!!", dat


    # dict = {}
    #
    # for path in out_files:
    #     y = find_dates(path, list_of_dates)
    #
    #     dict["{}".format(path)] = y
    #
    # print "big dictoionary", dict
    #
    #
    # form_dict = {}
    #
    # for key, value in dict.iteritems():
    #
    #     pixel_number = key[109,111]
    #
    #     print "pixel number -{}- for path -{}-".format(pixel_number, key)
    #
    #     modified_key = key
    #
    #     form_dict["{}".format(modified_key)] = value


    dict = {}

    print("full outfiles", out_files)

    for i in range(0, 13): # 0, 16
        pix = pd.DataFrame([])
        for j in range(i, i + (len(out_files)-12), 13): # len(out_files)-15), 16

            # print "j", j

            # print 'outfiles j', out_files[j]

            y = find_dates(out_files[j], list_of_dates)

            # print 'Y', y

            pix = pix.append(y)
        dict["Pixel_{}".format(i + 1)] = pix
        pix.to_csv("/Volumes/SeagateExpansionDrive/juliet_inverse_problem/gabe_original_data_March_8_2018/p %d.csv" % i,
                   index=False)

    #print "the pixels", dict['Pixel_15']

    return dict


def run():
    """
    calls every other function for us.
    """
    list_of_dates = ['07/15/2000', '09/15/2000', '07/15/2001', '09/15/2001', '07/15/2002', '09/15/2002', '07/15/2003',
                     '09/15/2003', '07/15/2004', '09/15/2004', '07/15/2005', '09/15/2005', '07/15/2006', '09/15/2006',
                     '07/15/2007', '09/15/2007', '07/15/2008', '09/15/2008', '07/15/2009', '09/15/2009', '07/15/2010',
                     '09/15/2010']

    main_path = "/Volumes/SeagateExpansionDrive/juliet_inverse_problem/gabe_original_data_March_8_2018"

    # should evenutally yield a dict of dataframes
    relevant_trackers = tracker_iterator(main_path, list_of_dates)

    print(relevant_trackers)

if __name__ == "__main__":

    print("Hello World")

    # run the main function of the script
    run()











    # outInd = pd.DataFrame({'Index':listMatchInd})
    # print outInd
    #
    # print type(outInd)
    #
    # outInd2=outIn.values.tolist()
    # print outInd2
    #
    # print type(outInd2)

    # out=[]
    # for i in indx:
    # 	if i in :
    # 	    return x= df.ix[i,:]
    # 		print "let's see", x
    #
    # 		out.append(x)



    #	if any(x in df['Date'][i] for x in keywords_mod):


    # out=[]
    # for i in output:
    # 	return df.ix[i,:]
    # out.append(df.ix[i,:])
    # print "what we need",out


    # out=df.ix[output]
    # output.to_csv("new_data.csv", index=False)



    # listMatchDate = []
    #
    # for i in range(len(df.index)):
    #
    #     if any(x in df['Date'][i] for x in keywords_mod):
    #         listMatchDate.append(df['Date'][i])
    #
    #         print listMatchDate
    #
    # output = pd.DataFrame({'Date':listMatchDate})
    # print output
    # out=df.ix[output]
    # output.to_csv("new_data.csv", index=False)



    #  		indxs_we_want.append(indx)
    #  		print indxs_we_want

    # # for i in df.rows:
    # #
    #     print "i", i
    #     #if any(x in df['Date'][i] for x in keywords):
    #
    #
    # output = pd.DataFrame({'Date':listMatchDate})
    # output.to_csv("new_data.csv", index=False)