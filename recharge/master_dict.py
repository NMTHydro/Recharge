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
The purpose of this module is to initialize empty etrm arrays before run.

returns dict with all rasters under keys of etrm variable names

dgketchum 24 JUL 2016
"""

from numpy import ones


def initialize_master_dict(list_of_variables, raster_shape):

    dictionary = {}
    for key in list_of_variables:
        dictionary.update({key: ones(raster_shape)})
    return dictionary

# ============= EOF =============================================
