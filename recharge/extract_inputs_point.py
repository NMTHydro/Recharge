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

from recharge.point_extract_utility import get_dynamic_inputs_from_shape


def extract_etrm_point_inputs(shapefile, ndvi, prism, penman, simulation_period, out_location):

    get_dynamic_inputs_from_shape(shapefile, ndvi, prism, penman, simulation_period, out_location)


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    inputs = os.path.join('F:\\', 'ETRM_Inputs')
    ndvi_path = os.path.join(inputs, 'NDVI', 'NDVI_std_all')
    prism_path = os.path.join(inputs, 'PRISM')
    penman_path = os.path.join(inputs, 'PM_RAD')
    statics = os.path.join(inputs, 'statics')
    sa_path = os.path.join(inputs, 'sensitivity_analysis')
    save_path = os.path.join(sa_path, 'SA_extracts')
    shape = os.path.join(sa_path, 'sensitivity_points', 'SA_pnts_four_17OCT16.shp')
    period = datetime(2000, 1, 1), datetime(2013, 12, 31)
    extract_etrm_point_inputs(shape, ndvi_path, prism_path, penman_path, period, save_path)

# ==========================  EOF  ==============================================
