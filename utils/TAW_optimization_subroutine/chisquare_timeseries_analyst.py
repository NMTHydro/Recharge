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
from datetime import date
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
        sys.exit(1)

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

    return value


def run_point_extract(point_path, raster_path, ending, landsat=False, sseb=False, output_path=None):
    """

    :param output_path:
    :param point_path:
    :param raster_path:
    :param ending:
    :return:
    """

    # Begin extraction from the point path.
    feature_dictionary = x_y_extract(point_path)
    print "feature dictionary", feature_dictionary

    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():

        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

        # === Iterate the rasters ===

        # Containers to hold the dates and values for the rasters
        raster_date = []
        raster_values = []

        sseb_dict = {}

        # store the raster values and image dates for the x and y coordinate pair into the lists
        for path, dir, file in os.walk(raster_path, topdown=False):

            print path, dir, file

            for file in file:
                if file.endswith(ending):

                    # path to the raster file
                    raster_address = os.path.join(path, file)


                    if landsat:

                        # Format the date into dt object
                        date_str = file.split('_')[0]
                        date_str = date_str[-12:-5]

                        print "date string {}".format(date_str)
                        # get a datetime object from a julian date
                        r_date = datetime.strptime(date_str, '%Y%j').date()
                        raster_date.append(r_date)

                    if sseb:
                        name = file.split('.')[0]
                        year = int(name.split('_')[-2])
                        month = int(name.split('_')[-1])
                        r_date = date(year, month, 1)
                        raster_date.append(r_date)


                    # get the raster value using raster_extract() function
                    value = raster_extract(raster_address, x, y)
                    raster_values.append(value)

        if landsat:
            # format the values from the different dates into a dataframe
            output_dict = {'date': raster_date, 'value': raster_values}
            output_df = pd.DataFrame(output_dict, columns=['date', 'value'])
            csv_path = os.path.join(output_path, "point_shape_id_{}.csv".format(feature))

            # use the pandas.to_csv() method to output to csv
            output_df.to_csv(csv_path)

        if sseb:
            output_dict = {'date': raster_date, 'value': raster_values}

            sseb_dict['{}'.format(feature)] = output_dict

    if sseb:
        return sseb_dict


    print "COMPLETE"

def run_chi_analyst(dc_path, optimal_taw_path, chi_square_path, shape_path, output_path):
    """"""

    # Begin extraction from the point path.
    feature_dictionary = x_y_extract(shape_path)
    print "feature dictionary", feature_dictionary

    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

        # === Iterate the rasters ===
        taws = []
        chi_square_vals = []

        # store the raster values and image dates for the x and y coordinate pair into the lists
        for path, dir, file in os.walk(chi_square_path, topdown=True):
            # print path, dir, file

            for f in file:
                print f

                if f.startswith('rss') and f.endswith('.tif'):

                    filepath = os.path.join(path, f)

                    file_name = f.split('.')[0]
                    taw_val = int(file_name.split('_')[-1])
                    taws.append(taw_val)

                    chi_value = raster_extract(filepath, x, y)
                    chi_square_vals.append(chi_value)

        # extract delta chi
        delta_chi_val = raster_extract(dc_path, x, y)

        plt.scatter(taws, chi_square_vals, label='chi square')

        plt.title('plot of chi square against taw for a pixel')

        plt.xlabel('TAW')
        plt.ylabel('chi sq')

        plt.grid(True)

        plt.axhline(y=delta_chi_val, color='r', linestyle='-', label='95% ci line')
        plt.legend(loc='upper center')

        plt.show()





if __name__ == "__main__":


    # delta chi path
    dc_path = '/Volumes/Seagate_Blue/taw_optimization_etrm_outputs_april_8_N_Central_nm_2m/outputs_april_15/delta_chi.tif'

    # optimal TAW
    optimal_taw_path= '/Volumes/Seagate_Blue/taw_optimization_etrm_outputs_april_8_N_Central_nm_2m/outputs_april_15/optimized_taw.tif'

    # General path (to get Chi^2)
    chi_square_path = '/Volumes/Seagate_Blue/taw_optimization_etrm_outputs_april_8_N_Central_nm_2m/outputs_april_15'

    # path to shapefile

    shape_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results_april_8/point_extract.shp'

    # output location
    output_path = '/Volumes/Seagate_Blue/taw_optimization_etrm_outputs_april_8_N_Central_nm_2m/outputs_april_15/point_extract_output'

    run_chi_analyst(dc_path, optimal_taw_path, chi_square_path, shape_path, output_path)

    #
    # # path to a single point shapefile:
    # point_path = '/Users/Gabe/Desktop/juliet_stuff/remote_sensing_data_extraction/shapefile/data_extracter.shp'
    #
    # # path to the rasters (RZWF)
    # raster_path = '/Users/Gabe/Desktop/hard_drive_overflow/METRIC_ETRM_Jornada_RZWF_P33R37'
    #
    # # files end with this extension
    # ending = '.img'
    #
    # run_point_extract(point_path, raster_path, ending, landsat=True, output_path=output_path)