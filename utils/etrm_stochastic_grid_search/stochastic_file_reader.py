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
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# ============= standard library imports ========================

def fubar_date_get(filenames):
    dates = [date(int(os.path.split(name)[1].split('.')[0].split('_')[-3]),
                  int(os.path.split(name)[1].split('.')[0].split('_')[-2]),
                  int(os.path.split(name)[1].split('.')[0].split('_')[-1])) for name in filenames]

    return dates


if __name__ == "__main__":

    site = 'ses'
    stochastic_file_root = '/Volumes/Seagate_Expansion_Drive/calibration_approach/mini_model_outputs/{}'.format(site)
    var = 'eta'
    taw = '425'

    filename = '{}_taw_{}.csv'.format(var, taw)

    filepath = os.path.join(stochastic_file_root, filename)

    site_df = pd.read_csv(filepath, header=0)

    print 'site df \n', site_df


    # filenames = site_df['seed0file']
    #
    # # making a date object from the filename
    # dates = [date(int(os.path.split(name)[1].split('.')[0].split('_')[-3]),
    #               int(os.path.split(name)[1].split('.')[0].split('_')[-2]),
    #               int(os.path.split(name)[1].split('.')[0].split('_')[-1])) for name in filenames]
    # # for name in filenames:
    # #     d = os.path.split(name)[1]
    # #     n = d.split('.')[0]
    # #     nlist = n.split('_')
    # #
    # #     ndate = date(int(nlist[-3]), int(nlist[-2]), int(nlist[-1]))

    seed0dates = fubar_date_get(site_df['seed0file'])

    print 'dates \n', seed0dates

    print site_df.keys()

    seed0data = site_df[' seed0val']

    seed1dates = fubar_date_get(site_df[' seed0date'])
    seed1data = site_df[' seed1file']

    seed2dates = fubar_date_get(site_df[' seed1val'])
    seed2data = site_df[' seed1date']

    plt.plot_date(seed0dates, seed0data, color='blue')
    plt.plot(seed0dates, seed0data, color='blue')

    plt.plot_date(seed1dates, seed1data, color='green')
    plt.plot(seed1dates, seed1data, color='green')

    plt.plot_date(seed2dates, seed2data, color='red')
    plt.plot(seed2dates, seed2data, color='red')


    plt.show()


    #============================ TEST cumulative ============================



