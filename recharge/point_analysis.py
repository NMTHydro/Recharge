# ===============================================================================
# Copyright 2016 gabe-parrish
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

"""This module is designed to run a set of pre-processed (extract_inputs_point) points for
individual pixels and run the model in point mode. You should be able to use this module
just like ameriflux_analysis but for any points you've chosen for the model. This module will
not process the raw observed ameriflux data from the ameriflux towers. It is not specific to ameriflux."""

# ============= standard library imports ========================
import os

# ============= local library imports ===========================
from datetime import datetime
from pandas import concat, DataFrame

from recharge.time_series_manager import amf_obs_time_series, get_etrm_time_series
from recharge.etrm_processes import Processes

import os
from osgeo import gdal, ogr
from dateutil import rrule
from pandas import DataFrame, date_range
from numpy import nan

SIMULATION_PERIOD = datetime(2007, 1, 1), datetime(2013, 12, 29)


# I need to replace the BASE_AMF_DICT with a different dict which I must make from GDAL somehow.


def get_point_dict(coords_path):
    """ This function here is going to go to the shapefile path, extract coordinates, and put the coords and a list
     together like:

     # POINT_DICT = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
#                  '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
#                  '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
#                  '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
#                  '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
#                  '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}}

and then we'll take that and pass it to get_extracted_data which will run processes in point mode for each
location in the dict."""


    count = 0
    outer_dict = {}
    ds = ogr.Open(coords_path)
    print "this is ds: {}".format(ds)
    lyr = ds.GetLayer()
    for feat in lyr:
        try:
            name = feat.GetField('Name')
        except ValueError:
            name = feat.GetField('Sample')
        # print name
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()
        mx = int(mx)
        my = int(my)
        # next we'll need to make a dict.
        inner_dict = {'Coords': '{} {}'.format(mx, my), 'Name': '{}'.format(name)}
        count += 1
        outer_dict[count] = inner_dict

    point_dict = outer_dict

    return point_dict


def get_extracted_data(point_dict, simulation_period, etrm_extract=None,
                       static_inputs=None, initial_path=None, save_csv=None, save_cleaned_data=None,
                       save_combo=False): # maybe won't need some of these arguments.
    """ This function here takes the point dict and runs ETRM processes on it along with the inputs."""

    get_etrm_time_series(etrm_extract, dict_=point_dict)

    print 'amf dict w/ etrm input time series: \n{}'.format(point_dict)  # fix this so it appends to all sites
    # print 'ameriflux dict: {}'.format(amf_dict)

    for key, val in point_dict.iteritems():

        # instantiate for each item to get a clean master dict
        etrm = Processes(simulation_period, save_csv, static_inputs=static_inputs, point_dict=point_dict,
                         initial_inputs=initial_path)

        print 'point dict, pre-etrm run {}'.format(point_dict) # for testing

        print '\n key : {}'.format(key)
        # print 'find etrm dataframe as amf_dict[key][''etrm'']\n{}'.format(amf_dict[key]['etrm'])

        tracker = etrm.run(simulation_period, point_dict=point_dict, point_dict_key=key, modify_soils=True,
                           apply_rofrac=0.7, allen_ceff=0.8)

        # look out for that key! might be a problem

        # print 'tracker after etrm run: \n {}'.format(tracker)
        csv_path_filename = os.path.join(save_csv, '{}.csv'.format(val['Name']))
        print 'this should be your csv: {}'.format(csv_path_filename)

        # saves the model results to the tracker. Keep this part.
        tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')


        # I think we don't need these. They are the obs AMF or combo files
        # we only want trackers
        # amf_obs_etrm_combo = DataFrame(concat((val['AMF_Data'], tracker), axis=1, join='outer'))
        #
        # obs_etrm_comb_out = os.path.join(save_combo, '{}_Ceff.csv'.format(val['Name']))
        #
        # print 'this should be your combo csv: {}'.format(obs_etrm_comb_out)
        # amf_obs_etrm_combo.to_csv(obs_etrm_comb_out, index_label='Date')
        # # print 'tracker for {}: {}'.format(key, tracker)

    return None




if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    inputs = os.path.join('/Volumes', 'Seagate Expansion Drive', 'ETRM_Inputs') # 'F:\\', 'ETRM_Inputs'
    coords_path = os.path.join('/', 'Users', 'Gabe', 'Desktop', 'QGIS_Ameriflux',
                               'coords_no_nulls.shp')  # how to get to the shapefile we need to extract coords.
    amf_path = os.path.join(inputs, 'ameriflux_ex_sac') # OK
    amf_obs_root = os.path.join(amf_path, 'AMF_Data') # OK
    amf_extract = os.path.join(amf_path, 'AMF_extracts') # OK
    amf_trackers = os.path.join(amf_path, 'AMF_ETRM_output', 'trackers') # OK
    initial_conditions_path = os.path.join(inputs, 'initialize')
    static_inputs_path = os.path.join(inputs, 'statics')
    csv_output = os.path.join(amf_path, 'AMF_ETRM_output') # OK
    amf_obs_processed = os.path.join(amf_path, 'AMF_obs_processed') # OK
    amf_etrm_combo = os.path.join(amf_path, 'AMF_results_combo') # OK
    print amf_obs_root # testing

    # a function that takes uses GDAL to get the coordinates of points.
    point_dict = get_point_dict(coords_path)

    get_extracted_data(point_dict, SIMULATION_PERIOD, etrm_extract=amf_extract,
                       static_inputs=static_inputs_path, initial_path=initial_conditions_path,
                       save_csv=amf_trackers, save_combo=amf_etrm_combo, save_cleaned_data=False) # maybe won't need some of these components

