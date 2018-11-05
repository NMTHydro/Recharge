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
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
# ============= local library imports ===========================
from cumulative_depletions import raster_extract, write_raster, depletion_calc



def cumulative_SSEB_PRISM(pris_path, ssebop_path, prism_output, sseb_output ):
    """"""

    # function to calculate the depletion at a monthly timestep
    #  within that function, output the running depletion raster that results from each month's F_in-F_out
    start_date = datetime.strptime("2000-2", "%Y-%m")
    end_date = datetime.strptime("2013-12", "%Y-%m")

    months_in_series = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)

    precip_name = "tot_precip_{}_{}.tif"
    ssebop_name = "ssebop_{}_{}_warped.tif"

    # These numpy arrays will hold the cumulative total
    total_prism = np.zeros((2525, 2272), dtype=float)
    total_ssebop = np.zeros((2525, 2272), dtype=float)

    for i in range(months_in_series + 1):

        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(pris_path, precip_name.format(date.year, date.month))
        ssebop = os.path.join(ssebop_path, ssebop_name.format(date.year, date.month))

        print 'precip', precip
        print 'ssebop', ssebop

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        ssebop_arr, transform, dim, proj, dt = raster_extract(ssebop)

        # accumulate totals in the arrays
        total_ssebop += ssebop_arr
        total_prism += precip_arr

        ct_prism_name = "ct_precip_{}_{}.tif".format(date.year, date.month)
        ct_ssebop_name = "ct_ssebop_{}_{}.tif".format(date.year, date.month)

        # for the last raster, output to a different directory, which we want for another analysis.
        if ct_prism_name == "ct_precip_2013_12.tif": #todo don't hardcode
            prism_output = os.path.join(prism_output, 'terminal_cumulation')
            write_raster(total_prism, transform, prism_output, ct_prism_name, dim, proj, dt)
        else:
            write_raster(total_prism, transform, prism_output, ct_prism_name, dim, proj, dt)

        if ct_ssebop_name == "ct_ssebop_2013_12.tif":  # todo don't hardcode
            sseb_output = os.path.join(sseb_output, 'terminal_cumulation')
            write_raster(total_prism, transform, prism_output, ct_prism_name, dim, proj, dt)
        else:
            write_raster(total_ssebop, transform, sseb_output, ct_ssebop_name, dim, proj, dt)

def run_W_E_mod(ssebop_path, pris_path, output_folder, ct_ratio):
    """
    This tracks depletions and outputs only positive or zero depletions at each timestep like Wang-Erlandsson.Each
    timestep SSEB is reduced by (PRISM_ct/SSEB_ct)
    :return:
    """

    if isinstance(ct_ratio, basestring):
        ct_ratio_arr, transform, dim, proj, dt = raster_extract(ct_ratio)

    else:
        ct_ratio_arr = ct_ratio

    print 'shape', ct_ratio_arr.shape

    # seems like we need to start in Feb of 2000 (ETRM monthly precip outputs only start in Feb 2000...)

    # function to calculate the depletion at a monthly timestep
    #  within that function, output the running depletion raster that results from each month's F_in-F_out
    start_date = datetime.strptime("2000-2", "%Y-%m")
    end_date = datetime.strptime("2013-12", "%Y-%m")

    months_in_series = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)

    precip_name = "tot_precip_{}_{}.tif"
    ssebop_name = "ssebop_{}_{}_warped.tif"

    # initialize depletion counter at zero.
    depletion_counter = np.zeros((2525, 2272), dtype=float)
    # keep track of the maximum depletion map
    max_depletion = np.zeros((2525, 2272), dtype=float)
    # keep track of totals over time (after multiplying by PRISM_ct/SSEB_ct)
    total_ssebop = np.zeros((2525, 2272), dtype=float)
    total_prism = np.zeros((2525, 2272), dtype=float)
    for i in range(months_in_series + 1):
        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(pris_path, precip_name.format(date.year, date.month))
        ssebop = os.path.join(ssebop_path, ssebop_name.format(date.year, date.month))

        print 'precip', precip
        print 'ssebop', ssebop

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        ssebop_arr, transform, dim, proj, dt = raster_extract(ssebop)

        # augment/reduce SSEB by the ratio of precip_ct to SSEB_ct
        print
        ssebop_arr = ssebop_arr * ct_ratio_arr

        total_ssebop += ssebop_arr
        total_prism += precip_arr

        # oldmax = max_depletion

        # depletion for the current monthly timestep
        depletion_delta = depletion_calc(ssebop_arr, precip_arr)

        # add to the running depletion tally
        depletion_counter += depletion_delta

        # for any values that become negative, make them zero. Assume runoff...Wang-Erlandsson (2016)
        depletion_counter[depletion_counter < 0.0] = 0.0

        # find the new all-time max for each pixel in raster
        newmax = np.maximum(depletion_counter, max_depletion)
        max_depletion = newmax

        # for each monthly timestep, take the cumulative depletion condition and output it as a raster
        depletion_name = "cumulative_depletion_{}_{}.tif".format(date.year, date.month)
        write_raster(depletion_counter, transform, output_folder, depletion_name, dim, proj, dt)

    # output the maximum depletion
    max_depletion_name = 'max_depletion_{}_{}.tif'.format(start_date.year, end_date.year)
    write_raster(max_depletion, transform, output_folder, max_depletion_name, dim, proj, dt)

    # output total SSEBop (to test wheter it looks like the netcdf file)
    total_ssebop_name = "total_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(total_ssebop, transform, output_folder, total_ssebop_name, dim, proj, dt)

    # output the average SSEBop (to test whether it looks like the netcdf file)
    average_ssebop = total_ssebop / float(months_in_series)
    average_ssebop_name = "average_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(average_ssebop, transform, output_folder, average_ssebop_name, dim, proj, dt)

def run_neg_depletions(ssebop_path, pris_path, output_folder, ct_ratio):
    """This function outputs depletions that may go negative. Each timestep SSEB is reduced by (PRISM_ct/SSEB_ct)"""

    if isinstance(ct_ratio, basestring):
        ct_ratio_arr, transform, dim, proj, dt = raster_extract(ct_ratio)

    else:
        ct_ratio_arr = ct_ratio

    print 'shape', ct_ratio_arr.shape

    # seems like we need to start in Feb of 2000 (ETRM monthly precip outputs only start in Feb 2000...)

    # function to calculate the depletion at a monthly timestep
    #  within that function, output the running depletion raster that results from each month's F_in-F_out
    start_date = datetime.strptime("2000-2", "%Y-%m")
    end_date = datetime.strptime("2013-12", "%Y-%m")

    months_in_series = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)

    precip_name = "tot_precip_{}_{}.tif"
    ssebop_name = "ssebop_{}_{}_warped.tif"

    # initialize depletion counter at zero.
    depletion_counter = np.zeros((2525, 2272), dtype=float)
    # keep track of the maximum depletion map
    max_depletion = np.zeros((2525, 2272), dtype=float)
    # keep track of totals over time (after multiplying by PRISM_ct/SSEB_ct)
    total_ssebop = np.zeros((2525, 2272), dtype=float)
    total_prism = np.zeros((2525, 2272), dtype=float)
    for i in range(months_in_series + 1):
        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(pris_path, precip_name.format(date.year, date.month))
        ssebop = os.path.join(ssebop_path, ssebop_name.format(date.year, date.month))

        print 'precip', precip
        print 'ssebop', ssebop

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        ssebop_arr, transform, dim, proj, dt = raster_extract(ssebop)

        # augment/reduce SSEB by the ratio of precip_ct to SSEB_ct
        print
        ssebop_arr = ssebop_arr * ct_ratio_arr

        total_ssebop += ssebop_arr
        total_prism += precip_arr

        # oldmax = max_depletion

        # depletion for the current monthly timestep
        depletion_delta = depletion_calc(ssebop_arr, precip_arr)

        # add to the running depletion tally
        depletion_counter += depletion_delta

        # for any values that become negative, make them zero. Assume runoff...Wang-Erlandsson (2016)
        # # todo - comment out to allow depletions to be positive
        # depletion_counter[depletion_counter < 0.0] = 0.0

        # find the new all-time max for each pixel in raster
        newmax = np.maximum(depletion_counter, max_depletion)
        max_depletion = newmax

        # for each monthly timestep, take the cumulative depletion condition and output it as a raster
        depletion_name = "cumulative_depletion_{}_{}.tif".format(date.year, date.month)
        write_raster(depletion_counter, transform, output_folder, depletion_name, dim, proj, dt)

    # output the maximum depletion
    max_depletion_name = 'max_depletion_{}_{}.tif'.format(start_date.year, end_date.year)
    write_raster(max_depletion, transform, output_folder, max_depletion_name, dim, proj, dt)

    # output total SSEBop (to test wheter it looks like the netcdf file)
    total_ssebop_name = "total_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(total_ssebop, transform, output_folder, total_ssebop_name, dim, proj, dt)

    # output the average SSEBop (to test whether it looks like the netcdf file)
    average_ssebop = total_ssebop / float(months_in_series)
    average_ssebop_name = "average_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(average_ssebop, transform, output_folder, average_ssebop_name, dim, proj, dt)

def ct_ratio_calc(prism_ct_path, sseb_ct_path, ratio_output):
    """"""

    precip_arr, transform, dim, proj, dt = raster_extract(prism_ct_path)
    sseb_arr, transform, dim, proj, dt = raster_extract(sseb_ct_path)

    print precip_arr.shape, sseb_arr.shape

    ct_ratio_arr = precip_arr/sseb_arr

    ct_ratio_name = "ct_p_sseb_ratio_2013_12"
    write_raster(ct_ratio_arr, transform, ratio_output, ct_ratio_name, dim, proj, dt)

    return ct_ratio_arr

def W_E_neg_depletions_processing():
    """
    Here we take the end result of the cumulative SSEB ET and the PRISM precip at the end of the time series and we get
     the ratio of PRISM_ct to SSEB_ct. We then use that ratio to reduce SSEB at each timestep of the depletion. We will
      do two analyses after the ratio is determined.:
      - One where depletions are allowed to go negative.
      - Another where depletions are held to be zero or positive as in Wang-Erlandsson et al 2016
    :return:
    """
    ### Step 1
    # # first we shall determine the ratio of the cumulative SSEB to the cumulative PRISM
    # sseb_dir = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/SSEBop/SSEBOP_Geotiff_warped"
    # prism_dir = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"
    #
    # sseb_output_dir = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_SSEB"
    # prism_output_dir = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_prism"
    #
    # cumulative_SSEB_PRISM(pris_path=prism_dir, ssebop_path=sseb_dir, prism_output=prism_output_dir,
    #                       sseb_output=sseb_output_dir)

    # ### Step 2
    # prism_ct_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_prism/terminal_cumulation/ct_precip_2013_12.tif"
    # sseb_ct_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_SSEB/terminal_cumulation/ct_ssebop_2013_12.tif"
    # # store the ratio of ct_precip to ct_sseb
    # ratio_output ="/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_prism_sseb_ratio"
    #
    # # use the cumulative depletions to do calculate the (prism_ct/sseb_ct) ratio
    #
    # # Todo (something strange going on w the ct ratio calc)
    # ct_ratio_calc(prism_ct_path, sseb_ct_path, ratio_output)
    # # ended up getting the ratio using QGIS Raster calculator

    ### Step 3 do the mod negative calculations

    # QGIS geotiff of prism_ct/sseb_ct
    ct_ratio_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_prism_sseb_ratio/ct_p_sseb_ratio_2013_12_QGIS.tif"

    # path to monthly ETa
    ssebop_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/SSEBop/SSEBOP_Geotiff_warped"

    # path to monthly Prism
    pris_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"

    # output path
    # output_folder = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_depletions"

    # output_folder = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cum_depletions_neg_mod"

    # run_neg_depletions(ssebop_path=ssebop_path, pris_path=pris_path, output_folder=output_folder, ct_ratio=ct_ratio_path)

    ### Step 4, Now zeroing out after WA
    output_folder = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cum_depletions_WA_mod"

    run_W_E_mod(ssebop_path=ssebop_path, pris_path=pris_path, output_folder=output_folder,
                       ct_ratio=ct_ratio_path)


if __name__ == "__main__":

    W_E_neg_depletions_processing()