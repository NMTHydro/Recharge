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
The purpose of this module is to set ETRM constant.

returns dict with all rasters under keys of etrm variable names

dgketchum 24 JUL 2016
"""


def set_constants(soil_evap_depth=40, et_depletion_factor=0.4, min_basal_crop_coef=0.15,
                  max_basal_crop_coef=1.2,
                  max_ke=1.0, min_snow_albedo=0.45, max_snow_albedo=0.90):

    dictionary = dict(ze=soil_evap_depth, p=et_depletion_factor, kc_min=min_basal_crop_coef,
                      kc_max=max_basal_crop_coef,
                      ke_max=max_ke, a_min=min_snow_albedo, a_max=max_snow_albedo)

    return dictionary
