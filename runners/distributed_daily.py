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


def run(time_tuple, date_range, input_root, output_root):
    etrm = Processes(date_range, input_root, output_root)
    etrm.raster_managers_manager(date_range, input_root, time_tuple, save_specific_dates=True)
    etrm.run()


if __name__ == '__main__':
    start_year = 2013
    start_month = 12
    start_day = 30

    end_year = 2013
    end_month = 12
    end_day = 31

    hard_drive_path = os.path.join('/Volumes', 'Seagate Expansion Drive')
    inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')
    outputs_path = os.path.join(hard_drive_path, 'ETRM_Results')
    datetime_date = datetime(start_year, start_month, start_day).date()
    run(datetime_date, (datetime(start_year, start_month, start_day),
         datetime(end_year, end_month, end_day)),
        inputs_path,
        outputs_path)

# ============= EOF =============================================
