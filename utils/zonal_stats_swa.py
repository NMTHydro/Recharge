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
import numpy as np
from rasterio import mask
import pandas as pd
from matplotlib import pyplot as plt

# ============= local library imports ===========================



def find_format(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            yield file_

def zone_stats(zone_arr, v_id, nodata_val=-9999):
    """
    Extracts zonal statistics for an array.
    :param zone_arr:
    :param v_id:
    :param nodata_val:
    :return: returns a tuple of shape id, value sum, value mean, and value count
    """

    zone_lst = zone_arr.flatten().tolist()
    zone_arr = np.array(zone_lst)

    good_vals = zone_arr[zone_arr != nodata_val]

    # print 'len of good vals list: {}'.format(len(good_vals))
    # print 'sum of good vals list: {}'.format(np.nansum(good_vals))

    # do the stats

    v_sum = np.nansum(good_vals)
    v_mean = np.nanmean(good_vals)
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
    # print 'raster shape: {}'.format(image.shape)
    # print 'raster {}'.format(image)
    # plt.imshow(image[0])
    # plt.show()
    return image[0]

def run(in_path, shp_path, out_path, run_id, param_id, divisions, time_type):

    # Need to create a way to store the tabular data. Try a list of lists.
    # For each month in the big list, there will be a list of tuples containing the area name and the sum recharge.


    shape_order = []
    if time_type == 'monthly':
        shape_order.append('month')
    elif time_type == 'annual':
        shape_order.append('year')
    for shape in find_format(shp_path, '*.shp'):
        shape_name = shape.split('.')[0]
        v_id = shape_name.split('_')[-1]
        shape_order.append(v_id)

    raster_alldat = [shape_order]
    raster_sums = [shape_order]
    raster_means = [shape_order]
    raster_counts = [shape_order]

    param_id_crit = param_id + '*.tif'
    for raster in find_format(in_path, param_id_crit):
        print '##### raster name: ', raster
        raster_path = os.path.join(in_path, raster)
        raster_name_parts = raster.split('.')[0].split('_')
        if time_type == 'monthly':
            raster_date = str(raster_name_parts[3]) + '/' + str(raster_name_parts[2])
        elif time_type == 'annual':
            raster_date = str(raster_name_parts[2])
        period_alldat = []
        period_sums = [raster_date]
        period_means = [raster_date]
        period_counts = [raster_date]

        for shape in find_format(shp_path, '*.shp'):

            # shape_data  is in format (v_id, v_sum, v_mean, v_count)

            shape_name = shape.split('.')[0]
            v_id = shape_name.split('_')[-1]   # v_id = shape_name[-4:]
            print '## shape id', v_id
            shp_file = os.path.join(shp_path, shape)
            zone = shapefile_extract(shp_file, raster_path)
            shape_data = zone_stats(zone, v_id)

            period_alldat.append(shape_data)
            period_sums.append(shape_data[1])
            period_means.append(shape_data[2])
            period_counts.append(shape_data[3])

        print 'period sums', period_sums
        print 'period means', period_means
        print 'period counts', period_counts
        raster_alldat.append(period_alldat)
        raster_sums.append(period_sums)
        raster_means.append(period_means)
        raster_counts.append(period_counts)
        print 'interim raster sum table', raster_sums
        print 'interim raster mean table', raster_means
        print 'interim raster count table', raster_counts

    print 'final raster sum table', raster_sums

    ras_sums_df = pd.DataFrame(raster_sums)
    sums_out = os.path.join(out_path, param_id + '_' + run_id + '_' + divisions + '_' + time_type + '_sums.csv')
    print 'saving {}'.format(sums_out)
    ras_sums_df.to_csv(sums_out)

    ras_means_df = pd.DataFrame(raster_means)
    means_out = os.path.join(out_path, param_id + '_' + run_id + '_' + divisions + '_' + time_type + '_means.csv')
    print 'saving {}'.format(means_out)
    ras_means_df.to_csv(means_out)

    ras_counts_df = pd.DataFrame(raster_counts)
    counts_out = os.path.join(out_path, param_id + '_' + run_id + '_' + divisions + '_' + time_type + '_counts.csv')
    print 'saving {}'.format(counts_out)
    ras_counts_df.to_csv(counts_out)


if __name__ == "__main__":
    time_type = 'monthly'  # or 'annual' set by user monthly/annual
    run_nums = ['190918_10_09_Recursive_TAWrange', '190913_08_45_SSEBop',
                '190916_17_55_EcoModel01-75_halfdrystart', '190915_11_19_JPL', '190912_16_26_EcoModel05-75',
                '190917_12_36_NRCS_soilsdatabase']
    param_names = ['tot_infil', 'tot_eta', 'tot_precip', 'tot_ro']
    division_types = ['planning_region_names', 'major_basins', 'counties_NM']
    results_root = 'C:\\Users\\Mike\\PyRANA\\PyRANA_results000'
    for run_num in run_nums:
        if time_type == 'monthly':
            pyrana_result_path = os.path.join(results_root, run_num, 'monthly_rasters')
        elif time_type == 'annual':
            pyrana_result_path = os.path.join(results_root, run_num, 'annual_rasters')
        table_out_path = os.path.join(results_root, run_num)
        for param_name in param_names:
            for division_type in division_types:
                shape_split_path = os.path.join('C:\\Users\\Mike\\PyRANA\\NMDSWB_Zones', division_type)
                run(pyrana_result_path, shape_split_path, table_out_path, run_num, param_name, division_type, time_type)


    # run_num = '190129_16_50'
    # param_name = 'tot_infil'
    # division_type = 'Planning_regions'

    # ======== EOF ==============\n