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
from app.generic_runner import run_dataset
# ============= standard library imports ========================
import os

def run(config_root):

    for i in os.listdir(config_root):
        cfg_path = os.path.join(config_root, i)

        run_dataset(cfg_path=cfg_path)

if __name__ == "__main__":

    """ The point of this script is to reduce the ETRM model for a number of small models that one wishes to use."""

    # path where all the configuration files are stored
    config_root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_configs'

    run(config_root)