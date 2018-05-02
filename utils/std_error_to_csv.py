# ===============================================================================
# Copyright 2018 ross
# Modified by Gabe Parrish
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
import os


def calculate_rzswf(row, loc):

    # This dictionary relates the min and max storages selected for each probe location in the jornada.
    min_max_dict = {"C01": (20.0, 60.0), "C02": (20.0, 56.0), "C03": (20.0, 61.0), "C04": (20.0, 63.0),
                    "C05": (17.0, 62.0), "C06": (19.0, 54.0), "C07": (14.0, 44.0), "C08": (10.0, 41.0),
                    "C09": (12.0, 36.0), "C10": (09.0, 31.0), "C11": (8.0, 32.0), "C12": (5.0, 27.0),
                    "C13": (3.0, 28.0), "C14": (4.0, 30.0),
                    "C15": (4.0, 29.0), "C16": (4.0, 30.0), "C17": (5.0, 30.0), "C18": (4.0, 30.0),
                    "C19": (5.0, 33.0), "C20": (6.0, 32.0), "C21": (6.0, 33.0), "C22": (8.0, 35.0),
                    "C23": (7.0, 33.0), "C24": (7.0, 34.0), "C25": (8.0, 36.0), "C26": (10.0, 35.0),
                    "C27": (9.0, 32.0), "C28": (8.0, 35.0),
                    "C29": (8.0, 32.0), "C31": (7.0, 33.0), "C32": (8.0, 34.0), "C33": (5.0, 28.0),
                    "C34": (6.0, 31.0), "C35": (5.0, 31.0), "C36": (6.0, 32.0), "C37": (7.0, 30.0),
                    "C38": (7.0, 32.0), "C39": (6.0, 31.0), "C40": (7.0, 32.0), "C41": (5.0, 31.0),
                    "C42": (5.0, 31.0), "C43": (6.0, 33.0),
                    "C44": (4.0, 28.0), "C45": (5.0, 30.0), "C46": (4.0, 31.0), "C47": (6.0, 30.0),
                    "C48": (5.0, 30.0), "C51": (4.0, 29.0), "C52": (4.0, 28.0), "C53": (5.0, 30.0),
                    "C54": (5.0, 30.0), "C55": (4.0, 29.0), "C56": (40.0, 29.0), "C57": (3.0, 30.0),
                    "C58": (3.0, 24.0), "C59": (2.0, 28.0),
                    "C60": (1.0, 27.0), "C61": (2.0, 27.0), "C62": (2.0, 26.0), "C63": (3.0, 28.0),
                    "C64": (3.0, 28.0), "C65": (6.0, 30.0), "C66": (4.0, 28.0), "C67": (4.0, 31.0),
                    "C68": (3.0, 30.0), "C69": (3.0, 28.0), "C70": (5.0, 32.0), "C71": (4.0, 31.0),
                    "C72": (5.0, 30.0), "C73": (2.0, 29.0),
                    "C74": (1.0, 27.0), "C75": (1.0, 27.0), "C76": (0.0, 25.0), "C77": (0.0, 26.0),
                    "C78": (0.0, 25.0), "C79": (0.0, 26.0), "C80": (0.0, 25.0), "C81": (0.0, 21.0),
                    "C82": (0.0, 25.0), "C83": (1.0, 26.0), "C84": (1.0, 27.0), "C85": (0.0, 26.0),
                    "C86": (0.0, 23.0), "C87": (1.0, 25.0),
                    "C88": (1.0, 24.0), "C89": (0.0, 23.0)}

    # instantiate a variable to hold each soil water value
    s = 0
    # 140 cm total depth
    # first number is the depth of instrument, second number is the thickness of representative layer.
    # print "location -> {}".format(loc)
    for k, wt in ((30, 45), (60, 20), (90, 25), (110, 20), (130, 30)):
        # build the paths for each depth.
        k = 'swc_{}cm'.format(k)
        # print "K {}".format(k)
        # this is how you skip over "." entries in the dataframe, by using try-except
        try:
            v = float(row[k])
        except ValueError:
            # return here takes you back to the next iteration of the loop so you skip any values that give a value err
            return
        # filter out erroneous negative values
        if v < 0:
            return

        # add up the storage
        s += v * wt

        # print "little s {}".format(v * wt)

    print "STORAGE - {}".format(s)

    # normalize the storage to get RZSWF (Root Zone Soil Water Fraction)
    if s - min_max_dict[loc][0] < 0:
        # soil water fraction goes to zero if the chosen minimum happens to be larger than the storage value
        # I realize calculating this is redundant but i do so for clarity
        rzswf = (s - s)/(min_max_dict[loc][1] - s)
        print "should be zero -> {}".format(rzswf)
    else:
        rzswf = (s - min_max_dict[loc][0])/(min_max_dict[loc][1] - min_max_dict[loc][0])

    # return both the date and the root zone soil water fraction
    return row['date'], rzswf


def calculate_pixel(df, locations):
    """

    :param df: is the dataframe we read in.
    :param locations: a list of strings with the names of the locations of each tube in the transect within a given
    pixel.
    :return: a list of lists of [[(),()], [(),()]] for every swc tube in the pixel
    """

    # print "locations \n", locations

    def func(loc):
        """

        :param loc: is a location from the list "locations"
        :return:
        """
        print "Doing location {}".format(loc)
        # filter the dictionary for all entries corresponding to the swc probe location
        fdf = df[df['location'] == loc]

        # calulates the storage of the water stores the values in a list.
        # calculate_depth_average() calculates normalized storage (RZWF) using the min_max dictionary
        ss = [calculate_rzswf(row, loc) for i, row in fdf.iterrows()]
        # print "SS \n", ss

        # filters for none values
        ss = [a for a in ss if a is not None]
        # ss is a list of tuples of (date, storage)
        # zipping *ss gives a list of [(all the dates), (all the storages)]
        return zip(*ss)

    series = [func(location) for location in locations]
    # series is a list of lists of [[(),()], [(),()], ... ] for every swc tube in the pixel
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


def calculate_se(vs):
    """
    Get the standard error for the group of tube RZSWF values on a given date
    :param vs: a list of values (tube measurements) for a given day within a pixel.
    :return: the standard error of RZSWF
    """

    # print "Calculating Standard Error of RZSWF"
    # print "Value List: \n {}".format(vs)

    # number of values (tube measurements) for a given day.
    n = len(vs)

    # get the mean
    mean = sum(vs)/ n

    # subtract the mean from each number and square the result
    i_minus_m = []
    for i in vs:
        j = (i - mean) ** 2
        i_minus_m.append(j)

    # find the mean of the new subtracted list and take the square root
    std_dev = (sum(i_minus_m)/n) ** 0.5

    # standard error is std_dev over square root of n
    std_err = std_dev/(n ** 0.5)

    return std_err


def calculate_avg(vs):
    n = len(vs)
    return sum(vs) / n


def calculate(series):
    """

    :param series: a list of lists of [[(),()], [(),()]] for every swc tube in the pixel
    :return:
    """
    # gets every date tuple in the list
    dates = [t for t, v in series]
    # define the dates as a set
    ds = set(dates[0])
    # get the intersection of every other set.
    for d in dates[1:]:
        ds = ds.intersection(set(d))

    def func(di):
        """
        Here is where you get the matching dates...
        :param di:
        :return:
        """
        # check for matching dates in the intersected and ordered set with the values from the series.
        ns = [get_matching_date(di, zip(*cs)) for cs in series] # ns is the matching values
        # if the value is not none...
        ns = [ni for ni in ns if ni is not None]
        # print "Here is your ns {}".format(ns)
        # calculate the error of the mean for that value.
        if ns:
            # TODO - return an average value as well...

            # print "date -> {} \n sem -> {} \n avg -> {}".format(datetime.strptime(di, '%m/%d/%Y'), calculate_sem(ns), calculate_avg(ns))
            return datetime.strptime(di, '%m/%d/%Y'), calculate_se(ns), calculate_avg(ns)

    # sets are NOT ordered so you need to find the ones that match up.
    # vs = [func(di) for di in sorted(list(ds), reverse=True)]
    date_se_avg = [func(di) for di in sorted(list(ds), reverse=True)]
    # vs = [vi for vi in vs if vi is not None]
    date_se_avg = [i for i in date_se_avg if i is not None]
    # return zip(*vs)
    return zip(*date_se_avg)


def plot_timeseries(xs, ys, color='blue'):
    plt.scatter(xs, ys, color=color)


def main():

    output_path = "/Users/Gabe/Desktop/juliet_stuff/juliet_jornada_plot_stats"

    # path to the file
    p = 'jornada_data.csv'
    # read the csv in with pandas
    df = pd.read_csv(p, header=72)
    # print df.keys()

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

        #[[(),()], [(),()]] where the tuples are dates and RZSWF for every swc tube in the pixel
        das = calculate_pixel(df, locations) # gets the storage for each tube

        # timeseries = [(dates), (std_errors)]
        timeseries = calculate(das)

        # save to a .csv
        write_dict = {'date':timeseries[0], 'std_err_rzswf':timeseries[1], 'mean_rzswf':timeseries[2]}
        write_df = pd.DataFrame(write_dict, columns=['date', 'std_err_rzswf', 'mean_rzswf'])

        # write the std err of mean, mean and the dates to a .csv for each pixel...
        writepath = os.path.join(output_path, "Pixel_{}_RZSWF_stats.csv".format(pixel))
        write_df.to_csv(writepath)

        #==============================
    #     print "pixel {}".format(pixel)
    #     print "locations {}".format(locations)
    #     print 'time_series[1]', timeseries[1]
    #
    #     plot_timeseries(*timeseries, color=colornames[i % nc])
    #
    # plt.show()


if __name__ == '__main__':
    main()
# ============= EOF =============================================
