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
The purpose of this module is to repeatedly
1) run PyRANA starting with a full TAW (initially given a TAW of 1000 mm
2) use depletion tracking to estimate a new TAW for each pixel
3) Re-run PyRANA using the new TAW (starting with 0 depletion, i.e., full of water)
iterate steps 2 and 3

The idea is to recursively set TAW, assuming that PyRANA has the best available water-limited ET estimate.
Prior to testing this, it is unclear if TAW can be zoomed into this way.

dancadol 27 December 2018
"""
import shutil
import sys
import os
from app.generic_runner import run
from app.paths import paths
from utils.depletions_modeling.cumulative_depletions import run_W_E, run_rename
from app.config import Config

pp = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(pp)))


def run_iterate():
    runs = 1  # user sets the number of repeated runs to be performed
    # Set the cfg path to the  CONFIG file
    cfg_path = os.path.join("C:\Users\Mike\PyRANA", 'PYRANA_CONFIG.yml')
    cfg = Config(cfg_path)
    for i in range(0, runs):
        # Run PyRANA
        print 'doing iteration {}'.format(i)
        run(cfg_path=cfg_path)
        output_root = paths.results_root
        # output_root = 'C:\Users\Mike\PyRANA\PyRANA_results000\\190114_10_07'

        # Rename the monthly precip and ETa files for use with cumulative depletion script
            # This is no longer necessary: _write_raster was changed to output in year_month order
        # monthly_raster_path = os.path.join(output_root, 'monthly_rasters')
        # run_rename(param_path=monthly_raster_path, param='precip')
        # run_rename(param_path=monthly_raster_path, param='eta')

        # Calculate the max cumulative depletion
        eta_path = os.path.join(output_root, 'monthly_rasters')
        pris_path = os.path.join(output_root, 'monthly_rasters')
        # output_folder = 'C:\Users\Mike\PyRANA\PyRANA_results\depletion_{}'.format(i)
        output_folder = os.path.join(output_root, 'depletion_{:02n}'.format(i))
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        run_W_E(cfg.runspecs[0], eta_path=eta_path, pris_path=pris_path,
                output_folder=output_folder, is_ssebop=False, shape=(2525, 2272))
        # Save the max depletion raster as the new TAW raster and
        # replace the old TAW raster in the static inputs folder with the new TAW raster
        start_date, end_date = cfg.runspecs[0].date_range
        max_dep_file = 'max_depletion_{}_{}.tif'.format(start_date.year, end_date.year)
        max_dep_path = os.path.join(output_root, 'depletion_{:02n}'.format(i), max_dep_file)
        taw_store_root = 'C:\Users\Mike\PyRANA\PyRANA_inputs_recursive_AOI'
        taw_store_path = os.path.join(taw_store_root, 'TAWs', 'taw_{:02n}.tif'.format(i))
        shutil.copyfile(max_dep_path, taw_store_path)

        taw_path = os.path.join(taw_store_root, 'statics', 'taw_reduced.tif')
        shutil.copyfile(taw_store_path, taw_path)


if __name__ == '__main__':

    run_iterate()
