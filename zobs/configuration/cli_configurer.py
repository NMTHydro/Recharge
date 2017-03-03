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
from datetime import datetime

from recharge.configuration.configurer import BaseConfigurer


class CLIConfigurer(BaseConfigurer):

    def _get_kind(self):
        kind = self.kind
        if kind is None:
            kind = raw_input('Model Kind [cmb]: ')
        self.kind = kind
        return kind

    def _get_start_date(self):
        start_date = self._start_date
        if start_date is None:
            start_date = raw_input('Start date, format YYYY/MM/DD [2007/01/01]: ')

        self._start_date = start_date
        return start_date

    def _get_end_date(self):
        end_date = self._end_date
        if end_date is None:
            end_date = raw_input('End date, format YYYY/MM/DD [2013/12/29]: ')

        self._end_date = end_date
        return end_date

    def _get_configuration(self, cfg):
        # allow user to modify default configuration here
        return cfg

# ============= EOF =============================================
