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

from osgeo import gdal
from numpy import array, ones, maximum
from calendar import monthrange
from datetime import datetime
import os


class ManageRasters(object):

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

    def update_save_raster(self, master, annual_dict,  monthly_dict, last_month_master, last_year_master,
                           outputs, date_object, raster_output_data, save_dates=None, save_outputs=None):

        mo_date = monthrange(date_object.year, date_object.month)
        if save_dates:
            for element in save_outputs:
                self._update(master, monthly_dict, last_month_master, element)
                self._write_raster(monthly_dict, element, date_object, raster_output_data, period='monthly')

        if date_object.day == mo_date[1]:
            for element in outputs:
                self._update(master, monthly_dict, last_month_master, element)
                self._write_raster(monthly_dict, element, date_object, raster_output_data, period='monthly')

        if date_object.day == 31 and date_object.month == 12:
            for element in outputs:
                self._update(master, annual_dict, last_year_master, element)
                self._write_raster(annual_dict, element, date_object, raster_output_data, period='annual')
        return None

    def _update(self, master_dict, previous_master, cumulative_dict, var):
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

    def _open_raster(self, input_path, filename):
        print ' raster name is {a}\\{b}'.format(a=input_path, b=filename)
        raster_open = gdal.Open('{a}\\{b}'.format(a=input_path, b=filename))
        return raster_open
            
# ============= EOF =============================================