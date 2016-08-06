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
from recharge.user_constants import set_constants


set_printoptions(linewidth=700, precision=2)

simulation_period = datetime(2000, 1, 1), datetime(2000, 12, 31)
monsoon_dates = datetime(simulation_period[0].year, 6, 1), datetime(simulation_period[1].year, 10, 1)

constants = set_constants(soil_evap_depth=40, et_depletion_factor=0.4, min_basal_crop_coef=0.15,
                          max_ke=1.0, min_snow_albedo=0.45, max_snow_albedo=0.90, snow_alpha=0.2,
                          snow_beta=11.0)

extent = []  # we should eventually have a program to run etrm on a given extent

save_dates = []
save_outputs = []


def get_distributed_recharge(date_range, monsoon, raster_out_data, user_constants, select_dates=None,
                             select_outputs=None):

    etrm = Processes(static_inputs_path, initial_conditions_path, user_constants)

    etrm.run(date_range, ndvi_path, prism_path, penman_path, monsoon, raster_out_data)

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
    output_path = os.path.join('F:\\', 'ETRM_Results')
    out_date = datetime.now()
    out_pack = (output_path, out_date)
    get_distributed_recharge(simulation_period, monsoon_dates, out_pack, constants)

# ============= EOF =============================================

