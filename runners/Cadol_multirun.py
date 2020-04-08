# ===============================================================================
# Copyright 2018 Daniel Cadol
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
The purpose of this module is to repeatedly run batches of PyRANA (ETRM with
added stochastic runoff capability) instances. This monte carlo repetition
enables analysis of the range and central tendency of the model results.

this module provides (1) function -- run_reps.

dancadol 16 July 2018
"""

import sys
import os
from app.generic_runner import run


pp = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(pp)))


def run_reps():
    runs = 1  # user sets the number of repeated runs to be performed
    for i in range(0, runs):
        # if multiple locations are to be analyzed, each will require a new yaml config file
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff1.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff2.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff3.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff4.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff5.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff6.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff7.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff8.yml')
        run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG_ceff9.yml')
        # # run(cfg_path='C:\Users\Mike\ETRM_CONFIG_placitas.yml')
        # run(cfg_path='C:\Users\Mike\ETRM_CONFIG_picacho.yml')
        # run(cfg_path='C:\Users\Mike\ETRM_CONFIG_rincon.yml')
        # run(cfg_path='C:\Users\Mike\ETRM_CONFIG_overshot.yml')


if __name__ == '__main__':

    run_reps()
    # run(cfg_path='C:\Users\Mike\PyRANA\PYRANA_CONFIG.yml')
