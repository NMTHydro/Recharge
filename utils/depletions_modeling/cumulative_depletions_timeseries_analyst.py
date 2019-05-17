# ===============================================================================
# Copyright 2019 Jan Hendrickx and Gabriel Parrish
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
from osgeo import ogr, gdal
import sys
from datetime import datetime
from datetime import date, timedelta
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

# ============= local library imports ===========================

"""
The purpose of this script is to use gdal/ogr to extract values of specific pixels
from a number of rasters for a given set of images based on a point shapefile.

========= PseudoCode =========

1) User makes point shapefiles in QGIS...

2) X and Y coord of shapefiles are extracted with OGR one by one:

For each shapefile:

    a) driver = ogr.GetDriverByName('')
    b) datasource = driver.Open('path.shp', 0)
    c) layer = dataSource.GetLayer()
    d) feature = layer.GetFeature(0)
    e) geometry = feature.GetGeometryRef()
    f) geometry.GetX(), GetY()

    3) x and y coords are used to read from a time series of rasters.

    For each raster:

        a) ds = gdal.Open('path', GA_ReadOnly)
        b) (get size) rows = ds.RasterYSize, cols = ds.RasterXSize, bands = ds.RasterCount
        c) (Get gorefference info) transform = ds.GetGeoTransform
        d) calculate pixel offset using x and y coords and geotransform info
        e) get the data as an array from the offsets in (d) data = band.ReadAsArray(xOffset, yOffset, 1, 1)
        value = data[0,0]

4) Value is added to a dataframe along with the date (which has been extracted before), and is output to a .csv file
for the given shapefile.

"""

def x_y_extract(point_path):
    """"""
    # get an appropriate driver
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # open the shapefile. Use 0 for read-only mode.
    datasource_obj = driver.Open(point_path, 0)
    if datasource_obj is None:
        print "cannot open {}".format(point_path)
        sys.exit(1)

    # get the layer object from the datasource
    layer_obj = datasource_obj.GetLayer()

    # get the features in the layer
    feature_count = layer_obj.GetFeatureCount()

    print "there are {} features".format(feature_count)

    # # get the feature of the shapefile. You can loop through features, but there should only be one.
    # feature = layer_obj.GetFeature(2)

    feature_dict = {}
    for i in range(1, feature_count+1, 1):

        feature = layer_obj.GetNextFeature()

        # you could get a features 'fields' like feature.GetField('id')
        field = feature.GetField('id')

        print "field -> {}".format(field)

        # but we just want the geometry of the feature
        geometry = feature.GetGeometryRef()

        # get the x and y
        x = geometry.GetX()
        y = geometry.GetY()

        print "x -> {}, y -> {}".format(x, y)

        feature_dict[field] = (x, y)

        # housekeeping
        feature.Destroy()  # always destroy the feature before the datasource

    # housekeeping
    datasource_obj.Destroy()

    return feature_dict


def raster_extract(raster_path, x, y):
    """

    :param raster_path:
    :param x:
    :param y:
    :return:
    """

    # don't forget to register
    gdal.AllRegister()

    # open the raster datasource
    datasource_obj = gdal.Open(raster_path)
    if datasource_obj is None:
        print "Can't open the datasource from {}".format(raster_path)

        # Here we make a modification, if there is missing data for any reason, just skip and sub in zeroes....
        return 0, False

    # get the size of image (for reading)
    rows = datasource_obj.RasterYSize
    cols = datasource_obj.RasterXSize

    # get georefference info to eventually calculate the offset:
    transform = datasource_obj.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    width_of_pixel = transform[1]
    height_of_pixel = transform[5]

    # read in a band (only one band)
    band = datasource_obj.GetRasterBand(1)
    # ReadAsArray(xoffset, yoffset, xcount, ycount)
    data = band.ReadAsArray(0, 0, cols, rows)



    # get the offsets so you can read the data from the correct position in the array.
    x_offset = int((x - xOrigin) / width_of_pixel)
    y_offset = int((y-yOrigin) / height_of_pixel)

    # is this a [rows, columns] thing?
    value = data[y_offset, x_offset]

    # print "VALUE {}".format(value)

    # # housekeeping
    # datasource_obj.Destroy()

    return value, True

def run_time_series_analyst(depletions_path, start_date, end_date, front_matter, shape_path, site_name = ''):


    depletions_lst = []
    date_list = []

    # construct the paths to the files in order
    d = (end_date - start_date)

    for i in range(d.days + 1):
        current_date = start_date
        current_date += timedelta(days=i)
        filename = '{}{}_{}_{}.tif'.format(front_matter, current_date.year, current_date.month, current_date.day)
        # print i
        # print filename
        filepath = os.path.join(depletions_path, filename)
        depletions_lst.append(filepath)

        # populate the timeseries here
        date_list.append(date(int(current_date.year), int(current_date.month), int(current_date.day)))

    print 'depletions list', depletions_lst
    print 'date list', date_list

    # open the shapefile and start extracting

    feature_dictionary = x_y_extract(shape_path)

    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

    # there is only one shapefile so now go and get values for each date within the loop
    dep_vals = []
    missing_vals = []
    for f in depletions_lst:
        dep_val, t_f = raster_extract(f, x, y)
        dep_vals.append(dep_val)

        # append true or false to missing vals list. True if val present. False if val missing.
        missing_vals.append(t_f)


    # filter out missing values from dep_vals and date_list
    dep_vals_clean = []
    date_list_clean = []
    for dep, dt, bul in zip(dep_vals, date_list, missing_vals):
        if bul:
            # if true, there was a value
            dep_vals_clean.append(dep)
            date_list_clean.append(dt)


    plt.plot(date_list_clean, dep_vals_clean, label='depletions in mm')

    plt.title(site_name)

    plt.xlabel('Date')
    plt.ylabel('Cumulative Depletions in mm')

    plt.grid(True)

    plt.legend(loc='upper center')

    plt.show()



if __name__ == "__main__":

    depletions_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE/jpl_depletions'

    start_date = date(2002, 1, 1)
    end_date = date(2013, 12, 31)

    front_matter = 'cumulative_depletion_'

    # shape_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results_april_8/point_extract.shp'
    shape_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE/qgis_jpl_depletions/Magdalena_mtn_extract.shp'
    # shape_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE/qgis_jpl_depletions/sangre_peak_extract.shp'
    # shape_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE/qgis_jpl_depletions/Sevilleta_plain_extract.shp'
    # print end_date - start_date3
    #
    # d = (end_date - start_date)
    #
    # print start_date + d
    #
    # for i in range(d.days):
    #     print i

    run_time_series_analyst(depletions_path, start_date, end_date, front_matter, shape_path, site_name='Magdalena Mountains')



