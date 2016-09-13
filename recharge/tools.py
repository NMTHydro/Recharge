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


def millimeter_to_acreft(param):
    return '{:.2e}'.format((param.sum() / 1000) * (250**2) / 1233.48)


def save_master_tracker(tracker, raster_out_root):

    csv_path_filename = os.path.join(raster_out_root, 'etrm_master_tracker.csv')
    print 'this should be your master tracker csv: {}'.format(csv_path_filename)
    tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')

    return None


if __name__ == '__main__':
    pass

# =================================== EOF =========================
