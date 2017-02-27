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


BASE_AMF_DICT = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
                 '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
                 '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
                 '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
                 '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
                 '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}}


def run(input_root, simulation_period):
    amf_dict = amf_obs_time_series(BASE_AMF_DICT,
                                   input_root,
                                   complete_days_only=True,
                                   return_low_err=True)

    amf_path = os.path.join(input_root, 'ameriflux_sites')  # OK
    etrm_extract = os.path.join(amf_path, 'AMF_extracts')
    output_root = os.path.join(amf_path, 'AMF_ETRM_output')
    combo_root = os.path.join(amf_path, 'AMF_results_combo')

    get_etrm_time_series(etrm_extract, dict_=amf_dict)
    for key, val in amf_dict.iteritems():
        etrm = Processes(simulation_period, input_root, output_root)
        etrm.run(ro_reinf_frac=0.7, allen_ceff=0.8)

        save_run(etrm, output_root, combo_root, val)


def save_run(etrm, output_root, combo_root, val):
    path = os.path.join(output_root, '{}.csv'.format(val['Name']))
    etrm.tracker.to_csv(path, na_rep='nan', index_label='Date')

    amf_obs_etrm_combo = DataFrame(concat((val['AMF_Data'], etrm.tracker), axis=1, join='outer'))
    obs_etrm_comb_out = os.path.join(combo_root, '{}_Ceff.csv'.format(val['Name']))

    print 'this should be your combo csv: {}'.format(obs_etrm_comb_out)
    amf_obs_etrm_combo.to_csv(obs_etrm_comb_out, index_label='Date')


if __name__ == '__main__':
    ir = os.path.join('/Volumes', 'Seagate Expansion Drive', 'ETRM_Inputs')
    sim = datetime(2007, 1, 1), datetime(2013, 12, 29)

    run(ir, sim)

# ============= EOF =============================================
