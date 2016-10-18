# ===============================================================================
# Copyright 2016 ross
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
import yaml
# ============= local library imports  ==========================

from recharge.configuration.configurer import BaseConfigurer


class YAMLConfigurer(BaseConfigurer):
    def __init__(self, p):
        if os.path.isfile(p):
            with open(p, 'r') as rfile:
                self._yd = yaml.load(rfile)
        else:
            print 'invalid file: {}'.format(p)

    def _get_kind(self):
        return self._yd['kind']

    def _get_simulation_period(self):
        return self._yd['start_date'], self._yd['end_date']

    def _get_configuration(self, cfg):
        return cfg

# ============= EOF =============================================
