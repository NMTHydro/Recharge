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

this module provides (1) function -- get_distributed_recharge.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""

from datetime import datetime
import os
from numpy import set_printoptions

from recharge.etrm_processes import Processes


set_printoptions(linewidth=700, precision=2)

simulation_period = datetime(2000, 1, 1), datetime(2000, 1, 10)

extent = []  # we should eventually have a program to run etrm on a given extent

save_dates = []
save_outputs = []


def get_distributed_recharge(date_range, ndvi, prism, penman, raster_out_data, select_dates=None,
                             select_outputs=None, clip_polygons=None, save_csv=None):

    etrm = Processes(static_inputs_path, initial_conditions_path)

    tracker = etrm.run(date_range, results_path=raster_out_data, ndvi_path=ndvi, prism_path=prism,
                       penman_path=penman, polygons=clip_polygons)

    # print 'tracker after etrm run: \n {}'.format(tracker)
    csv_path_filename = os.path.join(save_csv, 'etrm_master_tracker.csv')
    print 'this should be your csv: {}'.format(csv_path_filename)
    tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')

    return None


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    initial_conditions_path = os.path.join(os.path.abspath(os.sep), 'Recharge_GIS', 'Array_Results', 'initialize')
    dynamic_inputs_path = os.path.join('F:\\', 'ETRM_Inputs')
    static_inputs_path = os.path.join(dynamic_inputs_path, 'current_use')
    ndvi_path = os.path.join(dynamic_inputs_path, 'NDVI', 'NDVI_std_all')
    prism_path = os.path.join(dynamic_inputs_path, 'PRISM')
    penman_path = os.path.join(dynamic_inputs_path, 'PM_RAD')
    output_polygons = os.path.join(dynamic_inputs_path, 'NM_Geo_Shapes')
    output_path = os.path.join('F:\\', 'ETRM_Results')
    get_distributed_recharge(simulation_period, ndvi_path, prism_path, penman_path, output_path,
                             clip_polygons=output_polygons, save_csv=output_path)

# ============= EOF =============================================

