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
from pandas import concat, DataFrame

from recharge.time_series_manager import amf_obs_time_series, get_etrm_time_series # from recharge.time_series_manager import amf_obs_time_series, get_etrm_time_series
from recharge.etrm_processes import Processes   # from recharge.etrm_processes import Processes

SIMULATION_PERIOD = datetime(2007, 1, 1), datetime(2013, 12, 29) # my-hard coding in time_series manager has disabled this function.

BASE_AMF_DICT = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
                 '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
                 '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
                 '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
                 '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
                 '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}}


def get_ameriflux_data(amf_file_path, simulation_period, etrm_extract=None,
                       static_inputs=None, initial_path=None, save_csv=None, save_cleaned_data=None,
                       save_combo=False):
    amf_dict = amf_obs_time_series(BASE_AMF_DICT, amf_file_path, complete_days_only=True,
                                   save_cleaned_data_path=save_cleaned_data, return_low_err=True)
    if save_cleaned_data:
        return None
    # print 'amf dict w/ AMF time series: \n{}'.format(amf_dict)

    get_etrm_time_series(etrm_extract, dict_=amf_dict)
    # print 'amf dict w/ etrm input time series: \n{}'.format(amf_dict)  # fix this so it appends to all sites
    # print 'ameriflux dict: {}'.format(amf_dict)

    for key, val in amf_dict.iteritems():
        # instantiate for each item to get a clean master dict
        etrm = Processes(simulation_period, save_csv, static_inputs=static_inputs, point_dict=amf_dict,
                         initial_inputs=initial_path)
        # print 'amf dict, pre-etrm run {}'.format(amf_dict)
        print '\n key : {}'.format(key)
        # print 'find etrm dataframe as amf_dict[key][''etrm'']\n{}'.format(amf_dict[key]['etrm'])
        tracker = etrm.run(simulation_period, point_dict=amf_dict, point_dict_key=key, modify_soils=False,
                           apply_rofrac=0.7, allen_ceff=0.5)
        # print 'tracker after etrm run: \n {}'.format(tracker)
        csv_path_filename = os.path.join(save_csv, '{}.csv'.format(val['Name']))
        print 'this should be your csv: {}'.format(csv_path_filename)

        tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')

        amf_obs_etrm_combo = DataFrame(concat((val['AMF_Data'], tracker), axis=1, join='outer'))

        obs_etrm_comb_out = os.path.join(save_combo, '{}_Ceff.csv'.format(val['Name']))

        print 'this should be your combo csv: {}'.format(obs_etrm_comb_out)
        amf_obs_etrm_combo.to_csv(obs_etrm_comb_out, index_label='Date')
        # print 'tracker for {}: {}'.format(key, tracker)

    return None


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    inputs = os.path.join('/Users/dcadol/Documents/ResearchProjects/FocusedRechargeModel','ETRM_Inputs') # 'F:\\', 'ETRM_Inputs'
    amf_path = os.path.join(inputs, 'ameriflux_sites') # OK
    amf_obs_root = os.path.join(amf_path, 'AMF_Data') # OK
    amf_extract = os.path.join(amf_path, 'AMF_extracts') # OK
    amf_trackers = os.path.join(amf_path, 'AMF_ETRM_output', 'trackers') # OK
    initial_conditions_path = os.path.join(inputs, 'initialize')
    static_inputs_path = os.path.join(inputs, 'statics')
    csv_output = os.path.join(amf_path, 'AMF_ETRM_output') # OK
    amf_obs_processed = os.path.join(amf_path, 'AMF_obs_processed') # OK
    amf_etrm_combo = os.path.join(amf_path, 'AMF_results_combo') # OK
    print amf_obs_root # testing
    get_ameriflux_data(amf_obs_root, SIMULATION_PERIOD, etrm_extract=amf_extract,
                       static_inputs=static_inputs_path, initial_path=initial_conditions_path,
                       save_csv=amf_trackers, save_combo=amf_etrm_combo, save_cleaned_data=False)

# ============= EOF =============================================
