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
import math
import rasterio
import fiona
import ogr, gdal, osr
import numpy as np
from rasterio import mask
from matplotlib import pyplot as plt

# ============= local library imports ===========================



def find_format(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            yield file_

def zone_stats(zone_arr, v_id, nodata_val=-9999):
    """"""

    # print 'zone arr shape', zone_arr.shape
    zone_lst = zone_arr.flatten().tolist()
    # print 'len of zone list', len(zone_lst)

    good_vals = []
    for i in zone_lst:
        if i != nodata_val:
            good_vals.append(i)
    # print 'length of good vals', len(good_vals)

    # do the stats

    v_sum = np.sum(good_vals)
    v_mean = np.mean(good_vals)
    v_count = len(good_vals)

    return (v_id, v_sum, v_mean, v_count)


def shapefile_extract(shapefile, raster_image):
    """
    pulls out an array of a raster vs shapefile
    :param shapefile:
    :param raster_image:
    :return:
    """

    with fiona.open(shapefile) as shp:
        geometry = [feature['geometry'] for feature in shp]
        # print 'geometry {}'.format(geometry)
    with rasterio.open(raster_image) as rast:
        # print 'raster image', raster_image
        image, transform = rasterio.mask.mask(rast, geometry, crop=True, nodata=-9999)

    # print 'transform', transform
    # print 'shape', image.shape
    # plt.imshow(image[0])
    # plt.show()
    return image[0]

def run(in_path, shp, out_path):

    # Need to create a way to store the tabular data. Try a list of lists.
    # For each month in the big list, there will be a list of tuples containing the area name and the sum recharge.


    # todo - output a list of tuples

    raster_alldat = []
    raster_sums = []
    raster_means = []
    raster_counts = []

    for raster in find_format(in_path, 'tot_infil*.tif'):
        print '##### raster name: ', raster
        raster_path = os.path.join(in_path, raster)
        month_alldat = []
        month_sums = []
        month_means = []
        month_counts = []

        for shape in os.listdir(shp):

            # shape_data  is in format (v_id, v_sum, v_mean, v_count)

            if shape.endswith('.shp'):
                shape_name = shape.split('.')[0]
                v_id = shape_name[-4:]
                print '## shape id', v_id
                shp_path = os.path.join(shp, shape)
                zone = shapefile_extract(shp_path, raster_path)
                shape_data = zone_stats(zone, v_id)

                month_alldat.append(shape_data)
                month_sums.append(shape_data[1])
                month_means.append([shape_data[2]])
                month_counts.append([shape_data[3]])

        print 'month sums', month_sums
        print 'month means', month_means
        print 'month counts', month_counts
        raster_alldat.append(month_alldat)
        raster_sums.append(month_sums)
        raster_means.append(month_means)
        raster_counts.append(month_counts)
        print 'interim raster sum table', raster_sums
        print 'interim raster mean table', raster_means
        print 'interim raster count table', raster_counts

    print 'final raster sum table', raster_sums





# =====================================================================================================================

        # the raster
        # ras_datasource = gdal.Open(raster)
    #
    #     # the vector
    #     shape_datasource = ogr.Open(shp)
    #     layer_obj = shape_datasource.GetLayer()
    #
    #     # get number of features in the layer
    #     num_features = layer_obj.GetFeatureCount()
    #
    #     # ====== iterate through features =========
    #
    #     for i in range(num_features):
    #         feature = layer_obj.GetFeature(i)
    #         print "feature id {}".format(feature.GetField('id'))
    #
    #         # this name is used for the naming convention of the output tables...
    #         feature_name = 'polygonid{}'.format(feature.GetField('id'))
    #
    #         print 'feature name: ', feature_name


if __name__ == "__main__":
    # pyrana_results_raster_path = 'C:\\Users\\Mike\\PyRANA\\PyRANA_results000\\190126_05_56\\monthly_rasters'
    # shapfile_split_path = 'C:\Users\Mike\PyRANA\NMDSWB_Zones\Planning_regions'
    # table_output_path = 'C:\\Users\\Mike\\PyRANA\\PyRANA_results000\\190126_05_56'

    pyrana_results_raster_path = '/Users/dcadol/Desktop/academic_docs_II/test_DAN/rasters'
    shapfile_split_path = '/Users/dcadol/Desktop/academic_docs_II/test_DAN/shapefiles'
    table_output_path = '/Users/dcadol/Desktop/academic_docs_II/test_DAN/table'

    run(pyrana_results_raster_path, shapfile_split_path, table_output_path)

    # ======== EOF ==============\n