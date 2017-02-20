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

# ============= local library imports ===========================
import os
from datetime import datetime

from osgeo import ogr

from recharge.etrm_processes import Processes
from recharge.time_series_manager import get_etrm_time_series


# I need to replace the BASE_AMF_DICT with a different dict which I must make from GDAL somehow.

def run(input_root, coords_path):

    # a function that takes uses GDAL to get the coordinates of points.
    point_dict = get_point_dict(coords_path)

    amf_path = os.path.join(input_root, 'ameriflux_ex_sac')  # OK

    amf_extract = os.path.join(amf_path, 'AMF_extracts')  # OK
    amf_trackers = os.path.join(amf_path, 'AMF_ETRM_output', 'trackers')  # OK
    initial_conditions_path = os.path.join(input_root, 'initialize')
    static_inputs_path = os.path.join(input_root, 'statics')

    simulation_period = datetime(2007, 1, 1), datetime(2013, 12, 29)

    get_etrm_time_series(amf_extract, dict_=point_dict)

    print 'amf dict w/ etrm input time series: \n{}'.format(point_dict)  # fix this so it appends to all sites

    for key, val in point_dict.iteritems():
        # instantiate for each item to get a clean master dict
        etrm = Processes(simulation_period, amf_trackers, static_inputs=static_inputs_path, point_dict=point_dict,
                         initial_inputs=initial_conditions_path)

        print 'point dict, pre-etrm run {}'.format(point_dict)  # for testing
        print 'key : {}'.format(key)

        tracker = etrm.run(simulation_period, point_dict=point_dict, point_dict_key=key, modify_soils=True,
                           apply_rofrac=0.7, allen_ceff=0.8)

        # print 'tracker after etrm run: \n {}'.format(tracker)
        csv_path_filename = os.path.join(amf_trackers, '{}.csv'.format(val['Name']))
        print 'this should be your csv: {}'.format(csv_path_filename)

        # saves the model results to the tracker. Keep this part.
        tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')


def get_point_dict(coords_path):
    """ This function here is going to go to the shapefile path, extract coordinates, and put the coords and a list
     together like:

     POINT_DICT = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
                 '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
                 '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
                 '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
                 '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
                 '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}}

and then we'll take that and pass it to get_extracted_data which will run processes in point mode for each
location in the dict."""

    count = 0
    point_dict = {}
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
        point_dict[count] = inner_dict

    return point_dict

if __name__ == '__main__':
    # get to the shapefile we need to extract coords.
    home = os.path.expanduser('~')
    coords_path = os.path.join(home, 'Desktop', 'QGIS_Ameriflux', 'coords_no_nulls.shp')
    ir = os.path.join('/Volumes', 'Seagate Expansion Drive', 'ETRM_Inputs')

    run(ir, coords_path)

# ============= EOF =============================================
