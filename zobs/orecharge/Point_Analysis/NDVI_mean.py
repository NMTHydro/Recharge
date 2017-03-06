
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
pKcb = np.zeros(taw.shape)
cum_kcb = min_val
taw = []
aws_open = []
x = 0
for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
    doy = dday.timetuple().tm_yday
    if 121 < doy < 305:
        pass
    else:
        x += 1
        print "Time : {a} day {b}_{c}".format(a=str(datetime.datetime.now() - startTime), b=doy, c=dday.year)
        #  NDVI to kcb
        if dday.year == 2000:
            path = 'F:\\NDVI\\NDVI_std_all'
            ras_list = os.listdir('F:\\NDVI\\NDVI_std_all')
            obj = [1, 49, 81, 113, 145, 177, 209, 241, 273, 305, 337]
            if doy < 49:
                strt = 1
                band = doy
                nd = 48
                raster = '{a}\\T{b}_{c}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(a=path,
                                                                                        b=str(strt).rjust(3, '0'),
                                                                                        c=str(nd).rjust(3, '0'))
                ndvi_open = gdal.Open(raster)
                ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
                ndvi_open = []
                kcb = ndvi * 1.25
            else:
                for num in obj[1:]:
                    diff = doy - num
                    if 0 <= diff <= 31:
                        pos = obj.index(num)
                        strt = obj[pos]
                        band = diff + 1
                        if num == 337:
                            nd = num + 29
                        else:
                            nd = num + 31
                        raster = '{a}\\T{b}_{c}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(a=path,
                                                                                                b=str(strt).rjust(3, '0'),
                                                                                                c=str(nd).rjust(3, '0'))
                        ndvi_open = gdal.Open(raster)
                        ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
                        ndvi_open = []
                        kcb = ndvi * 1.25

        elif dday.year == 2001:
            path = "F:\\NDVI\\NDVI_std_all"
            obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
                   225, 241, 257, 273, 289, 305, 321, 337, 353]
            for num in obj:
                diff = doy - num
                if 0 <= diff <= 15:
                    pos = obj.index(num)
                    strt = obj[pos]
                    band = diff + 1
                    if num == 353:
                        nd = num + 12
                    else:
                        nd = num + 15
                    raster = '{a}\\{b}_{c}_{d}.tif'.format(a=path, b=dday.year, c=strt, d=nd)
                    ndvi_open = gdal.Open(raster)
                    ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
                    ndvi_open = []
                    kcb = ndvi * 1.25

        else:
            path = "F:\\NDVI\\NDVI_std_all"
            obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
                   225, 241, 257, 273, 289, 305, 321, 337, 353]
            for num in obj:
                diff = doy - num
                if 0 <= diff <= 15:
                    pos = obj.index(num)
                    strt = obj[pos]
                    band = diff + 1
                    if num == 353:
                        nd = num + 12
                    else:
                        nd = num + 15
                    raster = '{a}\\{b}_{c}.tif'.format(a=path, b=dday.year, c=pos+1, d=nd)
                    ndvi_open = gdal.Open(raster)
                    ndvi = np.array(ndvi_open.GetRasterBand(band).ReadAsArray(), dtype=float)
                    ndvi_open = []
                    kcb = ndvi * 1.25
    kcb = np.where(np.isnan(kcb) == True, pKcb, kcb)
    kcb = np.where(kcb > 3.0, pKcb, kcb)
    cum_kcb += kcb
mean_kcb = cum_kcb / x
outputs = [mean_kcb]
output_names = ['mean_kcb2']
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