# ===============================================================================
# Copyright 2019 Jan Hendrickx and Gabriel Parrish
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
from datetime import datetime, timedelta
# ============= standard library imports ========================

prism_directory = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_inputs/' \
                  'wjs_aoi/PRISM/precip/800m_std_all_original'

first_day = 'precip_20000101.tif'

output_directory = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_inputs/' \
                   'wjs_aoi/PRISM/precip/800m_std_all'

for f in os.listdir(prism_directory):

    if f == first_day:
        print '*******'
        print 'do not do this one'
        print '*******'

    else:

        # chop up de stringy
        fname = f.split('_')[1]
        datestring = fname.split('.')[0]
        print '====='
        print 'old datestirng {}'.format(datestring)

        # make into a datetime operation for ease of operations.
        f_dt = datetime.strptime(datestring, '%Y%m%d')

        # subtract a day
        new_dt = f_dt - timedelta(days=1)

        # new filename
        new_fname = 'precip_{}{:02d}{:02d}.tif'.format(new_dt.year, new_dt.month, new_dt.day)
        print 'new fname', new_fname

        os.rename(os.path.join(prism_directory, f), os.path.join(output_directory, new_fname))


