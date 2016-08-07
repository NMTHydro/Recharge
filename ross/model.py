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
import logging
import os
import time
from datetime import datetime

# ============= local library imports  ==========================
import yaml

from ross.etrm_funcs import InvalidDataSourceException


class BaseModel:
    _start = None
    _end = None
    _start_month = None
    _end_month = None

    _runtime = None
    cfg = None

    _verbose = False

    def run(self, config_path, verbose=False):
        logging.info('=================== RUN ===================')
        cfg = self.config(config_path, verbose)
        if not cfg:
            logging.warning('Failed to configure model')
            return
        else:
            self.report_config(cfg)

        try:
            if not self.initialize():
                logging.warning('Failed to initialize model')
                return
        except InvalidDataSourceException:
            logging.warning('**** MODEL FAILED. Not all data was located ****')
            return

        st = time.time()
        self.run_model()
        self._runtime = time.time() - st

        logging.info('Model Completed Successfully')
        self.report_results()

    def run_model(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

    def config(self, path, verbose):
        """
        Configure the model

        :return:
        """
        self._verbose = verbose

        if os.path.isfile(path):
            with open(path, 'r') as rfile:
                cfg = yaml.load(rfile)
        else:
            logging.warning('************************************')
            logging.info('Failed locating configuration')
            ret = raw_input('Would you like to continue with default configuration? [y]/n >> ')
            if ret not in ('\n', '', 'y'):
                return
            cfg = self._default_config()

        if cfg:
            try:
                self._load_config(cfg)
                return cfg
            except KeyError, e:
                logging.warning('Invalid configuration: {}'.format(e))
                return

    def report_results(self):
        logging.info('=============== Model Results ===============')
        logging.info('Run Time (m): {}'.format(self._runtime / 60.))
        logging.info('=============================================')

    def report_config(self, cfg):
        logging.info('=============== Model Configuration ===============')
        for k, v in cfg.iteritems():
            logging.info('{:<20s}= {}'.format(k, v))
        logging.info('===================================================')

    # private
    def _default_config(self):
        pass

    def _load_config(self, cfg):
        pass

    def _load_start_end(self, cfg):
        try:
            y, m, d = map(int, cfg['start'].split('-'))
        except ValueError, e:
            logging.warning('Invalid start date "{}". error={}'.format(cfg['start'], e))
            return

        self._start = start = datetime(y, m, d)
        try:
            y, m, d = map(int, cfg['start'].split('-'))
        except ValueError, e:
            logging.warning('Invalid start date "{}". error={}'.format(cfg['start'], e))
            return

        self._end = datetime(y, m, d)

        sm = int(cfg['start_month'])
        self._start_month = datetime(start.year, sm, 1).timetuple().tm_yday
        em = int(cfg['end_month'])
        self._end_month = datetime(start.year, em, 1).timetuple().tm_yday
# ============= EOF =============================================
