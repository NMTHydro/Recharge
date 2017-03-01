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
import time


def add_extension(p, ext='.txt'):
    if not p.endswith(ext):
        p = '{}{}'.format(p, ext)
    return p


def millimeter_to_acreft(param):
    return '{:.2e}'.format((param.sum() / 1000) * (250**2) / 1233.48)


def save_master_tracker(tracker, raster_out_root):

    csv_path_filename = os.path.join(raster_out_root, 'etrm_master_tracker.csv')
    print 'this should be your master tracker csv: {}'.format(csv_path_filename)
    tracker.to_csv(csv_path_filename, na_rep='nan', index_label='Date')


def unique_path(root, base, extension):
    """
    simple function for getting a unique path in a given directory

    very simplistic should not be heavily relied upon without modification

    :param root:
    :param base:
    :param extension:
    :return:
    """
    cnt = 0
    while 1:
        path = os.path.join(root, '{}-{:04n}{}'.format(base, cnt, extension))
        if not os.path.isfile(path):
            return path
        cnt += 1


def time_it(func, *args, **kw):
    print '######### {:<30s} STARTED'.format(func.func_name)
    st = time.time()
    ret = func(*args, **kw)
    print '######### {:<30s} execution time={:0.3f}'.format(func.func_name, time.time() - st)
    return ret


# =================================== EOF =========================
