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
from osgeo import gdal
from numpy import array, asarray
from numpy.ma import masked_where, nomask, filled
from datetime import datetime
import os


def convert_raster_to_array(input_raster_path, raster, band=1):
    """
    Convert .tif raster into a numpy numerical array.

    :param input_raster_path: Path to raster.
    :param raster: Raster name with *.tif
    :param band: Band of raster sought.
    :return: Numpy array.
    """
    raster_open = gdal.Open(os.path.join(input_raster_path, raster))
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

# def apply_mask(mask_path, rast_to_mask):
#     #raster_attrib = get_geo(mask_path)
#     out = None
#     file_name = next((filename for filename in os.listdir(mask_path) if filename.endswith('.tif')), None)
#     if file_name is not None:
#         #file_name = mask_raster[0]
#         mask_array = convert_raster_to_array(mask_path,file_name)
#         masked_arr = masked_where(mask_array == 0, rast_to_mask)
#         out = masked_arr.compressed()
#
#     return out

def apply_mask(mask_path, arr):
    out = None
    file_name = next((fn for fn in os.listdir(mask_path) if fn.endswith('.tif')), None)
    if file_name is not None:
        mask = convert_raster_to_array(mask_path, file_name)
        idxs = asarray(mask, dtype=bool)
        # or
        # idxs = where(mask==1)[0]
        out = arr[idxs].flatten()
    return out

def remake_array(mask_path, arr):
    out = None
    file_name = next((filename for filename in os.listdir(mask_path) if filename.endswith('.tif')), None)
    if file_name is not None:
        mask_array = convert_raster_to_array(mask_path, file_name)
        masked_arr = masked_where(mask_array == 0, mask_array)
        masked_arr[~masked_arr.mask]=arr.ravel()
        masked_arr.mask = nomask
        arr = masked_arr.filled(0)
        out = arr

    return out

def save_daily_pts(filename, day, ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):

    year = day.strftime('%Y')
    this_month = day.strftime('%m')
    month_day = day.strftime('%d')
    print('Saving daily NDVI data for {}-{}-{}'.format(year, this_month, month_day))
    for a, b, c, d, e, f, g, h, i in zip(ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):
        with open(filename, "a") as wfile:
            wfile.write('{},{},{},{},{},{},{},{},{},{},{},{} \n'.format(year, this_month, month_day, a, b, c, d, e, f, g, h, i))


# def save_daily_pts(filename, day, ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):
#     year = day.strftime('%Y')
#     this_month = day.strftime('%m')
#     month_day = day.strftime('%d')
#     for datum in zip(ndvi, temp, precip, etr, petr, nlcd, dem, slope, aspect):
#         with open(filename, "a") as wfile:
#             wfile.write('{},{},{},{],{},{},{},{},{},{},{},{}'.format(year,this_month,month_day,*datum))


def make_results_dir(out_path, shapes):
    """
    Creates a directory tree of empty folders that will recieve ETRM model output rasters.

    :param out_path: Parent directory within which an ETRM_results_date folder will be created.
    :param shapes: Folder contains sub-directories with shapefiles of geographies to be analyzed.
    :return: dict of directory paths
    """

    empties = ['annual_rasters', 'monthly_rasters', 'simulation_tot_rasters', 'annual_tabulated',
               'monthly_tabulated', 'daily_tabulated', 'daily_rasters']
    now = datetime.now()
    tag = now.strftime('%Y_%m_%d')
    folder = 'ETRM_Results_{}'.format(tag)
    os.chdir(out_path)
    new_dir = os.path.join(out_path, folder)
    results_directories = {x: None for x in empties}
    results_directories['root'] = os.path.join(out_path, folder)
    if not os.path.isdir(folder):
        os.makedirs(new_dir)
        for item in empties:
            empty = os.path.join(new_dir, item)
            os.makedirs(empty)
            results_directories[item] = empty
        region_types = os.listdir(shapes)
        for tab_folder in ['annual_tabulated', 'monthly_tabulated', 'daily_tabulated']:
            results_directories[tab_folder] = {}
            for region_type in region_types:
                a, b = region_type.split('_P')
                dst = os.path.join(new_dir, tab_folder, a)
                os.makedirs(dst)
                results_directories[tab_folder].update({a: dst})
    else:
        for item in empties:
            empty = os.path.join(new_dir, item)
            results_directories[item] = os.path.join(empty)
        region_types = os.listdir(shapes)
        for tab_folder in ['annual_tabulated', 'monthly_tabulated', 'daily_tabulated']:
            results_directories[tab_folder] = {}
            for region_type in region_types:
                a, b = region_type.split('_P')
                dst = os.path.join(new_dir, tab_folder, a)
                results_directories[tab_folder].update({a: dst})
    print 'results dirs: \n{}'.format(results_directories)
    return results_directories


if __name__ == '__main__':
    pass

# =================================== EOF =========================
