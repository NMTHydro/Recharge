# ===============================================================================
# Copyright 2018 gabe-parrish
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
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ============= local library imports ===========================


def parse_file(path, first_col, num_cols):
    """

    :param path:
    :return:
    """
    # initialize dicts and lists....
    ascii_unformatted_dict = {}
    good_lines = []
    ascii_dict = {}

    with open(path, 'r') as readfile:
        for line in readfile:
            # print "line ->{}".format(line)

            # kill the spaces, make a list, check by the length of the list.
            line_lst = line.split(" ")
            # print "line list -> {}".format(line_lst)

            #kill spaces

            space_free = list(filter(lambda a: a != '', line_lst))

            # print "space free! -> {}".format(space_free)

            if len(space_free) == num_cols and space_free[0] != first_col:
                # print "spacefree in loop", space_free
                goodln = space_free
                # Turn the lines into floats...
                bestln = [float(i) for i in goodln]
                # ascii_unformatted_dict['good_lines'].append(bestln)
                good_lines.append(bestln)

    # print "the full goodlines list of lists \n", good_lines

    # put column numbers in a list
    rng_list = []
    for i in range(num_cols):
        # print "eye", i+1
        rng_list.append(i+1)

    # add empty lists to ascii_dict to append to later...
    for i in rng_list:
        ascii_dict["{}".format(i)] = []
    # use zip() to pull the correct list item from each line of the ascii into the correct column heading set up in...
    # ...the ascii_dict
    for lst in good_lines:
        for h, val in zip(rng_list, lst):
            # print "h", h
            # print "val", val
            ascii_dict["{}".format(h)].append(val)
    # print "new ascii dict {}".format(ascii_dict)

    return ascii_dict


def plotter(x, y):
    """

    :param x: your dependent variable
    :param y: your independent variable
    :return:
    """
    # todo - make little gridlines
    # create a variable for ideal ndvi
    ndvi = x
    ideal_etrf = []
    for i in ndvi:
        if i >= 0.8:
            ideal_etrf.append(1)

        elif i < 0.8:
            ideal_etrf.append(i * 1.25)

    # turn your x and y into numpy arrays
    x = np.array(x)
    y = np.array(y)
    ideal_etrf = np.array(ideal_etrf)

    ETrF_vs_NDVI = plt.figure()
    aa = ETrF_vs_NDVI.add_subplot(111)
    aa.set_title('ETrF vs NDVI', fontweight='bold')
    aa.set_xlabel('NDVI', style='italic')
    aa.set_ylabel('ETrF', style='italic')
    aa.scatter(x, y, facecolors='none', edgecolors='blue')
    aa.scatter(x, ideal_etrf, facecolors='none', edgecolors='red')
    plt.minorticks_on()
    # aa.grid(b=True, which='major', color='k')
    aa.grid(b=True, which='minor', color='white')
    plt.tight_layout()
    # TODO - UNCOMMENT AND CHANGE THE PATH TO SAVE THE FIGURE AS A PDF TO A GIVEN LOCATION.
    # plt.savefig(
    #      "/Volumes/SeagateExpansionDrive/jan_metric_PHX_GR/green_river_stack/stack_output/20150728_ETrF_NDVI_gr.pdf")

    plt.show()


def simple_plot(x,y):
    """"""

    # turn your x and y into numpy arrays
    x = np.array(x)
    y = np.array(y)

    plt.scatter(x, y)
    plt.show()

def df_filter(df, good_codes, code_col):
    """

    :param df: pandas dataframe
    :param good_codes: is a list of ints of desirable codes
    :param code_col: is a string that indicates which col of dataframe your codes are in
    :return: filtered dataframe w only rows that contain good codes.
    """
    # for code in good_codes:
    #
    #     df = df[df[code_col] != code]
    #
    # print "filtered df {}".format(df)
    #
    # return df
    code = df[code_col]

    # print "CODE\n", code

    for i in code:

        if i not in good_codes:

            df = df[df[code_col] != i]

    return df

def run_ascii():
    """
    JAN START HERE - G

    Reads in an ascii file from erdas, parses the information and stores it as a numpy array for plotting.
    :return:
    """

    # TODO - CHANGE FOR EVERY NEW ASCII
    # Here's the path to a particular ascii file to start out.
    path = "/Users/Gabe/Desktop/hard_drive_overflow/lt50330372008128pac01_etrf_ndvi_alb_lst_bqa_nad83.asc"

    # Give the parser the string of the first column header so that the parsing can be done corectly
    first_col = "X"

    # TODO- CHANGE EVERY TIME YOU CHANGE THE NUMBER OF COLUMNS IN THE ASCII
    # Give the parser the number of cols
    num_cols = 7

    # changed in function from the last version......
    parsed_dict = parse_file(path, first_col, num_cols)

    # output the parsed_dict to a csv file and then proceed to filter the csv file for undesirable values...
    # first we turn the dictionary into a dataframe...
    # build the list of columns for dataframe conversion
    colums = []
    for key in parsed_dict.keys():
        colums.append(key)
    df = pd.DataFrame(parsed_dict, columns=colums)

    # TODO - CHANGE THE OUTPUT PATH/filename FOR YOUR SYSTEM FOR THE UNFILTERED FILE
    # put the unfiltered dataframe out to a .csv in a location of our choice
    filename = "landsat" # what do you want the files name to be?
    output_path = "/Users/Gabe/Desktop"
    # TODO - CHANGE header = True and index = True if you want headers or indices in the .csv
    df.to_csv("{}/unfiltered_{}.csv".format(output_path, filename), header=False, index=False)

    # Now, filter the data:
    # TODO - FILL this list with codes that you want to KEEP
    desirable_codes = [672, 676, 680, 684]
    # TODO - CHANGE THE CODE COL IF FOR WHATEVER REASON THE COLUMN WITH THE CODES CHANGES LOCATION IN THE ASCII FILE.
    code_col = '7'
    df = df_filter(df, desirable_codes, code_col)

    print("The Filtered Dataframe {}".format(df))

    # TODO - CHANGE header = True and index = True if you want headers or indices in the .csv
    df.to_csv("{}/filtered_{}.csv".format(output_path, filename), header=False, index=False)

    # TODO - CHANGE IF YOU WANT TO PLOT SOMETHING DIFFERENT
    # Note that you will need to know which column in the ascii file your variable was in order to plot it here.
    # what two variables do you want to plot?
    # in this we're plotting columns three and four...
    # Since we did df_filter() on the dataframe all we plot here are values that correspond to desirable codes...
    x = df['3']
    y = df['4']

    # TODO - LEAVE THIS UNCOMMENTED FOR PLOTS OF NDVI AND ETRF
    # this plotter function is customized for NDVI vs ETRF plotting
    plotter(x, y)

    # TODO - UNCOMMENT THESE LINES IF YOU ARENT PLOTTING ETRF AND NDVI AGAINST EACH OTHER
    # # for a simple x, y plot use
    # simple_plot(x, y)

if __name__ == "__main__":

    run_ascii()