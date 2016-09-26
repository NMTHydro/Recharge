# ===============================================================================
# Copyright 2016 gabe_parrish
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
# =============================================================================== #
"""
The purpose of this module is to check #####

this module provides (1) function -- check_rasters.

dgketchum 9 Sept 2016
"""

#import os
#from dateutil import rrule
#from datetime import datetime # this is a robust formatting function

import numpy

import pandas

from recharge.dynamic_raster_finder import get_prism()


def landsat_analysis(period):

    for day in rrule.rrule(rrule.DAILY, dtstart=period[0], until=period[1]):
        # find good landsat images
        pass

if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    dynamic_inputs_path = os.path.join('F:\\', 'ETRM_Inputs')
    simulation_period = datetime(2013, 1, 1), datetime.now()
    landsat_analysis = ()

# ============= EOF =============================================

