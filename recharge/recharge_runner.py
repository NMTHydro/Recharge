# ===============================================================================
# Copyright 2016 ross
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
from datetime import datetime
from pandas import DataFrame
from pandas import concat
# ============= local library imports  ==========================
from recharge.dict_setup import cmb_sample_site_data
from recharge.etrm_processes import Processes
from recharge.time_series_manager import get_etrm_time_series, amf_obs_time_series


def get_configuration(cfg=None):
    # ask user for some values
    if cfg is None:
        cfg = {}

    if 'kind' not in cfg:
        while 1:
            kind = raw_input('Model Kind [cmb]: ')
            if not kind:
                kind = 'cmb'

            if kind not in ('cmb', 'ameriflux'):
                print 'invalid kind "{}". Use either "cmb" or "ameriflux"'.format(kind)
            else:
                break

    if 'simulation_period' not in cfg:
        # need to handle invalid data formats
        start_date = raw_input('Start date, format YYYY/MM/DD [2007/01/01]: ')
        if not start_date:
            start_date = '2007/01/01'

        end_date = raw_input('End date, format YYYY/MM/DD [2013/12/29]: ')
        if not end_date:
            end_date = '2013/12/29'
        start_date = datetime(*(map(int, start_date.split('/'))))
        end_date = datetime(*(map(int, end_date.split('/'))))
        cfg['simulation_period'] = start_date, end_date

    if 'base_amf_dict' not in cfg:
        base_amf_dict = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
                         '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
                         '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
                         '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
                         '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
                         '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}}

        cfg['base_amf_dict'] = base_amf_dict

    inputs = os.path.join('F:\\', 'ETRM_Inputs')
    if kind == 'cmb':
        cmb_path = os.path.join(inputs, 'chloride_mass_balance')
        cmb_shp = os.path.join(cmb_path, 'shapefiles', 'CMB_sites_27SEP16.shp')
        extracts = os.path.join(cmb_path, 'CMB_extracts')
        trackers = os.path.join(cmb_path, 'CMB_ETRM_output', 'CMB_trackers')
        static_inputs_path = os.path.join(inputs, 'statics')
        initial_conditions_path = os.path.join(inputs, 'initialize')

        cfg['extract_path'] = extracts
        cfg['cmb_shapefile'] = cmb_shp

    else:
        amf_path = os.path.join(inputs, 'ameriflux_sites')
        amf_obs_root = os.path.join(amf_path, 'AMF_Data')
        amf_extract = os.path.join(amf_path, 'AMF_extracts')
        trackers = os.path.join(amf_path, 'AMF_ETRM_output', 'trackers')
        initial_conditions_path = os.path.join(inputs, 'initialize')
        static_inputs_path = os.path.join(inputs, 'statics')
        csv_output = os.path.join(amf_path, 'AMF_ETRM_output')
        amf_obs_processed = os.path.join(amf_path, 'AMF_obs_processed')
        amf_etrm_combo = os.path.join(amf_path, 'AMF_results_combo')

        cfg['etrm_extract'] = amf_extract
        cfg['amf_file_path'] = amf_obs_root
        cfg['save_cleaned_data'] = True
        cfg['save_combo'] = amf_etrm_combo

    cfg['save_csv'] = trackers
    cfg['initial_path'] = initial_conditions_path
    cfg['static_inputs'] = static_inputs_path

    return cfg


def cmb_analysis(config):
    d = cmb_sample_site_data(config['cmb_shapefile'])
    get_etrm_time_series(d, config['extract_path'])

    run_model(d, config)


def ameriflux(config):
    d = amf_obs_time_series(config['base_amf_dict'],
                            config['amf_file_path'], complete_days_only=True,
                            save_cleaned_data_path=config['save_cleaned_data'], return_low_err=True)
    if config['save_cleaned_data']:
        return None

    get_etrm_time_series(d, inputs_path=config['etrm_extract'], kind='amf')
    run_model(d, config.ameriflux_hook)


def ameriflux_hook(config, tracker, val):
    amf_obs_etrm_combo = DataFrame(concat((val['AMF_Data'], tracker), axis=1, join='outer'))
    obs_etrm_comb_out = os.path.join(config['save_combo'], '{}_combo.csv'.format(val['Name']))

    print 'this should be your combo csv: {}'.format(obs_etrm_comb_out)
    amf_obs_etrm_combo.to_csv(obs_etrm_comb_out, index_label='Date')


def run_model(d, config, hook=None):
    simulation_period = config['simulation_period']

    save_csv = config['save_csv']
    initial_path = config['initial_path']
    static_inputs = config['static_inputs']

    for key, val in d.iteritems():
        # instantiate for each item to get a clean master dict
        etrm = Processes(simulation_period, save_csv, static_inputs=static_inputs, point_dict=d,
                         initial_inputs=initial_path)

        # print 'amf dict, pre-etrm run {}'.format(amf_dict)
        print 'key : {}'.format(key)

        # print 'find etrm dataframe as amf_dict[key][''etrm'']\n{}'.format(amf_dict[key]['etrm'])
        tracker = etrm.run(simulation_period, point_dict=d[key], point_dict_key=key)
        # print 'tracker after etrm run: \n {}'.format(tracker)
        csv_path_filename = os.path.join(save_csv, '{}.csv'.format(val['Name']))

        print 'this should be your csv: {}'.format(csv_path_filename)

        tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')
        print 'tracker for {}: {}'.format(key, tracker)

        if hook:
            hook(config, tracker, val)


def welcome():
    print '''
  _____  ______ _____ _    _          _____   _____ ______
 |  __ \|  ____/ ____| |  | |   /\   |  __ \ / ____|  ____|
 | |__) | |__ | |    | |__| |  /  \  | |__) | |  __| |__
 |  _  /|  __|| |    |  __  | / /\ \ |  _  /| | |_ |  __|
 | | \ \| |___| |____| |  | |/ ____ \| | \ \| |__| | |____
 |_|  \_\______\_____|_|  |_/_/    \_\_|  \_\\_____|______|


---*---*---*---*---*---*---*---*---*---*---*---*
Welcome to Recharge.
---*---*---*---*---*---*---*---*---*---*---*---*
Developers: David Ketchum (NMT), Jake Ross (NMBGMR)
Date: 10-16-2016
'''


def main():
    welcome()
    kind, config = get_configuration()
    if kind == 'cmb':
        cmb_analysis(config)
    elif kind == 'ameriflux':
        ameriflux(config)

if __name__ == '__main__':
    main()

# ============= EOF =============================================
