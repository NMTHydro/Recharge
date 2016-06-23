# ===============================================================================
# Copyright 2016 ross
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

# ============= standard library imports ========================
import os
import logging
from math import isnan

import yaml
from numpy import array, where, zeros
from osgeo import gdal


# ============= local library imports  ==========================

class InvalidDataSourceException(BaseException):
    def __init__(self, path):
        self._path = path

    def __str__(self):
        return 'InvalidDataSource. Could not locate "{}"'.format(self._path)


def get_config(path):
    if os.path.isfile(path):
        with open(path, 'r') as rfile:
            cfg = yaml.load(rfile)
    else:
        logging.warning('************************************')
        logging.info('Failed locating configuration')
        ret = raw_input('Would you like to continue with default configuration? [y]/n >> ')
        if ret not in ('\n', '', 'y'):
            return

        input_root = os.path.join('F:', 'ETRM_Inputs')
        results_root = os.path.join('F:', 'ETRM_Results')
        cfg = {'current_use': os.path.join('C:', 'Recharge_GIS', 'OSG_Data', 'current_use'),
               'array_results': os.path.join('C:', 'Recharge_GIS', 'Array_Results', 'initialize'),
               'ndvi': os.path.join(input_root, 'NDVI', 'NDVI_std_all'),
               'prism': os.path.join(input_root, 'PRISM', 'Precip', '800m_std_all'),
               'prism_min_temp': os.path.join(input_root, 'PRISM', 'Temp', 'Minimum_standard'),
               'prism_max_temp': os.path.join(input_root, 'PRISM', 'Temp', 'Maximum_standard'),
               'pm_data': os.path.join(input_root, 'PM_RAD'),
               'annual_results': os.path.join(results_root, 'Annual_results'),
               'monthly_results': os.path.join(results_root, 'Monthly_results'),
               'output_tag': '23MAY',
               'start': '2000-1-1',
               'end': '2000-12-31',
               'start_month': 6,
               'end_month': 10,
               }
    return cfg


def tif_path(root, name):
    """

    :param root:
    :param name:
    :return:
    """
    if not name.endswith('.tif'):
        name = '{}.tif'.format(name)

    path = os.path.join(root, name)
    return path


def tif_params(root, name, band=1):
    """

    :param root:
    :param name:
    :param band:
    :return:
    """
    path = tif_path(root, name)
    obj = gdal.Open(path)
    band = obj.GetRasterBand(band)
    d = {'cols': obj.RasterXSize, 'rows': obj.RasterYSize,
         'bands': obj.RasterCount,
         'band': band,
         'projection': obj.GetProjection(),
         'geo_transform': obj.GetGeoTransform(),
         'datatype': band.DataType}

    # probably not necessary
    del obj

    return d


def tif_to_array(root, name, band=1):
    """
    Helper function for getting an array from a tiff

    :param root: directory
    :type root: str
    :param name: name of file
    :type name: str
    :param band: band
    :type band: int
    :return: numpy.ndarray
    """
    if not name.endswith('.tif'):
        name = '{}.tif'.format(name)

    path = os.path.join(root, name)
    if not os.path.isfile(path):
        logging.critical('Could not locate {}'.format(path))
        raise InvalidDataSourceException(path)

    rband = gdal.Open(path).GetRasterBand(band)
    return array(rband.ReadAsArray())


def clean(d):
    """
    Replace NaN with 0

    :param d: input array
    :type d: numpy.ndarray
    :return: numpy.ndarray
    """
    return where(isnan(d), zeros(d.shape), d)

# ============= EOF =============================================
