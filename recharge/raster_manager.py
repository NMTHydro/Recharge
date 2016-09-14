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
from numpy import array, where, zeros, count_nonzero, random
from calendar import monthrange
import os

from recharge.raster_tools import make_results_dir
from recharge.raster_tools import get_raster_geo_attributes as get_geo
import recharge.dict_setup


class Rasters(object):
    def __init__(self, path_to_representative_raster, polygons, outputs, simulation_period, output_root,
                 write_frequency=None):

        self._write_freq = write_frequency
        self._polygons = polygons
        self._outputs = outputs
        self._geo = get_geo(path_to_representative_raster)
        self._output_tracker = recharge.dict_setup.initialize_raster_tracker(outputs,
                                                                             (self._geo['rows'], self._geo['cols']))
        self._results_dir = make_results_dir(output_root, polygons)
        self._simulation_period = simulation_period
        self._tabular_dict = recharge.dict_setup.initialize_tabular_dict(polygons, outputs, simulation_period)

    def update_raster_obj(self, master, date_object, save_specific_dates=None):

        mo_date = monthrange(date_object.year, date_object.month)

        # save data for a certain day
        if save_specific_dates:
            if date_object in save_specific_dates:
                for element in self._outputs:
                    self._write_raster(element, date_object, period='single_day', master=master)

        # save daily data (this will take a long time)
        if self._write_freq == 'daily':
            for element in self._outputs:
                data_array = master[element]
                self._sum_raster_by_shape(element, date_object, data_array)
                print 'tab dict: \n{}'.format(self._tabular_dict)

        # save monthly data
        # etrm_processes.run._save_tabulated_results_to_csv will resample to annual
        if date_object.day == mo_date[1]:
            print ''
            print 'saving monthly data for {}'.format(date_object)
            for element in self._outputs:
                self._update_raster_tracker(master, element)
                self._write_raster(element, date_object, period='monthly')
                self._sum_raster_by_shape(element, date_object)

        # save annual data
        if date_object.day == 31 and date_object.month == 12:
            for element in self._outputs:
                self._update_raster_tracker(master, element, annual=True)
                self._write_raster(element, date_object, period='annual')

        if date_object == self._simulation_period[1]:

            print 'saving the simulation master tracker'
            self._save_tabulated_results_to_csv(self._results_dir, self._polygons)
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

        elif period == 'single_day':
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

    def _sum_raster_by_shape(self, parameter, date, data_arr=None):

        region_folders = os.listdir(self._polygons)
        print 'processing parameter: {}'.format(parameter)

        for region_folder in region_folders:
            print 'input geo shapes region: {}'.format(region_folder)
            region_type = os.path.basename(region_folder).replace('_Polygons', '')
            all_geo_files = os.listdir(os.path.join(self._polygons, region_folder))
            shape_files = [shapefile for shapefile in all_geo_files if shapefile.endswith('.shp')]
            print 'files in region {}:\n{}'.format(region_type, all_geo_files)
            print ''
            for geometry in shape_files:
                sub_region = geometry.strip('.shp')
                shp_name = os.path.join(self._polygons, region_folder, geometry)
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
                # print '{} mask array is {} cells, or {}%'.format(sub_region, count_nonzero(mask_array),
                #                                                  (float(count_nonzero(mask_array)) /
                #                                                   mask_array.size) * 100)

                if data_arr is None:
                    masked_arr = where(mask_array > 0, self._output_tracker['current_month'][parameter],
                                       zeros(data_arr.shape))
                else:
                    masked_arr = where(mask_array > 0, data_arr, zeros(data_arr.shape))

                arr_sum = masked_arr.sum()
                param_cubic_meters = (arr_sum / 1000) * (250 ** 2)
                df =
                df.loc[date, 'CBM'] = param_cubic_meters
                param_acre_feet = param_cubic_meters / 1233.48
                df.loc[date, 'AF'] = param_acre_feet
                print '{} {} {:.2e} AF'.format(sub_region, parameter, param_acre_feet)
                print ''

        return None

    def _save_tabulated_results_to_csv(self, results_directories, polygons):

        print 'results directories: {}'.format(results_directories)
        folders = os.listdir(polygons)
        for in_fold in folders:
            print 'saving tab data for input region: {}'.format(in_fold)
            region_type = os.path.basename(in_fold).replace('_Polygons', '')
            files = os.listdir(os.path.join(polygons, os.path.basename(in_fold)))
            print 'tab data from shapes: {}'.format([infile for infile in files if infile.endswith('.shp')])
            for element in files:
                if element.endswith('.shp'):
                    sub_region = element.strip('.shp')

                    df = self._tabular_dict[region_type][sub_region]

                    if self._write_freq == 'daily':
                        df_month = df.resample('M').sum()
                        save_loc_day = os.path.join(results_directories['daily_tabulated'][region_type],
                                                    '{}.csv'.format(sub_region))
                    else:
                        df_month = self._tabular_dict[region_type][sub_region]
                        save_loc_day = None

                    df_annual = df_month.resample('A').sum()

                    save_loc_annu = os.path.join(results_directories['annual_tabulated'][region_type],
                                                 '{}.csv'.format(sub_region))

                    save_loc_month = os.path.join(results_directories['root'],
                                                  results_directories['monthly_tabulated'][region_type],
                                                  '{}.csv'.format(sub_region))

                    if self._write_freq == 'daily':
                        dfs = [df, df_month, df_annual]
                        locations = [save_loc_day, save_loc_month, save_loc_annu]
                    else:
                        dfs = [df_month, df_annual]
                        locations = [save_loc_month, save_loc_annu]

                    for df, location in zip(dfs, locations):
                        print 'this should be your location csv: {}'.format(location)
                        df.to_csv(location, na_rep='nan', index_label='Date')
        return None


if __name__ == '__main__':
    pass

# ============= EOF =============================================
