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
from runners.paths import paths


def extract_etrm_point_inputs(input_root, output_root, simulation_period):
    # ndvi_path = os.path.join(input_root, 'NDVI', 'NDVI_std_all')
    # prism_path = os.path.join(input_root, 'PRISM')
    # penman_path = os.path.join(input_root, 'PM_RAD')

    paths.build(input_root)

    # statics = os.path.join(input_root, 'statics')
    # sa_path = os.path.join(input_root, 'shapefiles')  # (input_root, 'shapefiles')
    # sb_path is where the outputs are going. sa_path used to be for sensitivity analysis.
    # sb_path = os.path.join(input_root, 'ameriflux_ex_sac')  # ameriflux_sites
    # save_path = sb_path  # os.path.join(sa_path, 'AMF_extracts')
    # save_path = sb_path  # os.path.join(sa_path, 'AMF_extracts')

    shapefile = os.path.join('/Users', 'Gabe', 'Desktop', 'QGIS_Ameriflux', 'coords_attempt3.shp')
    # shape = os.path.join(sa_path, 'amf_sites_UTM.shp')

    print("Here is the save path {}".format(output_root))
    get_dynamic_inputs_from_shape(shapefile, simulation_period, output_root)


if __name__ == '__main__':
    input_root = os.path.join('/Volumes', 'Seagate Expansion Drive')
    output_root = os.path.join(input_root, 'ameriflux_ex_sac')
    simulation_period = datetime(2000, 1, 1), datetime(2013, 12, 31)

    extract_etrm_point_inputs(input_root, output_root, simulation_period)


# ==========================  EOF  ==============================================
