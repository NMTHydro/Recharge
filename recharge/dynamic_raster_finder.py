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
from osgeo import gdal

from recharge import NUMS, PRISM_YEARS
from recharge.raster import Raster


def get_inputs_at_point(coords, full_path):
    """
    Finds the point value for any coordinate in a raster object.

    :param coords: Coordinates in format '999999 0000000' UTM
    :type coords: str
    :param full_path: Path to raster.
    :type full_path: str
    :return: Point value of a raster, float
    """
    if type(coords) == str:
        mx, my = coords.split(' ')
        mx, my = int(mx), int(my)
    else:
        mx, my = coords
    # print 'coords: {}, {}'.format(mx, my)
    dataset = gdal.Open(full_path)
    gt = dataset.GetGeoTransform()

    # print "This here is the full path: {}".format(full_path) # For testing
    band = dataset.GetRasterBand(1)
    px = abs(int((mx - gt[0]) / gt[1]))
    py = int((my - gt[3]) / gt[5])
    obj = band.ReadAsArray(px, py, 1, 1)

    return obj[0][0]


def post_process_ndvi(name, in_path, previous_kcb, band=1, scalar=1.25):
    raster = Raster(name, root=in_path, band=band)
    ndvi = raster.masked()
    kcb = ndvi * scalar

    if previous_kcb is not None:
        kcb = where(isnan(kcb) is True, previous_kcb, kcb)
        kcb = where(abs(kcb) > 100.0, previous_kcb, kcb)

    return kcb


def get_spline_kcb(in_path, date_object, previous_kcb=None):
    year = str(date_object.year)

    tail = 'ndvi{}_{:03n}.tif'.format(year, date_object.timetuple().tm_yday)
    path = os.path.join(year, tail)
    # ndvi = apply_mask(mask_path, convert_raster_to_array(in_path, raster))

    raster = Raster(path, root=in_path)
    ndvi = raster.masked()
    return post_process_ndvi(ndvi, previous_kcb=previous_kcb)



def get_individ_kcb(in_path, date_object, previous_kcb=None):
    year = str(date_object.year)
    tail = 'NDVI{}_{:02n}_{:02n}.tif'.format(year,
                                             date_object.timetuple().tm_mon,
                                             date_object.timetuple().tm_mday)

    name = os.path.join(year, tail)
    # ndvi = apply_mask(mask_path, convert_raster_to_array(in_path, raster))
    return post_process_ndvi(name, in_path, previous_kcb)
    # raster = Raster(path, root=in_path)
    # ndvi = raster.masked()
    #
    # kcb = ndvi * 1.25
    #
    # if previous_kcb is not None:
    #     kcb = where(isnan(kcb) is True, previous_kcb, kcb)
    #     kcb = where(abs(kcb) > 100.0, previous_kcb, kcb)
    # return kcb


def get_kcb(in_path, date_object, previous_kcb=None):
    """
    Find NDVI image and convert to Kcb.

    :param in_path: NDVI input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :param previous_kcb: Previous day's kcb value.
    :param coords: Call if using to get point data using point_extract_utility.
    :return: numpy array object
    """
    # print date_object
    doy = date_object.timetuple().tm_yday
    year = date_object.year

    if year == 2000:
        band = 1
        name = '{}_{}.tif'.format(year, doy)
    elif year == 2001:
        for num in NUMS:
            diff = doy - num
            if 0 <= diff <= 15:
                start = num
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15

                band = diff + 1
                name = '{}_{}_{}.tif'.format(year, start, nd)
                break
    else:
        for i, num in enumerate(NUMS):
            diff = doy - num
            if 0 <= diff <= 15:
                band = diff + 1
                name = '{}_{}.tif'.format(year, i + 1)
                break

    # if coords:
    #     ndvi = get_inputs_at_point(coords, os.path.join(in_path, raster))
    #     kcb = ndvi * 1.25
    #     return kcb

    # else:
    # ndvi = apply_mask(mask_path, convert_raster_to_array(in_path, raster, band=band))

    # raster = Raster(name, root=in_path, band=band)
    # ndvi = raster.masked()
    #
    # kcb = ndvi * 1.25
    #
    # if previous_kcb is None:
    #     pass
    # else:
    #     kcb = where(isnan(kcb) is True, previous_kcb, kcb)
    #     kcb = where(abs(kcb) > 100.0, previous_kcb, kcb)
    #
    # return kcb
    return post_process_ndvi(name, in_path, previous_kcb, band)

# def get_kcb(in_path, date_object, previous_kcb=None, coords=None):
#     """
#     Find NDVI image and convert to Kcb.
#
#     :param in_path: NDVI input data path.
#     :type in_path: str
#     :param date_object: Datetime object of date.
#     :param previous_kcb: Previous day's kcb value.
#     :param coords: Call if using to get point data using point_extract_utility.
#     :return: numpy array object
#     """
#     # print date_object
#     doy = date_object.timetuple().tm_yday
#     if date_object.year == 2000:
#         raster = '{}_{}.tif'.format(date_object.year, doy)
#         if coords:
#             ndvi = recharge.point_extract_utility.get_inputs_at_point(coords, os.path.join(in_path, raster))
#             kcb = ndvi * 1.25
#             return kcb
#         ndvi = convert_raster_to_array(in_path, raster, band=1)
#         kcb = ndvi * 1.25
#
#     elif date_object.year == 2001:
#         for pos, num in enumerate(NUMS):
#             diff = doy - num
#             if 0 <= diff <= 15:
#                 # pos = obj.index(num)
#                 # start = obj[pos]
#                 start = num
#                 band = diff + 1
#                 if num == 353:
#                     nd = num + 12
#                 else:
#                     nd = num + 15
#                 raster = os.path.join(in_path, '{}_{}_{}.tif'.format(date_object.year, start, nd))
#                 # raster = '{a}\\{b}_{c}_{d}.tif'.format(a=in_path, b=date_object.year, c=start, d=nd)
#                 if coords:
#                     ndvi = recharge.point_extract_utility.get_inputs_at_point(coords, os.path.join(in_path, raster))
#                     kcb = ndvi * 1.25
#                     return kcb
#                 ndvi = convert_raster_to_array(in_path, raster, band=band)
#                 kcb = ndvi * 1.25
#
#     else:
#
#         for num in obj:
#             diff = doy - num
#             if 0 <= diff <= 15:
#                 pos = obj.index(num)
#                 band = diff + 1
#
#                 # if num == 353:
#                 #     nd = num + 12
#                 # else:
#                 #     nd = num + 15
#
#                 raster = os.path.join(in_path, '{}_{}.tif'.format(date_object.year, pos + 1))
#                 # raster = '{a}\\{b}_{c}.tif'.format(a=in_path, b=date_object.year, c=pos + 1, d=nd)
#                 if coords:
#                     ndvi = recharge.point_extract_utility.get_inputs_at_point(coords, os.path.join(in_path, raster))
#                     kcb = ndvi * 1.25
#                     return kcb
#                 ndvi = convert_raster_to_array(in_path, raster, band=band)
#                 kcb = ndvi * 1.25
#
#     if previous_kcb is None:
#         pass
#     else:
#         kcb = where(isnan(kcb) == True, previous_kcb, kcb)
#         kcb = where(abs(kcb) > 100., previous_kcb, kcb)
#
#     return kcb
#

def get_prism(root, date_object, variable='precip'):
    """
    Find PRISM image.

    :param variable: type of PRISM variable sought
    :type variable: str
    :param root: PRISM input data path.
    :type root: str
    :param date_object: Datetime object of date.
    :param coords: Call if using to get point data using point_extract_utility.
    :type coords: str
    :return: numpy array object
    """
    year = date_object.year
    tail = '{}{:02n}{:02n}.tif'.format(year, date_object.month, date_object.day)

    if variable == 'precip':

        root = os.path.join(root, 'precip', '800m_std_all')  # this will need to be fixed
        name = 'PRISMD2_NMHW2mi_{}'.format(tail)

    elif variable == 'min_temp':
        root = os.path.join(root, 'Temp', 'Minimum_standard')
        if year in PRISM_YEARS:
            name = 'cai_tmin_us_us_30s_{}'.format(tail)
        else:
            name = 'TempMin_NMHW2Buff_{}'.format(tail)

    elif variable == 'max_temp':
        root = os.path.join(root, 'Temp', 'Maximum_standard')
        name = 'TempMax_NMHW2Buff_{}'.format(tail)

    raster = Raster(name, root=root)
    return raster.masked()

    # if coords:
    #     ret = get_inputs_at_point(coords, os.path.join(root, raster))
    # else:
    #     ret = convert_raster_to_array(root, raster)
    #
    # return apply_mask(mask_path, ret)


def get_penman(root, date_object, variable='etrs'):
    """
    Find PENMAN image.

    :param variable: type of PENMAN variable sought
    :type variable: str
    :param in_path: PENMAN input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :param coords: Call if using to get point data using point_extract_utility.
    :type coords: str
    :return: numpy array object
    """

    year = date_object.year
    tail = '{}_{:03n}.tif'.format(year, date_object.timetuple().tm_yday)

    if variable == 'etrs':
        name = os.path.join('PM{}'.format(year), 'PM_NM_{}'.format(tail))

    elif variable == 'rlin':
        name = os.path.join('PM{}'.format(year), 'RLIN_NM_{}'.format(tail))

    elif variable == 'rg':
        name = os.path.join('rad{}'.format(year), 'RTOT_{}'.format(tail))

    raster = Raster(name, root=root)
    return raster.masked()
    # if coords:
    #     ret = get_inputs_at_point(coords, os.path.join(in_path, raster))
    # else:
    #     ret = convert_raster_to_array(in_path, raster)
    #
    # return apply_mask(mask_path, ret)

# ============= EOF =============================================
