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
from pandas import DataFrame
from pandas import concat
# ============= local library imports  ==========================
from recharge.configuration.cli_configurer import CLIConfigurer
from recharge.configuration.yaml_configurer import YAMLConfigurer
from recharge.dict_setup import cmb_sample_site_data
from recharge.etrm_processes import Processes
from recharge.time_series_manager import get_etrm_time_series, amf_obs_time_series


def cmb_analysis(config):
    d = cmb_sample_site_data(config.cmb_shapefile)
    get_etrm_time_series(d, config.extract_path)

    run_model(d, config)


def ameriflux(config):
    d = amf_obs_time_series(config.base_amf_dict,
                            config.amf_file_path, complete_days_only=True,
                            save_cleaned_data_path=config.save_cleaned_data, return_low_err=True)
    if config.save_cleaned_data:
        return None

    get_etrm_time_series(d, inputs_path=config.etrm_extract, kind='amf')
    run_model(d, config, ameriflux_hook)


def ameriflux_hook(config, tracker, val):
    amf_obs_etrm_combo = DataFrame(concat((val['AMF_Data'], tracker), axis=1, join='outer'))
    obs_etrm_comb_out = os.path.join(config.save_combo, '{}_combo.csv'.format(val['Name']))

    print 'this should be your combo csv: {}'.format(obs_etrm_comb_out)
    amf_obs_etrm_combo.to_csv(obs_etrm_comb_out, index_label='Date')


def run_model(d, config, hook=None):
    simulation_period = config.simulation_period

    save_csv = config.save_csv
    initial_path = config.initial_path
    static_inputs = config.static_inputs

    for key, val in d.iteritems():
        # instantiate for each item to get a clean master dict
        etrm = Processes(simulation_period, save_csv, static_inputs=static_inputs, point_dict=d,
                         initial_inputs=initial_path)

        # print 'amf dict, pre-etrm run {}'.format(amf_dict)
        print 'key : {}'.format(key)

        # print 'find etrm dataframe as amf_dict[key][''etrm'']\n{}'.format(amf_dict[key]['etrm'])
        etrm.run(simulation_period, point_dict=d[key], point_dict_key=key)

        csv_path_filename = os.path.join(save_csv, '{}.csv'.format(val['Name'])) if d else None
        etrm.save_tracker(csv_path_filename)

        if hook:
            hook(config, etrm.tracker, val)


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


def main(use_yaml_config=False):
    welcome()
    if use_yaml_config:
        p = 'etrm_config.yaml'
        configurer = YAMLConfigurer(p)
    else:
        configurer = CLIConfigurer()

    kind, config = configurer.get_configuration()
    if kind == 'cmb':
        cmb_analysis(config)
    elif kind == 'ameriflux':
        ameriflux(config)

if __name__ == '__main__':
    main(True)

# ============= EOF =============================================
