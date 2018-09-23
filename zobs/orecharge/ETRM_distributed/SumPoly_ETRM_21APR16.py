from datetime import datetime
from dateutil import rrule
from osgeo import gdal, ogr
import numpy as np
import os

np.set_printoptions(linewidth=700, precision=2)


def cells(array):
    window = array[480:510, 940:970]
    return window

start, end = datetime(2000, 1, 1), datetime(2013, 12, 31)
ras_path = 'F:\\Monthly_results\\apr21'
input_folder = ['C:\\Recharge_GIS\\NM_WRPRs\\indiv_region_shps', 'C:\\Recharge_GIS\\NM_Counties\\indiv_county_shps',
                'C:\\Recharge_GIS\\NM_Gorundwater_Basins\\OSE_DGWB_byBasin\\NM_GWBs_individs']
output_folder = ['F:\Monthly_tabulated\WRPR_rslt_tabulated', 'F:\Monthly_tabulated\NM_Co_rslt_tabulated',
                 'F:\Monthly_tabulated\OSE_DGWB_rslt_tabulated']

for in_fold in input_folder:
    print(in_fold)
    temp_folder = 'C:\\Recharge_GIS\\OSG_Data\\qgis_rasters\\temp_layers'
    os.chdir(temp_folder)
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            if name.endswith('temp.tif'):
                os.remove('{}\\{}'.format(temp_folder, name))
    os.chdir(in_fold)
    for root, dirs, files in os.walk(".", topdown=False):
        for element in files:
            if element.endswith('.shp'):
                shp_name = '{}\\{}'.format(in_fold, element)
                ds = ogr.Open(shp_name)
                lyr = ds.GetLayer()

                raster = 'precip_{}_{}'.format(1, 2000)
                ppt_open = gdal.Open('{a}\\{b}.tif'.format(a=ras_path, b=raster))
                dataset = ppt_open
                temp = '{}\\{}_temp{}.tif'.format(temp_folder, element[20:-4], input_folder.index(in_fold))
                gt = ppt_open.GetGeoTransform()
                col, row = ppt_open.RasterXSize, ppt_open.RasterYSize
                rasterDS = gdal.GetDriverByName('GTiff').Create(temp, col, row, 1, gdal.GDT_Byte)
                rasterDS.SetProjection(lyr.GetSpatialRef().ExportToWkt())
                rasterDS.SetGeoTransform(gt)
                rBand = rasterDS.GetRasterBand(1)
                rBand.SetNoDataValue(0.0)
                rBand.Fill(0.0)
                err = gdal.RasterizeLayer(rasterDS, [1], lyr, options=["ALL_TOUCHED=TRUE", "OGRLayerShadow=FALSE"])
                rasterDS.FlushCache()
                mask = rasterDS.GetRasterBand(1).ReadAsArray()
                mask = np.array(mask)

                for feat in lyr:
                    pos = input_folder.index(in_fold)
                    if pos == 0:
                        name = feat.GetField("name")
                    elif pos == 1:
                        name = feat.GetField("Name")
                    else:
                        name = feat.GetField("Basin")
                    geom = feat.GetGeometryRef()

                    date = []
                    ppt_cbm = []
                    ppt_af = []
                    snow_cbm = []
                    snow_af = []
                    et_cbm = []
                    et_af = []
                    infil_cbm = []
                    infil_af = []
                    delta_stor_cbm = []
                    delta_stor_af = []

                    for mo in rrule.rrule(rrule.MONTHLY, dtstart=start, until=end):
                        raster = 'precip_{}_{}'.format(mo.month, mo.year)
                        ppt_open = gdal.Open('{a}\\{b}.tif'.format(a=ras_path, b=raster))
                        ppt_obj = np.array(ppt_open.GetRasterBand(1).ReadAsArray(), dtype=float)
                        ppt_obj = np.where(mask > 0, ppt_obj, np.zeros(ppt_obj.shape))
                        ppt_sum = np.sum(ppt_obj)
                        ppt_cubic_meters = (ppt_sum / 1000) * (250 ** 2)
                        ppt_acre_feet = ppt_cubic_meters / 1233.48

                        ppt_cbm.append(ppt_cubic_meters)
                        ppt_af.append(ppt_acre_feet)

                        date_obj = '{}/{}'.format(mo.month, mo.year)
                        date.append(date_obj)
                    print('precip for {} done'.format(name))

                    for mo in rrule.rrule(rrule.MONTHLY, dtstart=start, until=end):
                        raster = 'snow_ras_{}_{}'.format(mo.month, mo.year)
                        snow_open = gdal.Open('{a}\\{b}.tif'.format(a=ras_path, b=raster))
                        snow_obj = np.array(snow_open.GetRasterBand(1).ReadAsArray(), dtype=float)
                        snow_obj = np.where(mask > 0, snow_obj, np.zeros(snow_obj.shape))
                        snow_sum = np.sum(snow_obj)
                        snow_cubic_meters = (snow_sum / 1000) * (250 ** 2)
                        snow_acre_feet = snow_cubic_meters / 1233.48

                        snow_cbm.append(snow_cubic_meters)
                        snow_af.append(snow_acre_feet)
                    print('snow for {} done'.format(name))

                    for mo in rrule.rrule(rrule.MONTHLY, dtstart=start, until=end):
                        raster = 'et_{}_{}'.format(mo.month, mo.year)
                        et_open = gdal.Open('{a}\\{b}.tif'.format(a=ras_path, b=raster))
                        et_obj = np.array(et_open.GetRasterBand(1).ReadAsArray(), dtype=float)
                        et_obj = np.where(mask > 0, et_obj, np.zeros(et_obj.shape))
                        et_sum = np.sum(et_obj)
                        et_cubic_meters = (et_sum / 1000) * (250 ** 2)
                        et_acre_feet = et_cubic_meters / 1233.48

                        et_cbm.append(et_cubic_meters)
                        et_af.append(et_acre_feet)
                    print('et for {} done'.format(name))

                    for mo in rrule.rrule(rrule.MONTHLY, dtstart=start, until=end):
                        raster = 'infil_{}_{}'.format(mo.month, mo.year)
                        infil_open = gdal.Open('{a}\\{b}.tif'.format(a=ras_path, b=raster))
                        infil_obj = np.array(infil_open.GetRasterBand(1).ReadAsArray(), dtype=float)
                        infil_obj = np.where(mask > 0, infil_obj, np.zeros(infil_obj.shape))
                        infil_sum = np.sum(infil_obj)
                        infil_cubic_meters = (infil_sum / 1000) * (250 ** 2)
                        infil_acre_feet = infil_cubic_meters / 1233.48

                        infil_cbm.append(infil_cubic_meters)
                        infil_af.append(infil_acre_feet)
                    print('infil for {} done'.format(name))

                    for mo in rrule.rrule(rrule.MONTHLY, dtstart=start, until=end):
                        raster = 'delta_s_mo_{}_{}'.format(mo.month, mo.year)
                        delta_stor_open = gdal.Open('{a}\\{b}.tif'.format(a=ras_path, b=raster))
                        delta_stor_obj = np.array(delta_stor_open.GetRasterBand(1).ReadAsArray(), dtype=float)
                        delta_stor_obj = np.where(mask > 0, delta_stor_obj, np.zeros(delta_stor_obj.shape))
                        delta_stor_sum = np.sum(delta_stor_obj)
                        delta_stor_cubic_meters = (delta_stor_sum / 1000) * (250 ** 2)
                        delta_stor_acre_feet = delta_stor_cubic_meters / 1233.48

                        delta_stor_cbm.append(delta_stor_cubic_meters)
                        delta_stor_af.append(delta_stor_acre_feet)
                    print('delta storage for {} done'.format(name))

                date = np.array(date, object)
                ppt_cbm = np.array(ppt_cbm, dtype=float)
                ppt_af = np.array(ppt_af, dtype=float)
                snow_cbm = np.array(snow_cbm, dtype=float)
                snow_af = np.array(snow_af, dtype=float)
                et_cbm = np.array(et_cbm, dtype=float)
                et_af = np.array(et_af, dtype=float)
                infil_cbm = np.array(infil_cbm, dtype=float)
                infil_af = np.array(infil_af, dtype=float)
                delta_stor_cbm = np.array(delta_stor_cbm, dtype=float)
                delta_stor_af = np.array(delta_stor_af, dtype=float)

                b = np.array([['date', 'Precipitation [m^3]', 'Precipitation [AF]', 'Snow Water Equivalent [m^3]',
                               'Snow Water Equivalent [AF]', 'Evapotranspiration [m^3]', 'Evapotranspiration [AF]',
                               'Diffuse Recharge [m^3]', 'Diffuse Recharge [AF]', 'Soil Water Storage Change [m^3]',
                               'Soil Water Storage Change [AF]']])

                recs = np.column_stack((date, ppt_cbm, ppt_af, snow_cbm, snow_af, et_cbm, et_af, infil_cbm, infil_af,
                                        delta_stor_cbm, delta_stor_af))

                end_sums = [sum(x[:, y]) for x, y in recs[:, 1:]]

                path = 'F:\\Monthly_tabulated'
                np.savetxt('{}\{}.csv'.format(output_folder[pos], name),
                           recs, fmt=['%s', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f',
                           '%1.3f', '%1.3f'], delimiter=',')

                fmt = ",".join(["%s"] + ["%10.6e"] * (recs.shape[1]-1))

                with open('{}\{}.csv'.format(output_folder[pos], name), 'wb') as f:
                    f.write(b"date, Precipitation [m^3], Precipitation [AF], Snow Water Equivalent [m^3], "
                            "Snow Water Equivalent [AF], Evapotranspiration [m^3], Evapotranspiration [AF], "
                            "Diffuse Recharge [m^3], Diffuse Recharge [AF], Soil Water Storage Change [m^3], "
                            "   Soil Water Storage Change [AF]\n")
                    np.savetxt(f, recs, fmt=fmt, delimiter=',')

                print("You have been saved!")

# test mask arrays by saving and loading in a GIS
# driver = gdal.GetDriverByName('GTiff')
# filename = 'C:\Recharge_GIS\OSG_Data\qgis_rasters\{}.tif'.format(name)
# cols = dataset.RasterXSize
# rows = dataset.RasterYSize
# bands = dataset.RasterCount
# band = dataset.GetRasterBand(1)
# datatype = band.DataType
# outDataset = driver.Create(filename, cols, rows, bands, datatype)
# geoTransform = dataset.GetGeoTransform()
# outDataset.SetGeoTransform(geoTransform)
# proj = dataset.GetProjection()
# outDataset.SetProjection(proj)
# outBand = outDataset.GetRasterBand(1)
# outBand.WriteArray(mask, 0, 0)
# outband = None
