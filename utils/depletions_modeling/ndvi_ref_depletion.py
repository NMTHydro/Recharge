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
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# ============= local library imports ===========================
from utils.depletions_modeling.cumulative_depletions import raster_extract, write_raster, depletion_calc


def main():
    """"""
    pass

def generate_monthly_eta(ndvi_path, etrf_path, output_path, date_specs):
    """
    generates monthly cumulative ETa based on ETa = [(1.25 * NDVI_PyRana) * ETrF_gadget]
    :param ndvi_path:
    :param etrf_path:
    :param output_path:
    :return:
    """

    (start_day, start_month, start_year, end_day, end_month, end_year) = date_specs

    start_date = datetime(start_year, start_month, start_day).date()
    end_date = datetime(end_year, end_month, end_day).date()

    # get how many total days there are in the series.
    period_delta = end_date - start_date
    delta_days = period_delta.days

    print 'intervening days {}'.format(delta_days)

    # names for NDVI and Penman Monteith ref ET form ETRM inputs file structures

    # .format(year, month, day)
    ndvi_name = 'NDVI{}_{:02d}_{:02d}.tif'
    # .format(year, julian_date)
    refet_name = 'PM_NM_{}_{:03d}.tif'


    # at each iteration we move the current date up by this much.
    daily_period = timedelta(days=1)

    # this is the period we'll acumulate over. We'll check to see if current date is
    accumulation_period = relativedelta(months=+1)

    # use the accumulation period to make a list of tuples that is the first day of the month and contains an empty
    # numpy array of ETRM dimensions.
    first_days_of_month = []
    current_date = start_date
    for i in range(delta_days + 1):

        if current_date.day == 1:
            first_days_of_month.append((current_date, np.zeros((2525, 2272), dtype=float)))

        current_date += relativedelta(days=+1)

    # iterate through each month based on the first days of the month

    print 'len first days of month ', len(first_days_of_month)
    for dm_tup in first_days_of_month:

        (month_start_date, month_arr) = dm_tup
        month_end_date = month_start_date + relativedelta(months=+1) - relativedelta(days=1)

        # get how many total days there are in the series.
        month_delta = month_end_date - month_start_date
        days_in_month = month_delta.days

        print 'month start date \n {} \n month end date \n {}'.format(month_start_date, month_end_date)

        # for all the days in the month, accumulate to the monthly array
        current_date = month_start_date
        for i in range(days_in_month + 1):

            # todo, print the date as a string for every date in the series
            # todo, then print the date as year and julian date
            print 'current date: ', ndvi_name.format(current_date.year, current_date.month, current_date.day)
            ndvi_loc = ndvi_name.format(current_date.year, current_date.month, current_date.day)

            current_date_tup = current_date.timetuple()
            current_year = current_date.year
            julian_date = current_date_tup.tm_yday
            print 'current year and J date: ', refet_name.format(current_year, julian_date)
            refet_loc = refet_name.format(current_year, julian_date)

            # TODO - calculate ETA

            # read in ndvi and ref et
            ndvi_arr, transform, dim, proj, dt = raster_extract(os.path.join(ndvi_path, '{}'.format(current_year),
                                                                             ndvi_loc))
            refet_arr, transform, dim, proj, dt = raster_extract(os.path.join(etrf_path, 'PM{}'.format(current_year),
                                                                              refet_loc))
            # calculate the eta === See Allen, Irmak and Trezza (2011) ====
            eta_arr = (1.25 * ndvi_arr) * refet_arr

            month_arr += eta_arr
            # TODO - accumulate ETA to monthly array

            # on the last day of the month output the array as a raster.
            if current_date == month_end_date:
                name = 'cum_allen_et_{}_{}.tif'.format(current_year, current_date.month)
                write_raster(month_arr, transform, output_path, name, dim, proj, dt)

            current_date += relativedelta(days=+1)

def run_W_E(monthly_et_path, monthly_precip_path, output_folder, date_specs, precip_name, et_name, label):
    """

    :return:
    """

    # function to calculate the depletion at a monthly timestep
    #  within that function, output the running depletion raster that results from each month's F_in-F_out
    (start_day, start_month, start_year, end_day, end_month, end_year) = date_specs
    start_date = datetime(start_year, start_month, start_day).date()
    end_date = datetime(end_year, end_month, end_day).date()

    months_in_series = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)



    # at each timestep, keep track of how negative the depletion has gotten
    depletion_ledger = np.zeros((2525, 2272), dtype=float)
    # initialize depletion counter at zero.
    depletion_counter = np.zeros((2525, 2272), dtype=float)
    # keep track of the maximum depletion map
    max_depletion = np.zeros((2525, 2272), dtype=float)
    # depletion_list = []
    total_et = np.zeros((2525, 2272), dtype=float)
    for i in range(months_in_series + 1):

        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(monthly_precip_path, precip_name.format(date.year, date.month))
        eta = os.path.join(monthly_et_path, et_name.format(date.year, date.month))

        print 'precip', precip
        print 'ssebop', eta

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        eta_arr, transform, dim, proj, dt = raster_extract(eta)

        total_et += eta_arr

        # oldmax = max_depletion

        # depletion for the current monthly timestep
        depletion_delta = depletion_calc(eta_arr, precip_arr)

        # add to the running depletion tally
        print depletion_delta.shape
        print depletion_counter.shape
        depletion_counter += depletion_delta
        depletion_ledger += depletion_delta

        # # for any values that become negative, make them zero. Assume runoff...Wang-Erlandsson (2016)
        # # todo - to ONLY allow positive depletions
        # depletion_counter[depletion_counter < 0.0] = 0.0

        # newmax_bool = [depletion_counter > max_depletion]
        # newmax = depletion_counter[newmax_bool == True]
        newmax = np.maximum(depletion_counter, max_depletion)

        max_depletion = newmax

        # print "is this messed up?", oldmax == newmax

        # for each monthly timestep, take the cumulative depletion condition and output it as a raster
        depletion_name = "{}_cumulative_depletion_{}_{}.tif".format(label, date.year, date.month)
        write_raster(depletion_counter, transform, output_folder, depletion_name, dim, proj, dt)

    # output the maximum depletion
    max_depletion_name = '{}_max_depletion_{}_{}.tif'.format(label, start_date.year, end_date.year)
    write_raster(max_depletion, transform, output_folder, max_depletion_name, dim, proj, dt)

    # output total SSEBop (to test wheter it looks like the netcdf file)
    total_ssebop_name = "{}_total_et_{}_{}.tif".format(label, start_date.year, end_date.year)
    write_raster(total_et, transform, output_folder, total_ssebop_name, dim, proj, dt)

    # output the average SSEBop (to test whether it looks like the netcdf file)
    average_ssebop = total_et/float(months_in_series)
    average_ssebop_name = "{}_average_et_{}_{}.tif".format(label, start_date.year, end_date.year)
    write_raster(average_ssebop, transform, output_folder, average_ssebop_name, dim, proj, dt)

def cumulative_eta_precip(precip_path, eta_path, precip_output, eta_output, date_specs, precip_name, et_name, label):
    """"""

    (start_day, start_month, start_year, end_day, end_month, end_year) = date_specs
    start_date = datetime(start_year, start_month, start_day).date()
    end_date = datetime(end_year, end_month, end_day).date()

    months_in_series = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)

    # These numpy arrays will hold the cumulative total
    total_precip = np.zeros((2525, 2272), dtype=float)
    total_eta = np.zeros((2525, 2272), dtype=float)

    for i in range(months_in_series + 1):

        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(precip_path, precip_name.format(date.year, date.month))
        eta = os.path.join(eta_path, et_name.format(date.year, date.month))

        print 'precip', precip
        print 'ssebop', eta

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        eta_arr, transform, dim, proj, dt = raster_extract(eta)

        # accumulate totals in the arrays
        total_eta += eta_arr
        total_precip += precip_arr

        ct_precip_name = "{}_ct_precip_{}_{}.tif".format(label, date.year, date.month)
        ct_eta_name = "{}_ct_eta_{}_{}.tif".format(label, date.year, date.month)

        # for the last raster, output to a different directory, which we want for another analysis.
        if ct_precip_name.endswith("ct_precip_2013_12.tif"): #todo don't hardcode
            precip_output = os.path.join(precip_output, 'terminal_cumulation')
            write_raster(total_precip, transform, precip_output, ct_precip_name, dim, proj, dt)
        else:
            write_raster(total_precip, transform, precip_output, ct_precip_name, dim, proj, dt)

        if ct_eta_name == "{}_ct_ssebop_2013_12.tif".format(label):  # todo don't hardcode
            eta_output = os.path.join(eta_output, 'terminal_cumulation')
            write_raster(total_precip, transform, precip_output, ct_precip_name, dim, proj, dt)
        else:
            write_raster(total_eta, transform, eta_output, ct_eta_name, dim, proj, dt)

if __name__ == '__main__':

    # # ==== For accumulating each month's total ETa in mm ====
    # ndvi_root = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/NDVI/NDVI'
    #
    # etrf_root = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/PM_RAD'
    #
    # eta_output_root = '/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/ETRM_cumulative_depletions_research/ndvi_WA/ndvi_based_eta'
    #
    # start_day = 1
    # end_day = 31
    # start_month = 1
    # end_month = 12
    # start_year = 2000
    # end_year = 2013
    #
    # date_specs = (start_day, start_month, start_year, end_day, end_month, end_year)
    #
    # generate_monthly_eta(ndvi_root, etrf_root, eta_output_root, date_specs)

    # # ======= Do WANG ANDERSON ======
    # # path to monthly ETa
    # monthly_et_path = "/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/" \
    #                   "ETRM_cumulative_depletions_research/ndvi_WA/ndvi_based_eta"
    # # path to monthly Prism
    # monthly_precip_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"
    #
    # # output path
    # # output_folder = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_depletions"
    # output_folder = "/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/" \
    #                   "ETRM_cumulative_depletions_research/ndvi_WA/ndvi_pos_neg"
    #
    # precip_name = "tot_precip_{}_{}.tif"
    # et_name = "cum_allen_et_{}_{}.tif"
    #
    # label = 'alfalfa_pos_neg'
    #
    # start_day = 1
    # end_day = 31
    # # NOTE: start on FEB of the start year
    # start_month = 2
    # end_month = 12
    # start_year = 2000
    # end_year = 2013
    #
    # date_specs = (start_day, start_month, start_year, end_day, end_month, end_year)
    #
    # run_W_E(monthly_et_path, monthly_precip_path, output_folder, date_specs, precip_name, et_name, label)


    # ===== Output cumulative eta and precip =====
    # main()

    # first we shall determine the ratio of the cumulative alfalfa ETa to the cumulative PRISM precip
    eta_dir = "/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/" \
              "ETRM_cumulative_depletions_research/ndvi_WA/ndvi_based_eta"
    prism_dir = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"

    eta_output_dir = "/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/ETRM_cumulative_depletions_research/ndvi_WA/cumulatives/cum_eta"
    precip_output_dir = "/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/ETRM_cumulative_depletions_research/ndvi_WA/cumulatives/cum_precip"
    precip_name = "tot_precip_{}_{}.tif"
    et_name = "cum_allen_et_{}_{}.tif"
    label = 'alfalfa'

    start_day = 1
    end_day = 31
    start_month = 2
    end_month = 12
    start_year = 2000
    end_year = 2013
    date_specs = (start_day, start_month, start_year, end_day, end_month, end_year)

    cumulative_eta_precip(precip_path=prism_dir, eta_path=eta_dir, precip_output=precip_output_dir,
                          eta_output=eta_output_dir, date_specs=date_specs, precip_name=precip_name, et_name=et_name, label=label)


