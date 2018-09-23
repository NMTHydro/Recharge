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
from numpy import ones, arange, r_, meshgrid
import osr
from datetime import datetime, timedelta
from dateutil import rrule
import scipy.ndimage as ndimage

from recharge import NUMS, NUMSIZE
from recharge.tools import write_map, read_map
from app.paths import paths
# For Walnut Gulch
C = 243	#2304,NM
R = 74 #3154,NM


def time_interpolation(base_dir, day, finalyear):

    year = day.year

    #base_dir = 'G:\\Walnut\\Modis\\'
    # output  'F:\\ETRM_Inputs\\NDVI_spline\\'

    cnt = day.timetuple().tm_yday
    i = 0
    first_date = 0
    while first_date == 0:
        # print(i)
        if cnt == NUMS[i]:
            first_date = NUMS[i]
            next_date = NUMS[i + 1]
        elif (cnt < NUMS[i]) and (cnt > NUMS[i - 1]):
            # print('two')
            first_date = NUMS[i - 1]
            next_date = NUMS[i]
        elif (cnt > NUMS[i]) and (cnt < NUMS[i + 1]):
            # print('three')
            # print(NUMS[i + 1])
            first_date = NUMS[i]
            next_date = NUMS[i + 1]
        elif (cnt >= 353) and (year == finalyear):
            first_date = NUMS[NUMSIZE - 1]
            # print('first_date: ', first_date)
            next_date = first_date
            # print('next_date: ', next_date)
        elif cnt >= 353:
            first_date = NUMS[NUMSIZE - 1]
            # print('first_date: ', first_date)
            i = 0
            next_date = NUMS[i]
            # print('next_date: ', next_date)

        i += 1

    print('-----------------------------------------------------------------------------')
    print('DOY:', cnt)
    # print(year)
    raster_first_date = datetime(year, 1, 1) + timedelta(first_date - 1)
    print('raster first date: ', raster_first_date)

    td = timedelta(next_date - 1)
    if (cnt >= 353) and (year == finalyear):
        newyear = year
        raster_next_date = datetime(newyear, 1, 1) + td
    elif cnt >= 353:
        newyear = year + 1
        # print(year)
        raster_next_date = datetime(newyear, 1, 1) + td
    elif cnt < 353:
        newyear = year
        raster_next_date = datetime(newyear, 1, 1) + td

    rfd = raster_first_date.timetuple()
    # tail = '{}_{:02n}_{:02n}.tif'.format(year, rfd.tm_mon, rfd.tm_mday)
    tail = '{}{:03n}.tif'.format(year, rfd.tm_yday)


    raster_now = os.path.join(base_dir, '{}'.format(tail))
    print('First raster to interpolate: ', raster_now)

    # resX, resY, cols, rows, Lon, Lat, ndvi, prj, FillVal = read_map(os.path.join(base_dir, raster_now), 'Gtiff')
    ndvi = read_map(os.path.join(base_dir, raster_now), 'Gtiff')[6]

    rnd = raster_next_date.timetuple()
    # tail2 = '{}_{:02n}_{:02n}.tif'.format(newyear, rnd.tm_mon, rnd.tm_mday)
    tail2 = '{}{:03n}.tif'.format(newyear, rnd.tm_yday)

    raster_next = os.path.join(base_dir, '{}'.format(tail2))
    print('Future raster to interpolate with: ', raster_next)

    # resX, resY, cols, rows, Lon, Lat, ndvinext, prj, FillVal = read_map(os.path.join(base_dir, raster_next), 'Gtiff')
    ndvinext = read_map(os.path.join(base_dir, raster_next), 'Gtiff')[6]

    # arr1 = ndvi
    # arr2 = ndvinext

    # rejoin Linke, LinkeNext into a single array of shape (2, 2160, 4320)
    arr = r_['0,3', ndvi, ndvinext]
    # print('arr.shape',arr.shape)

    # define the grid coordinates where you want to interpolate
    latitude_index = arange(R)
    longitude_index = arange(C)
    y, x = meshgrid(longitude_index, latitude_index)
    # print('X',X)
    # print(X.shape)
    # print('Y',Y)
    # print(Y.shape)

    # Setup time variables for interpolation
    days_dif = raster_next_date - day
    days_dif = float(days_dif.days)
    max_days_diff = raster_next_date - raster_first_date
    max_days_diff = float(max_days_diff.days)
    # proportion = float(days_dif / max_days_diff)
    # print('proportion',proportion)
    print('day', day)
    print('days difference from next ndvi raster', days_dif)
    print('out of max days difference', max_days_diff)

    if (cnt >= 353) and (year == finalyear):
        interp = 0.0  # Set to 0 otherwise will divide by zero and give error
    else:
        interp = 1 - (days_dif / max_days_diff)  # 1 = weight completely next month values, 0 = previous month
    print('interp ratio between monthly images', interp)

    # 0.5 corresponds to half way between arr1 and arr2
    coordinates = ones((R, C)) * interp, x, y
    # coordones = np.ones((2525, 2272)) * interp
    # print('coordinates',coordinates)
    # print(coordones.shape)

    # given arrays, interpolate at coordinates (could be any subset but in this case using full arrays)
    newarr = ndimage.map_coordinates(arr, coordinates, order=2)

    return newarr


# def add_one_month(dt0):
#     dt1 = dt0.replace(day=1)
#     dt2 = dt1 + timedelta(days=32)
#     dt3 = dt2.replace(day=1)
#     return dt3
#
# def subtract_one_month(dt0):
#     dt1 = dt0.replace(day=1)
#     dt2 = dt1 - timedelta(days=2)
#     dt3 = dt2.replace(day=1)
#     return dt3


def main():
    paths.build('F:')

    startday = datetime(2000, 2, 18, 0)
    endday = datetime(2016, 1, 1, 0)
    finalyear = 2016

    base_dir = 'H:\\Walnut\\Modis\\'#paths.ndvi_individ
    output ='H:\\Walnut\\Modis\\InterNew'#paths.ndvi_spline

    ref_map = os.path.join(base_dir, 'RR2000049.tif')
    _, _, _, _, lon, lat, linke, prj, fill_val = read_map(ref_map, 'Gtiff')

    srs = osr.SpatialReference(prj)
    sr_wkt = srs.ExportToWkt()

    for day in rrule.rrule(rrule.DAILY, dtstart=startday, until=endday):
        nr = day.strftime('%j')
        year = day.strftime('%Y')

        # ndvi_daily = time_interpolation(day, lat, lon, finalyear)
        ndvi_daily = time_interpolation(base_dir, day, finalyear)

        # Write daily values to new daily rasters
        daily_doy = 'ndvi{}_{}.tif'.format(year, nr) # or modis, lol
        outpath = os.path.join(output, year)

        if not os.path.exists(outpath):
            os.makedirs(outpath)

        outname = os.path.join(outpath, daily_doy)
        write_map(outname, 'Gtiff', lon, lat, ndvi_daily, sr_wkt, fill_val)


if __name__ == '__main__':
    main()


# =================================== EOF =========================
# def readMap(fileName, fileFormat):
#     """
#     read geographical file into memory
#
#     :param fileName: Name of the file to read
#     :param fileFormat: Gdal format string
#     :param logger: logger object
#     :return: resX, resY, cols, rows, x, y, data, FillVal
#     """
#
#     # Open file for binary-reading
#
#     mapFormat = gdal.GetDriverByName(fileFormat)
#     mapFormat.Register()
#     ds = gdal.Open(fileName)
#     prj = ds.GetProjection()
#     # Retrieve geoTransform info
#     geotrans = ds.GetGeoTransform()
#     originX = geotrans[0]
#     originY = geotrans[3]
#     resX = geotrans[1]
#     resY = geotrans[5]
#     cols = ds.RasterXSize
#     rows = ds.RasterYSize
#     x = np.linspace(originX + resX / 2, originX + resX / 2 + resX * (cols - 1), cols)
#     y = np.linspace(originY + resY / 2, originY + resY / 2 + resY * (rows - 1), rows)
#     # Retrieve raster
#     RasterBand = ds.GetRasterBand(1)  # there's only 1 band, starting from 1
#     # print(x)
#     # print(y)
#
#     data = RasterBand.ReadAsArray(0, 0, cols, rows)
#     FillVal = RasterBand.GetNoDataValue()
#     RasterBand = None
#     del ds
#     return resX, resY, cols, rows, x, y, data, prj, FillVal
#
#
# def writeMap(fileName, fileFormat, x, y, data, prj, FillVal):
#     """
#     Write geographical data into file. Also replave NaN bu FillVall
#
#     :param fileName:
#     :param fileFormat:
#     :param x:
#     :param y:
#     :param data:
#     :param FillVal:
#     :return:
#     """
#
#     verbose = False
#     gdal.AllRegister()
#     driver1 = gdal.GetDriverByName('GTiff')
#     driver2 = gdal.GetDriverByName(fileFormat)
#
#     data[np.isnan(data)] = FillVal
#     # Processing
#     if verbose:
#         print 'Writing to temporary file ' + fileName + '.tif'
#         print "Output format: " + fileFormat
#     # Create Output filename from (FEWS) product name and date and open for writing
#     TempDataset = driver1.Create(fileName + '.tif', data.shape[1], data.shape[0], 1, gdal.GDT_Float32)
#     # Give georeferences
#     xul = x[0] - (x[1] - x[0]) / 2
#     yul = y[0] + (y[0] - y[1]) / 2
#
#     TempDataset.SetGeoTransform([xul, x[1] - x[0], 0, yul, 0, y[1] - y[0]])
#     TempDataset.SetProjection(prj)
#     # get rasterband entry
#     TempBand = TempDataset.GetRasterBand(1)
#     # fill rasterband with array
#     TempBand.WriteArray(data, 0, 0)
#     TempBand.FlushCache()
#     TempBand.SetNoDataValue(FillVal)
#     # Create data to write to correct format (supported by 'CreateCopy')
#     if verbose:
#         print 'Writing to ' + fileName
#     outDataset = driver2.CreateCopy(fileName, TempDataset, 0)
#     TempDataset = None
#     outDataset = None
#     if verbose:
#         print 'Removing temporary file ' + fileName + '.tif'
#     os.remove(fileName + '.tif');
#
#     if verbose:
#         print 'Writing to ' + fileName + ' is done!'