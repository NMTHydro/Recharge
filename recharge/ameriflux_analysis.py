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

from recharge.time_series_manager import amf_obs_time_series, get_etrm_time_series
from recharge.etrm_processes import Processes
from recharge.user_constants import set_constants

simulation_dates = datetime(2007, 1, 1), datetime(2013, 12, 31)
user_const = set_constants()
base_amf_dict = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_conifer'},
                 '2': {'Coords': '355774 3969864', 'Name': 'Valles_ponderosa'},
                 '3': {'Coords': '339552 3800667', 'Name': 'Sev_shrub'},
                 '4': {'Coords': '343495 3803640', 'Name': 'Sev_grass'},
                 '5': {'Coords': '386288 3811461', 'Name': 'Heritage_pinyon_juniper'},
                 '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_juniper_savanna'}}


def get_ameriflux_data(ameriflux_dict, amf_file_path, simulation_period, etrm_extract=None,
                       static_inputs=None, initial_path=None):

    amf_dict = amf_obs_time_series(ameriflux_dict, amf_file_path, save_cleaned_data_path=False)

    get_etrm_time_series(amf_dict, inputs_path=etrm_extract)
    etrm = Processes(static_inputs=static_inputs, constants=user_const, point=True, point_dict=amf_dict)

    print amf_dict

    # for key, val in amf_dict.iteritems():
    #     val.update({'etrm': etrm.run(simulation_period)})

    return None

if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    recharge = os.path.join(root, 'Documents', 'Recharge')
    amf_obs_root = os.path.join(recharge, 'aET', 'AMF_Data')
    amf_extract = os.path.join(recharge, 'aET', 'AMF_extracts')
    initial_conditions_path = os.path.join(os.path.abspath(os.sep), 'Recharge_GIS', 'Array_Results', 'initialize')
    static_inputs_path = os.path.join(os.path.abspath(os.sep), 'Recharge_GIS', 'OSG_Data', 'current_use')
    get_ameriflux_data(base_amf_dict, amf_obs_root, simulation_dates, etrm_extract=amf_extract,
                       static_inputs=static_inputs_path, initial_path=initial_conditions_path)

# ============= EOF =============================================
