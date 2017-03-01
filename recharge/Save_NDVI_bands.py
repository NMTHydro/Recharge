import os
import sys
import datetime
import gdal
from numpy import linspace, isnan, where
from dateutil import rrule
from recharge.raster_tools import remake_array, apply_mask, convert_raster_to_array

NUMS = (1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
        225, 241, 257, 273, 289, 305, 321, 337, 353)

def readMap(fileName, fileFormat):
    """
    ead geographical file into memory

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
    if ds is None:
        print('Could not open ' + fileName + '. Something went wrong!! Shutting down')
        sys.exit(1)
    # Retrieve geoTransform info
    geotrans = ds.GetGeoTransform()
    originX = geotrans[0]
    originY = geotrans[3]
    resX    = geotrans[1]
    resY    = geotrans[5]
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    x = linspace(originX+resX/2,originX+resX/2+resX*(cols-1),cols)
    y = linspace(originY+resY/2,originY+resY/2+resY*(rows-1),rows)
    # Retrieve raster
    RasterBand = ds.GetRasterBand(1) # there's only 1 band, starting from 1
    data = RasterBand.ReadAsArray(0,0,cols,rows)
    FillVal = RasterBand.GetNoDataValue()
    RasterBand = None
    del ds
    return resX, resY, cols, rows, x, y, data, prj, FillVal

def writeMap(fileName, fileFormat, x, y, data, prj, FillVal):
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


def get_kcb(mask_path, in_path, date_object, previous_kcb=None, coords=None):
    """
    Find NDVI image and convert to Kcb.

    :param in_path: NDVI input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :param previous_kcb: Previous day's kcb value.
    :param coords: Call if using to get point data using point_extract_utility.
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
    mask = 'Mask'
    mask_path = os.path.join(input_root, mask)
    ndvi_path = os.path.join(input_root, 'NDVI', 'NDVI_std_all')

    penman_path = os.path.join(input_root, 'PM_RAD')
    penman_example = 'PM_NM_2000_001.tif'
    map_for_reference = os.path.join(penman_path, '2000', penman_example)
    resX, resY, cols, rows, x, y, data, prj, FillVal = readMap(map_for_reference,'Gtiff')

    # print('ndvi_path',ndvi_path)

    start = datetime.datetime(2000,1,1,0)
    end = datetime.datetime(2001,12,31,0)

    for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        year = day.strftime('%Y')
        month = day.strftime('%m')
        day_mth = day.strftime('%d')


        new_dir = 'NDVI_individ'
        yearstr = str(year)
        output_dir = os.path.join(input_root, new_dir,yearstr)
        # print(output_dir)


        ndvi = get_kcb(mask_path, ndvi_path, day, previous_kcb=None, coords=None)
        FillVal = -999.
        # kcb = remake_array(mask_path, kcb)
        ndvi[ndvi == FillVal] = 0
        # print(ndvi, ndvi.shape)

        new_ndvi = 'NDVI{}_{}_{}.tif'.format(year,month,day_mth)
        ndvi_out = os.path.join(output_dir,new_ndvi)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        writeMap(ndvi_out, 'Gtiff', x, y, ndvi, prj, FillVal)
        print('Saving New NDVI file as ' + str(ndvi_out))






