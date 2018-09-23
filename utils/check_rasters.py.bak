# ===============================================================================
# Copyright 2016 dgketchum
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
The purpose of this module is to check standardized raster ETRM inputs for bad data.

this module provides (1) function -- check_rasters.

dgketchum 9 Sept 2016
"""

import os
from recharge.dynamic_raster_finder import get_penman, get_prism, get_kcb
from dateutil import rrule
from datetime import datetime
from numpy import where, zeros

simulation_period = datetime(2000, 1, 1), datetime(2002, 2, 25)


def check_rasters(ndvi, prism, penman, period):
    roots = [ndvi, prism, penman]
    total = 0.0
    for day in rrule.rrule(rrule.DAILY, dtstart=period[0], until=period[1]):

        # print ''
        print 'day : {}'.format(day)
        ndvi = get_kcb(roots[0], day)
        # print 'type = {}'.format(type(ndvi))
        print 'ndvi: min = {} max = {}, mean = {}'.format(ndvi.min(), ndvi.max(), ndvi.mean())
        # pm = get_penman(roots[2], day)
        # # print 'pm: min = {} max = {}, mean = {}'.format(pm.min(), pm.max(), pm.mean())
        # sum = (pm.sum() / 1000) * (250 ** 2) / 1233.48
        # print 'sum precip = {:.2e}'.format(sum)
        # if abs(sum) > 1.0e+7:
        #     print 'high pm on {}: {:.2e} AF'.format(day.strftime('%Y-%m-%d'), sum)
        #     print ''

        # ppt = get_prism(roots[1], day, variable='precip')
        # ppt = where(ppt < 0.0, zeros(ppt.shape), ppt)
        # sum = (ppt.sum() / 1000) * (250 ** 2) / 1233.48
        # total += sum
        # # print 'sum precip = {:.2e}'.format(sum)
        # if sum > 1.0e+7:
        #     print ''
        #     print 'high precip on {}: {:.2e} AF'.format(day.strftime('%Y-%m-%d'), sum)
        # print 'ppt: min = {} max = {}, mean = {}'.format(ppt.min(), ppt.max(), ppt.mean())
        # min_temp = get_prism(roots[1], day, variable='min_temp')
        # print 'min_temp: min = {} max = {}, mean = {}'.format(min_temp.min(), min_temp.max(), min_temp.mean())
        # max_temp = get_prism(roots[1], day, variable='max_temp')
        # print 'max_temp: min = {} max = {}, mean = {}'.format(max_temp.min(), max_temp.max(), max_temp.mean())
        # dct = {'ndvi': ndvi, 'pm': pm, 'ppt': ppt, 'min_temp': min_temp, 'max_temp': max_temp}
        # for key, item in dct.iteritems():
    # print 'total precip: {}'.format(total)

if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    dynamic_inputs_path = os.path.join('F:\\', 'ETRM_Inputs')
    ppt_path = os.path.join(dynamic_inputs_path, 'NDVI', 'NDVI_std_all')
    prism_path = os.path.join(dynamic_inputs_path, 'PRISM')
    penman_path = os.path.join(dynamic_inputs_path, 'PM_RAD')
    check_rasters(ppt_path, prism_path, penman_path, simulation_period)

# ============= EOF =============================================

