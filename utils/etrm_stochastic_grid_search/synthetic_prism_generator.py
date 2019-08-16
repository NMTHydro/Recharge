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
import pandas as pd
import numpy as np
# ============= standard library imports ========================
from utils.TAW_optimization_subroutine.calculate_delta_chi import numpy_to_geotiff
from utils.TAW_optimization_subroutine.create_geo_info_file import extract_geo_info


sample_file = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_inputs/vcp_aoi/PRISM/precip/800m_std_all/precip_20000107.tif'

etrm_prism_name_format = 'precip_{}{:02d}{:02d}.tif'

# TODO - do the extraction
# ameriflux_file = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/wjs/taw_25_dataset.csv'
ameriflux_file = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_II/vcp/taw_25_dataset.csv'

false_prism_path = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_inputs/vcp_false_prism'

amf_data = pd.read_csv(ameriflux_file, parse_dates=True)

amf_data = amf_data[amf_data['amf_precip_values'].notnull() & amf_data['prism_values'].notnull()]

amf_dates = pd.to_datetime(amf_data['seed1date_x']).to_list()

amf_precip = amf_data['amf_precip_values'].to_list()

print 'amf dates\n', amf_dates

prism_vals = amf_data['prism_values'].to_list()
#
print 'prism vals \n', prism_vals

print 'len prism {}, len dates {}, len amfprecip {}'.format(len(prism_vals), len(amf_dates), len(amf_precip))


geo_info = extract_geo_info(sample_file)

print geo_info

for ad, ap in zip(amf_dates, amf_precip):

    etrm_prism_name = etrm_prism_name_format.format(ad.year, ad.month, ad.day)

    print 'name: ', etrm_prism_name

    false_prism_arr = np.zeros(geo_info['dimensions'])

    false_prism_arr[1, 1] = ap

    print false_prism_arr

    numpy_to_geotiff(false_prism_arr, geo_info, output_path=false_prism_path, output_name=etrm_prism_name)