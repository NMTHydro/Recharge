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

import datetime
# from datetime import datetime
import numpy as np
# import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


# ============= local library imports ===========================



def grab(df_subset):
    ''' makes life easy by turning df subset values into arrays.'''

    array = np.array(df_subset.values.tolist())

    return array


def get_columns(dataframe):
    """gets the columns of the whole dataframe. Return a dict of colums with names."""
    tracker_dict = {}

    # for every column index in dataframe, get column and grab(column),\
    #  then store resultant array in a dict['column index'] = array
    cols = list(dataframe)
    for item in cols:
        #print 'column value \n {}'.format(dataframe[item])
        col = grab(dataframe[item])
        tracker_dict['{}'.format(item)] = col
    #print 'tracker dict', tracker_dict

    return tracker_dict


def reader_function(path):
    """
    takes a path, reads that in as a dataframe, then puts it back into a dict.
    """
    read_file = pd.read_csv(path)
    return read_file


def grapher(col_dict, x, y, plot_output, function_count, together=False):
    """
    input: x is a list of independent variables or a time series. y is a list of dependent variables.
    """

    color_list = ['green', 'blue', 'red', 'purple', 'black', 'orange', 'yellow', 'maroon']
    if together == False:

        # We plot everything separately
        for x_item in x:
            count = 0
            print 'col_dict x item', col_dict[x_item]
            if x_item == 'Date':
                date_list = col_dict[x_item].tolist()
                #print 'to stirng', col_dict[x_item].tostring()
                date_list = [datetime.datetime.strptime(item, "%Y-%m-%d") for item in date_list]
                ex = date_list
                #print 'ex', ex
            else:
                ex = col_dict[x_item]
            for y_item in y:
                fig = plt.figure()
                aa = fig.add_subplot(111)
                aa.set_title('tracker uni-plot', fontweight='bold')
                aa.set_xlabel('{}'.format(x_item), style='italic')
                aa.set_ylabel('{}'.format(y_item), style='italic')
                aa.plot(ex, col_dict[y_item], color = color_list[count], label=y_item )
                aa.legend(loc='upper right', frameon=True, prop={'size': 10})
                plt.tight_layout()
                plt.savefig('{}/{}_separate{}{}.png'.format(plot_output, y_item, count, function_count))
                count += 1
    if together == True:
        # We plot everything together. # yes
        for x_item in x:
            count = 0
            fig = plt.figure()
            aa = fig.add_subplot(111)
            aa.set_title('tracker multi-plot', fontweight='bold')
            aa.set_xlabel('{}'.format(x_item), style='italic')
            if x_item == 'Date':
                date_list = col_dict[x_item].tolist()
                #print 'to stirng', col_dict[x_item].tostring()
                date_list = [datetime.datetime.strptime(item, "%Y-%m-%d") for item in date_list]
                ex = date_list
                #print 'ex', ex
            else:
                ex = col_dict[x_item]
            for y_item in y:
                aa.set_ylabel('{}'.format(y_item), style='italic')
                aa.plot(ex, col_dict[y_item], color=color_list[count], label=y_item)
                count += 1
            aa.legend(loc='upper right', frameon=True, prop={'size': 10})
            plt.tight_layout()
            plt.savefig('{}/{}_together{}.png'.format(plot_output, x_item, function_count))


def run_tracker_plot(path, x, y, plot_output, function_count, multi=True):
    """Runs the plotter
    path: complete filepath to a csv
    x: list of strings of the column headings you want as independent variables
    e.g. x = ['Date', 'rzsm']
    y: list of strings of the column headings you want as dependent variables
    e.g. y = ['rain', 'soil_ksat', 'eta', 'rzsm']
    multi = True is default which means the graph makes one graph for each ind var with all dep variables on the same plot
    multi = False means graph will make one ind/dep variable plot for each ind variable and each dep variable.
    eg. three ind vars, three dep vars, 3x3 = 9 graphs total.

    This function makes plots for one csv at a time.
    """

    # now you need to read all the files and return a dict of pandas dataframes.
    dataframe = reader_function(path)
    print 'dataframe', dataframe
    # send in the dict containing the df to a grapher function and get to graphing!
    col_dict = get_columns(dataframe)
    grapher(col_dict, x, y, plot_output, function_count, together=multi)

    print 'complete?!?!'

if __name__ == "__main__":
    run_tracker_plot()

    # TODO find a way to pre-configure what you want to plot, then give x axis stuff (time series) and y axis stuff to grapher.
    # TODO - I must eventually devise a way to use this with the one to one RZSM plots, or make this into an object that can handle something like that.