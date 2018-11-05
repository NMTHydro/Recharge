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
import glob
import numpy as np
import gdal
from gdalconst import *
import sys
# ============= local library imports ===========================

def write_raster(array, geotransform, output_path, output_filename, dimensions, projection, datatype):
    """

    :param array:
    :param geotransform:
    :param output_path:
    :param output_filename:
    :param dimensions:
    :param projection:
    :param datatype:
    :return:
    """

    filename = os.path.join(output_path, output_filename)

    driver = gdal.GetDriverByName('GTiff')
    # path, cols, rows, bandnumber, data type (if not specified, as below, the default is GDT_Byte)

    output_dataset = driver.Create(filename, dimensions[0], dimensions[1], 1, GDT_Float32)

    # we write TO the output band
    output_band = output_dataset.GetRasterBand(1)

    # we don't need to do an offset
    output_band.WriteArray(array, 0, 0)

    print 'done writing, Master.'

    # set the geotransform in order to georefference the image
    output_dataset.SetGeoTransform(geotransform)
    # set the projection
    output_dataset.SetProjection(projection)

def raster_extract(raster_path):
    """
    extracts array and geotransform information from the raster...

    :param raster_path: string - path to a raster, probably a GeoTIFF
    :return: raster array
    """
    print 'raster extract running'
    # don't forget to register
    gdal.AllRegister()

    datasource_obj = gdal.Open(raster_path, GA_ReadOnly)
    # open the raster datasource
    if datasource_obj is None:
        print "Can't open the datasource from {}".format(raster_path)
        sys.exit(1)

    # get the size of image (for reading)
    rows = datasource_obj.RasterYSize
    cols = datasource_obj.RasterXSize
    dimensions = (cols, rows)
    projection = datasource_obj.GetProjection()

    # # get georefference info
    transform = datasource_obj.GetGeoTransform()
    # xOrigin = transform[0]
    # yOrigin = transform[3]
    # width_of_pixel = transform[1]
    # height_of_pixel = transform[5]

    # read in a band (only one band)
    band = datasource_obj.GetRasterBand(1)
    # get the datatype
    dt = band.DataType
    print 'here is the data type of the original raster -> {}'.format(dt)
    # ReadAsArray(xoffset, yoffset, xcount, ycount)
    data = band.ReadAsArray(0, 0, cols, rows).astype(np.float32)

    arr_3d = np.zeros((rows, cols, datasource_obj.RasterCount))

    arr_3d[:, :, 0] = data
    # save memory
    # datasource_obj = None

    return data, transform, dimensions, projection, dt

def accumulate_arrays(path, runs, years_analysis, vars, start_year, arr_shape):
    """

    :param path:
    :param runs:
    :param years_analysis:
    :param vars:
    :return:
    """
    averaged_arrays = {}
    for v in vars:

        for i in range(years_analysis + 1):
            print i

            print 2000+i

            year_int = start_year + i

            cumulative_array = np.zeros(arr_shape)

            for i in range(runs):
                # print "_{:02d}".format(i+1)

                runs_string = "_{:02d}".format(i+1)

                filename = "{}_{}.tif".format(v, year_int)
                # print filename
                # print 'path to file', "{}/annual_rasters{}/{}".format(path, runs_string, filename)
                arr, transform, dim, proj, dt = raster_extract("{}/annual_rasters{}/{}".format(path, runs_string, filename))

                # accumulate array totals for the each stochastic run
                cumulative_array += arr

            average_arr = cumulative_array/runs

            averaged_arrays["{}_{}.tif".format(v, year_int)] = average_arr

    print 'averaged arrays,', averaged_arrays

    return averaged_arrays



def run():
    """

    :return:
    """
    path_to_yearlies = "/Volumes/Seagate_Expansion_Drive/sunshine_valley/clipped_outputs_10_15_18"

    output_path = "/Volumes/Seagate_Expansion_Drive/sunshine_valley/averaged_yearlies_10_15_18"

    # sample file to get georefference info...
    sample_tif = "/Volumes/Seagate_Expansion_Drive/sunshine_valley/clipped_outputs_10_15_18/annual_rasters_01/tot_eta_2001.tif"

    arr, transform, dim, proj, dt = raster_extract(sample_tif)

    shp = arr.shape

    number_of_runs = 22

    start_year = 2000

    years_of_analysis = 13
    # todo - took out 'tot_etrs' bc tot_etrs_2002 missing??
    variables = ['tot_eta','tot_infil', 'tot_precip', 'tot_ro']

    averaged_arrays = accumulate_arrays(path=path_to_yearlies, runs=number_of_runs, years_analysis=years_of_analysis, vars=variables,
                      start_year=start_year, arr_shape=shp)

    for k, v in averaged_arrays.iteritems():

        write_raster(v, transform, output_path, output_filename=k, dimensions=dim, datatype=dt, projection=proj)

    # for i in range(number_of_runs):
    #
    #     print "annual_rasters_{:02}".format(i+1)
    #
    #     direct = "annual_rasters_{:02}".format(i+1)
    #
    #     directory_path = os.path.join(path_to_yearlies, direct)
    #
    #     for file in os.listdir(directory_path):
    #         print 'file', file
    #
    #         for i in range(years_of_analysis):
    #             print glob.glob("{}/".format(directory_path))
    #
    #             # todo - how do we match the outputs one at a time across directories?
    #             # use rasterio. Try writing out pseudocode.


if __name__ == "__main__":
    run()