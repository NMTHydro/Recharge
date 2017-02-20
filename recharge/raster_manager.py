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
The purpose of this module is to create a ETRM-style raster object. This carries important geographic information
and water balance components used in output data.

this module provides (1) class -- class Rasters(object):

dgketchum 24 JUL 2016
"""

# from osgeo import gdal, ogr
import gdal
import ogr

from numpy import array, where, zeros
from calendar import monthrange
import os

from recharge.raster_tools import make_results_dir, apply_mask, remake_array
from recharge.raster_tools import get_raster_geo_attributes as get_geo, convert_raster_to_array as to_array
from recharge.dict_setup import initialize_tabular_dict, initialize_raster_tracker

OUTPUTS = ('infil', 'etrs', 'eta', 'precip', 'kcb')
DAILY_OUTPUTS = ('infil', 'etrs', 'eta', 'precip')

class RasterManager(object):
    def __init__(self, path_to_representative_raster, polygons, simulation_period, output_root,
                 write_frequency=None):

        self._write_freq = write_frequency
        self._polygons = polygons
        self._simulation_period = simulation_period

        # _outputs are flux totals, monthly and annual are found with _update_raster_tracker()
        # daily totals only need master values (i.e., 'infil' rather than 'tot_infil'
        # and thus we assign a list of daily outputs
        # TODO: Hardcoded tot_infil vs invil, tot_etrs vs etrs etc.
        # self._outputs = ('infil', 'etrs', 'eta', 'precip', 'kcb')  # infil change to tot_infil
        if write_frequency == 'daily':
            # daily outputs should just be normal fluxes, while _outputs are of simulation totals
            print 'your daily outputs will be from: {}'.format(DAILY_OUTPUTS)

        self._geo = get_geo(path_to_representative_raster)
        self._output_tracker = initialize_raster_tracker(OUTPUTS, (self._geo['rows'], self._geo['cols']))
        self._results_dir = make_results_dir(output_root, polygons)
        self._tabular_dict = initialize_tabular_dict(polygons, OUTPUTS, simulation_period, write_frequency)

    def update_raster_obj(self, master, mask_path, date_object, save_specific_dates=None):
        """
        Checks if the date is specified for writing output and calls the write and tabulation methods.

        :param master: master dict object from etrm.Processes
        :param date_object: datetime date object
        :param save_specific_dates: list of datetime objects for which output is written
        :return: None
        """
        mo_date = monthrange(date_object.year, date_object.month)

        # save data for a certain day
        if save_specific_dates:
            if date_object in save_specific_dates:
                for element in DAILY_OUTPUTS:
                    self._write_raster(element, date_object, period='single_day', master=master)

        # save daily data (this will take a long time)
        # don't use 'tot_parameter' or you will sum totals
        # just use the normal daily fluxes from master, aka _daily_outputs
        if self._write_freq == 'daily':
            for element in DAILY_OUTPUTS:
                arr = remake_array(mask_path, master[element])
                self._sum_raster_by_shape(element, date_object, arr)

        # save monthly data
        # etrm_processes.run._save_tabulated_results_to_csv will re-sample to annual
        if date_object.day == mo_date[1]:
            print ''
            print 'saving monthly data for {}'.format(date_object)
            for element in OUTPUTS:
                arr = remake_array(mask_path, master[element])
                self._update_raster_tracker(arr, element, period='monthly')
                self._write_raster(element, date_object, period='monthly')
                if not self._write_freq:
                    self._sum_raster_by_shape(element, date_object)

        # save annual data
        if date_object.month == 12 and date_object.day == 31:
            for element in OUTPUTS:
                arr = remake_array(mask_path, master[element])
                self._update_raster_tracker(arr, element, period='annual')
                self._write_raster(element, date_object, period='annual')

    def save_csv(self):
        print 'tab dict: \n{}'.format(self._tabular_dict)
        print 'saving the simulation master tracker'
        self._save_tabulated_results_to_csv(self._results_dir, self._polygons)

    def _update_raster_tracker(self, vv, var, period):
        """ Updates the cumulative rasters each period as indicated.

        This function is to prepare a dict of rasters showing the flux over the past time period (month, year).

        :param master_dict: master from etrm_processes.Processes
        :param var: vars are all accumulation terms from master
        :return: None
        """

        if period == 'annual':
            self._output_tracker['current_year'][var] = vv - self._output_tracker['last_yr'][var]
            self._output_tracker['last_yr'][var] = vv
        elif period == 'monthly':

            self._output_tracker['current_month'][var] = vv - self._output_tracker['last_mo'][var]

            print 'mean value master {} today: {}'.format(var, vv.mean())
            print 'mean value output tracker today: {}'.format(self._output_tracker['current_month'][var].mean())
            print 'mean value output tracker yesterday: {}'.format(self._output_tracker['last_mo'][var].mean())

            self._output_tracker['last_mo'][var] = vv

    def _write_raster(self, key, date, period=None, master=None):

        print ''
        print 'Saving {}_{}_{}'.format(key, date.month, date.year)

        rd = self._results_dir
        root = rd['root']
        tracker = self._output_tracker
        if period == 'annual':
            file_ = '{}_{}.tif'.format(key, date.year)
            filename = os.path.join(root, rd['annual_rasters'], file_)
            array_to_save = tracker['current_year'][key]

        elif period == 'monthly':
            file_ = '{}_{}_{}.tif'.format(key, date.month, date.year)
            filename = os.path.join(root, rd['monthly_rasters'], file_)
            array_to_save = tracker['current_month'][key]
            print 'saving {}, mean: {}'.format(key, tracker['current_month'][key].mean())

        elif period == 'single_day':
            file_ = '{}_{}_{}_{}.tif'.format(key, date.year, date.month, date.year)
            filename = os.path.join(root, rd['daily_rasters'], file_)
            array_to_save = master[key]

        elif period == 'simulation':
            file_ = '{}_{}_{}.tif'.format(key, self._simulation_period[0], self._simulation_period[1])
            filename = os.path.join(root, rd['simulation_tot_rasters'], file_)
            array_to_save = master[key]

        else:
            array_to_save = None
            filename = None

        driver = gdal.GetDriverByName('GTiff')
        geo = self._geo
        out_data_set = driver.Create(filename, geo['cols'], geo['rows'],
                                     geo['bands'], geo['data_type'])
        out_data_set.SetGeoTransform(geo['geotransform'])
        out_data_set.SetProjection(geo['projection'])
        output_band = out_data_set.GetRasterBand(1)
        output_band.WriteArray(array_to_save, 0, 0)
        print 'written array {} mean value: {}'.format(key, array_to_save.mean())
        del out_data_set, output_band

    def _sum_raster_by_shape(self, parameter, date, data_arr=None):
        """
        Finds a water balance component over a particular geography and adds to a tabular dataset (dataframe) object.

        :param parameter: Water balance component.
        :param date: Datetime date object.
        :param data_arr:
        :return:
        """
        region_folders = os.listdir(self._polygons)
        # print 'processing parameter: {}'.format(parameter)
        current_month = self._output_tracker['current_month']

        for region_folder in region_folders:
            # print 'input geo shapes region: {}'.format(region_folder)
            region_type = os.path.basename(region_folder).replace('_Polygons', '')
            all_geo_files = os.listdir(os.path.join(self._polygons, region_folder))
            shape_files = [shapefile for shapefile in all_geo_files if shapefile.endswith('.shp')]
            # print 'files in region {}:\n{}'.format(region_type, all_geo_files)
            # print ''
            for geometry in shape_files:
                sub_region, _ = os.path.splitext(geometry)
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

                # if summing monthly or annual data, use the current month/year values
                # use daily for testing
                if data_arr is None:
                    masked_arr = where(mask_array > 0, current_month[parameter],
                                       zeros(current_month[parameter].shape))

                # if summing daily data, just use data array, which is from the master dict[data_array]
                else:
                    masked_arr = where(mask_array > 0, data_arr, zeros(data_arr.shape))

                arr_sum = masked_arr.sum()
                param_cubic_meters = (arr_sum / 1000) * (self._geo['resolution'] ** 2)
                # ==========================================================================
                print 'tabular dict: {}'.format(self._tabular_dict)
                print 'parameter: {}'.format(parameter)
                # ===========================================================================
                df = self._tabular_dict[region_type][sub_region][parameter, 'CBM']  # <= problem here

                df.loc[date] = param_cubic_meters
                # print 'df for {} on {} = {}'.format(parameter, date, df.loc[date])

                param_acre_feet = param_cubic_meters / 1233.48
                df = self._tabular_dict[region_type][sub_region][parameter, 'AF']
                df.loc[date] = param_acre_feet
                # print 'df for {} on {} = {}'.format(parameter, date, df.loc[date])
                if param_acre_feet > 0.0:
                    print '{} {} {:.2e} AF'.format(sub_region, parameter, param_acre_feet)

        return None

    def _save_tabulated_results_to_csv(self, results_directories, polygons):
        """
        Save tabulated dataframe object to csv.  Resample to specified time periods.

        :param results_directories: Path to results folders.  This is created automatically in make_results_dir
        :param polygons: Folder containing polygon folders of each type of geography (counties, etc.)
        :return: None
        """
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

                        df_month = df.resample('M').sum()
                        save_loc_day = None

                    df_annual = df_month.resample('A').sum()

                    save_loc_annu = os.path.join(results_directories['annual_tabulated'][region_type],
                                                 '{}.csv'.format(sub_region))

                    # save_loc_month = os.path.join(results_directories['root'],
                    # results_directories['monthly_tabulated'][region_type],
                    # '{}.csv'.format(sub_region))
                    save_loc_month = os.path.join(results_directories['monthly_tabulated'][region_type],
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


# ============= EOF =============================================
