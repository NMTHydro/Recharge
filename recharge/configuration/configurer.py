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
# ============= local library imports  ==========================
from recharge.configuration.config import CMBConfiguration, AmerifluxConfiguration


class BaseConfigurer:
    def get_configuration(self):
        kind = self._get_kind()
        if kind == 'cmb':
            cfg = CMBConfiguration()
        else:
            cfg = AmerifluxConfiguration()

        cfg.simulation_period = self._get_simulation_period()
        cfg = self._get_configuration(cfg)
        return kind, cfg

    # private
    def _get_kind(self):
        raise NotImplementedError

    def _get_simulation_period(self):
        raise NotImplementedError

    def _get_configuration(self, cfg):
        raise NotImplementedError

# ============= EOF =============================================
