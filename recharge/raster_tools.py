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

import rasterio
from affine import Affine
from numpy import array, asarray, meshgrid, frompyfunc, arange
from numpy.ma import masked_where, nomask
from osgeo import gdal
from pandas import DataFrame


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


def make_results_dir(out_root, shapes):
    """
    Creates a directory tree of empty folders that will recieve ETRM model output rasters.

    :param out_path: Parent directory within which an ETRM_results_date folder will be created.
    :param shapes: Folder contains sub-directories with shapefiles of geographies to be analyzed.
    :return: dict of directory paths
    """

    empties = ('annual_rasters', 'monthly_rasters', 'simulation_tot_rasters', 'annual_tabulated',
               'monthly_tabulated', 'daily_tabulated', 'daily_rasters')
    now = datetime.now()
    tag = now.strftime('%Y_%m_%d')

    out_root = os.path.join(out_root, 'ETRM_Results_{}'.format(tag))

    results_directories = {'root': out_root}

    if not os.path.isdir(out_root):
        os.makedirs(out_root)
        for item in empties:
            empty = os.path.join(out_root, item)
            os.makedirs(empty)
            results_directories[item] = empty

    else:
        results_directories = {item: os.path.join(out_root, item) for item in empties}

    region_types = os.listdir(shapes)
    for tab_folder in ('annual_tabulated', 'monthly_tabulated', 'daily_tabulated'):
        d = {}
        for region_type in region_types:
            a, b = region_type.split('_P')
            dst = os.path.join(out_root, tab_folder, a)
            os.makedirs(dst)
            d[a] = dst

    results_directories[tab_folder] = d

    print 'results dirs: \n{}'.format(results_directories)
    return results_directories


def get_gps_coordinates(tiff_path):
    with rasterio.open(tiff_path) as r:
        t0 = r.affine  # upper-left pixel corner affine transform
        # arr = r.read(1)  # pixel values
        mesh = meshgrid(arange(r.width), arange(r.height))  # cols, rows
        t1 = t0 * Affine.translation(0.5, 0.5)

        transform = frompyfunc(lambda pt: pt * t1)
        mesh = transform(mesh)

        return mesh
        # northings, eastings = mesh.T
        # return northings, eastings


def tiff_framer(root, mask_path, tiff_list):
    mask_arr = get_mask(mask_path)

    gps = get_gps_coordinates(mask_path)

    arrs = [convert_raster_to_array(root, tiff_name) for tiff_name in tiff_list]

    nrows, ncols = arrs[0].shape

    def rowfactory(r, c):
        return gps[r, c] + tuple([arr[r, c] for arr in arrs])

    rows = [rowfactory(ri, ci) for ri in xrange(nrows) for ci in xrange(ncols) if mask_arr[ri, ci]]
    df = DataFrame(rows)
    return df


def coord_getter_old(tiff_path):
    """
    http://gis.stackexchange.com/questions/129847/obtain-coordinates-and-corresponding-pixel-values-from-geotiff-using-python-gdal
    """
    import numpy as np
    # Read raster
    with rasterio.open(tiff_path) as r:
        t0 = r.affine  # upper-left pixel corner affine transform
        # p1 = Proj(r.crs)
        a = r.read(1)  # pixel values

    # All rows and columns
    cols, rows = meshgrid(arange(a.shape[1]), arange(a.shape[0]))

    # Get affine transform for pixel centres
    t1 = t0 * Affine.translation(0.5, 0.5)
    print "T1", t1
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * t1

    # All eastings and northings (there is probably a faster way to do this)
    northings, eastings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

    # suggested Jake Edits. Talk to him soon.
    # mesh = meshgrid(arange(cols.shape[1]), arange(rows.shape[0]))

    # print 'mesh', mesh

    # northings, eastings = [(c,r)* T1 for c, r in mesh.T]

    # northings, eastings = (p1*mesh.T).T

    print 'northings', northings
    print 'eastings', eastings

    return eastings, northings


if __name__ == '__main__':
    root = '/Users/ross/Sandbox/ETRM'
    tnames = ['eta_7_2012.tif', 'etrs_7_2012.tif']
    mp = os.path.join(root, 'mask', 'zuni_1.tif')

    tiff_framer(root, mp, tnames)

# =================================== EOF =========================
