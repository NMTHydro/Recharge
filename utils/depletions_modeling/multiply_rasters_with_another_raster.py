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
import os

# ============= standard library imports ========================
from utils.depletions_modeling.cumulative_depletions import raster_extract, write_raster


root = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'

output_dir = '/Volumes/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_et_ratio_modified'

jpl_prism_ratio_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE_2012/qgis/jpleta_prism_ratio_2012.tif'

jpl_prism_ratio, transform, dimensions, projection, dt = raster_extract(jpl_prism_ratio_path)


for file in os.listdir(root):

    print 'file: {}'.format(file)

    if file.endswith('.tif'):

        file_name = file[:-4]

        new_fname = '{}_ratiomod.tif'.format(file_name)

        data, transform, dimensions, projection, dt = raster_extract(os.path.join(root, file))

        jpl_mod = data / jpl_prism_ratio

        write_raster(jpl_mod, transform, output_dir, new_fname, dimensions, projection, dt)