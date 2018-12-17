# ===============================================================================
# Copyright 2018 gabe-parrish
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
import os
import time
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
# ============= local library imports ===========================
from utils.depletions_modeling.cumulative_depletions import raster_extract, write_raster, depletion_calc

def PyRana_WE(data_path, output_path, date_specs):
    """
    We run the Wang-Erlandsson approach with PyRANA outputs on the monthly time step. Ingredients are PyRANA adjusted
    Precip as inputs and total ETa from the dual crop coefficient model as outputs. This is merely to perform a sanity
     check with SSEB data.
    :return:
    """

    (start_month, start_year, end_month, end_year) = date_specs
    months_in_series = ((end_year - start_year) * 12) + (end_month - start_month)

    start_date = datetime(start_year, start_month, 1).date()
    end_date = datetime(end_year, end_month, 1).date()

    # at each timestep, keep track of how negative the depletion has gotten
    depletion_ledger = np.zeros((2525, 2272), dtype=float)
    # initialize depletion counter at zero.
    depletion_counter = np.zeros((2525, 2272), dtype=float)
    # keep track of the maximum depletion map
    max_depletion = np.zeros((2525, 2272), dtype=float)
    # to compare with SSEB
    total_eta = np.zeros((2525, 2272), dtype=float)

    for i in range(months_in_series + 1):

        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(data_path, "tot_precip_{}_{}.tif".format(date.month, date.year))
        eta = os.path.join(data_path, "tot_eta_{}_{}.tif".format(date.month, date.year))

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        eta_arr, transform, dim, proj, dt = raster_extract(eta)

        total_eta += eta_arr

        depletion_delta = depletion_calc(eta_arr, precip_arr)

        # add to the running depletion tally
        print depletion_delta.shape
        print depletion_counter.shape
        depletion_counter += depletion_delta
        depletion_ledger += depletion_delta

        # for any values that become negative, make them zero. Assume runoff...Wang-Erlandsson (2016)
        # todo - uncomment to ONLY allow positive depletions
        depletion_counter[depletion_counter < 0.0] = 0.0

        # newmax_bool = [depletion_counter > max_depletion]
        # newmax = depletion_counter[newmax_bool == True]
        newmax = np.maximum(depletion_counter, max_depletion)

        max_depletion = newmax

        # for each monthly timestep, take the cumulative depletion condition and output it as a raster
        depletion_name = "pyrana_cumulative_depletion_{}_{}.tif".format(date.year, date.month)
        write_raster(depletion_counter, transform, output_path, depletion_name, dim, proj, dt)

    # output the maximum depletion
    max_depletion_name = 'pyrana_max_depletion_{}_{}.tif'.format(start_date.year, end_date.year)
    write_raster(max_depletion, transform, output_path, max_depletion_name, dim, proj, dt)

    # output total SSEBop (to test wheter it looks like the netcdf file)
    total_ssebop_name = "total_eta_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(total_eta, transform, output_path, total_ssebop_name, dim, proj, dt)


if __name__ == "__main__":

    root_etrm_outputs = '/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/180727_17_33'


    data_file = os.path.join(root_etrm_outputs, 'monthly_rasters')

    output_folder = '/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/ETRM_cumulative_depletions_research/ETRM_WA_pos_only'

    start_month = 1
    end_month = 12
    start_year = 2001
    end_year = 2013

    date_specs = (start_month, start_year, end_month, end_year)


    PyRana_WE(data_file, output_folder, date_specs)

    # TODO - do the same with 1.25*NDVI = ETa and PRISM