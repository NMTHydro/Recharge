
import datetime
from osgeo import gdal
import numpy as np

def cells(array):
    window = array[480:510, 940:970]
    return window

np.set_printoptions(precision=2, linewidth=700)

path = 'C:\\Recharge_GIS\\OSG_Data\\current_use'
raster = 'aws_ras_15apr1'
aws_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
dataset = aws_open
taw = np.array(aws_open.GetRasterBand(1).ReadAsArray(), dtype=float)
min_val = np.ones(taw.shape) * 0.001
taw = np.maximum(taw, min_val)
aws_open = []

path = 'C:\\Recharge_GIS\\OSG_Data\\qgis_rasters'
raster = 'aws_mm_21apr_std'
aws_st_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
taw_st = np.array(aws_st_open.GetRasterBand(1).ReadAsArray(), dtype=float)
taw_st = np.maximum(taw_st, min_val)
aws_st_open = []

result = np.where(taw_st > taw, taw_st, taw)

outputs = [result, taw]
output_names = ['aws_mod', 'taw']
x = 0
now = datetime.datetime.now()
tag = '{}_{}_{}_{}'.format(now.month, now.day, now.hour, now.minute)
for element in outputs:
    name = output_names[x]
    print("Saving {a}".format(a=name))
    driver = gdal.GetDriverByName('GTiff')
    filename = 'C:\\Recharge_GIS\\OSG_Data\\qgis_rasters\\{a}_{b}.tif'.format(a=name, b=tag)
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
