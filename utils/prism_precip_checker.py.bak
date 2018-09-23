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
from datetime import datetime, timedelta
import rasterio
import numpy as np

# ============= local library imports ===========================


"""
This module is designed to look at ETRM PRISM data before a certain date and to quantify how much rain there was within
a given AOI during a specified period.

"""

def days_prior_func(date_list, days_prior):
    """

    :param date_list: a list of date strings in ISO format.
    :param days_prior: # of days prior to date we want to investigate.
    :return: a dictionary with a list of all the dates prior
    """

    print "days prior", days_prior
    storage = {}
    for date in date_list:

        main_day = datetime.strptime(date, "%Y-%m-%d")

        print "main day", main_day

        lst = []
        for i in range(0, days_prior, 1):
            d = main_day - timedelta(days=i)
            #convert back to a string
            d = datetime.strftime(d, "%Y-%m-%d")
            lst.append(d)

        print "list", lst

        storage["{}".format(date)] = lst

    print "storage", storage
    return storage



def find_files(date_list, prism_path, days_prior):
    """
    :param days_prior: number of days prior to the date we want to look at.
    :param date_list: list of dates in ISO format
    :param prism_path: path to prism tiff files for ETRM
    :return: dict of date:path of date and whatever number of days prior.
    """

    days_prior_dict = days_prior_func(date_list, days_prior)

    print "prior days", days_prior
    date_dict = {}
    for path, directory, file in os.walk(prism_path):

        # print "FILE", file

        for key, value in days_prior_dict.iteritems():
            p_list = []
            for date in value:
                d = date.split("-")
                # print "d", d
                #str = ""
                date_string = "".join(d)
                # print "date string", date_string
                for i in file:
                    name = i.split(".")[0]
                    # print "name", name

                    if i.endswith('.tif') and name.endswith("{}".format(date_string)):
                        # print "Heres your guy {}".format(i)
                        p = os.path.join(path, i)
                        p_list.append(p)
                        # date_dict["{}".format(date)] = p
            # print "length {}".format(len(p_list))
            date_dict["{}".format(key)] = p_list
    print "DATE DICT", date_dict
    return date_dict

def raster_reader(date_dict):
    """

    :param date_dict: key is date in ISO format. Value is a list of paths to tiff files of Prism precip images prior
    to the date.
    :return: a dictionary where key is date in ISO format. Values are a list of raster arrays.
    """

    raster_dict = {}
    for key, value in date_dict.iteritems():

        arr_list = []
        for file in value:
            with rasterio.open(file) as raster:
                arr = raster.read(1)
                arr_list.append(arr)

        raster_dict["{}".format(key)] = (arr_list, value)

    return raster_dict

def format_outputter(raster_dict):
    """
    Formats a text file of statistics for each raster of prior dates.
    :param raster_dict:
    :return:
    """

    with open("/Users/Gabe/Desktop/prism_precip_checker_output.txt", "w") as write_file:

        write_file.write("Prism Output \n \n \n \n ")
        for key, value in raster_dict.iteritems():

            print "value[0]", value[0]
            print "value[0][0]", value[0][0]

            write_file.write("\n \n \n{}\n \n \n".format(key))

            for array, path in zip(value[0], value[1]):
                lst = path.split(".")
                str = lst[0]
                write_file.write("Array {}\n".format(str[-8:]))
                # for i in array:
                zero_array = not np.any(array)
                print "Zero Arr -> {}".format(zero_array)
                write_file.write("{}  {}\n".format("All zeroes?", zero_array))



def main():
    """
    main function calls all the other functions in the script
    :return:
    """

    # make a list of the dates that Jan thinks could work that you want to examine for prior precipitation,
    # in ISO frmt YYYY-MM-DD
    date_list = ['2000-05-09', '2000-05-17', "2000-09-14", '2000-09-30', '2001-06-05', '2001-06-13', '2001-09-09',
                 '2001-09-25', '2002-05-07','2002-05-15', '2002-05-23', '2002-06-08', '2002-06-16', '2002-07-02',
                 '2002-08-11', '2002-09-20', '2003-05-10', '2003-05-18', '2003-06-11', '2004-05-12', '2004-05-28',
                 '2004-06-13', '2005-05-31', '2005-07-02', '2005-09-20', '2007-05-21', '2008-05-07', '2008-06-08',
                 '2009-05-10', '2009-07-29', '2009-10-01', '2010-05-13', '2010-06-14', '2011-04-30']

    # path to the prism tif files.
    prism_path = "/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/PRISM/Precip/800m_std_all"

    # what I want out is a dictionary of the dates as keys with a subdict w/
    # {rain: T/F, avg_precip: value, total_acre_feet: value, std_dev: value}

    # first we need a dictionary of the date:filepath, so we can read it in as an array with rasterio
    date_dict = find_files(date_list, prism_path, days_prior=7)

    # now the dictionary gets read in using rasterio
    raster_dict = raster_reader(date_dict)

    # which produces a dict of dates with values which area a tuple of two lists.
    # the first is a list of arrays, the second is a list of paths. This way they can be zipped later on
    # TODO - a function that outputs a list of statistics for each raster to a text file.
    format_outputter(raster_dict)

if __name__ == "__main__":

    main()

#
# def find_files(date_list, prism_path, days_prior):
#     """
#     :param days_prior: number of days prior to the date we want to look at.
#     :param date_list: list of dates in ISO format
#     :param prism_path: path to prism tiff files for ETRM
#     :return: dict of date:path of date and whatever number of days prior.
#     """
#     print "prior days", days_prior
#     date_dict = {}
#     for path, directory, file in os.walk(prism_path):
#
#         # print "FILE", file
#         for date in date_list:
#             d = date.split("-")
#             # print "d", d
#             #str = ""
#             date_string = "".join(d)
#             # print "date string", date_string
#             for i in file:
#                 name = i.split(".")[0]
#                 # print "name", name
#                 if i.endswith('.tif') and name.endswith("{}".format(date_string)):
#                     # print "Heres your guy {}".format(i)
#                     p = os.path.join(path, i)
#                     date_dict["{}".format(date)] = p
#     print "DATE DICT", date_dict
#     return date_dict