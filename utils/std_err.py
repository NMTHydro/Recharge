# ===============================================================================
# Copyright 2018 ross
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
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt


def calculate_depth_average(row):
    s = 0
    swt = 0
    for k, wt in ((30, 45), (60, 20), (90, 25), (110, 20), (130, 30)):
        # build the paths for each depth.
        k = 'swc_{}cm'.format(k)
        # this is how you skip over "." entries in the dataframe, by using try-except
        try:
            v = float(row[k])
        except ValueError:
            # return here takes you back to the next iteration of the loop so you skip any values that give a value err
            return

        if v < 0:
            return

        # add up the storage
        s += v * wt

        # add up the depths of each layer
        #swt += wt
    # return both the date and the weighted average storage
    return row['date'], s #/ swt


def calculate_pixel(df, locations):
    """

    :param df: is the dataframe we read in.
    :param locations: a list of strings with the names of the locations of each tube in the transect within a given
    pixel.
    :return: a list of lists of [[(),()], [(),()]] for every swc tube in the pixel
    """

    def func(loc):
        """

        :param loc: is a location from the list "locations"
        :return:
        """

        # filter the dictionary for all entries corresponding to the swc probe location
        fdf = df[df['location'] == loc]

        # calulates the storage of the water stores the values in a list.
        ss = [calculate_depth_average(row) for i, row in fdf.iterrows()]
        # filters for none values
        ss = [a for a in ss if a is not None]

        # ss is a list of tuples of (date, storage)
        # zipping *ss gives a list of [(all the dates), (all the storages)]
        return zip(*ss)

    series = [func(location) for location in locations]
    # series is a list of lists of [[(),()], [(),()]] for every swc tube in the pixel
    return series


def get_matching_date(di, cs):
    """
    Checks if the dates match.
    :param di:
    :param cs:
    :return: the value of the swc probe corresponding to the the matching date
    """
    for cdi, cvi in cs:
        if cdi == di:
            return cvi


def calculate_sem(vs):
    n = len(vs)
    return sum(vs) / n ** 1.5


def calculate_avg(vs):
    n = len(vs)
    return sum(vs) / n


def calculate(series):
    """

    :param series: a list of lists of [[(),()], [(),()]] for every swc tube in the pixel
    :return:
    """
    # gets every dates tuple in the list
    dates = [t for t, v in series]
    # define the dates as a set
    ds = set(dates[0])
    # get the intersection of every other set.
    for d in dates[1:]:
        ds = ds.intersection(set(d))

    def func(di):
        """"""
        # check for matching dates in the intersected and ordered set with the values from the series.
        ns = [get_matching_date(di, zip(*cs)) for cs in series] # ns is the matching values
        # if the value is not none...
        ns = [ni for ni in ns if ni is not None]
        print "Here is your ns {}".format(ns)
        # calculate the error of the mean for that value.
        if ns:
            return datetime.strptime(di, '%m/%d/%Y'), calculate_sem(ns) #, calculate_avg(ns)

    # sets are NOT ordered so you need to find the ones that match up.
    # vs = [func(di) for di in sorted(list(ds), reverse=True)]
    storages = [func(di) for di in sorted(list(ds), reverse=True)]
    # vs = [vi for vi in vs if vi is not None]
    storages = [i for i in storages if i is not None]
    # return zip(*vs)
    return zip(*storages)


def plot_timeseries(xs, ys, color='blue'):
    plt.scatter(xs, ys, color=color)


def main():

    # path to the file
    p = 'jornada_data.csv'
    # read the csv in with pandas
    df = pd.read_csv(p, header=72)
    print df.keys()

    # We use this dictionary to keep track of which locations correspond to which pixels.
    pixel_location_dict = {"000": ["C01", "C02"], "001": ["C03", "C04", "C05", "C06", "C07", "C08", "C09"],
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

    # Here we graph the standard error
    colornames = ['red', 'blue', 'green', 'black', 'yellow']
    nc = len(colornames)

    # i is a number. the items (pixel, locations) in the location dict are stored in a tuple
    for i, (pixel, locations) in enumerate(pixel_location_dict.items()):

        #[[(),()], [(),()]] where the tuples are dates and values for every swc tube in the pixel
        das = calculate_pixel(df, locations)



    #     timeseries = calculate(das)
    #
    #     print "pixel -> {}, \n timeseries -> \n {}".format(pixel, timeseries)
    #     # print "pixel {}".format(pixel)
    #     # print "locations {}".format(locations)
    #     # print 'time_series[1]', timeseries[1]
    #
    #     plot_timeseries(*timeseries, color=colornames[i % nc])
    #
    # plt.show()


if __name__ == '__main__':
    main()
# ============= EOF =============================================
