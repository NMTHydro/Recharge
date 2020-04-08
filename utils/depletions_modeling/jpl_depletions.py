# ===============================================================================
# Copyright 2019 Jan Hendrickx and Gabriel Parrish
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
from datetime import datetime, date
# ============= standard library imports ========================
from utils.depletions_modeling.cumulative_depletions import run_W_E

# jpl_eta_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'
jpl_eta_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_et_ratio_modified'
prism_path = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/PRISM/Precip/800m_std_all'

output = '/Volumes/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_depletions_mod'

eta_output = '/Volumes/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_cum_eta_mod'
prism_output = '/Volumes/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_cum_prism_mod'

shape = 2525, 2272

start_date = date(2002, 01, 01)
end_date = date(2012, 12, 31)

run_W_E(cfg=None, eta_path=jpl_eta_path, pris_path=prism_path, output_folder=output, is_ssebop=False, is_jpl=True,
        shape=shape, start_date=start_date, end_date=end_date, time_step='daily', eta_output=eta_output, precip_output=prism_output)