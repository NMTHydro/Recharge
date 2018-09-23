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

import numpy as np

# ============= local library imports ===========================




# read in the full ETRF raster.




# Loop through the raster

def linear_adj(ndvi_arr, etrf_arr, Adj_low, Adj_high):

    shape = ndvi_arr.shape

    print("shape array should be", shape, etrf_arr.shape)

    ndvi_bare = 0.15  # After Rick Allen Nov. 2016

    ndvi_veg = 0.75

    #empty list to store values which will then be turned into array.
    etrf_list = []

    for ndvi, ETrF in zip(ndvi_arr.ravel(), etrf_arr.ravel()):

        if ndvi < 0.05:
            ETrFadj = ETrF
            etrf_list.append(ETrFadj)

        elif ndvi >= 0.05 and ndvi<ndvi_bare:
            ETrFadj = ETrF + Adj_low
            etrf_list.append(ETrFadj)

        elif ndvi>= ndvi_bare and ndvi<ndvi_veg:
            ETrFadj = ETrF + Adj_low * (1-ETrF) + Adj_high * ETrF # proportional adjustment based on ETrF
            etrf_list.append(ETrFadj)

        elif ndvi >= ndvi_veg:
            ETrFadj = ETrF + Adj_high
            etrf_list.append(ETrFadj)

    ETrFadj = np.array(etrf_list).reshape(shape)

    return ETrFadj


def write_raster(stack_path, etrf_name,image, path, bounds):
    """
    image is the array that wou want to write,

    path is the output path

    window is the boundary of the window where the rasters overlap.

    driver
    width
    height
    count
    dtype
    crs
    transform
    nodata

    :return:
    """

    etrf_path = os.path.join(stack_path, etrf_name + '{}'.format(".ETrF.tif"))

    with rasterio.open(etrf_path) as src:
        cee_rs = src.crs
        T = src.affine

    path = os.path.join(path, 'adjusted_etrf_test_1.tif')

    # with rasterio.open(path,'w', driver='GTiff', height= image.shape[0], width= image.shape[1], count=1,
    #                    dtype=image.dtype, crs=cee_rs, transform=T) as etrf_adj:
    with rasterio.open(path, 'w', driver='GTiff', height=image.shape[0], width=image.shape[1], count=1,
                       dtype=image.dtype, crs=cee_rs, transform=T) as etrf_adj:

        window = etrf_adj.window(*bounds)

        etrf_adj.write(image, window=window, indexes=1) # use the same window as before

        # etrf_adj.close()


def find_bounds(stack_location):

    comparison_list = []
    comparison_dict = {}
    for directory_path, subdir, file in os.walk(stack_location, topdown=False):

        for tf in file:
            if tf.endswith(".tif"):
                tiff_path = os.path.join(directory_path, tf)

                with rasterio.open(tiff_path) as src:
                    ras = src.read(1)

                    # raster.shape -> (###,###)
                    #
                    #     raster.shape[1] raster.shape[0]

                    comparison_list.append(ras.shape[0] * ras.shape[1])

                    comparison_dict["{}".format(ras.shape[0] * ras.shape[1])] = tiff_path

    # get the minimum dimensions raster.
    val = min(comparison_list)
    min_raster_path = comparison_dict["{}".format(val)]

    print (min_raster_path)
    with rasterio.open(min_raster_path) as raster:

        ras = raster.read(1)

        print('ras shape 0', ras.shape[0])

        print('ras shape 1', ras.shape[1])

        window = ((0, ras.shape[0]), (0, ras.shape[1]))

        print("WINDOW", window)
        bounds = raster.window_bounds(window)

        print("BOUNDS", bounds)

        return bounds

    pass

def raster_dict_maker(stack_location, bounds):

    # Take the bounds from the minimum raster and for each raster in the dir,
    # get the correct window to be read in for the dict using the bounds from the min raster.
    raster_dict = {}
    for directory_path, subdir, file in os.walk(stack_location, topdown=False):

        for tf in file:
            if tf.endswith(".tif"):
                tiff_path = os.path.join(directory_path, tf)

                with rasterio.open(tiff_path) as r:
                    T0 = r.affine  # upper-left pixel corner affine transform

                    print(T0)

                    window = r.window(*bounds)

                    print("edited window", window)

                    A = r.read(1, window=window)

                print("A", A)
                print("A shape", A.shape)

                raster_dict['{}'.format(tf.split(".")[0])] = (A, tiff_path)


    return raster_dict

def run():

    Adj_low = 0.06

    Adj_high = -0.14

    drive_path = os.path.join('/', 'Volumes', 'SeagateExpansionDrive', )
    stack_path = os.path.join(drive_path, "jan_metric", 'for_stacking')
    output_path = os.path.join(drive_path, 'jan_metric', 'etrf_adjusted')

    bounds = find_bounds(stack_path)

    ndvi_name = 'LT50350312011230PAC01_NDVI'

    etrf_name = 'LT50350312011230PAC01_ETrF'

    raster_dict = raster_dict_maker(stack_path, bounds)

    ndvi_arr = raster_dict[ndvi_name][0]

    etrf_arr = raster_dict[etrf_name][0]

    print('ndvi array', ndvi_arr)

    print('etrf array', etrf_arr)


    etrf_adj_arr = linear_adj(ndvi_arr, etrf_arr, Adj_low, Adj_high)


    print("adjusted etrf array", etrf_adj_arr)

    print("adjust shape", etrf_adj_arr.shape)


    write_raster(stack_path, etrf_name, etrf_adj_arr, output_path, bounds)




if __name__ == "__main__":

    run()