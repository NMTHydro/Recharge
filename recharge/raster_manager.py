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

from pprint import pprint, pformat

"""
The purpose of this module is to create a ETRM-style raster object. This carries important geographic information
and water balance components used in output data.

this module provides (1) class -- class Rasters(object):

dgketchum 24 JUL 2016
"""

import os
from calendar import monthrange

import gdal
import ogr
from numpy import array, where, zeros

from app.paths import paths
from recharge import OUTPUTS, ANNUAL_TRACKER_KEYS, DAILY_TRACKER_KEYS, MONTHLY_TRACKER_KEYS, \
    CURRENT_YEAR, CURRENT_MONTH, CURRENT_DAY
from recharge.dict_setup import initialize_tabular_dict, initialize_raster_tracker
from recharge.raster import Raster
from recharge.raster_tools import get_raster_geo_attributes
from recharge.raster_tools import make_results_dir, convert_array_to_raster


class RasterManager(object):
    _save_dates = None

    def __init__(self, cfg):
        self._cfg = cfg
        self._write_freq = write_freq = cfg.write_freq
        self._simulation_period = simulation_period = cfg.date_range

        # _outputs are flux totals, monthly and annual are found with _update_raster_tracker()
        # daily totals only need master values (i.e., 'infil' rather than 'tot_infil'
        # and thus we assign a list of daily outputs
        # TODO: Hardcoded tot_infil vs invil, tot_etrs vs etrs etc.
        # self._outputs = ('infil', 'etrs', 'eta', 'precip', 'kcb')  # infil change to tot_infil
        if write_freq == 'daily':
            # daily outputs should just be normal fluxes, while _outputs are of simulation totals
            print 'your daily outputs will be from: {}'.format(cfg.daily_outputs)

        self._geo = get_raster_geo_attributes(paths.static_inputs)
        self._output_tracker = initialize_raster_tracker((self._geo['rows'], self._geo['cols']))
        self._results_dir = make_results_dir()
        self._tabular_dict = initialize_tabular_dict(simulation_period, write_freq)

    def set_save_dates(self, dates):
        self._save_dates = dates

    def update_raster_obj(self, master, date_object):
        """
        Checks if the date is specified for writing output and calls the write and tabulation methods.

        :param master: master dict object from etrm.Processes
        :param date_object: datetime date object
        :return: None
        """
        mo_date = monthrange(date_object.year, date_object.month)

        # save daily data (this will take a long time)
        # don't use 'tot_parameter' or you will sum totals
        # just use the normal daily fluxes from master, aka _daily_outputs

        if self._write_freq == 'daily':
            dailys = [(element, Raster.fromarray(master[element]).unmasked()) for element in self._cfg.daily_outputs]
            for element, arr in dailys:
                self._sum_raster_by_shape(element, date_object, arr)

            print "Heres the save dates", self._save_dates
            if self._save_dates:
                print 'Date object {}. {}'.format(date_object, date_object in self._save_dates)
                if date_object in self._save_dates:
                    self._set_outputs(dailys, date_object, 'daily')

        outputs = [(element, Raster.fromarray(master[element]).unmasked()) for element in OUTPUTS]
        # save monthly data
        # etrm_processes.run._save_tabulated_results_to_csv will re-sample to annual
        if date_object.day == mo_date[1]:
            print 'saving monthly data for {}'.format(date_object)
            self._set_outputs(outputs, date_object, 'monthly')

        # save annual data
        if date_object.month == 12 and date_object.day == 31:
            self._set_outputs(outputs, date_object, 'annual')

    def _set_outputs(self, outputs, date_object, period):
        for element, arr in outputs:
            self._update_raster_tracker(arr, element, period=period)
            self._write_raster(element, date_object, period=period)

            if not self._write_freq and period == 'monthly':
                self._sum_raster_by_shape(element, date_object)

    def save_csv(self):
        print 'tab dict: \n{}'.format(self._tabular_dict)
        print 'saving the simulation master tracker'
        self._save_tabulated_results_to_csv(self._results_dir, paths.polygons)

    def _update_raster_tracker(self, vv, var, period):
        """ Updates the cumulative rasters each period as indicated.

        This function is to prepare a dict of rasters showing the flux over the past time period (month, year).

        :param master_dict: master from etrm_processes.Processes
        :param var: vars are all accumulation terms from master
        :return: None
        """

        periods = ('annual', 'daily', 'monthly')

        if period not in periods:
            msg = 'invalid period "{}" cannot update tracker. period most be one of {}'.format(period, periods)

            print msg
            raise NotImplementedError(msg)

        tracker = self._output_tracker
        if period == 'annual':
            ckey, lkey = ANNUAL_TRACKER_KEYS
        elif period == 'daily':
            ckey, lkey = DAILY_TRACKER_KEYS
        elif period == 'monthly':
            ckey, lkey = MONTHLY_TRACKER_KEYS

        print 'ckey={}, lkey={}, period={}'.format(ckey, lkey, period)
        print 'mean value master {} today: {}'.format(var, vv.mean())
        print 'mean value output tracker today: {}'.format(tracker[ckey][var].mean())
        print 'mean value output tracker yesterday: {}'.format(tracker[lkey][var].mean())

        tracker[ckey][var] = vv - tracker[lkey][var]
        tracker[lkey][var] = vv

    def _write_raster(self, key, date, period=None, master=None):
        """
        get array from tracker and save to file

        file name based on attribute and period e.g

        dr_05_2017.tif is a monthly raster of dr
        de_01_01_2017.tif is daily raster of de

        """

        print 'Saving {}_{}_{}'.format(key, date.month, date.year)
        # print "mask path -> {}".format(mask_path)
        rd = self._results_dir
        # root = rd['root'] # results directory doesn't have a root; all
        tracker = self._output_tracker
        if period == 'annual':
            name = '{}_{}.tif'.format(key, date.year)
            filename = os.path.join(rd['annual_rasters'], name)
            array_to_save = tracker[CURRENT_YEAR][key]

        elif period == 'monthly':
            name = '{}_{}_{}.tif'.format(key, date.month, date.year)
            filename = os.path.join(rd['monthly_rasters'], name)
            array_to_save = tracker[CURRENT_MONTH][key]

        elif period == 'daily':
            name = '{}_{}_{}_{}.tif'.format(key, date.day, date.month, date.year)
            filename = os.path.join(rd['daily_rasters'], name)
            array_to_save = tracker[CURRENT_DAY][key]

        elif period == 'simulation':
            name = '{}_{}_{}.tif'.format(key, self._simulation_period[0], self._simulation_period[1])
            filename = os.path.join(rd['simulation_tot_rasters'], name)
            array_to_save = master[key]
        else:
            array_to_save = None
            filename = None

        print 'saving {} raster to {}'.format(key, filename)
        print 'written array {} mean value: {}'.format(key, array_to_save.mean())
        convert_array_to_raster(filename, array_to_save, self._geo)

    def _sum_raster_by_shape(self, parameter, date, data_arr=None):
        """
        Finds a water balance component over a particular geography and adds to a tabular dataset (dataframe) object.

        :param parameter: Water balance component.
        :param date: Datetime date object.
        :param data_arr:
        :return:
        """
        region_folders = os.listdir(paths.polygons)
        # print 'processing parameter: {}'.format(parameter)
        current_month = self._output_tracker['current_month']

        for region_folder in region_folders:
            # print 'input geo shapes region: {}'.format(region_folder)
            region_type = os.path.basename(region_folder).replace('_Polygons', '')
            all_geo_files = os.listdir(os.path.join(paths.polygons, region_folder))
            shape_files = [shapefile for shapefile in all_geo_files if shapefile.endswith('.shp')]
            # print 'files in region {}:\n{}'.format(region_type, all_geo_files)
            # print ''
            for geometry in shape_files:
                sub_region, _ = os.path.splitext(geometry)
                shp_name = os.path.join(paths.polygons, region_folder, geometry)
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
        print('results directories: "{}"'.format(pformat(results_directories, indent=2)))
        folders = os.listdir(polygons)

        print 'polygon directories: "{}"'.format(folders)
        if not folders:
            print 'no files/folders in "{}"'.format(polygons)
            return

        for in_fold in folders:
            print 'saving tab data for input region: {}'.format(in_fold)
            region_type = os.path.basename(in_fold).replace('_Polygons', '')

            root = os.path.join(polygons, os.path.basename(in_fold))
            files = os.listdir(root)

            files = [infile for infile in files if infile.endswith('.shp')]

            if not files:
                print 'no shape files in "{}"'.format(root)
                continue

            print 'tab data from shapes: {}'.format(files)
            for element in files:
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
