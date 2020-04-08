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
from app.paths import paths
from app.generic_runner import run_model
from app.config import Config

BASE_AMF_DICT = {# '1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
                 '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
                 # '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
                 # '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
                 # '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
                 # '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}
                 }


def run(input_root, simulation_period):
    paths.build(input_root)

    amf_dict = amf_obs_time_series(BASE_AMF_DICT,
                                   complete_days_only=True,
                                   return_low_err=True)
    # get_etrm_time_series(paths.amf_extract, dict_=amf_dict)
    for k, v in amf_dict.iteritems():
        for kk, vv in v.iteritems():
            if isinstance(vv, DataFrame):
                p = os.path.join(paths.amf_output_root,'{}_{}.csv'.format(k, kk))
                print 'writing to {}'.format(p)
                vv.to_csv(p)
    val = amf_dict.values()[0]

    cfg = Config()
    for runspec in cfg.runspecs:
        paths.build(runspec.input_root, runspec.output_root)

        etrm = Processes(runspec)
        etrm.configure_run(runspec)
        etrm.run()

    save_run(etrm, val)

    # for key, val in amf_dict.iteritems():
        # etrm = Processes(cfg.runspecs[0])
        # etrm.run(ro_reinf_frac=0.7, allen_ceff=0.8)
        # save_run(etrm, val)


def save_run(etrm, val):
    # tracker is deprecated, try commenting this out
    # path = os.path.join(paths.amf_output_root, '{}.csv'.format(val['Name']))
    # etrm.tracker.to_csv(path, na_rep='nan', index_label='Date')

    amf_obs_etrm_combo = DataFrame(concat((val['AMF_Data'], etrm.point_tracker), axis=1, join='outer'))
    obs_etrm_comb_out = os.path.join(paths.amf_combo_root, '{}_Ceff.csv'.format(val['Name']))

    print 'this should be your combo csv: {}'.format(obs_etrm_comb_out)
    amf_obs_etrm_combo.to_csv(obs_etrm_comb_out, index_label='Date')


if __name__ == '__main__':
    # ir = os.path.join('/Volumes', 'Seagate Expansion Drive', 'ETRM_Inputs')
    # ir = os.path.join('/Volumes', 'Seagate Expansion Drive')
    ir = os.path.join('C:\Users\Mike\PyRANA\ETRM_inputs_Ameriflux')
    sim = datetime(2007, 1, 1), datetime(2013, 12, 29)

    run(ir, sim)

# ============= EOF =============================================
