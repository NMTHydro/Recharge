# ===============================================================================
# Copyright 2016 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance
# with the License.
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

# =================================IMPORTS=======================================
import os
import matplotlib.pyplot as plt
from matplotlib import rc
from numpy import linspace, array, add, multiply, set_printoptions
from pandas import read_pickle, set_option, options


def round_to_value(number, roundto):
    return round(number / roundto) * roundto


rc('mathtext', default='regular')

set_option('display.max_rows', None)
set_option('display.max_columns', None)
set_option('display.width', None)
set_option('display.precision', 3)
options.display.float_format = '${:,.2f}'.format
set_printoptions(threshold=3000, edgeitems=5000, precision=3)
set_option('display.height', None)
set_option('display.max_rows', None)

TEMPS = range(-5, 6)
ALL_PCT = [x * 0.1 for x in range(5, 16)]
ndvi_range = linspace(0.9, 1.7, 11)

NDVI_RANGE = array([round_to_value(x, 0.05) for x in ndvi_range])


def make_spider_plot(dataframe, ndvi, all_pct, temps, fig_path=None, show=False):
    display_pct = [(int(x)) for x in add(multiply(all_pct, 100.0), -100)]

    dfs = os.listdir(dataframe)
    print 'pickled dfs: {}'.format(dfs)
    filename = '_basic_sensitivity_2.pkl'
    if filename in dfs:
        df = read_pickle(os.path.join(dataframe, filename))
        df.to_csv(os.path.join(fig_path, 'sample_df_basic_2.csv'))
        pass
        print df
        xx = 1
        for index, row in df.iterrows():
            fig = plt.figure(xx, figsize=(20, 10))
            ax1 = fig.add_subplot(111)
            ax2 = ax1.twiny()
            ax3 = ax1.twiny()
            fig.subplots_adjust(bottom=0.2)
            print 'shape temps: {}, shape row[0]: {}'.format(len(temps), len(row[0]))
            ax2.plot(temps, row[0], 'black', label='Temperature (+/- 5 deg C)', marker='8')
            ax1.plot(display_pct, row[1], 'blue', label='Precipitation (+/- 50%)', marker='8')
            ax1.plot(display_pct, row[2], 'purple', label='Reference Evapotranspiration (+/- 50%)', marker='8')
            ax1.plot(display_pct, row[3], 'brown', label='Total Available Water (+/- 50%)', marker='8')
            ax3.plot(ndvi, row[4], 'green', linestyle='-.', label='Normalized Density Vegetation\n'
                                                                  ' Index Conversion Factor (0.9 - 1.8)', marker='8')
            ax1.plot(display_pct, row[5], 'red', label='Soil Hydraulic Conductivity (+/- 50%)', marker='8')
            ax1.set_xlabel(r"Parameter Change (%)", fontsize=16)
            ax1.set_ylabel(r"Total Recharge in 14-Year Simulation (mm)", fontsize=16)

            ax2.set_xlabel(r"Temperature Change (C)", fontsize=16)
            ax2.xaxis.set_ticks_position("bottom")
            ax2.xaxis.set_label_position("bottom")
            ax2.spines["bottom"].set_position(("axes", -0.15))
            ax2.set_frame_on(True)
            ax2.patch.set_visible(False)
            for sp in ax2.spines.itervalues():
                sp.set_visible(False)
            ax2.spines['bottom'].set_visible(True)

            ax3.set_xlabel(r"NDVI to Crop Coefficient Conversion Factor", fontsize=16)
            ax3.xaxis.set_ticks_position("top")
            ax3.xaxis.set_label_position("top")
            # ax3.spines["top"].set_position(("axes", 1.0))
            ax3.set_frame_on(True)
            ax3.patch.set_visible(False)
            for sp in ax3.spines.itervalues():
                sp.set_visible(False)
            ax3.spines['top'].set_visible(True)
            plt.title('Variation of ETRM Pysical Parameters at {}'.format(str(index).replace('_', ' ')),
                      y=1.08, fontsize=20)
            handle1, label1 = ax1.get_legend_handles_labels()
            handle2, label2 = ax2.get_legend_handles_labels()
            handle3, label3 = ax3.get_legend_handles_labels()
            handles, labels = handle1 + handle2 + handle3, label1 + label2 + label3
            ax1.legend(handles, labels, loc=0)
            if show:
                plt.show()
            # if fig_path:
            #     plt.savefig(os.path.join(fig_path, '{}_spider'.format(index)), dpi=600, ext='jpg', close=True,
            #                 verbose=True)
            plt.close(fig)


if __name__ == '__main__':
    root = os.path.join('F:\\', 'ETRM_Inputs')
    sensitivity = os.path.join(root, 'sensitivity_analysis')
    pickles = os.path.join(sensitivity, 'pickled')
    figure_save_path = os.path.join(sensitivity, 'figures')
    make_spider_plot(pickles, NDVI_RANGE, ALL_PCT, TEMPS, figure_save_path, show=True)


# ==========================  EOF  ==============================================
