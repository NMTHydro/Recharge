# ===============================================================================
# Copyright 2016 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance
# with the License.
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

# =================================IMPORTS=======================================
import os
from datetime import datetime
from pandas import concat, DataFrame

from recharge.time_series_manager import amf_obs_time_series, get_etrm_time_series
from recharge.etrm_processes import Processes

BASE_AMF_DICT = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
                 '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
                 '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
                 '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
                 '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
                 '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}}


def amf_observation_analysis(amf_file_path, save_cleaned_data=None):
    amf_dict = amf_obs_time_series(BASE_AMF_DICT, amf_file_path, complete_days_only=True,
                                   save_cleaned_data_path=save_cleaned_data, return_low_err=True)


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print('home: {}'.format(home))
    root = os.path.join(home)
    inputs = os.path.join('F:\\', 'ETRM_Inputs')
    amf_path = os.path.join(inputs, 'ameriflux_sites')
    amf_obs_root = os.path.join(amf_path, 'AMF_Data')
    amf_obs_processed = os.path.join(amf_path, 'AMF_obs_processed')
    amf_etrm_combo = os.path.join(amf_path, 'AMF_results_combo')
    amf_observation_analysis(amf_obs_root)

# ==========================  EOF  ==============================================
