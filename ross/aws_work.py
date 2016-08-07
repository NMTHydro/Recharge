# ===============================================================================
# Copyright 2016 ross
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

# Modified from ETRM_distributed/ETRM_savAnMo_5MAY16.py
# Developed by David Ketchum NMT 2016

# ============= standard library imports ========================
import logging
import os
from datetime import datetime

from numpy import ones, maximum, where
# ============= local library imports  ==========================
from ross.etrm_funcs import tif_to_array, tif_params, write_tiff


def aws():
    root = os.path.join('C:', 'Recharge_GIS', 'OSG_Data', 'current_use')
    name = 'aws_ras_15apr1'
    taw = tif_to_array(root, name)
    min_val = ones(taw.shape) * 0.001
    taw = maximum(taw, min_val)

    params = tif_params(root, name)

    root = os.path.join('C:', 'Recharge_GIS', 'OSG_Data', 'qgis_rasters')
    name = 'aws_mm_21apr_std'
    taw_st = tif_to_array(root, name)
    taw_st = maximum(taw_st, min_val)

    result = where(taw_st > taw, taw_st, taw)

    now = datetime.now()
    tag = '{}_{}_{}_{}'.format(now.month, now.day, now.hour, now.minute)
    oroot = os.path.join('C:', 'Recharge_GIS', 'OSG_Data', 'qgis_rasters')

    for (name, data) in ((result, 'aws_mod'), (taw, 'taw')):
        logging.info('Saving {}'.format(name))

        oname = os.path.join(oroot, '{}_{}.tif'.format(name, tag))
        write_tiff(oname, params, data)


if __name__ == '__main__':
    aws()
# ============= EOF =============================================
