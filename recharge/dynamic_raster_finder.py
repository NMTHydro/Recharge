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
The purpose of this module is to find a raster file for a specified day.

this module provides (2) function -- find_ndvi, find_prism.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""

import os
from numpy import where, isnan

from recharge.raster_tools import convert_raster_to_array
import recharge.point_extract_utility


def get_kcb(in_path, date_object, previous_kcb=None, coords=None):
    # print date_object
    doy = date_object.timetuple().tm_yday
    if date_object.year == 2000:
        raster = '{}_{}.tif'.format(date_object.year, doy)
        if coords:
            ndvi = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
            kcb = ndvi * 1.25
            return kcb
        ndvi = convert_raster_to_array(in_path, raster, band=1)
        kcb = ndvi * 1.25

    elif date_object.year == 2001:
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        for num in obj:
            diff = doy - num
            if 0 <= diff <= 15:
                pos = obj.index(num)
                start = obj[pos]
                band = diff + 1
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15
                raster = '{a}\\{b}_{c}_{d}.tif'.format(a=in_path, b=date_object.year, c=start, d=nd)
                if coords:
                    ndvi = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
                    kcb = ndvi * 1.25
                    return kcb
                ndvi = convert_raster_to_array(in_path, raster, band=band)
                kcb = ndvi * 1.25

    else:
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        for num in obj:
            diff = doy - num
            if 0 <= diff <= 15:
                pos = obj.index(num)
                band = diff + 1
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15
                raster = '{a}\\{b}_{c}.tif'.format(a=in_path, b=date_object.year, c=pos + 1, d=nd)
                if coords:
                    ndvi = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
                    kcb = ndvi * 1.25
                    return kcb
                ndvi = convert_raster_to_array(in_path, raster, band=band)
                kcb = ndvi * 1.25

    if previous_kcb is None:
        pass
    else:
        kcb = where(isnan(kcb) == True, previous_kcb, kcb)
        kcb = where(abs(kcb) > 100., previous_kcb, kcb)

    return kcb


def get_prism(in_path, date_object, variable='precip', coords=None):

    if variable == 'precip':

        path = os.path.join(in_path, 'precip', '800m_std_all')  # this will need to be fixed
        raster = 'PRISMD2_NMHW2mi_{}{}{}.tif'.format(date_object.year,
                                                     str(date_object.month).rjust(2, '0'),
                                                     str(date_object.day).rjust(2, '0'))
        if coords:
            ppt = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
            return ppt
        # print 'ppt raster: {}'.format(raster)
        ppt = convert_raster_to_array(path, raster)

        return ppt

    elif variable == 'min_temp':
        if date_object.year in [2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013]:
            path = os.path.join(in_path, 'Temp', 'Minimum_standard')
            raster = 'cai_tmin_us_us_30s_{}{}{}.tif'.format(date_object.year,
                                                            str(date_object.month).rjust(2, '0'),
                                                            str(date_object.day).rjust(2, '0'))
            if coords:
                min_temp = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
                return min_temp

            min_temp = convert_raster_to_array(path, raster)

        else:
            path = os.path.join(in_path, 'Temp', 'Minimum_standard')
            raster = 'TempMin_NMHW2Buff_{}{}{}.tif'.format(date_object.year,
                                                           str(date_object.month).rjust(2, '0'),
                                                           str(date_object.day).rjust(2, '0'))
            if coords:
                min_temp = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
                return min_temp
            min_temp = convert_raster_to_array(path, raster)

        return min_temp

    if variable == 'max_temp':
        path = os.path.join(in_path, 'Temp', 'Maximum_standard')
        raster = 'TempMax_NMHW2Buff_{}{}{}.tif'.format(date_object.year,
                                                       str(date_object.month).rjust(2, '0'),
                                                       str(date_object.day).rjust(2, '0'))
        if coords:
            max_temp = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
            return max_temp
        max_temp = convert_raster_to_array(path, raster)
        return max_temp


def get_penman(in_path, date_object, variable='etrs', coords=None):
    doy = date_object.timetuple().tm_yday

    if variable == 'etrs':
        raster = 'PM{}\\PM_NM_{}_{}.tif'.format(date_object.year, date_object.year, str(doy).rjust(3, '0'))
        if coords:
            etrs = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
            return etrs
        etrs = convert_raster_to_array(in_path, raster)

        return etrs
    elif variable == 'rlin':
        raster = 'PM{}\\RLIN_NM_{}_{}.tif'.format(date_object.year, date_object.year, str(doy).rjust(3, '0'))
        if coords:
            rlin = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
            return rlin
        rlin = convert_raster_to_array(in_path, raster)

        return rlin
    elif variable == 'rg':
        raster = 'rad{}\\RTOT_{}_{}.tif'.format(date_object.year, date_object.year, str(doy).rjust(3, '0'))
        if coords:
            rg = recharge.point_extract_utility.get_inputs_at_point(coords, raster)
            return rg
        rg = convert_raster_to_array(in_path, raster)

        return rg

# ============= EOF =============================================
