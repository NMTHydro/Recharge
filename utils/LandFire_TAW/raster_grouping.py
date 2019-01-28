# ===============================================================================
# Copyright 2018 gabe-parrish
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
import pandas as pd
import numpy as np
import gdal

# ============= local library imports ===========================
from recharge.raster_tools import convert_raster_to_array, get_raster_geo_attributes
from utils.depletions_modeling.cumulative_depletions import write_raster


def get_raster_geo(filepath):
    """
    Creates a dict of geographic attributes from a single raster file.

    :param filepath: Path to rasterfile.
    :return: dict of geographic attributes.
    """
    dataset = gdal.Open(filepath)

    band = dataset.GetRasterBand(1)
    raster_geo_dict = {'cols': dataset.RasterXSize, 'rows': dataset.RasterYSize, 'bands': dataset.RasterCount,
                       'data_type': band.DataType, 'projection': dataset.GetProjection(),
                       'geotransform': dataset.GetGeoTransform(), 'resolution': dataset.GetGeoTransform()[1]}
    return raster_geo_dict


def read_codes(path):

    eco_dict = {}
    with open(path, 'r') as rfile:
        for line in rfile:
            if not line.split(',')[0] == 'code':
                vals = line.split(',')
                eco_dict['{}'.format(vals[-1][:-1])] = int(vals[0])

    return eco_dict


def arr_overprint(arr, val, newval):
    """
    Overprints a given raster value with a new value
    :param arr:
    :param val:
    :param newval:
    :return:
    """
    arr[arr == val] = newval


def arr_modify(arr, dict, grouplist, startcode):
    """"""
    for grouping in grouplist:
        print 'grouping', grouping
        startcode += 1
        # TODO - output some kind of report to document which things were recoded
        for ecosystem in grouping:
            arr_overprint(arr, dict[ecosystem], startcode)

    return arr


def main(eco_path, lf_path, ecos_to_group, startcode, outinfo):
    """"""

    # need a dictionary relating names to codes
    eco_dict = read_codes(eco_path)
    print eco_dict

    # get the raster array
    landfire_arr = convert_raster_to_array(lf_path)

    # get the geo information for the raster
    landfire_geo = get_raster_geo(lf_path)
    print landfire_geo

    # take the array and group by code, overprint the previous raster codes with the startcode and return the array
    grouped_arr = arr_modify(landfire_arr, eco_dict, ecos_to_group, startcode)

    print grouped_arr
    print landfire_geo['geotransform']
    print outinfo[0], outinfo[1]
    print (landfire_geo['rows'], landfire_geo['cols'])
    print landfire_geo['projection']

    write_raster(grouped_arr, landfire_geo['geotransform'], outinfo[0], outinfo[1],
                 (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])


if __name__ == "__main__":

    # path to the codes, counts and ecosystem names for the Landfire Dataset.
    # ...File produced by Landfire_Eco_Stringparse.py
    eco_path = '/Users/Gabe/Desktop/academic_docs/LandFire/raster_report/raster_report_processed.csv'

    # path to new mexican landfire data
    lf_path = '/Users/Gabe/Desktop/academic_docs/LandFire/CO_NM_Landfire_1_0_0_EVT/NM_Landfire_1.0.0_EVT_clip.tif'

    # ====== User-Defined Ecosystem Groupings ======

    pj = ('Colorado_Plateau_Pinyon-Juniper_Woodland', 'Southern_Rocky_Mountain_Pinyon-Juniper_Woodland',
          'Madrean_Pinyon-Juniper_Woodland', 'Great_Basin_Pinyon-Juniper_Woodland')

    # should juniper woodlands be included and grouped here?
    juniper_sav = ('Southern_Rocky_Mountain_Juniper_Woodland_and_Savanna', 'Madrean_Juniper_Savanna',
                   'Inter-Mountain_Basins_Juniper_Savanna')
    # are sandy grasslands to be separated out or lumped?
    desert_grass = ('Apacherian-Chihuahuan_Semi-Desert_Grassland_and_Steppe',
                    'Inter-Mountain_Basins_Semi-Desert_Grassland', 'Chihuahuan_Loamy_Plains_Desert_Grassland',
                    'Chihuahuan_Sandy_Plains_Semi-Desert_Grassland',
                    'Chihuahuan-Sonoran_Desert_Bottomland_and_Swale_Grassland')

    creosote = ('Chihuahuan_Creosotebush_Desert_Scrub', 'Sonora-Mojave_Creosotebush-White_Bursage_Desert_Scrub')

    # is scrub misleadingly similar sounding? maybe group the succulent scrub and the catcus scrub together.
    # maybe group salt-desert shrubs away from others?
    scrub = ('Chihuahuan_Mixed_Desert_and_Thorn_Scrub', 'Inter-Mountain_Basins_Mixed_Salt_Desert_Scrub',
             'Chihuahuan_Stabilized_Coppice_Dune_and_Sand_Flat_Scrub', 'Chihuahuan_Mixed_Salt_Desert_Scrub',
             'Chihuahuan_Succulent_Desert_Scrub', 'Sonoran_Mid-Elevation_Desert_Scrub',
             'Sonoran_Paloverde-Mixed_Cacti_Desert_Scrub', 'Sonora-Mojave_Mixed_Salt_Desert_Scrub',
             'Mojave_Mid-Elevation_Mixed_Desert_Scrub')

    ecos_to_group = [pj, juniper_sav, desert_grass, creosote, scrub]

    # START CODE -> new code level to describe new grouped units (all raster values will be 20,000 or higher).
    startcode = 6000


    # ====== User-Defined Output path ======
    outpath = '/Users/Gabe/Desktop/academic_docs/LandFire/grouped_lf_rasters'
    outname = 'nm_lf_group_pj-junipersav-desgrass-creosote-scrub.tif'

    # outfile = os.path.join(outpath, outname)
    outinfo = [outpath, outname]

    main(eco_path, lf_path, ecos_to_group, startcode, outinfo)