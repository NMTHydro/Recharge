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

from datetime import datetime
import os
from recharge.etrm_processes import Processes


def run(root, output_root):

    date_range = datetime(2013, 12, 29), datetime(2013, 12, 31)

    mask_path = os.path.join(root, 'Mask')

    etrm = Processes(date_range, mask_path,
                     output_root= output_root,
                     polygons= os.path.join(root, 'Blank_Geo'),
                     static_inputs= os.path.join(root, 'statics'),
                     initial_inputs=os.path.join(root, 'initialize'))

    ndvi = os.path.join(root, 'NDVI', 'NDVI_std_all')
    prism = os.path.join(root, 'PRISM')
    penman = os.path.join(root, 'PM_RAD')

    etrm.run(ndvi_path=ndvi, prism_path=prism, penman_path=penman)


if __name__ == '__main__':
    run('F:\\ETRM_Inputs',
        'F:\\ETRM_Results')

# ============= EOF =============================================
