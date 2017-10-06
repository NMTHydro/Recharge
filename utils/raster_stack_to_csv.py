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
import rasterio
from rasterio import windows
import numpy as np
from numpy import meshgrid, arange
from affine import Affine
from pyproj import Proj, transform
from utils.pixel_coord_finder import coord_getter
from recharge.raster_tools import convert_raster_to_array, convert_array_to_raster

import multiprocessing as mp

import pandas as pd

# ============= local library imports ===========================


def x_y(path_to_an_array): # input

    with rasterio.open(path_to_an_array) as r: # input[1] is path
        T0 = r.affine  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        A = r.read(1)  # pixel values

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[1]), np.arange(A.shape[1])) # input[0] is the array

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    #print "T1",T1
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * T1

    # All eastings and northings (there is probably a faster way to do this)
    northings, eastings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

    return eastings, northings


def data_frame_formatter(raster_dictionary):

    """

    :param raster_dictionary:
    :return: saved csvs

    Each raster will get written into a dict with certain info, then the dict will get turned into a
    dataframe and the dataframes will all get merged into one. This will then be exported and saved as a csv.
    Cool? Cool.

    dict = {column heading : [list of values]}

    cols = x(easting), y(northing), nlcd, ETrF, NDVI

    """

    nCores = 2

    ras_dict = {}

    print "ras dict being populated"
    input_path = raster_dictionary['aligned_nlcd_full_warp_near_clip_3336'][1]

    print input_path

    x, y = x_y(input_path)

    x = x.ravel().tolist()

    # print "x flatten tolist", x

    y = y.ravel().tolist()

    ras_dict["x"] = x
    ras_dict["y"] = y

    print "x, y is done. Starting k, v loop"

    for k, v in raster_dictionary.iteritems():

        # inputs = [v[0], v[1]]
        #
        # print "v 0 ", v[0]
        #
        # print "v 1", v[1]
        #
        # x, y = x_y(inputs)
        # pool = mp.Pool(processes=nCores)
        # x, y = pool.map(x_y, [v[0], v[1]])

        # x = x.ravel().tolist()
        #
        # # print "x flatten tolist", x
        #
        # y = y.ravel().tolist()
        #
        # ras_dict["x"] = x
        # ras_dict["y"] = y

        ras_dict["{}".format(k)] = v[0].ravel().tolist()

    print "Done wi kv loop"

    col_list = ["x", "y"]

    for key in ras_dict.keys():

        col_list.append(key)


    #print ras_dict

    for k, v in ras_dict.iteritems():

        print len(v)

    # df = pd.DataFrame(ras_dict, columns=col_list)
    #
    # # print df
    #
    # print "SAVING"
    #
    # df.to_csv("/Volumes/SeagateExpansionDrive/stack_csv.csv")


def run():
    drive_path = os.path.join('/', 'Volumes', 'SeagateExpansionDrive', )
    tiff_path = os.path.join(drive_path, 'for_stacking', 'aligned_nlcd_full_warp_near_clip_3336.tif')
    stack_location = os.path.join(drive_path, 'for_stacking')
    #x, y = coord_getter(tiff_path)

    # print "x", x
    #
    # print "y", y

    raster_dict = {}

    for directory_path, subdir, file in os.walk(stack_location, topdown=False):

        #print 'dir path', directory_path
        # print file
        for tf in file:
            if tf.endswith(".tif"):
                tiff_path = os.path.join(directory_path, tf)
                with rasterio.open(tiff_path) as r:
                    T0 = r.affine  # upper-left pixel corner affine transform
                    p1 = Proj(r.crs)
                    A = r.read(1)  # pixel values
                print "A", A
                print "A shape", A.shape
                raster_dict['{}'.format(tf.split(".")[0])] = (A, tiff_path)


    print 'raster dict', raster_dict

    print "Starting the formatter"

    data_frame_formatter(raster_dict)

    # nCores = os.environ

    # nCores = 2
    #
    # print nCores
    #
    # nSmp = 10000000
    #
    # m = 40
    #
    # def f(input):
    #     np.random.seed(input[0])
    #
    #     return np.mean(np.random.normal(0, 1, input[1]))
    #
    # # create list of tuples to iterate over
    # inputs = [(i, nSmp) for i in xrange(m)]
    #
    # inputs[0:2]
    #
    # pool = mp.Pool(processes = nCores)
    #
    # results = pool.map(f, inputs[0:2])
    #
    # print results


if __name__ == "__main__":

    run()