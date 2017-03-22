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
The purpose of this module is to provide some simple tools needed for raster processing.


"""
import os
from datetime import datetime
from pprint import pformat

import rasterio
from affine import Affine
from numpy import array, asarray
from numpy.ma import masked_where, nomask
from osgeo import gdal
from pandas import DataFrame

from app.paths import paths


def convert_array_to_raster(output_path, arr, geo, output_band=1):
    driver = gdal.GetDriverByName('GTiff')
    out_data_set = driver.Create(output_path, geo['cols'], geo['rows'],
                                 geo['bands'], geo['data_type'])
    out_data_set.SetGeoTransform(geo['geotransform'])
    out_data_set.SetProjection(geo['projection'])

    output_band = out_data_set.GetRasterBand(output_band)
    output_band.WriteArray(arr, 0, 0)
    del out_data_set, output_band


def convert_raster_to_array(input_raster_path, raster, band=1):
    """
    Convert .tif raster into a numpy numerical array.

    :param input_raster_path: Path to raster.
    :param raster: Raster name with \*.tif
    :param band: Band of raster sought.

    :return: Numpy array.
    """
    # print "input raster path", input_raster_path
    # print "raster", raster
    p = os.path.join(input_raster_path, raster)
    # print "filepath", os.path.isfile(p)
    # print p
    if not os.path.isfile(p):
        print 'Not a valid file: {}'.format(p)

    raster_open = gdal.Open(p)
    ras = array(raster_open.GetRasterBand(band).ReadAsArray(), dtype=float)
    return ras


def get_raster_geo_attributes(root):
    """
    Creates a dict of geographic attributes from any of the pre-processed standardized rasters.

    :param root: Path to a folder with pre-processed standardized rasters.
    :return: dict of geographic attributes.
    """
    # statics = [filename for filename in os.listdir(statics_path) if filename.endswith('.tif')]
    # file_name = statics[0]
    file_name = next((fn for fn in os.listdir(root) if fn.endswith('.tif')), None)
    dataset = gdal.Open(os.path.join(root, file_name))

    band = dataset.GetRasterBand(1)
    raster_geo_dict = {'cols': dataset.RasterXSize, 'rows': dataset.RasterYSize, 'bands': dataset.RasterCount,
                       'data_type': band.DataType, 'projection': dataset.GetProjection(),
                       'geotransform': dataset.GetGeoTransform(), 'resolution': dataset.GetGeoTransform()[1]}
    return raster_geo_dict


def apply_mask(mask_path, arr):
    out = None
    idxs = get_mask(mask_path)
    if idxs is not None:
        out = arr[idxs].flatten()
    return out


def get_mask(path):
    file_name = next((fn for fn in os.listdir(path) if fn.endswith('.tif')), None)

    if file_name is not None:
        return get_mask_arr(path, file_name)
        # if file_name is not None:
        #     mask = convert_raster_to_array(path, file_name)
        #     idxs = asarray(mask, dtype=bool)
        # return idxs


def get_mask_arr(path, name):
    mask = convert_raster_to_array(path, name)
    idxs = asarray(mask, dtype=bool)
    return idxs


def remake_array(mask_path, arr):
    out = None
    file_name = next((filename for filename in os.listdir(mask_path) if filename.endswith('.tif')), None)
    if file_name is not None:
        mask_array = convert_raster_to_array(mask_path, file_name)
        masked_arr = masked_where(mask_array == 0, mask_array)
        # print masked_arr
        # print '!~~', masked_arr[~masked_arr.mask]
        # print arr.shape
        # print masked_arr[~masked_arr.mask].shape
        masked_arr[~masked_arr.mask] = arr.ravel()
        masked_arr.mask = nomask

        arr = masked_arr.filled(0)
        out = arr

    return out


def save_daily_pts(wfile, day, data):
    """
        data =x_cord, y_cord, ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect
    """

    year = day.strftime('%Y')
    this_month = day.strftime('%m')
    month_day = day.strftime('%d')
    print('Saving daily NDVI data for {}-{}-{}'.format(year, this_month, month_day))
    for row in data:
        timestamp = '{},{},{}'.format(year, this_month, month_day)
        # use map(str, row) to convert each element from a float to a str
        row = ','.join(map(str, row))
        wfile.write('{},{}\n'.format(timestamp, row))

    # in case you are worried about data not getting written to file if the script crashes mid-execution
    wfile.flush()
    # comment this out if you are not worried. The only reason i thought you might be is because of the use of 'a' to
    # open a file


def save_daily_pts_old(filename, day, ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):
    year = day.strftime('%Y')
    this_month = day.strftime('%m')
    month_day = day.strftime('%d')
    print('Saving daily NDVI data for {}-{}-{}'.format(year, this_month, month_day))
    for a, b, c, d, e, f, g, h, i in zip(ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):
        with open(filename, "a") as wfile:
            wfile.write(
                '{},{},{},{},{},{},{},{},{},{},{},{} \n'.format(year, this_month, month_day, a, b, c, d, e, f, g, h, i))


# def save_daily_pts(filename, day, ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):
#     year = day.strftime('%Y')
#     this_month = day.strftime('%m')
#     month_day = day.strftime('%d')
#     for datum in zip(ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):
#         with open(filename, "a") as wfile:
#             wfile.write('{},{},{},{],{},{},{},{},{},{},{},{}'.format(year,this_month,month_day,*datum))


def make_results_dir(out_root=None, shapes=None):
    """
    Creates a directory tree of empty folders that will recieve ETRM model output rasters.

    :param out_path: Parent directory within which an ETRM_results_date folder will be created.
    :param shapes: Folder contains sub-directories with shapefiles of geographies to be analyzed.
    :return: dict of directory paths
    """

    empties = ('annual_rasters', 'monthly_rasters', 'simulation_tot_rasters', 'annual_tabulated',
               'monthly_tabulated', 'daily_tabulated', 'daily_rasters')

    if out_root is None:
        out_root = paths.results_root

    if shapes is None:
        shapes = paths.polygons

    results_directories = {'root': out_root}

    if not os.path.isdir(out_root):
        os.makedirs(out_root)
        for item in empties:
            empty = os.path.join(out_root, item)
            os.makedirs(empty)
            results_directories[item] = empty

    else:
        results_directories = {item: os.path.join(out_root, item) for item in empties}

    if shapes and os.path.isdir(shapes):
        region_types = os.listdir(shapes)
        for tab_folder in ('annual_tabulated', 'monthly_tabulated', 'daily_tabulated'):
            d = {}
            for region_type in region_types:
                a, b = region_type.split('_P')
                dst = os.path.join(out_root, tab_folder, a)
                os.makedirs(dst)
                d[a] = dst

            results_directories[tab_folder] = d

    print 'results dirs: {}'.format(pformat(results_directories, indent=2))
    return results_directories


def get_tiff_transform(tiff_path):
    with rasterio.open(tiff_path) as rfile:
        t0 = rfile.affine  # upper-left pixel corner affine transform
        return t0


def get_tiff_transform_func(tiff_path, tx=0.5, ty=0.5):
    with rasterio.open(tiff_path) as rfile:
        t0 = rfile.affine  # upper-left pixel corner affine transform
        t1 = t0 * Affine.translation(tx, ty)
        return lambda pt: pt * t1


def tiff_framer(mask_path, tiff_list):
    """
    this function stacks tiffs depth-wise, applys a mask and creates a DataFrame

    E,N,Tiff0,Tiff1,...TiffN

    :param mask_path: path to mask tiff
    :param tiff_list: list of tiff paths

    :return DataFrame
    """

    mask_arr = get_mask_arr(*os.path.split(mask_path))

    import time

    transform = get_tiff_transform_func(mask_path)

    st = time.time()
    arrs = [convert_raster_to_array(*os.path.split(tiff_path)) for tiff_path in tiff_list]
    print 'get arrays', time.time() - st

    nrows, ncols = arrs[0].shape

    def rowfactory(r, c):
        gps_pt = transform((c, r))
        return (int(gps_pt[0]), int(gps_pt[1])) + tuple(a[r, c] for a in arrs)

    st = time.time()
    rows = [rowfactory(ri, ci) for ri in xrange(nrows) for ci in xrange(ncols) if mask_arr[ri, ci]]
    print 'get rows', time.time() - st

    df = DataFrame(rows)
    return df


if __name__ == '__main__':
    rr = '/Users/ross/Sandbox/ETRM'
    tnames = ['eta_7_2012.tif', 'etrs_7_2012.tif']
    tnames = ['de_30_12_2013.tif', 'dr_30_12_2013.tif']

    mp = os.path.join(rr, 'mask', 'zuni_1.tif')
    print tiff_framer(mp, [os.path.join(rr, ti) for ti in tnames])

# =================================== EOF =========================
