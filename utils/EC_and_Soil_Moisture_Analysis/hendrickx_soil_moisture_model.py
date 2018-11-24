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
from gdalconst import *

# ============= local library imports ===========================


def raster_extract(raster_path):
    """

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

    return data, arr_3d, transform, dimensions, projection, dt

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
    # print 'bool less than 75', bool_lessthan75.shape

    RZWF[bool_75 != 0] = 1.0
    # print 'rzwf post bool', RZWF.shape
    RZWF[bool_lessthan75 != 0] = (ETrF[bool_lessthan75 != 0]/0.75) * ETrF[bool_lessthan75 != 0] + ((ETrF[bool_lessthan75 != 0])/(2 * 0.75 - ETrF[bool_lessthan75 != 0]))*(1-ETrF[bool_lessthan75 != 0])

    # for val in tqdm.tqdm(np.nditer(ETrF)):
    #     if val >= 0.75:
    #         RZWF = 1.0
    #
    #     elif val < 0.75:
    #         RZWF = (ETrF/0.75) * ETrF + ((ETrF)/(2 * 0.75 - ETrF))*(1-ETrF)

    return RZWF

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

    #save memory
    # output_dataset = None

def main():
    """
    The purpose of this script is to take an ETrF/NDVI CORRECTED and PRECIP CHECKED ETrF raster image and convert it into a
     Root Zone Water Fraction (RZWF) raster based on the method laid out by Jan M. Hendrickx in his logfile:
     Log for METRIC_ETRM TAW study_22_mar_2018.docx

    :return:
    """

    # testing
    path_to_raster = '/Users/Gabe/Desktop/NM_DEM_slope/test_RZSM_processing/original_EEFLUX_images_20090713' \
                     '/LT50330362009194PAC02_ETrF/LT50330362009194PAC02_ETrF.etrf.tif'

    output_filename ='LT50330362009194PAC02_RZWF.tif'

    output_path = '/Users/Gabe/Desktop/NM_DEM_slope/test_RZSM_processing'

    raster_array, arr_3d, transform, dimensions, projection, datatype = raster_extract(path_to_raster)


    print 'This is the Transform', transform

    # # print timeit.timeit('raster_extract()')
    #
    # print 'this is the array', raster_array
    #
    # RZWF_array = stress_function(raster_array)
    #
    # arr_3d_RZWF = np.zeros(arr_3d.shape)
    #
    # arr_3d_RZWF[:, :, 0] = RZWF_array
    #
    # # map_plot = plt.imshow(arr_3d[:, :, 0])
    # # plt.show()
    # #
    # # rzwf_plot = plt.imshow(arr_3d_RZWF[:, :, 0])
    # # plt.show()
    #
    # # now we write the raster to a file.
    # write_raster(RZWF_array, transform, output_path, output_filename, dimensions, projection, datatype)


if __name__ == "__main__":
    main()