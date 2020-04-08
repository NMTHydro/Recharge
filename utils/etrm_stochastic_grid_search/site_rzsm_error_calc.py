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
import math
# ============= standard library imports ========================


def calc_rzsm_error(sitename, error):
    """"""

    print 'calculating error for {}'.format(sitename)
    if sitename == 'vcp' or sitename == 'vcm':

        shallow_flight = 80.0
        middle_flight = 170.0
        deep_flight = 300.0

        soil_depth = (shallow_flight + middle_flight + deep_flight)

        shallow_frac = shallow_flight / soil_depth
        mid_frac = middle_flight / soil_depth
        deep_frac = deep_flight / soil_depth

        # Add the errors in quadradure assuming each probe is independent
        # sqrt(((1/3)s1)^2+((2/3)s2)^2)

        absolute_error = math.sqrt(((error * shallow_frac)**2) + ((error * mid_frac)**2) + ((error * deep_frac)**2))


    elif sitename == 'wjs':

        shallow_flight = 80.0
        middle_flight = 170.0
        deep_flight = 200.0

        soil_depth = (shallow_flight + middle_flight + deep_flight)

        shallow_frac = shallow_flight / soil_depth
        mid_frac = middle_flight / soil_depth
        deep_frac = deep_flight / soil_depth

        # Add the errors in quadradure assuming each probe is independent
        # sqrt(((1/3)s1)^2+((2/3)s2)^2)

        absolute_error = math.sqrt(((error * shallow_frac) ** 2) + ((error * mid_frac) ** 2) + ((error * deep_frac) ** 2))

    elif sitename == 'mpj':

        shallow_flight = 80.0
        middle_flight = 70.0
        deep_flight = 200.0

        soil_depth = (shallow_flight + middle_flight + deep_flight)

        shallow_frac = shallow_flight / soil_depth
        mid_frac = middle_flight / soil_depth
        deep_frac = deep_flight / soil_depth

        # Add the errors in quadradure assuming each probe is independent
        # sqrt(((1/3)s1)^2+((2/3)s2)^2)

        absolute_error = math.sqrt(((error * shallow_frac) ** 2) + ((error * mid_frac) ** 2) + ((error * deep_frac) ** 2))

    elif sitename == 'ses' or sitename == 'seg':

        shallow_flight = 80.0
        middle_flight = 170.0
        deep_flight = 300.0

        soil_depth = (shallow_flight + middle_flight + deep_flight)

        shallow_frac = shallow_flight / soil_depth
        mid_frac = middle_flight / soil_depth
        deep_frac = deep_flight / soil_depth

        # Add the errors in quadradure assuming each probe is independent
        # sqrt(((1/3)s1)^2+((2/3)s2)^2)

        absolute_error = math.sqrt(((error * shallow_frac) ** 2) + ((error * mid_frac) ** 2) + ((error * deep_frac) ** 2))

    return absolute_error
