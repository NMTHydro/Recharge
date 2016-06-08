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
# ============= local library imports  ==========================


# ============= EOF =============================================
import os
from math import isnan

from numpy import array, where, zeros
from osgeo import gdal


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