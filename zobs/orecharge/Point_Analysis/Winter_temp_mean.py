
import datetime
import os
from dateutil import rrule
from osgeo import gdal
import numpy as np

np.set_printoptions(linewidth=700, precision=2)

startTime = datetime.datetime.now()
print startTime


def cells(array):
    window = array[480:510, 940:970]
    return window

# Set start datetime object
start, end = datetime.datetime(2000, 1, 1), datetime.datetime(2013, 12, 31)

path = 'C:\\Recharge_GIS\\OSG_Data\\current_use'
raster = 'aws_mod_4_21_10_0'
aws_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
taw = np.array(aws_open.GetRasterBand(1).ReadAsArray(), dtype=float)
dataset = aws_open
min_val = np.ones(taw.shape)
aws_open = []
cum_temp = np.zeros(taw.shape)
taw = []
x = 0
for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
    doy = dday.timetuple().tm_yday
    if 121 < doy < 305:
        pass
    else:
        x += 1
        print "Time : {a} day {b}_{c}".format(a=str(datetime.datetime.now() - startTime), b=doy, c=dday.year)
        #  PRISM to mintemp, maxtemp, temp
        if dday.year in [2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013]:
            path = "F:\\PRISM\\Temp\\Minimum_standard"
            raster = '{a}\\cai_tmin_us_us_30s_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                                    c=str(dday.month).rjust(2, '0'),
                                                                    d=str(dday.day).rjust(2, '0'))
            minTemp_open = gdal.Open(raster)
            min_temp = np.array(minTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
            minTemp_open = []
        else:
            path = "F:\\PRISM\\Temp\\Minimum_standard"
            raster = '{a}\\TempMin_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                                   c=str(dday.month).rjust(2, '0'),
                                                                   d=str(dday.day).rjust(2, '0'))
            minTemp_open = gdal.Open(raster)
            min_temp = np.array(minTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
            minTemp_open = []
        path = "F:\\PRISM\\Temp\\Maximum_standard"
        raster = '{a}\\TempMax_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year,
                                                               c=str(dday.month).rjust(2, '0'),
                                                               d=str(dday.day).rjust(2, '0'))
        maxTemp_open = gdal.Open(raster)
        max_temp = np.array(maxTemp_open.GetRasterBand(1).ReadAsArray(), dtype=float)
        maxTemp_open = []

        temp = (min_temp + max_temp)/2
        temp = np.where(temp < -30.0, -999.0, temp)
        temp = np.where(temp > 40, -999.0, temp)
    cum_temp += temp

mean_temp = cum_temp / x
outputs = [mean_temp]
output_names = ['mean_winter_temp']
x = 0
now = datetime.datetime.now()
tag = '{}_{}'.format(now.month, now.day)
for element in outputs:
    name = output_names[x]
    print "Saving {a}".format(a=name)
    driver = gdal.GetDriverByName('GTiff')
    filename = 'C:\\Recharge_GIS\\Array_Results\\{a}.tif'.format(a=name)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    bands = dataset.RasterCount
    band = dataset.GetRasterBand(1)
    datatype = band.DataType
    outDataset = driver.Create(filename, cols, rows, bands, datatype)
    geoTransform = dataset.GetGeoTransform()
    outDataset.SetGeoTransform(geoTransform)
    proj = dataset.GetProjection()
    outDataset.SetProjection(proj)
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(element, 0, 0)
    x += 1