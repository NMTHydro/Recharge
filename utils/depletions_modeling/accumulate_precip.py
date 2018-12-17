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
import os
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# ============= local library imports ===========================
from utils.depletions_modeling.cumulative_depletions import raster_extract, write_raster

def generate_monthly_precip(precip_path, output_path, date_specs):
    """
    generates monthly cumulative ETa based on ETa = [(1.25 * NDVI_PyRana) * ETrF_gadget]
    :param precip_path:
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
            ndvi_arr, transform, dim, proj, dt = raster_extract(os.path.join(precip_path, '{}'.format(current_year),
                                                                             ndvi_loc))

            month_arr += eta_arr
            # TODO - accumulate ETA to monthly array

            # on the last day of the month output the array as a raster.
            if current_date == month_end_date:
                name = 'cum_allen_et_{}_{}.tif'.format(current_year, current_date.month)
                write_raster(month_arr, transform, output_path, name, dim, proj, dt)

            current_date += relativedelta(days=+1)