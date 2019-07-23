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
import pandas as pd
import numpy as np
# ============= standard library imports ========================

"""This script will average the stochastic file outputs across different runs. The average run will be created. Also,
 Other datasets time-series will be extracted so that the calibration can happen."""


def df_averager(df, runs):
    """"""
    print 'averaging df cols for each stochastic run'
    # to add totals
    count = 0
    sum_arr = np.zeros(df['seed0val'].shape)
    for i in range(runs):
        print 'seed {}'.format(i)
        colname = 'seed{}val'.format(i)

        vals = df[colname]

        sum_arr += vals

        count += 1

    avg_arr = sum_arr / count
    return avg_arr



if __name__ == "__main__":

    #### ====== Bit of Code to average sorted stochastic runs in csvs
    stochastic_root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/ses/stochastic_csvs/not_averaged'
    output_root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs/ses/stochastic_csvs/averaged'

    runs = 6

    dir_list = os.listdir(stochastic_root)

    for f in dir_list:
        fname = f.split('.')[0]
        varname = fname.split('_')[0]
        filepath = os.path.join(stochastic_root, f)

        file_df = pd.read_csv(filepath, header=0)

        avg_arr = df_averager(file_df, runs)

        file_df['average_vals_{}'.format(varname)] = avg_arr

        outname = '{}_average.csv'.format(fname)

        outpath = os.path.join(output_root, outname)

        file_df.to_csv(outpath)

    # print 'not finished'
    #
    # ### TODO - Add code to extract all the necessary datasets for calibration and figure making to be saved to the same .csv
    #
    # """Get PRISM, Ameriflux ET, Ameriflux soil moisture, AMERIFLUX precip, GADGET refET AND all 4 ETRM datasets side
    # by side for a given TAW and put em in the same csv for later reference."""

