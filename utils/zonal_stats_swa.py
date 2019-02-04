# ===============================================================================
# Copyright 2019 Daniel Cadol
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
"""
The purpose of this module is to take PyRANA output rasters, especially aquifer recharge (infilt) and
extract zonal statistics (total value or average value) for the various ways that the Statewide Water
Assessment divides New Mexico. For example, there is a major basins shapefile, a county shapefile and
a planning region shapefile. The output should be provided as a table of aquifer recharge volumes for
every month of the simulation (currently Feb 2000 - Dec 2013) for each shapefile feature.

dancadol 03 February 2019
"""

# ============= standard library imports ========================
import os
import fnmatch
import rasterio
import fiona
import ogr, gdal, osr
import numpy as np

# ============= local library imports ===========================



def find_format(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            yield file_


def shapefile_extract(shapefile, raster_image):
    """
    pulls out an array of a raster vs shapefile
    :param shapefile:
    :param raster_image:
    :return:
    """

    with fiona.open(shapefile) as shp:
        geometry = [feature['geometry'] for feature in shp]

    with rasterio.open(raster_image) as rast:
        print 'raster image', raster_image
        zone, transform = rasterio.mask.mask(rast, geometry, crop=True)
    return zone[0]


def run(in_path, shp, out_path):

    # Need to create a way to store the tabular data. Try a list of lists.
    # For each month in the big list, there will be a list of tuples containing the area name and the sum recharge.

    for raster in find_format(in_path, 'tot_infil*.tif'):
        # folder, rast_name = os.path.split(raster)
        # raster_name, extention = os.path.splitext(rast_name)

        # the raster
        ras_datasource = gdal.Open(raster)

        # the vector
        shape_datasource = ogr.Open(shp)
        layer_obj = shape_datasource.GetLayer()

        # get number of features in the layer
        num_features = layer_obj.GetFeatureCount()

        # ====== iterate through features =========

        for i in range(num_features):
            feature = layer_obj.GetFeature(i)
            print "feature id {}".format(feature.GetField('id'))

            # this name is used for the naming convention of the output tables...
            feature_name = 'polygonid{}'.format(feature.GetField('id'))


if __name__ == "__main__":
    pyrana_results_raster_path = 'C:/Users/Mike/PyRANA/PyRANA_results000/'
    shapfile_to_split = 'C:/Users/Mike/PyRANA/shapefiles/mainbasins.shp'
    table_output_path = 'C:/Users/Mike/PyRANA/PyRANA_results000/'
    run(pyrana_results_raster_path, shapfile_to_split, table_output_path)

    # ======== EOF ==============\n