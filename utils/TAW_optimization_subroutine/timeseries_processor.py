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
import pandas
# ============= standard library imports ========================


"""Functions that manipulate timeseries using Pandas"""

def accumulator(time_df, time_unit='days', cum_int=1):
    """

    :param time_df: datetime indexed pandas dataframe
    :param time_unit: string - either hours, days, months, years
    :param cum_int: interger of number of time units to be accumulated
    :return:
    """

    # todo - make for hours months and years (only handles days RN)

    if time_unit == 'days':

        # res_df = time_df.resample('{}D'.format(cum_int), label='left').sum()
        res_df = time_df.resample('{}D'.format(cum_int), label='right').sum()

        return res_df

    else:
        print 'please specify either days, hours, months, years'