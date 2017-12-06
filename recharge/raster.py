# ===============================================================================
# Copyright 2017 ross
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

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
import os

from numpy import array, asarray
from numpy.ma import masked_where, nomask
from osgeo import gdal

from app.paths import paths

gmask = None
gmask_path = None


class Raster(object):
    _band = 1
    _path = None
    _arr = None
    _geo = None
    _masked_arr = None

    def __init__(self, path=None, root=None, band=1):
        if path is not None:
            if root is not None:
                path = os.path.join(root, path)
            self.open(path, band)

    @classmethod
    def fromarray(cls, arr, geo=None):
        r = cls()
        r._arr = arr
        r._geo = geo
        return r

    @property
    def geo(self):
        return self._geo

    @property
    def as_bool_array(self):
        return asarray(self._arr, dtype=bool)

    @property
    def array(self):
        """

        :return:
        """
        return self._masked_arr if self._masked_arr is not None else self._arr

    def set_array(self, arr):
        self._arr = arr

    def apply_mask(self):
        """
        apply mask to ourself

        :return:
        """
        self._masked_arr = self.masked()

    def filter_greater(self, fvalue, value):
        """
        where arr is greater than fvalue set arr to value
        :param fvalue: float
        :param value: float
        :return:
        """
        if self._masked_arr:
            arr = self._masked_arr
        else:
            arr = self._arr

        arr[arr > fvalue] = value

    def filter_less(self, fvalue, value):
        """
        where arr is greater than fvalue set arr to value
        :param fvalue: float
        :param value: float
        :return:
        """
        if self._masked_arr:
            arr = self._masked_arr
        else:
            arr = self._arr

        arr[arr < fvalue] = value

    def remove_negatives(self):
        self.filter_less(0, 0)

    def unmasked(self):
        idxs = self._get_masked_indices()
        # print 'asdfasfdsadf', idxs
        if idxs is not None:
            idxs = asarray(idxs, int)
            masked_arr = masked_where(idxs == 0, idxs)
            # print 'masked_arr: {}'.format((masked_arr))
            # print 'idxs: {}'.format((idxs))
            # print 'self ravel: {}'.format((self._arr.reshape(72, 242)))
            # print '~mask_etc: {}'.format((~masked_arr.mask))

            # masked_arr = self._arr.reshape(len(masked_arr), len(masked_arr[0]))
            masked_arr[~masked_arr.mask] = self._arr.ravel()
            masked_arr.mask = nomask
        else:
            masked_arr = self._arr#.ravel()

        return masked_arr
        # return masked_arr.filled(0)

    def masked(self):
        """
        returns valid points as 1-d array

        :return:
        """
        idxs = self._get_masked_indices()
        arr = self._arr
        if idxs is not None:
            arr = arr[idxs]
            arr = arr.flatten()
        return arr

    def open(self, path, band=1):
        """

        :param path: path to GeoTiff
        :param band:
        :return:
        """
        if not os.path.isfile(path):
            print 'Not a valid file: {}'.format(path)
            return

        self._path = path
        self._band = band
        raster = gdal.Open(self._path)
        rband = raster.GetRasterBand(band)
        self._arr = array(rband.ReadAsArray(), dtype=float)
        self._geo = {'cols': raster.RasterXSize, 'rows': raster.RasterYSize, 'bands': raster.RasterCount,
                     'data_type': rband.DataType, 'projection': raster.GetProjection(),
                     'geotransform': raster.GetGeoTransform(), 'resolution': raster.GetGeoTransform()[1]}

        del raster

    def save(self, output, arr=None, geo=None, band=None):
        """
        save an array as a GeoTiff

        :param arr:
        :param geo:
        :param band:
        :return:
        """
        if arr is None:
            arr = self._arr
        if geo is None:
            geo = self._geo
        if band is None:
            band = self._band

        self._save(output, arr, geo, band)

    # private
    def _get_masked_indices(self):
        global gmask_path, gmask
        if paths.mask:
            if gmask is None or gmask_path != paths.mask:
                if os.path.isfile(paths.mask):
                    print 'caching mask: {}'.format(paths.mask)
                    mask = Raster(paths.mask)
                    gmask = mask.as_bool_array
                    gmask_path = paths.mask

        return gmask

    def _save(self, path, arr, geo, band):
        driver = gdal.GetDriverByName('GTiff')
        out_data_set = driver.Create(path, geo['cols'], geo['rows'],
                                     geo['bands'], geo['data_type'])
        out_data_set.SetGeoTransform(geo['geotransform'])
        out_data_set.SetProjection(geo['projection'])

        output_band = out_data_set.GetRasterBand(band)
        output_band.WriteArray(arr, 0, 0)
        del out_data_set, output_band

# ============= EOF =============================================
