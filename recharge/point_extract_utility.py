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


import os
from osgeo import gdal, ogr
from dateutil import rrule
from pandas import DataFrame, date_range
from numpy import nan

import recharge.dynamic_raster_finder


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
    band = dataset.GetRasterBand(1)
    px = abs(int((mx - gt[0]) / gt[1]))
    py = int((my - gt[3]) / gt[5])
    obj = band.ReadAsArray(px, py, 1, 1)

    return obj[0][0]


def get_dynamic_inputs_from_shape(shapefile, ndvi, prism, penman, simulation_period, out_location):
    """
    Runs over a simulation period and extracts data from rasters and saves point data to csv.

    :param shapefile: Full path to a .shp file containing points within given rasters.
    :param ndvi: Path to NDVI .tif images.
    :param prism: Path to PORISM .tif images.
    :param penman: Path to PENMAN refET .tif images.
    :param simulation_period: Datetime object (start, end)
    :type simulation_period: tuple
    :param out_location: Save location (folder)
    :return: None
    """

    dynamic_keys = ['kcb', 'rg', 'etrs', 'min_temp', 'max_temp', 'temp', 'precip']

    ind = date_range(simulation_period[0], simulation_period[1], name='Date')
    df = DataFrame(columns=dynamic_keys, index=ind).fillna(nan)
    ds = ogr.Open(shapefile)
    lyr = ds.GetLayer()
    for feat in lyr:
        try:
            name = feat.GetField('Name')
        except ValueError:
            name = feat.GetField('Sample')
        print name
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()
        if name == 'Valles_Coniferous':
            print 'already did Valles Coniferous, skipping....'
        else:
            for day in rrule.rrule(rrule.DAILY, dtstart=simulation_period[0], until=simulation_period[1]):
                if day.timetuple().tm_yday == 01:
                    print 'year {}'.format(day.year)
                dynamics = [recharge.dynamic_raster_finder.get_kcb(ndvi, day, coords=(mx, my)),
                            recharge.dynamic_raster_finder.get_penman(penman, day, variable='rg', coords=(mx, my)),
                            recharge.dynamic_raster_finder.get_penman(penman, day, variable='etrs', coords=(mx, my)),
                            recharge.dynamic_raster_finder.get_prism(prism, day, variable='min_temp', coords=(mx, my)),
                            recharge.dynamic_raster_finder.get_prism(prism, day, variable='max_temp', coords=(mx, my)),
                            (
                            recharge.dynamic_raster_finder.get_prism(prism, day, variable='min_temp', coords=(mx, my)) +
                            recharge.dynamic_raster_finder.get_prism(prism, day, variable='max_temp',
                                                                     coords=(mx, my))) / 2.,
                            recharge.dynamic_raster_finder.get_prism(prism, day, variable='precip', coords=(mx, my))]

                df.loc[day] = dynamics

            print 'df for {}: \n{}'.format(name, df)
            csv_path_filename = os.path.join(out_location, '{}.csv'.format(name))
            df.to_csv(csv_path_filename, na_rep='nan', index_label='Date', header=True)

    return None


if __name__ == '__main__':
    pass

# ============= EOF =============================================
