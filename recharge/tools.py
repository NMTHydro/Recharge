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
from datetime import datetime
from dateutil import rrule
from numpy import linspace, isnan


def day_generator(start, end):
    if isinstance(start, (str, unicode)):
        start = datetime.strptime(start, '%m/%d/%Y')

    if isinstance(end, (str, unicode)):
        end = datetime.strptime(end, '%m/%d/%Y')

    return rrule.rrule(rrule.DAILY, dtstart=start, until=end)


def add_extension(p, ext='.txt'):
    if not p.endswith(ext):
        p = '{}{}'.format(p, ext)
    return p


def millimeter_to_acreft(param):
    return (param.sum() / 1000.0) * (250.0 ** 2) / 1233.48


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


def write_map(fileName, fileFormat, x, y, data, prj, FillVal):
    """
    Write geographical data into file. Also replave NaN bu FillVall

    :param fileName:
    :param fileFormat:
    :param x:
    :param y:
    :param data:
    :param FillVal:
    :return:
    """

    verbose = False
    gdal.AllRegister()
    driver1 = gdal.GetDriverByName('GTiff')
    driver2 = gdal.GetDriverByName(fileFormat)

    data[isnan(data)] = FillVal
    # Processing
    if verbose:
        print 'Writing to temporary file ' + fileName + '.tif'
        print "Output format: " + fileFormat
    # Create Output filename from (FEWS) product name and date and open for writing
    TempDataset = driver1.Create(fileName + '.tif', data.shape[1], data.shape[0], 1, gdal.GDT_Float32)
    # Give georeferences
    xul = x[0] - (x[1] - x[0]) / 2
    yul = y[0] + (y[0] - y[1]) / 2

    TempDataset.SetGeoTransform([xul, x[1] - x[0], 0, yul, 0, y[1] - y[0]])
    TempDataset.SetProjection(prj)
    # get rasterband entry
    TempBand = TempDataset.GetRasterBand(1)
    # fill rasterband with array
    TempBand.WriteArray(data, 0, 0)
    TempBand.FlushCache()
    TempBand.SetNoDataValue(FillVal)
    # Create data to write to correct format (supported by 'CreateCopy')
    if verbose:
        print 'Writing to ' + fileName
    outDataset = driver2.CreateCopy(fileName, TempDataset, 0)
    TempDataset = None
    outDataset = None
    if verbose:
        print 'Removing temporary file ' + fileName + '.tif'
    os.remove(fileName + '.tif');

    if verbose:
        print 'Writing to ' + fileName + ' is done!'

# =================================== EOF =========================
