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
import gdal
import sys
import numpy as np
from matplotlib import pyplot as plt
# from matplotlib import image as mpimg
import pandas as pd
import timeit
import tqdm

# ============= local library imports ===========================

def raster_extract(raster_path):
    """

    :param raster_path: string - path to a raster, probably a GeoTIFF
    :return: raster array
    """
    print 'raster extract running'
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

    # get georefference info
    transform = datasource_obj.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    width_of_pixel = transform[1]
    height_of_pixel = transform[5]

    # read in a band (only one band)
    band = datasource_obj.GetRasterBand(1)
    # ReadAsArray(xoffset, yoffset, xcount, ycount)
    data = band.ReadAsArray(0, 0, cols, rows)

    arr_3d = np.zeros((rows, cols, datasource_obj.RasterCount))

    arr_3d[:, :, 0] = data

    # # xlist = []
    # distfromorigin = 0
    # for x in range(rows):
    #     # xlist.append(xOrigin + distfromorigin)
    #     arr_3d[x, :, :] = xOrigin + distfromorigin
    #     distfromorigin += width_of_pixel
    #
    # # ylist = []
    # distfromorigin = 0
    # for y in range(cols):
    #     # ylist.append(yOrigin - distfromorigin)
    #     arr_3d[:, y, :] = yOrigin - distfromorigin
    #     distfromorigin += height_of_pixel

    # x_arr = np.array(xlist)
    # y_arr = np.array(ylist)
    flat_vals = data.ravel
    # print 'len x_arr', x_arr.shape
    # print 'len y arr', y_arr.shape

    # plot_data = (xlist, ylist, flat_vals)

    return data, arr_3d #plot_data

def stress_function(ETrF):
    """

    :param ETrF:
    :return:
    """
    print 'stress function running'
    # Make a RZWF array based on the size of ETrF
    dim = ETrF.shape

    print 'dim', dim

    RZWF = np.zeros(dim)

    bool_75 = ETrF >= 0.75
    bool_lessthan75 = ETrF < 0.75
    print 'bool less than 75', bool_lessthan75.shape

    RZWF[bool_75 != 0] = 1.0
    print 'rzwf post bool', RZWF.shape
    RZWF[bool_lessthan75 != 0] = (ETrF[bool_lessthan75 != 0]/0.75) * ETrF[bool_lessthan75 != 0] + ((ETrF[bool_lessthan75 != 0])/(2 * 0.75 - ETrF[bool_lessthan75 != 0]))*(1-ETrF[bool_lessthan75 != 0])

    # for val in tqdm.tqdm(np.nditer(ETrF)):
    #     if val >= 0.75:
    #         RZWF = 1.0
    #
    #     elif val < 0.75:
    #         RZWF = (ETrF/0.75) * ETrF + ((ETrF)/(2 * 0.75 - ETrF))*(1-ETrF)

    return RZWF

def main():
    """
    The purpose of this script is to take an ETrF/NDVI CORRECTED and PRECIP CHECKED ETrF raster image and convert it into a
     Root Zone Water Fraction (RZWF) raster based on the method laid out by Jan M. Hendrickx in his logfile:
     Log for METRIC_ETRM TAW study_22_mar_2018.docx

    :return:
    """

    # testing
    path_to_raster = '/Users/Gabe/Desktop/NM_DEM_slope/test_RZSM_processing/original_EEFLUX_images_20090713/' \
                     'LT50330362009194PAC02_ETrF/LT50330362009194PAC02_ETrF.etrf.tif'

    raster_array, arr_3d = raster_extract(path_to_raster)
    # print timeit.timeit('raster_extract()')

    print 'this is the array', raster_array

    # def test():
    #     """Stupid test function"""
    #     L = []
    #     for i in range(100):
    #         L.append(i)
    #
    # if __name__ == '__main__':
    #     import timeit
    #     print(timeit.timeit("test()", setup="from __main__ import test"))

    RZWF_array = stress_function(raster_array)

    arr_3d_RZWF = np.zeros(arr_3d.shape)

    arr_3d_RZWF[:, :, 0] = RZWF_array

    # print timeit.timeit('stress_function()')

    # plt.plot(RZWF_array)
    # plt.show()
    # img = mpimg.imread(RZWF_array)

    map_plot = plt.imshow(arr_3d[:, :, 0])
    plt.show()

    rzwf_plot = plt.imshow(arr_3d_RZWF[:, :, 0])
    plt.show()


if __name__ == "__main__":
    main()