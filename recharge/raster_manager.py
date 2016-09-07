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
"""
The purpose of this module is to calculate recharge over a defined geographic area.

this module provides (1) function -- run_distributed_ETRM.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""

from osgeo import gdal, ogr
from numpy import array, ones, maximum, where, zeros
from calendar import monthrange
from datetime import datetime
from pandas import DataFrame
import os


class Rasters(object):

    def __init__(self):
        pass

    def convert_raster_to_array(self, input_raster_path, raster,
                                minimum_value=None, band=1):
        # if not raster:
        ras = self._open_raster(input_path=input_raster_path, filename=raster)
        ras = array(ras.GetRasterBand(band).ReadAsArray(), dtype=float)
        if minimum_value:
            min_val = ones(ras.shape) * minimum_value
            ras = maximum(ras, min_val)
        return ras

    def update_save_raster(self, master, annual_dict, monthly_dict, last_month_master, last_year_master,
                           outputs, date_object, raster_output_data, shapefiles=None,
                           save_specific_dates=None, save_outputs=None):

        mo_date = monthrange(date_object.year, date_object.month)

        if save_specific_dates:
            # save data for a certain day
            for element in save_outputs:
                self._update(master, monthly_dict, last_month_master, element, master['first_day'])
                written_raster = self._write_raster(monthly_dict, element, date_object, raster_output_data,
                                                    period='monthly')
                self._sum_raster_by_shape(shapefiles, raster_output_data, written_raster, element, date_object,
                                          outputs, master['first_day'])

        # save monthly data
        if date_object.day == mo_date[1]:
            for element in outputs:
                self._update(master, monthly_dict, last_month_master, element, master['first_day'])
                written_raster = self._write_raster(monthly_dict, element, date_object, raster_output_data,
                                                    period='monthly')
                self._sum_raster_by_shape(shapefiles, raster_output_data, written_raster, element, date_object,
                                          outputs, master['first_day'])

        # save annual data
        if date_object.day == 31 and date_object.month == 12:
            for element in outputs:
                self._update(master, annual_dict, last_year_master, element, master['first_day'])
                written_raster = self._write_raster(annual_dict, element, date_object, raster_output_data,
                                                    period='annual')
                self._sum_raster_by_shape(shapefiles, raster_output_data, written_raster, element, date_object,
                                          outputs, master['first_day'])

        return None

    def _update(self, master_dict, previous_master, cumulative_dict, var, first):

        if first:
            cumulative_dict[var] = master_dict[var]
            previous_master[var] = master_dict[var]
        else:
            cumulative_dict[var] = master_dict[var] - previous_master[var]
            previous_master[var] = master_dict[var]

        return None

    def _write_raster(self, dictionary, key, date, raster_output_data, period=None):

        out_path, out_date_tag = raster_output_data
        out_date_tag = datetime.strftime(out_date_tag.now(), '%d_%m_%Y')
        print "Saving {}_{}_{}".format(key, date.month, date.year)

        if period == 'annual':
            file_ = '{}.tif'.format(key)
            filename = os.path.join(out_path, 'Annual_results', out_date_tag, file_)
        elif period == 'monthly':
            file_ = '{}.tif'.format(key)
            filename = os.path.join(out_path, 'Monthly_results', out_date_tag, file_)

        dataset = dictionary[key]
        driver = gdal.GetDriverByName('GTiff')
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        bands = dataset.RasterCount
        band = dataset.GetRasterBand(1)
        data_type = band.DataType
        out_data_set = driver.Create(filename, cols, rows, bands, data_type)
        geotransform = dataset.GetGeoTransform()
        out_data_set.SetGeoTransform(geotransform)
        projection = dataset.GetProjection()
        out_data_set.SetProjection(projection)
        output_band = out_data_set.GetRasterBand(1)
        output_band.WriteArray(dictionary[key], 0, 0)
        return filename

    def _sum_raster_by_shape(self, shapes, temp_folder, raster_name, parameter, date, outputs,
                             first):
        folders = os.listdir(shapes)
        if first:
            af_cbs_expand = [[x + '_[AF]', x + '_[cbm]'] for x in outputs]
            tabular_cols = [item for sublist in af_cbs_expand for item in sublist]
            tabular_output = DataFrame(columns=tabular_cols)
            tabular_dict = {}
            for in_fold in folders:
                region_type = os.path.basename(in_fold).strip('_Polygons')
                tabular_dict.update({region_type: {}})
                os.chdir(os.path.join(shapes,in_fold))
                for root, dirs, files in os.walk(".", topdown=False):
                    for element in files:
                        if element.endswith('.shp'):
                            sub_region = element.strip('.shp')
                            tabular_dict[region_type].update({sub_region: tabular_output})

        print 'your tabular results dict:\n'.format(tabular_dict)

        for in_fold in folders:
            print in_fold
            region_type = os.path.basename(in_fold).strip('_Polygons')
            os.chdir(os.path.join(shapes, in_fold))
            for root, dirs, files in os.walk(".", topdown=False):
                for element in files:
                    if element.endswith('.shp'):
                        sub_region = element.strip('.shp')
                        shp_name = os.path.join(shapes, in_fold, element)
                        polygon = ogr.Open(shp_name)
                        layer = polygon.GetLayer()
                        raster = gdal.Open(raster_name)
                        geotransform = raster.GetGeoTransform()
                        col, row = raster.RasterXSize, raster.RasterYSize
                        mask_raster = gdal.GetDriverByName('GTiff').Create(temp_folder, col, row, 1, gdal.GDT_Byte)
                        mask_raster.SetProjection(layer.GetSpatialRef().ExportToWkt())
                        mask_raster.SetGeoTransform(geotransform)
                        raster_band = mask_raster.GetRasterBand(1)
                        raster_band.SetNoDataValue(0.0)
                        raster_band.Fill(0.0)
                        gdal.RasterizeLayer(mask_raster, [1], layer, options=["ALL_TOUCHED=TRUE",
                                                                              "OGRLayerShadow=FALSE"])
                        mask_raster.FlushCache()
                        mask_array = mask_raster.GetRasterBand(1).ReadAsArray()
                        mask_array = array(mask_array)

                        param_obj = array(raster.GetRasterBand(1).ReadAsArray(), dtype=float)
                        param_obj = where(mask_array > 0, param_obj, zeros(param_obj.shape))
                        param_sum = sum(param_obj)
                        param_cubic_meters = (param_sum / 1000) * (250 ** 2)
                        param_acre_feet = param_cubic_meters / 1233.48
                        df = tabular_dict[region_type][sub_region]
                        df['{}_[cbm]'.format(parameter)].loc[date] = param_cubic_meters
                        df['{}_[AF]'.format(parameter)].loc[date] = param_acre_feet

        os.remove(os.path.join(temp_folder, 'temp.tif'))

    def _open_raster(self, input_path, filename):
        # print ' raster name is {a}\\{b}'.format(a=input_path, b=filename)
        raster_open = gdal.Open('{a}\\{b}'.format(a=input_path, b=filename))
        return raster_open

# ============= EOF =============================================