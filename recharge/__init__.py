# ===============================================================================
# Copyright 2016 Jake Ross
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

# ============= standard library imports ========================
# ============= local library imports  ==========================
NUMS = (1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209, 225, 241, 257, 273, 289, 305, 321, 337, 353)
NUMSIZE = len(NUMS)

PRISM_YEARS = (2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013)

STATIC_KEYS = 'bed_ksat', 'land_cover', 'plant_height', 'quat_deposits', 'rew', 'root_z', 'soil_ksat', 'taw', 'tew'
INITIAL_KEYS = 'de', 'dr', 'drew'

OUTPUTS = 'tot_infil', 'tot_etrs', 'tot_eta', 'tot_precip', 'tot_kcb', 'de', 'dr', 'drew'

MM = 'mm'

CURRENT_DAY = 'current_day'
CURRENT_MONTH = 'current_month'
CURRENT_YEAR = 'current_year'

ANNUAL_TRACKER_KEYS = CURRENT_YEAR, 'last_year'
MONTHLY_TRACKER_KEYS = CURRENT_MONTH, 'last_month'
DAILY_TRACKER_KEYS = CURRENT_DAY, 'yesterday'

TRACKER_KEYS = ANNUAL_TRACKER_KEYS + MONTHLY_TRACKER_KEYS + DAILY_TRACKER_KEYS
# ============= EOF =============================================



