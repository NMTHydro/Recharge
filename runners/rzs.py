# ===============================================================================
# Copyright 2017 ross
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

from recharge.raster_tools import rzs_mapper


def run():
    # ------PATHS-------

    output_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    hard_drive_path = os.path.join('/', 'Volumes', 'Seagate Expansion Drive')

    inputs_path = os.path.join(hard_drive_path, 'ETRM_inputs')
    tiff_root = os.path.join(hard_drive_path, 'ETRM_results', 'ETRM_Results_2017_03_13', 'daily_rasters')

    # -----dates-----
    # ----TIFFS----

    # tiff_list = ['de_27_12_2013.tif', 'dr_27_12_2013.tif', 'drew_27_12_2013.tif']
    # tiff_frame = tiff_framer(tiff_root, mask_path, tiff_list, tiff_path)

    # ---- TAW ----------
    # taw_df, taw_data_dict = taw_func(inputs_path)

    # ----- Take Stock ----
    # tiff_frame.to_excel('/Users/Gabe/Desktop/tiff_frame.xls')
    # taw_df.to_excel('/Users/Gabe/Desktop/taw_df.xls')

    # ------ RZSM = 1- (D/TAW) -------
    # rzsm_mapper(tiff_frame, taw_df, inputs_path)

    de = os.path.join(tiff_root, 'de_27_12_2013.tif')
    dr = os.path.join(tiff_root, 'dr_27_12_2013.tif')
    drew = os.path.join(tiff_root, 'drew_27_12_2013.tif')
    mask = os.path.join(inputs_path, 'Mask', 'zuni_1.tif')

    # set these paths
    taw_path = ''
    taw_unmod_path = ''

    rzs_mapper(output_path, taw_path, taw_unmod_path, de, dr, drew, mask)


if __name__ == '__main__':
    run()
# ============= EOF =============================================
