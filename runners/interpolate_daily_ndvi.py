import os
from collections import OrderedDict

import numpy as np
import pandas as pd
import osr, gdal
import datetime
from dateutil import rrule
from datetime import timedelta

from scipy import interpolate
import scipy.ndimage as ndimage

def readMap(fileName, fileFormat):
    """
    read geographical file into memory

    :param fileName: Name of the file to read
    :param fileFormat: Gdal format string
    :param logger: logger object
    :return: resX, resY, cols, rows, x, y, data, FillVal
    """

    #Open file for binary-reading

    mapFormat = gdal.GetDriverByName(fileFormat)
    mapFormat.Register()
    ds = gdal.Open(fileName)
    prj = ds.GetProjection()
    # Retrieve geoTransform info
    geotrans = ds.GetGeoTransform()
    originX = geotrans[0]
    originY = geotrans[3]
    resX    = geotrans[1]
    resY    = geotrans[5]
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    x = np.linspace(originX+resX/2,originX+resX/2+resX*(cols-1),cols)
    y = np.linspace(originY+resY/2,originY+resY/2+resY*(rows-1),rows)
    # Retrieve raster
    RasterBand = ds.GetRasterBand(1) # there's only 1 band, starting from 1
    #print(x)
    #print(y)

    data = RasterBand.ReadAsArray(0,0,cols,rows)
    FillVal = RasterBand.GetNoDataValue()
    RasterBand = None
    del ds
    return resX, resY, cols, rows, x, y, data, prj, FillVal
    
def writeMap(fileName, fileFormat, x, y, data,  prj, FillVal):
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

    data[np.isnan(data)] = FillVal
    # Processing
    if verbose:
        print 'Writing to temporary file ' + fileName + '.tif'
        print "Output format: " + fileFormat
    # Create Output filename from (FEWS) product name and date and open for writing
    TempDataset = driver1.Create(fileName + '.tif',data.shape[1],data.shape[0],1,gdal.GDT_Float32)
    # Give georeferences
    xul = x[0]-(x[1]-x[0])/2
    yul = y[0]+(y[0]-y[1])/2

    TempDataset.SetGeoTransform( [ xul, x[1]-x[0], 0, yul, 0, y[1]-y[0] ] )
    TempDataset.SetProjection(prj)
    # get rasterband entry
    TempBand = TempDataset.GetRasterBand(1)
    # fill rasterband with array
    TempBand.WriteArray(data,0,0)
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


def time_interpolation(day, Lat, Lon, finalyear):

    NUMS = (1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
            225, 241, 257, 273, 289, 305, 321, 337, 353)

    numsize = len(NUMS)
    year = day.year

    base_dir = 'F:\\ETRM_Inputs\\NDVI_individ\\'
    output = 'F:\\ETRM_Inputs\\NDVI_spline\\'

    cnt = day.timetuple().tm_yday
    i = 0
    first_date = 0
    while first_date == 0:
        # print(i)
        if cnt == NUMS[i]:
            first_date = NUMS[i]
            next_date = NUMS[i+1]
        elif (cnt < NUMS[i]) & (cnt > NUMS[i-1]):
            # print('two')
            first_date = NUMS[i - 1]
            next_date = NUMS[i]
        elif (cnt > NUMS[i]) & (cnt < NUMS[i+1]):
            # print('three')
            # print(NUMS[i + 1])
            first_date = NUMS[i]
            next_date = NUMS[i+1]
        elif (cnt >= 353) & (year == finalyear):
            first_date = NUMS[numsize-1]
            # print('first_date: ', first_date)
            next_date = first_date
            # print('next_date: ', next_date)
        elif (cnt >= 353):
            first_date = NUMS[numsize-1]
            # print('first_date: ', first_date)
            i = 0
            next_date = NUMS[i]
            # print('next_date: ', next_date)

        i += 1

    print('-----------------------------------------------------------------------------')
    print('DOY:', cnt)
    # print(year)
    raster_first_date = datetime.datetime(year, 1, 1) + datetime.timedelta(first_date-1)
    print('raster first date: ', raster_first_date)

    if (cnt >= 353) & (year == finalyear):
        newyear = year
        raster_next_date = datetime.datetime(newyear, 1, 1) + datetime.timedelta(next_date - 1)
    elif cnt >= 353:
        newyear =  year + 1
        # print(year)
        raster_next_date = datetime.datetime(newyear, 1, 1) + datetime.timedelta(next_date - 1)
    elif cnt < 353:
        newyear = year
        raster_next_date = datetime.datetime(newyear, 1, 1) + datetime.timedelta(next_date-1)

    tail = '{}_{:02n}_{:02n}.tif'.format(year, raster_first_date.timetuple().tm_mon, raster_first_date.timetuple().tm_mday)

    raster_now = os.path.join(base_dir, '{}'.format(year), 'NDVI{}'.format(tail))
    print('First raster to interpolate: ', raster_now)

    resX, resY, cols, rows, Lon, Lat, ndvi, prj, FillVal = readMap(os.path.join(base_dir, raster_now), 'Gtiff')

    tail2 = '{}_{:02n}_{:02n}.tif'.format(newyear, raster_next_date.timetuple().tm_mon, raster_next_date.timetuple().tm_mday)

    raster_next = os.path.join(base_dir, '{}'.format(newyear), 'NDVI{}'.format(tail2))
    print('Future raster to interpolate with: ', raster_next)

    resX, resY, cols, rows, Lon, Lat, ndvinext, prj, FillVal = readMap(os.path.join(base_dir, raster_next), 'Gtiff')


    latitude_index = np.arange(2525)
    longitude_index = np.arange(2272)
    arr1 = ndvi
    arr2 = ndvinext

    # rejoin Linke, LinkeNext into a single array of shape (2, 2160, 4320)
    arr = np.r_['0,3', ndvi, ndvinext]
    # print('arr.shape',arr.shape)

    # define the grid coordinates where you want to interpolate
    Y, X = np.meshgrid(longitude_index,latitude_index)
    # print('X',X)
    # print(X.shape)
    # print('Y',Y)
    # print(Y.shape)

    #Setup time variables for interpolation
    days_dif = raster_next_date - day
    days_dif = float(days_dif.days)
    max_days_diff = raster_next_date - raster_first_date
    max_days_diff = float(max_days_diff.days)
    # proportion = float(days_dif / max_days_diff)
    # print('proportion',proportion)
    print('day', day)
    print('days difference from next ndvi raster', days_dif)
    print('out of max days difference', max_days_diff)

    if (cnt >= 353) & (year == finalyear):
        interp = 0.0 #Set to 0 otherwise will divide by zero and give error
    else:
        interp = 1 - (days_dif / max_days_diff) #1 = weight completely next month values, 0 = previous month
    print('interp ratio between monthly images', interp)

    # 0.5 corresponds to half way between arr1 and arr2
    coordinates = np.ones((2525,2272))*interp, X, Y
    coordones = np.ones((2525,2272))*interp
    #print('coordinates',coordinates)
    #print(coordones.shape)

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
    base_dir = 'F:\\ETRM_Inputs\\NDVI_individ\\'
    output = 'F:\\ETRM_Inputs\\NDVI_spline\\'

    startday = datetime.datetime(2013,12,17,0)
    endday = datetime.datetime(2013,12,31,0)
    finalyear = 2013

    year = '2000'
    ref_map = os.path.join(base_dir, year, 'NDVI2000_01_01.tif')
    resX, resY, cols, rows, Lon, Lat, Linke, prj, FillVal = readMap(ref_map, 'Gtiff')

    srs = osr.SpatialReference(prj)
    sr_wkt = srs.ExportToWkt()

    for day in rrule.rrule(rrule.DAILY, dtstart=startday, until=endday):
        nr = day.strftime('%j')
        year = day.strftime('%Y')

        ndvi_daily = time_interpolation(day, Lat, Lon, finalyear)

        #Write daily values to new daily rasters
        daily_doy = 'ndvi{}_{}.tif'.format(year, nr)
        outpath = os.path.join(output, year)

        if not os.path.exists(outpath):
            os.makedirs(outpath)

        outname = os.path.join(outpath, daily_doy)
        writeMap(outname,'Gtiff', Lon, Lat, ndvi_daily, sr_wkt, FillVal)

if __name__ == '__main__':
    main()
    

