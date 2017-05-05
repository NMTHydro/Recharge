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


def run():
    cfg = Config()
    etrm = Processes(cfg)
    etrm.set_save_dates(cfg.save_dates)
    etrm.run(ro_reinf_frac=0.0, rew_ceff=1.0, evap_ceff=1.0)


if __name__ == '__main__':
    run()


# ============= EOF =============================================
