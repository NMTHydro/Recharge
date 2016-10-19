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
from numpy import array, set_printoptions
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

FACTORS = ['Temperature', 'Precipitation', 'Reference ET', 'Total Water Storage (TAW)',
           'Vegetation Density (NDVI)', 'Soil Ksat']


def make_tornado_plot(dataframe, factors, show=False, fig_path=None):
    dfs = os.listdir(dataframe)
    print 'pickled dfs: {}'.format(dfs)
    filename = 'norm_sensitivity.pkl'
    if filename in dfs:

        df = read_pickle(os.path.join(dataframe, filename))
        df.to_csv(os.path.join(fig_path, 'sample_df.csv'))
        print df
        xx = 1

        for index, row in dataframe.iterrows():
            print index, row
            base = row[0][5]
            lows = []
            for fact in row:
                lows.append(min(fact))
            lows = array(lows)
            values = []
            for fact in row:
                values.append(max(fact))

            # The y position for each variable
            ys = range(len(values))[::-1]  # top to bottom

            # Plot the bars, one by one
            for y, low, value in zip(ys, lows, values):
                # The width of the 'low' and 'high' pieces
                low_width = base - low
                high_width = value - base
                # Each bar is a "broken" horizontal bar chart
                plt.broken_barh(
                    [(low, low_width), (base, high_width)],
                    (y - 0.4, 0.8),
                    facecolors=['white', 'white'],  # Try different colors if you like
                    edgecolors=['black', 'black'],
                    linewidth=1)
                plt.subplots_adjust(left=0.32)

                # Display the value as text. It should be positioned in the center of
                # the 'high' bar, except if there isn't any room there, then it should be
                # next to bar instead.
                x = base + high_width / 2
                if x <= base:
                    x = base + high_width
                plt.text(x, y, str(round(value - low, 1)) + 'mm', va='center', ha='center')

            # Draw a vertical line down the middle
            plt.axvline(base, color='black')

            # Position the x-axis on the top, hide all the other spines (=axis lines)
            axes = plt.gca()  # (gca = get current axes)
            axes.spines['left'].set_visible(False)
            axes.spines['right'].set_visible(False)
            axes.spines['bottom'].set_visible(False)
            axes.xaxis.set_ticks_position('top')

            # Make the y-axis display the factors
            plt.yticks(ys, factors)
            plt.title('Calculated Recharge Ranges at {} (mm)'.format(index.replace('_', ' ')), y=1.05)
            # Set the portion of the x- and y-axes to show
            plt.xlim(min(-20, 1.2 * min(lows)), base + 1.1 * max(values))
            plt.ylim(-1, len(factors))
            # plt.show()
            if show:
                plt.show()
            if fig_path:
                plt.savefig('{}_tornado'.format(index), fig_path, ext='jpg', dpi=500, close=True, verbose=True)
            plt.close()


if __name__ == '__main__':
    root = os.path.join('F:\\', 'ETRM_Inputs')
    sensitivity = os.path.join(root, 'sensitivity_analysis')
    pickles = os.path.join(sensitivity, 'pickled')
    figure_save_path = os.path.join(sensitivity, 'figures')
    make_tornado_plot(pickles, FACTORS, fig_path=figure_save_path, show=True)


# ==========================  EOF  ==============================================
