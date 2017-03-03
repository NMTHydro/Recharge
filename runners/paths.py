# ===============================================================================
# Copyright 2017 ross
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

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
import os


class Paths:
    etrm_input_root = None
    etrm_output_root = None
    prism = None
    penman = None
    ndvi = None
    ndvi_std_all = None
    ndvi_individ = None
    static_inputs = None
    initial_inputs = None
    polygons = None
    mask = None

    def build(self, input_root, output_root=None):
        self.etrm_input_root = etrm_input_root = os.path.join(input_root,
                                                              'ETRM_Inputs')
        if output_root is None:
            output_root = input_root

        self.etrm_output_root = os.path.join(output_root, 'ETRM_Results')
        self.prism = os.path.join(etrm_input_root, 'PRISM')
        self.ndvi = os.path.join(etrm_input_root, 'NDVI')
        self.ndvi_std_all = os.path.join(self.ndvi, 'NDVI_std_all')
        self.ndvi_individ = os.path.join(self.ndvi, 'NDVI_individ')
        self.penman = os.path.join(etrm_input_root, 'PM_RAD')
        self.static_inputs = os.path.join(etrm_input_root, 'statics')
        self.initial_inputs = os.path.join(etrm_input_root, 'initial')

    def set_mask_path(self, path):
        self.mask = self.input_path(path)

    def input_path(self, path):
        return os.path.join(self.etrm_input_root, path)

    def set_polygons_path(self, p):
        self.polygons = self.input_path(p)


paths = Paths()
# ============= EOF =============================================
