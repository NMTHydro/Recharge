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
from numpy import array, where, zeros, isnan, count_nonzero
from calendar import monthrange
import os

from tools import save_tabulated_results_to_csv as save_csv
from recharge.raster_tools import make_results_dir
from recharge.raster_tools import get_raster_geo_attributes as get_geo
import recharge.dict_setup


class Rasters(object):
    def __init__(self, path_to_representative_raster, polygons, outputs, simulation_period, output_root):

        self._polygons = polygons
        self._outputs = outputs
        self._geo = get_geo(path_to_representative_raster)
        self._output_tracker = recharge.dict_setup.initialize_raster_tracker(outputs,
                                                                             (self._geo['rows'], self._geo['cols']))
        self._results_dir = make_results_dir(output_root, polygons)
        self._simulation_period = simulation_period
        self._tabular_dict = recharge.dict_setup.initialize_tabular_dict(polygons, outputs, simulation_period)

    def update_save_raster(self, master, date_object, save_specific_dates=None):

        mo_date = monthrange(date_object.year, date_object.month)

        # save data for a certain day
        if save_specific_dates:
            if date_object in save_specific_dates:
                for element in self._outputs:
                    self._write_raster(element, date_object, period='day', master=master)

        # save monthly data
        # etrm_processes.run._save_tabulated_results_to_csv will resample to annual
        if date_object.day == mo_date[1]:
            for element in self._outputs:
                data_array = master[element]
                self._update_raster_tracker(master, element)
                self._write_raster(element, date_object, period='monthly')
                self._sum_raster_by_shape(data_array, element, date_object)

        # save annual data
        if date_object.day == 31 and date_object.month == 12:
            for element in self._outputs:
                data_array = master[element]
                self._update_raster_tracker(master, element, annual=True)
                self._write_raster(element, date_object, period='annual')
                self._sum_raster_by_shape(data_array, element, date_object)

        if date_object == self._simulation_period:
            save_csv(self._tabular_dict, self._results_dir, self._polygons)
        return None

    def _update_raster_tracker(self, master_dict, var, annual=False):
        """ Updates the cummulative rasters each period as indicated.

        This function is to prepare a dict of rasters showing the flux over the past time period (month, year).

        :param master_dict: master from etrm_processes.Processes
        :param previous_master: last month's master dict
        :param cumulative_dict: the difference between this dict and last
        :param var: vars are all accumulation terms from master
        :param first: identify first day
        :return: None
        """

        if annual:
            self._output_tracker['current_year'][var] = master_dict[var] - self._output_tracker['last_yr'][var]
            self._output_tracker['last_yr'][var] = self._output_tracker['current_year'][var]

        self._output_tracker['current_month'][var] = master_dict[var] - self._output_tracker['last_mo'][var]
        self._output_tracker['last_mo'][var] = self._output_tracker['current_month'][var]
        return None

    def _write_raster(self, key, date, period=None, master=None):

        print ''
        print "Saving {}_{}_{}".format(key, date.month, date.year)

        if period == 'annual':
            file_ = '{}_{}.tif'.format(key, date.year)
            filename = os.path.join(self._results_dir['root'], self._results_dir['annual_rasters'], file_)
            array_to_save = self._output_tracker['current_year'][key]

        elif period == 'monthly':
            file_ = '{}_{}_{}.tif'.format(key, date.month, date.year)
            filename = os.path.join(self._results_dir['root'], self._results_dir['monthly_rasters'], file_)
            array_to_save = self._output_tracker['current_month'][key]

        elif period == 'daily':
            file_ = '{}_{}_{}_{}.tif'.format(key, date.year, date.month, date.year)
            filename = os.path.join(self._results_dir['root'], self._results_dir['daily_rasters'], file_)
            array_to_save = master[key]

        else:
            array_to_save = None
            filename = None

        driver = gdal.GetDriverByName('GTiff')
        out_data_set = driver.Create(filename, self._geo['cols'], self._geo['rows'],
                                     self._geo['bands'], self._geo['data_type'])
        out_data_set.SetGeoTransform(self._geo['geotransform'])
        out_data_set.SetProjection(self._geo['projection'])
        output_band = out_data_set.GetRasterBand(1)
        output_band.WriteArray(array_to_save, 0, 0)
        return None

    def _sum_raster_by_shape(self, param_obj, parameter, date):

        folders = os.listdir(self._polygons)
        # print 'processing parameter: {}'.format(parameter)
        for in_fold in folders:
            # print 'input geo shapes folder: {}'.format(in_fold)
            region_type = os.path.basename(in_fold).replace('_Polygons', '')
            shape_files = os.listdir(os.path.join(self._polygons, in_fold))
            # print 'files in region {}:\n{}'.format(region_type, files)
            for geometry in shape_files:
                if geometry.endswith('.shp'):
                    sub_region = geometry.strip('.shp')
                    shp_name = os.path.join(self._polygons, in_fold, geometry)
                    polygon = ogr.Open(shp_name)
                    layer = polygon.GetLayer()
                    driver = gdal.GetDriverByName('GTiff')
                    temp_raster = os.path.join(self._results_dir['root'], 'temp.tif')
                    mask_raster = driver.Create(temp_raster, self._geo['cols'], self._geo['rows'], 1,
                                                self._geo['data_type'])
                    mask_raster.SetProjection(layer.GetSpatialRef().ExportToWkt())
                    mask_raster.SetGeoTransform(self._geo['geotransform'])
                    raster_band = mask_raster.GetRasterBand(1)
                    raster_band.SetNoDataValue(0.0)
                    raster_band.Fill(0.0)
                    gdal.RasterizeLayer(mask_raster, [1], layer, options=["ALL_TOUCHED=TRUE",
                                                                          "OGRLayerShadow=FALSE"])
                    mask_raster.FlushCache()
                    mask_array = mask_raster.GetRasterBand(1).ReadAsArray()
                    del mask_raster
                    mask_array = array(mask_array)
                    print 'mask array is {} cells, of {}, or {}%'.format(count_nonzero(mask_array),
                                                                         mask_array.size,
                                                                         (float(count_nonzero(mask_array)) /
                                                                          mask_array.size) * 100)

                    param_obj = where(isnan(param_obj), zeros(param_obj.shape), param_obj)
                    param_obj = where(param_obj < 0, zeros(param_obj.shape), param_obj)
                    param_obj = where(mask_array > 0, param_obj, zeros(param_obj.shape))
                    param_sum = param_obj.sum()
                    param_cubic_meters = (param_sum / 1000) * (250 ** 2)
                    param_acre_feet = param_cubic_meters / 1233.48
                    df = self._tabular_dict[region_type][sub_region]
                    print '{} {} {:.2e} AF'.format(os.path.basename(shp_name).replace('.shp', ''),
                                                   parameter, param_acre_feet)
                    df['{}_[cbm]'.format(parameter)].loc[date] = param_cubic_meters
                    df['{}_[AF]'.format(parameter)].loc[date] = param_acre_feet
        return None


if __name__ == '__main__':
    pass

# ============= EOF =============================================
