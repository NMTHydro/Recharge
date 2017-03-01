# Copyright 2016 pmrevelle
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

import os
import sys
import datetime
import gdal
from numpy import linspace, isnan
from dateutil import rrule
from recharge.raster_tools import convert_raster_to_array

NUMS = (1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
        225, 241, 257, 273, 289, 305, 321, 337, 353)


def read_map(filename, fileformat):
    """
    ead geographical file into memory

    :param filename: Name of the file to read
    :param fileformat: Gdal format string
    :param logger: logger object
    :return: res_x, res_y, cols, rows, x, y, data, fill_val
    """

    # Open file for binary-reading

    mapFormat = gdal.GetDriverByName(fileformat)
    mapFormat.Register()
    ds = gdal.Open(filename)
    prj = ds.GetProjection()
    if ds is None:
        print('Could not open {}. Something went wrong!! Shutting down'.format(filename))
        sys.exit(1)

    # Retrieve geoTransform info
    geotrans = ds.GetGeoTransform()
    origin_x = geotrans[0]
    origin_y = geotrans[3]
    res_x = geotrans[1]
    res_y = geotrans[5]
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    x = linspace(origin_x + res_x / 2, origin_x + res_x / 2 + res_x * (cols - 1), cols)
    y = linspace(origin_y + res_y / 2, origin_y + res_y / 2 + res_y * (rows - 1), rows)
    # Retrieve raster
    raster_band = ds.GetRasterBand(1)  # there's only 1 band, starting from 1
    data = raster_band.ReadAsArray(0, 0, cols, rows)
    fill_val = raster_band.GetNoDataValue()

    # raster_band = None

    del ds
    return res_x, res_y, cols, rows, x, y, data, prj, fill_val


def write_map(filename, fileformat, x, y, data, prj, fillval):
    """
    Write geographical data into file. Also replace NaN by fillval

    :param filename:
    :param fileformat:
    :param x:
    :param y:
    :param data:
    :param fillval:
    :return:
    """

    verbose = False
    gdal.AllRegister()
    driver1 = gdal.GetDriverByName('GTiff')

    # driver2 = gdal.GetDriverByName(fileformat)

    data[isnan(data)] = fillval
    # Processing
    if verbose:
        print 'Writing to temporary file {}.tiff'.format(filename)
        print 'Output format: {}'.format(fileformat)

    # Create Output filename from (FEWS) product name and date and open for writing
    temp_dataset = driver1.Create('{}.tif'.format(filename), data.shape[1], data.shape[0], 1, gdal.GDT_Float32)
    # Give georeferences
    xul = x[0] - (x[1] - x[0]) / 2
    yul = y[0] + (y[0] - y[1]) / 2

    temp_dataset.SetGeoTransform([xul, x[1] - x[0], 0, yul, 0, y[1] - y[0]])
    temp_dataset.SetProjection(prj)
    # get rasterband entry
    temp_band = temp_dataset.GetRasterBand(1)
    # fill rasterband with array
    temp_band.WriteArray(data, 0, 0)
    temp_band.FlushCache()
    temp_band.SetNoDataValue(fillval)
    # Create data to write to correct format (supported by 'CreateCopy')
    if verbose:
        print 'Writing to {}'.format(filename)

    # outDataset = driver2.CreateCopy(filename, temp_dataset, 0)
    # temp_dataset = None
    # outDataset = None

    if verbose:
        print 'Removing temporary file {}.tiff'.format(filename)
    os.remove(filename + '.tif');

    if verbose:
        print 'Writing to {} is done!'.format(filename)


def get_kcb(in_path, date_object):
    """
    Find NDVI image and convert to Kcb.

    :param in_path: NDVI input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :return: numpy array object
    """
    # print date_object
    doy = date_object.timetuple().tm_yday
    year = date_object.year
    # print('date object', date_object)

    if year == 2000:
        band = 1
        raster = '{}_{}.tif'.format(year, doy)
    elif year == 2001:
        for num in NUMS:
            diff = doy - num
            if 0 <= diff <= 15:
                start = num
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15

                band = diff + 1
                raster = '{}_{}_{}.tif'.format(year, start, nd)
                print('raster', raster)
                break
    else:
        for i, num in enumerate(NUMS):
            diff = doy - num
            if 0 <= diff <= 15:
                band = diff + 1
                raster = '{}_{}.tif'.format(year, i + 1)
                break

    ndvi = convert_raster_to_array(in_path, raster, band=band)

    return ndvi


if __name__ == '__main__':
    input_root = 'F:\\ETRM_Inputs'
    # mask = 'Mask'
    # mask_path = os.path.join(input_root, mask)
    ndvi_path = os.path.join(input_root, 'NDVI', 'NDVI_std_all')

    penman_path = os.path.join(input_root, 'PM_RAD')
    penman_example = 'PM_NM_2000_001.tif'
    map_for_reference = os.path.join(penman_path, '2000', penman_example)
    resX, resY, cols, rows, x, y, data, prj, fill_val = read_map(map_for_reference, 'Gtiff')

    # print('ndvi_path',ndvi_path)

    start = datetime.datetime(2000, 1, 1, 0)
    end = datetime.datetime(2001, 12, 31, 0)

    fill_val = -999.

    for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        year = day.strftime('%Y')
        month = day.strftime('%m')
        day_mth = day.strftime('%d')

        new_dir = 'NDVI_individ'
        # yearstr = str(year)
        output_dir = os.path.join(input_root, new_dir, year)
        # print(output_dir)

        ndvi = get_kcb(ndvi_path, day)

        # kcb = remake_array(mask_path, kcb)
        ndvi[ndvi == fill_val] = 0
        # print(ndvi, ndvi.shape)

        new_ndvi = 'NDVI{}_{}_{}.tif'.format(year, month, day_mth)
        ndvi_out = os.path.join(output_dir, new_ndvi)

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        write_map(ndvi_out, 'Gtiff', x, y, ndvi, prj, fill_val)
        print('Saving New NDVI file as ' + str(ndvi_out))

# ============= EOF =============================================
