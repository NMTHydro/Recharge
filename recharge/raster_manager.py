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
from numpy import array, where, zeros, isnan
from calendar import monthrange
import os

from tools import millimeter_to_acreft as mm_af
from raster_tools import get_raster_geo_attributes as get_geo
from dict_setup import initialize_raster_tracker


class Rasters(object):

    def __init__(self, path_to_representative_raster, outputs):
        self._geo = get_geo(path_to_representative_raster)
        self._output_tracker = initialize_raster_tracker(outputs, (self._geo['rows'], self._geo['cols']))

    def update_save_raster(self, master, output_tracker, tab_dict, outputs, date_object, raster_output_path,
                           results_dir, shapefiles=None, save_specific_dates=None, save_outputs=None):

        # raster_track_dict = {'output_an': {'output': raster}, 'output_mo': {{'output': raster}},
        #                      'last_mo': {{'output': raster}}, 'last_yr': {{'output': raster}}}

        # outputs = ['tot_infil', 'tot_ref_et', 'tot_eta', 'tot_precip', 'tot_ro', 'tot_snow', 'tot_mass',
        #                  'tot_rain', 'tot_melt', 'soil_storage']

        mo_date = monthrange(date_object.year, date_object.month)

        # save data for a certain day
        if save_specific_dates:
            if date_object in save_specific_dates:
                for element in save_outputs:
                    written_raster = self._write_raster(output_tracker, element, date_object, raster_output_path,
                                                        self._geo, results_dir, period='day', master=master)
                    self._sum_raster_by_shape(written_raster, tab_dict, shapefiles, self._geo, element,
                                              date_object, raster_output_path)
        # # FOR TESTING: calculate  xth day #
        # if date_object.day == 03:
        #     print ''
        #     print 'attempting to update/save day: {}'.format(date_object)
        #     print 'outputs: {}'.format(outputs)
        #     for element in outputs:
        #         self._update_raster_tracker(master, output_tracker, element)
        #         written_raster = self._write_raster(output_tracker, element, date_object, raster_output_path,
        #                                             self._geo, results_dir, period='monthly')
        #
        #         self._sum_raster_by_shape(written_raster, tab_dict, shapefiles, self._geo, element,
        #                                   date_object, raster_output_path)
        #         print 'saving {} raster, tracker total: {} AF'.format(element,
        #                                                               mm_af(output_tracker['current_month'][element]))

        # save monthly data
        # etrm_processes.run._save_tabulated_results_to_csv will resample to annual
        if date_object.day == mo_date[1]:
            print ''
            print 'date : {}'.format(date_object.strftime('%B %Y'))
            for element in outputs:
                self._update_raster_tracker(master, output_tracker, element)
                self._write_raster(output_tracker, element, date_object, raster_output_path,
                                                    self._geo, results_dir, period='monthly')

                self._sum_raster_by_shape(tab_dict, shapefiles, self._geo, element,
                                          date_object, raster_output_path)

        # save annual data
        if date_object.day == 31 and date_object.month == 12:
            for element in outputs:
                self._update_raster_tracker(master, output_tracker, element, annual=True)
                self._write_raster(output_tracker, element, date_object, raster_output_path,
                                                    self._geo, results_dir, period='annual')

                self._sum_raster_by_shape(tab_dict, shapefiles, self._geo, element,
                                          date_object, raster_output_path)

        return None

    def _update_raster_tracker(self, master_dict, raster_output_tracker, var, annual=False):
        """ Updates the cummulative rasters each period as indicated.

        This function is to prepare a dict of rasters showing the flux over the past time period (month, year).

        :param master_dict: master from etrm_processes.Processes
        :param previous_master: last month's master dict
        :param cumulative_dict: the difference between this dict and last
        :param var: vars are all accumulation terms from master
        :param first: identify first day
        :return: None
        """

        # {'current_year': {}, 'current_month': {}, 'current_day': {}, 'last_mo': {}, 'last_yr': {}, 'last_day': {}}
        # print 'update variable # {} # total: {} AF'.format(var, mm_af(master_dict[var]))
        if annual:
            raster_output_tracker['current_year'][var] = master_dict[var] - raster_output_tracker['last_yr'][var]
            raster_output_tracker['last_yr'][var] = raster_output_tracker['current_year'][var]

        raster_output_tracker['current_month'][var] = master_dict[var] - raster_output_tracker['last_mo'][var]
        raster_output_tracker['last_mo'][var] = raster_output_tracker['current_month'][var]
        # print 'updated variable $ {} # total: {} AF'.format(var,
        #                                                     mm_af(raster_output_tracker['current_month'][var]))
        # print 'check against tot_ref_et: {} AF'.format(mm_af(master_dict['tot_ref_et']))
        # print 'check against tot_ppt: {} AF'.format(mm_af(master_dict['tot_precip']))

        return None

    def _write_raster(self, output_raster_dict, key, date, out_path, raster_geometry, results_directory, period=None,
                      master=None):

        print ''
        print "Saving {}_{}_{}".format(key, date.month, date.year)

        if period == 'annual':
            file_ = '{}_{}.tif'.format(key, date.year)
            filename = os.path.join(out_path, results_directory['annual_rasters'], file_)
            array_to_save = output_raster_dict['current_year'][key]
        elif period == 'monthly':
            file_ = '{}_{}_{}.tif'.format(key, date.month, date.year)
            filename = os.path.join(out_path, results_directory['monthly_rasters'], file_)
            array_to_save = output_raster_dict['current_month'][key]
        elif period == 'daily':
            file_ = '{}_{}_{}_{}.tif'.format(key, date.year, date.month, date.year)
            filename = os.path.join(out_path, results_directory['daily_rasters'], file_)
            array_to_save = master[key]
        else:
            array_to_save = None
            filename = None

        driver = gdal.GetDriverByName('GTiff')
        out_data_set = driver.Create(filename, raster_geometry['cols'], raster_geometry['rows'],
                                     raster_geometry['bands'], raster_geometry['data_type'])
        out_data_set.SetGeoTransform(raster_geometry['geotransform'])
        out_data_set.SetProjection(raster_geometry['projection'])
        output_band = out_data_set.GetRasterBand(1)
        output_band.WriteArray(array_to_save, 0, 0)

        return filename

    def _sum_raster_by_shape(self, raster, tabular_dict, shapes, geo_attributes, parameter, date,
                             output_path):

        folders = os.listdir(shapes)
        # print 'processing parameter: {}'.format(parameter)
        for in_fold in folders:
            # print 'input geo shapes folder: {}'.format(in_fold)
            region_type = os.path.basename(in_fold).replace('_Polygons', '')
            files = os.listdir(os.path.join(shapes, in_fold))
            # print 'files in region {}:\n{}'.format(region_type, files)
            for element in files:
                if element.endswith('.shp'):
                    sub_region = element.strip('.shp')
                    shp_name = os.path.join(shapes, in_fold, element)
                    polygon = ogr.Open(shp_name)
                    layer = polygon.GetLayer()
                    driver = gdal.GetDriverByName('GTiff')
                    temp_raster = os.path.join(output_path, 'temp.tif')
                    mask_raster = driver.Create(temp_raster, geo_attributes['cols'], geo_attributes['rows'], 1,
                                                geo_attributes['data_type'])
                    mask_raster.SetProjection(layer.GetSpatialRef().ExportToWkt())
                    mask_raster.SetGeoTransform(geo_attributes['geotransform'])
                    raster_band = mask_raster.GetRasterBand(1)
                    raster_band.SetNoDataValue(0.0)
                    raster_band.Fill(0.0)
                    gdal.RasterizeLayer(mask_raster, [1], layer, options=["ALL_TOUCHED=TRUE",
                                                                          "OGRLayerShadow=FALSE"])
                    mask_raster.FlushCache()
                    mask_array = mask_raster.GetRasterBand(1).ReadAsArray()
                    del mask_raster
                    mask_array = array(mask_array)
                    # print 'mask array is {} cells, of {}, or {}%'.format(count_nonzero(mask_array),
                    #                                                      mask_array.size,
                    #                                                      (float(count_nonzero(mask_array)) /
                    #                                                       mask_array.size) * 100)

                    raster_obj = gdal.Open(raster)
                    param_obj = array(raster_obj.GetRasterBand(1).ReadAsArray(), dtype=float)
                    param_obj = where(isnan(param_obj), zeros(param_obj.shape), param_obj)
                    param_obj = where(param_obj < 0, zeros(param_obj.shape), param_obj)
                    param_obj = where(mask_array > 0, param_obj, zeros(param_obj.shape))
                    param_sum = param_obj.sum()
                    param_cubic_meters = (param_sum / 1000) * (250 ** 2)
                    param_acre_feet = param_cubic_meters / 1233.48
                    df = tabular_dict[region_type][sub_region]
                    print '{} {} {:.2e} AF'.format(os.path.basename(shp_name).replace('.shp', ''),
                                                   parameter, param_acre_feet)
                    df['{}_[cbm]'.format(parameter)].loc[date] = param_cubic_meters
                    df['{}_[AF]'.format(parameter)].loc[date] = param_acre_feet
        return None

if __name__ == '__main__':
    pass

# ============= EOF =============================================
