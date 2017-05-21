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
import os
from datetime import datetime
from recharge.etrm_processes import Processes
from app.config import Config


def dist_daily_run():
    cfg = Config()
    etrm = Processes(cfg)
    etrm.set_save_dates(cfg.save_dates)
    etrm.run(ro_reinf_frac=0.0, rew_ceff=1.0, evap_ceff=1.0)

def dist_daily_taw_run():
    cfg2 = Config()
    cfg2.load()
    etrm2 = Processes(cfg2)
    etrm2.set_save_dates(cfg2.save_dates)
    etrm2.modify_taw(cfg2.taw_modification)
    etrm2.run()

if __name__ == '__main__':
    dist_daily_taw_run()

# ============= EOF =============================================
