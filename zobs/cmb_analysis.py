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
from datetime import datetime

from recharge.time_series_manager import get_etrm_time_series
from recharge.dict_setup import cmb_sample_site_data
from recharge.etrm_processes import Processes


def get_cmb_data(cmb_shapefile, extract_path, simulation_period, save_csv, static_inputs, initial_path):

    cmb_dict = cmb_sample_site_data(cmb_shapefile)

    get_etrm_time_series(cmb_dict, extract_path)

    for key, val in cmb_dict.iteritems():
        # instantiate for each item to get a clean master dict
        etrm = Processes(simulation_period, save_csv, static_inputs=static_inputs, point_dict=cmb_dict,
                         initial_inputs=initial_path)

        # print 'amf dict, pre-etrm run {}'.format(amf_dict)
        print('key : {}'.format(key))

        # print 'find etrm dataframe as amf_dict[key][''etrm'']\n{}'.format(amf_dict[key]['etrm'])
        tracker = etrm.run(simulation_period, point_dict=cmb_dict[key], point_dict_key=key)
        # print 'tracker after etrm run: \n {}'.format(tracker)
        csv_path_filename = os.path.join(save_csv, '{}.csv'.format(val['Name']))

        print('this should be your csv: {}'.format(csv_path_filename))

        tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')
        print('tracker for {}: {}'.format(key, tracker))

    return None


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print('home: {}'.format(home))
    inputs = os.path.join('F:\\', 'ETRM_Inputs')
    cmb_path = os.path.join(inputs, 'chloride_mass_balance')
    cmb_shp = os.path.join(cmb_path, 'shapefiles', 'CMB_sites_27SEP16.shp')
    extracts = os.path.join(cmb_path, 'CMB_extracts')
    trackers = os.path.join(cmb_path, 'CMB_ETRM_output', 'CMB_trackers')
    static_inputs_path = os.path.join(inputs, 'statics')
    initial_conditions_path = os.path.join(inputs, 'initialize')
    simulation_dates = datetime(2008, 1, 1), datetime(2013, 12, 31)
    get_cmb_data(cmb_shp, extracts, simulation_dates, trackers, static_inputs_path, initial_conditions_path)

# ============= EOF =============================================
