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
    kind = None

    def _get_kind(self):
        if self.kind is None:
            while 1:
                kind = raw_input('Model Kind [cmb]: ')
                if not kind:
                    kind = 'cmb'

                if kind not in ('cmb', 'ameriflux'):
                    print 'invalid kind "{}". Use either "cmb" or "ameriflux"'.format(kind)
                else:
                    break

        self.kind = kind
        return kind

    def _get_simulation_period(self):
        # need to handle invalid data formats
        start_date = raw_input('Start date, format YYYY/MM/DD [2007/01/01]: ')
        if not start_date:
            start_date = '2007/01/01'

        end_date = raw_input('End date, format YYYY/MM/DD [2013/12/29]: ')
        if not end_date:
            end_date = '2013/12/29'
        start_date = datetime(*(map(int, start_date.split('/'))))
        end_date = datetime(*(map(int, end_date.split('/'))))
        return start_date, end_date

    def _get_configuration(self, cfg):
        # allow user to modify default configuration here
        return cfg

# ============= EOF =============================================
