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
from recharge.dynamic_raster_finder import get_kcb, get_penman, get_prism
from runners.paths import paths


def get_dynamic_inputs_from_shape(shapefile,  simulation_period, out_location):
    """
    Runs over a simulation period and extracts data from rasters and saves point data to csv.

    :param shapefile: Full path to a .shp file containing points within given rasters.
    :param simulation_period: Datetime object (start, end)
    :type simulation_period: tuple
    :param out_location: Save location (folder)
    :return: None
    """

    ndvi = paths.ndvi_std_all
    prism = paths.prism
    penman = paths.penman

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
        coords = geom.GetX(), geom.GetY()
        """Took these last three lines out bc it was skipping Valles Coniferous and we don't want that necessarily."""
        #if name == 'Valles_Coniferous':
            #print 'already did Valles Coniferous, skipping....'
        #else:
        for day in rrule.rrule(rrule.DAILY, dtstart=simulation_period[0], until=simulation_period[1]):
            if day.timetuple().tm_yday == 01:
                print 'year {}'.format(day.year)

            min_temp = get_prism(prism, day, variable='min_temp', coords=coords)
            max_temp = get_prism(prism, day, variable='max_temp', coords=coords)

            dynamics = [get_kcb(ndvi, day, coords=coords),
                        get_penman(penman, day, variable='rg', coords=coords),
                        get_penman(penman, day, variable='etrs', coords=coords),
                        min_temp,
                        max_temp,
                        (min_temp+max_temp) / 2.,
                        get_prism(prism, day, variable='precip', coords=coords)]

            df.loc[day] = dynamics

        print 'df for {}: \n{}'.format(name, df)
        csv_path_filename = os.path.join(out_location, '{}.csv'.format(name))
        df.to_csv(csv_path_filename, na_rep='nan', index_label='Date', header=True)

    return None


if __name__ == '__main__':
    pass

# ============= EOF =============================================
