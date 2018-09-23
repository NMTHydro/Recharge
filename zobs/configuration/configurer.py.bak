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
import re

from datetime import datetime

import sys

from recharge.configuration.config import CMBConfiguration, AmerifluxConfiguration


class BaseConfigurer:
    kind = None
    start_date = None
    end_date = None
    user_interaction = True

    def get_configuration(self):
        print '--------------- {} Get Configuration---------------'.format(self.__class__.__name__)
        while 1:
            kind = self._get_kind()
            if kind is None:
                kind = 'cmb'

            if self._validate_kind(kind):
                print 'kind = {}'.format(kind)
                break
            else:
                if not self.user_interaction:
                    print 'failed to get configuration. could not get valid kind. kind={}'.format(kind)
                    sys.exit(1)

        if kind == 'cmb':
            cfg = CMBConfiguration()
        else:
            cfg = AmerifluxConfiguration()

        while 1:
            start = self._get_start_date()
            if self._validate_date_format(start):
                print 'start date = {}'.format(start)
                break
            if not self.user_interaction:
                print 'failed to get configuration. could not get valid start date. "{}"'.format(start)
                sys.exit(1)

        while 1:
            end = self._get_end_date()
            if self._validate_date_format(end):
                print 'end date = {}'.format(end)
                break
            if not self.user_interaction:
                print 'failed to get configuration. could not get valid end date. "{}"'.format(end)
                sys.exit(1)

        cfg.simulation_period = self._get_simulation_period(start, end)

        cfg = self._get_configuration(cfg)

        cfg.print_config()
        return kind, cfg

    # private
    def _validate_date_format(self, d):
        return bool(re.match(r'\d\d\d\d/\d\d/\d\d', d))

    def _validate_kind(self, kind):
        return kind in ('cmb', 'ameriflux')

    def _get_simulation_period(self, s, e):
        start_date = datetime(*(map(int, s.split('/'))))
        end_date = datetime(*(map(int, e.split('/'))))
        return start_date, end_date

    def _get_kind(self):
        raise NotImplementedError

    def _get_start_date(self):
        raise NotImplementedError

    def _get_end_date(self):
        raise NotImplementedError

    def _get_configuration(self, cfg):
        raise NotImplementedError

# ============= EOF =============================================
