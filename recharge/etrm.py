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
from math import isnan
from numpy import array, ones, where, zeros
from numpy.ma import maximum
from osgeo import gdal
from dateutil import rrule
from datetime import datetime
import os


# ============= local library imports  ==========================

# Modified from ETRM_distributed/ETRM_savAnMo_5MAY16.py
# Developed by David Ketchum NMT 2016


def tif_to_array(root, name, band=1):
    path = os.path.join(root, '{}.tif'.format(name))
    rband = gdal.Open(path).GetRasterBand(band)
    return array(rband.ReadAsArray(), dtype=float)


def clean(d, shape):
    return where(isnan(d) == True, zeros(shape), d)


class ETRM:
    _min_val = None
    _shape = None
    _qDeps = None
    _aws = None
    _nlcd_rt_z = None
    _nlcd_plt_hgt = None
    _ksat = None
    _tew = None
    _dr1 = None
    _de1 = None
    _drew = None
    _ndvi_root = 'F:\\ETRM_Inputs\\NDVI\\NDVI_std_all'
    _verbose = True

    def run(self):

        self._load_current_use()
        self._load_array_results()

        start_time = datetime.datetime.now()
        start = datetime.datetime(2000, 1, 1)
        end = datetime.datetime(2000, 12, 31)

        pkcb = zeros(self._shape)

        for i, dday in enumerate(rrule.rrule(rrule.DAILY, dtstart=start, until=end)):
            if i > 0:
                pkcb = kcb
            doy = dday.timetuple().tm_yday
            year = dday.year
            msg = 'Time : {a} day {b}_{c}'.format(datetime.now() - start_time, doy, )
            print msg

            if year == 2000:
                ndvi = self._calculate_ndvi_2000(doy)
            elif year == 2001:
                ndvi = self._calculate_ndvi_2001(year, doy)
            else:
                ndvi = self._calculate_ndvi(year)

            kcb = ndvi * 1.25
            kcb = maximum(kcb, self._min_val)
            kcb = where(isnan(kcb) == True, pkcb, kcb)

    # private
    def _load_current_use(self):
        root = 'C:\\Recharge_GIS\\OSG_Data\\current_use'
        qDeps = tif_to_array(root, 'Q_deps_std')

        min_val = ones(qDeps.shape) * 0.001
        qDeps = maximum(qDeps, min_val)

        aws = tif_to_array(root, 'aws_mod_4_21_10_0')
        aws = maximum(aws, min_val)

        nlcd_rt_z = tif_to_array(root, 'nlcd_root_dpth_15apr')
        nlcd_rt_z = maximum(nlcd_rt_z, min_val)

        nlcd_plt_hgt = tif_to_array(root, 'nlcd_plnt_hgt1_250_m_degraded1')
        nlcd_plt_hgt = maximum(nlcd_plt_hgt, min_val)

        ksat = tif_to_array(root, 'Soil_Ksat_15apr')
        ksat = maximum(ksat, min_val)

        tew = tif_to_array(root, 'tew_250_15apr')
        tew = maximum(tew, min_val)

        self._qDeps = qDeps
        self._aws = aws
        self._nlcd_rt_z = nlcd_rt_z
        self._nlcd_plt_hgt = nlcd_plt_hgt
        self._ksat = ksat
        self._tew = tew

        self._min_val = min_val
        self._shape = aws.shape

    def _load_array_results(self):
        shape = self._shape

        root = 'C:\\Recharge_GIS\\Array_Results\\initialize'

        tag = '4_19_23_11'
        de1 = tif_to_array(root, 'de_{}'.format(tag))
        de1 = clean(de1, shape)
        self._de1 = de1

        dr1 = tif_to_array(root, 'dr_{}'.format(tag))
        dr1 = clean(dr1, shape)
        self._dr1 = dr1

        drew = tif_to_array(root, 'drew_{}'.format(tag))
        drew = clean(drew, shape)
        self._drew = drew

    def _calculate_ndvi_2000(self, doy):

        base_name = 'T{:03n}_{:03n}_2000_etrf_subset_001_048_ndvi_daily'
        if doy < 49:
            a = 1
            b = 48
            name = base_name.format(a, b)
            if self._verbose:
                print 'calculate 1 {}'.format(name)
            ndvi = tif_to_array(self._ndvi_root, name, band=doy)
        else:
            obj = [1, 49, 81, 113, 145, 177, 209, 241, 273, 305, 337]

            idx = next((num for num in obj[1:] if 0 <= doy - num <= 31))

            diff = doy - idx
            offset = 29 if idx == 337 else 31

            strt = idx
            nd = idx + offset

            name = base_name.format(strt, nd)
            if self._verbose:
                print 'calculate 2 {}'.format(name)

            ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)

        return ndvi

    def _calculate_ndvi_2001(self, year, doy):
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        idx = next((num for num in obj[1:] if 0 <= doy - num <= 15))

        diff = doy - idx
        offset = 12 if idx == 353 else 15

        strt = idx
        nd = idx + offset

        name = '{}_{}_{}'.format(year, strt, nd)
        if self._verbose:
            print 'calculate 3 {}'.format(name)

        ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)
        return ndvi

    def _calculate_ndvi(self, year, doy):
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        idx = next((num for num in obj[1:] if 0 <= doy - num <= 15))

        diff = doy - idx
        name = '{}_{}'.format(year, obj.index(idx) + 1)
        if self._verbose:
            print 'calculate 4 {}'.format(name)

        ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)
        return ndvi


if __name__ == '__main__':

    e = ETRM()
    e.run()
# ============= EOF =============================================
