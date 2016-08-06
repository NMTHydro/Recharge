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
import os


class ManageRasters(object):

    def __init__(self, out_path):
        self._out_path = out_path
        pass

    def convert_raster_to_array(self, raster=None, input_raster_path=None,
                                filename=None, minimum_value=None, band=1):
        if not raster:
            raster = self._open_raster(input_path=input_raster_path, filename=filename)
        ras = array(raster.GetRasterBand(band).ReadAsArray(), dtype=float)
        if minimum_value:
            min_val = ones(ras.shape) * minimum_value
            ras = maximum(ras, min_val)
        return ras

    def save_raster(self, master_dictionary, outputs, date_object):
        mo_date = monthrange(date_object.year, date_object.month)
        if date_object.day == mo_date[1]:
            count_output = 0
            for element in outputs:
                self._write_raster(master_dictionary, element, date_object, 'monthly')
                self._update(master_dictionary, zero_out=True)
                count_output += 1
        if date_object.day == 31 and date_object.month == 12:
            count_output = 0
            for element in outputs:
                self._write_raster(master_dictionary, element, date_object, 'annual')
                self._update(master_dictionary, zero_out=True)
                count_output += 1

    def _update(self, dictionary, zero_out=False):
        pass
        if zero_out:

    def _open_raster(self, input_path, filename):
        ras_open = gdal.Open('{a}\\{b}'.format(a=input_path, b=filename))
        return ras_open

    def _write_raster(self, dictionary, key, date, period):
        dataset = dictionary['taw']
        print "Saving {}_{}_{}".format(key, date.month, date.year)
        driver = gdal.GetDriverByName('GTiff')
        filename = os.path.join(self._out_path, period)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        bands = dataset.RasterCount
        band = dataset.GetRasterBand(1)
        datatype = band.DataType
        outdataset = driver.Create(filename, cols, rows, bands, datatype)
        geotransform = dataset.GetGeoTransform()
        outdataset.SetGeoTransform(geotransform)
        proj = dataset.GetProjection()
        outdataset.SetProjection(proj)
        outband = outdataset.GetRasterBand(1)
        outband.WriteArray(dictionary[key], 0, 0)

# ============= EOF =============================================