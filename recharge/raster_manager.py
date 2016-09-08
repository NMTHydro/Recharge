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

    def get_raster_geo_attributes(self, statics_path):

        statics = [filename for filename in os.listdir(statics_path) if filename.endswith('.tif')]
        file_name = statics[0]
        dataset = gdal.Open(os.path.join(statics_path, file_name))
        band = dataset.GetRasterBand(1)
        raster_geo_dict = {'cols': dataset.RasterXSize, 'rows': dataset.RasterYSize, 'bands': dataset.RasterCount,
                           'data_type': band.DataType, 'projection': dataset.GetProjection(),
                           'geotransform': dataset.GetGeoTransform()}

        return raster_geo_dict

    def make_results_dir(self, out_path, shapes):
        empties = ['annual_rasters', 'monthly_rasters', 'ETRM_14_yr_rasters', 'annual_tabulated', 'monthly_tabulated']
        now = datetime.now()
        tag = now.strftime('%Y_%m_%d')
        folder = 'ETRM_Results_{}'.format(tag)
        os.chdir(out_path)
        new_dir = os.path.join(out_path, folder)

        if not os.path.isdir(folder):
            os.makedirs(new_dir)
            for item in empties:
                empty = os.path.join(new_dir, item)
                os.makedirs(empty)
            region_types = os.listdir(shapes)
            for tab_folder in ['annual_tabulated', 'monthly_tabulated']:
                for region_type in region_types:
                    a, b = region_type.split('_P')
                    os.makedirs(os.path.join(new_dir, tab_folder, a))

        return None

    def update_save_raster(self, master, output_tracker, tab_dict, outputs, date_object, raster_output_path,
                           geo_attributes, shapefiles=None, save_specific_dates=None, save_outputs=None):
        
        # raster_track_dict = {'output_an': {'output': raster}, 'output_mo': {{'output': raster}},
        #                      'last_mo': {{'output': raster}}, 'last_yr': {{'output': raster}}}
        
        # outputs = ['tot_infil', 'tot_ref_et', 'tot_eta', 'tot_precip', 'tot_ro', 'tot_swe']
        
        mo_date = monthrange(date_object.year, date_object.month)

        # save data for a certain day
        if save_specific_dates:
            if date_object in save_specific_dates:
                for element in save_outputs:
                    self._update_raster_tracker(master, output_tracker, element)
                    written_raster = self._write_raster(output_tracker, element, date_object, raster_output_path,
                                                        geo_attributes, period='monthly')
                    self._sum_raster_by_shape(tab_dict, shapefiles, raster_output_path, written_raster, element,
                                              date_object)
        # FOR TESTING: save 3rd day #
        if date_object.day == 03:
            print 'attempting to update/save day 3: {}'.format(date_object)
            print 'outputs: {}'.format(outputs)
            for element in outputs:
                self._update_raster_tracker(master, output_tracker, element)
                written_raster = self._write_raster(output_tracker, element, date_object, raster_output_path,
                                                    geo_attributes, period='monthly')
                self._sum_raster_by_shape(tab_dict, shapefiles, raster_output_path, written_raster, element,
                                          date_object)
        # save monthly data
        if date_object.day == mo_date[1]:
            for element in outputs:
                self._update_raster_tracker(master, output_tracker, element)
                written_raster = self._write_raster(output_tracker, element, date_object, raster_output_path,
                                                    geo_attributes, period='monthly')
                self._sum_raster_by_shape(tab_dict, shapefiles, raster_output_path, written_raster, element,
                                          date_object)

        # save annual data
        if date_object.day == 31 and date_object.month == 12:
            for element in outputs:
                self._update_raster_tracker(master, output_tracker, element)
                written_raster = self._write_raster(output_tracker, element, date_object, raster_output_path,
                                                    geo_attributes, period='annual')
                self._sum_raster_by_shape(tab_dict, shapefiles, raster_output_path, written_raster, element,
                                          date_object)

        return None

    def _update_raster_tracker(self, master_dict, raster_output_tracker, var):
        """ Updates the cummulative rasters each period as indicated.

        This function is to prepare a dict of rasters showing the flux over the past time period (month, year).

        :param master_dict: master from etrm_processes.Processes
        :param previous_master: last month's master dict
        :param cumulative_dict: the difference between this dict and last
        :param var: vars are all accumulation terms from master
        :param first: identify first day
        :return: None
        """

        raster_output_tracker['output_an'][var] = master_dict[var] - raster_output_tracker['last_yr'][var]
        raster_output_tracker['output_mo'][var] = master_dict[var] - raster_output_tracker['last_mo'][var]
        raster_output_tracker['last_yr'][var] = raster_output_tracker['output_an'][var]
        raster_output_tracker['last_mo'][var] = raster_output_tracker['output_mo'][var]

        return None

    def _write_raster(self, output_raster_dict, key, date, out_path, raster_geometry, period=None):

        print "Saving {}_{}_{}".format(key, date.month, date.year)

        if period == 'annual':
            file_ = '{}_{}.tif'.format(key, date.year)
            filename = os.path.join(out_path, 'Annual_results', file_)
            dataset = output_raster_dict['output_an'][key]
        elif period == 'monthly':
            file_ = '{}_{}_{}.tif'.format(key, date.month, date.year)
            filename = os.path.join(out_path, 'Monthly_results', file_)
            dataset = output_raster_dict['output_mo'][key]
        else:
            dataset = None
            filename = None

        driver = gdal.GetDriverByName('GTiff')
        out_data_set = driver.Create(filename, raster_geometry['cols'], raster_geometry['rows'],
                                     raster_geometry['bands'], raster_geometry['data_type'])
        out_data_set.SetGeoTransform(raster_geometry['geotransform'])
        out_data_set.SetProjection(raster_geometry['projection'])
        output_band = out_data_set.GetRasterBand(1)
        output_band.WriteArray(output_raster_dict[key], 0, 0)

        return filename

    def _sum_raster_by_shape(self, tabular_dict, shapes, temp_folder, raster_name, parameter, date):

        folders = os.listdir(shapes)

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