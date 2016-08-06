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
"""
The purpose of this module is to calculate recharge over a defined geographic area.

this module provides (1) function -- run_distributed_ETRM.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""

from datetime import datetime
import os
from numpy import set_printoptions

from recharge.etrm_processes import Processes


set_printoptions(linewidth=700, precision=2)

# Set start datetime object
start, end = datetime(2000, 1, 1), datetime(2000, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime(start.year, 11, 1), datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime(start.year, 6, 1), datetime(start.year, 10, 1)


def get_distributed_recharge(start_date, end_date, extent):

    etrm = Processes(static_inputs_path, initial_conditions_path)

    etrm.run(start, end, ndvi_path, prism_path, penman_path, sMon, eMon,)

    return None


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    static_inputs_path = os.path.join(os.path.abspath(os.sep), 'Recharge_GIS', 'OSG_Data', 'current_use')
    initial_conditions_path = os.path.join(os.path.abspath(os.sep), 'Recharge_GIS', 'Array_Results', 'initialize')
    dynamic_inputs_path = os.path.join('F:\\', 'ETRM_Inputs')
    ndvi_path = os.path.join(dynamic_inputs_path, 'NDVI', 'NDVI_std_all')
    prism_path = os.path.join(dynamic_inputs_path, 'PRISM')
    penman_path = os.path.join(dynamic_inputs_path, 'PM_RAD')
    # output_path = os.path.join('F', 'output')
    # fig_save = os.path.join(home, 'Documents', 'ArcGIS', 'results', 'July_results')
    # csv_save = os.path.join(home, 'Documents', 'ArcGIS', 'results', 'July_results')
    get_distributed_recharge(start, end, extent='NM')

# ============= EOF =============================================

