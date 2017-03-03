# ===============================================================================
# Copyright 2016 dgketchum
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
import time

import gdal
from numpy import linspace, isnan


def add_extension(p, ext='.txt'):
    if not p.endswith(ext):
        p = '{}{}'.format(p, ext)
    return p


def millimeter_to_acreft(param):
    return '{:.2e}'.format((param.sum() / 1000) * (250**2) / 1233.48)


def save_master_tracker(tracker, raster_out_root):

    csv_path_filename = os.path.join(raster_out_root, 'etrm_master_tracker.csv')
    print 'this should be your master tracker csv: {}'.format(csv_path_filename)
    tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')


def unique_path(root, base, extension):
    """
    simple function for getting a unique path in a given directory

    very simplistic should not be heavily relied upon without modification

    :param root:
    :param base:
    :param extension:
    :return:
    """
    cnt = 0
    while 1:
        path = os.path.join(root, '{}-{:04n}{}'.format(base, cnt, extension))
        if not os.path.isfile(path):
            return path
        cnt += 1


def time_it(func, *args, **kw):
    print '######### {:<30s} STARTED'.format(func.func_name)
    st = time.time()
    ret = func(*args, **kw)
    print '######### {:<30s} execution time={:0.3f}'.format(func.func_name, time.time() - st)
    return ret


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
        import sys
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

    driver2 = gdal.GetDriverByName(fileformat)

    tiffname = '{}.tif'.format(filename)
    data[isnan(data)] = fillval
    # Processing
    if verbose:
        print 'Writing to temporary file {}'.format(tiffname)
        print 'Output format: {}'.format(fileformat)

    # Create Output filename from (FEWS) product name and date and open for writing
    temp_dataset = driver1.Create(tiffname, data.shape[1], data.shape[0], 1, gdal.GDT_Float32)
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

    out = driver2.CreateCopy(filename, temp_dataset, 0)

    if verbose:
        print 'Removing temporary file {}.tiff'.format(filename)
    os.remove(filename + '.tif');

    if verbose:
        print 'Writing to {} is done!'.format(filename)

    del out
    del temp_dataset

# =================================== EOF =========================
