import os
from netCDF4 import Dataset
import gdal
from gdalconst import GDT_Float32
import numpy as np
from datetime import datetime as dt
from datetime import timedelta

print 'hello world'

def write_raster(array, geotransform, output_path, output_filename, dimensions, projection):
    """
    Write raster outputs a Geotiff to a specified location.

    :param array: an array to be printed as a raster
    :param geotransform: a list of intergers containing information about the size and resolution of the raster
    :param output_path: path where you want to output the raster.
    :param output_filename:
    :param dimensions: x and y dimensions of the raster
    :param projection: geographic projection string
    :param datatype: NA
    :return: NA
    """
    filename = os.path.join(output_path, output_filename)

    driver = gdal.GetDriverByName('GTiff')
    # path, cols, rows, bandnumber, data type (if not specified, as below, the default is GDT_Byte)
    output_dataset = driver.Create(filename, dimensions[0], dimensions[1], 1, GDT_Float32)

    # we write TO the output band
    output_band = output_dataset.GetRasterBand(1)
    # we don't need to do an offset
    array = np.flipud(array)# todo - transpose can't be right
    print 'shape of transpose', array.shape
    output_band.WriteArray(array, 0, 0)

    print 'done writing, Master.'

    # set the geotransform in order to georefference the image
    output_dataset.SetGeoTransform(geotransform)
    # set the projection
    output_dataset.SetProjection(projection)


def process_netcdf(path, output_path, projection, name_string):
    """

    :param path: path to a netcdf4 file
    :return: et arrays, geotransform and dimensions
    """

    main_dataset = Dataset(path, 'r+', format='NETCDF4')

    print 'main dataset variables \n', main_dataset.variables, ' \n ====='

    print 'main dataset.vars[time] \n', main_dataset.variables['time'] , '\n ======'

    time_list = np.array(main_dataset.variables['time']).tolist()

    print 'time array \n', time_list
    #below getting units out
    units = main_dataset.variables['time'].units
    print 'units\n', units

    start_date_string = units[-10:]

    print 'start date string \n', start_date_string

    start_date = dt.strptime(start_date_string, "%Y-%m-%d")

    print 'start date datetime', start_date

    # for i in time_list
    #     dt.

    date_list = []
    for d in time_list:
        datecount = start_date + timedelta(days=d)
        date_list.append(datecount)


    print 'here is your date list \n', date_list
    year_month = []
    for date in date_list:
        #dt.date_list(year, month, day, minutes, seconds)
        date.timetuple()
        month = str(date.month)
        year = str(date.year)
        year_month.append((year, month))
    print year_month

    # get the geotransform information: how big pixels are size of rows and colums
    # print 'ssebop dimensions', main_dataset.dimensions
    lat = main_dataset.dimensions['lat']
    latsze = lat.size
    # print 'lat',lat
    # print latsze

    lon = main_dataset.dimensions['lon']
    lonsze = lon.size
    # print lonsze

    # format of dimensions is (x coords, y coords) todo - maybe reverse this for numpy conventions...
    dimensions = (lonsze, latsze)
    # dimensions = (latsze, lonsze)

    print 'dimensions we try to use', dimensions
    # get pixel width/height from geospatial min and max
    # print 'latmin', main_dataset.geospatial_lat_min
    latmin = main_dataset.geospatial_lat_min
    latmax = main_dataset.geospatial_lat_max
    height_pixels = (latmax - latmin)/latsze
    # print 'heightpixels', height_pixels
    lonmin = main_dataset.geospatial_lon_min
    lonmax = main_dataset.geospatial_lon_max
    width_pixels = (lonmax - lonmin)/lonsze
    # print 'width pixels', width_pixels
    transform = (lonmin, width_pixels, 0, latmax, 0, -height_pixels) # todo
    # transform = (latmax, -height_pixels, 0, lonmin, 0, width_pixels)
    # print transform
    # get the entire et array
    et = main_dataset.variables['et']

    et_arr = np.array(et)
    # print 'et array', et_arr

    print 'shape', et_arr.shape
    #process the et array (separate time series)

    # print 'the first month raster', et_arr[1].shape

    # get the number of time dimensions for the net cdf
    # time = main_dataset.dimensions['time'].size
    time_dict = main_dataset.dimensions
    time_obj = time_dict['time']
    time_size_attr = time_obj.size

    for ind, tup in enumerate(year_month):

        outputfilename = "{}{}_{}.tif".format(name_string, tup[0], tup[1])
        array = et_arr[ind]
        print 'size of the array', array.shape
        write_raster(array, transform, output_path, outputfilename, dimensions, projection)



def run():
    """
    This is the function where the user specifies where to output net cdf as geotiff, where the netcdf file is, and
    what projection were using...
    :return:
    """
    # path to the net cdf file on our computer
    path = "/Users/Gabe/Desktop/NM_DEM_slope/SSEBop/monthly.nc"

    projection = 'EPSG:4326'

    output_path = '/Users/Gabe/Desktop/NM_DEM_slope/SSEBop/SSEBOP_Geotiff'

    # what the output geotiffs start with
    name_string = 'ssebop_'

    process_netcdf(path, output_path, projection, name_string)



if __name__ == "__main__":
    run()