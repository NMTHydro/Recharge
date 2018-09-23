# ===============================================================================
# Copyright 2016 gabe-parrish
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

# ============= standard library imports ========================
import os
import rasterio
from rasterio import windows
import numpy as np
from numpy import meshgrid, arange
from affine import Affine
from pyproj import Proj, transform
from utils.pixel_coord_finder import coord_getter
from recharge.raster_tools import convert_raster_to_array, convert_array_to_raster
import seaborn as sns
import matplotlib.pyplot as plt
import multiprocessing as mp
from utils.tracker_plot import grapher, get_columns
import pandas as pd

# ============= local library imports ===========================


def data_frame_formatter(raster_dictionary):

    """

    :param raster_dictionary:
    :return: saved csvs

    Each raster will get written into a dict with certain info, then the dict will get turned into a
    dataframe and the dataframes will all get merged into one. This will then be exported and saved as a csv.
    Cool? Cool.

    dict = {column heading : [list of values]}

    cols = x(easting), y(northing), nlcd, ETrF, NDVI

    """

    ras_dict = {}

    print("x, y is done. Starting k, v loop")

    for k, v in raster_dictionary.iteritems():

        #=======
        #print v[0]

        #index = np.argwhere(v[0]==0)

        #non_zero_vals = v[0][v[0] != 0] #v[0].delete(0, index)

        #print y
        #========

        ras_dict["{}".format(k)] = v[0].ravel().tolist() #v[0].tolist()

    print("Done wi kv loop")

    # col_list = ["x", "y"]

    col_list = []

    for key in ras_dict.keys():

        col_list.append(key)

    df = pd.DataFrame(ras_dict, columns=col_list)

    print("Done with main Dataframe")

    # AGRICULTURE
    # This way you get rid of the zero values associated with the unmasked areas.
    df_ag = df[df['raster_002_mask_attempt']>0]

    # Filter out slope values greater than three
    df_ag = df_ag[df_ag['slope_degree_reproj32613_aligned']<3]

    df_ag.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/ee_comparison_ag.csv")

    print("Done writing ag data frame")

    # NATURAL AREAS
    # This way you get rid of the zero values associated with the unmasked areas.
    df_nat = df[df['natural_areas_raster_mask']>0]

    # Filter out slope values greater than three
    df_nat = df_nat[df_nat['slope_degree_reproj32613_aligned']<3]

    df_nat.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/ee_comparison_nat.csv")

    print("Done writing natural data frame")


    #============================
    # TODO - Fix hard-coding here
    # df_filter = df.loc[df['nlcd_align_path35_dixon_wy'].isin([81, 80])]
    # df_filter.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/for_stacking/stack_csv.csv")

    # TODO - and here
    # y = df_filter.ix[:, 'LT50350312011166PAC01_ETrF']
    # x = df_filter.ix[:, "LT50350312011166PAC01_NDVI"]

    ### IF doing at-large NLCD filtering
    # df = df[df['aligned_nlcd_full_warp_near_clip_3336']>80 | df['aligned_nlcd_full_warp_near_clip_3336']< 81]
    # ============================


    # TODO - comment out if using nlcd filter at-large

    # AGRICULTURAL
    ETrF_ag = df_ag.ix[:, "LT50350312011230PAC01_ETrF"]

    ETrF_adj_ag = df_ag.ix[:, 'adjusted_etrf_test_2'] # LT50350312011230PAC01_ETrF

    #ndvi_ag = df_ag.ix[:, "LT50350312011230PAC01_NDVI"]

    ETa_ag = df_ag.ix[:, "ETa_20110818_eeflux"]

    ETa_adj_ag = df_ag.ix[:, "ETa_adj_20110818_eeflux"]


    # NATURAL

    ETrF_nat = df_nat.ix[:, "LT50350312011230PAC01_ETrF"]

    ETrF_adj_nat = df_nat.ix[:, 'adjusted_etrf_test_2']  # LT50350312011230PAC01_ETrF

    # ndvi_ag = df_ag.ix[:, "LT50350312011230PAC01_NDVI"]

    ETa_nat = df_nat.ix[:, "ETa_20110818_eeflux"]

    ETa_adj_nat = df_nat.ix[:, "ETa_adj_20110818_eeflux"]



    #=======GRAPHING PORTION=======

    # AGRICULTURAL
    ETrF_ag_hist = plt.figure()
    aa = ETrF_ag_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_ag, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETrF_ag_hist_eeflux.pdf")

    ETrF_ag_adj_hist = plt.figure()
    aa = ETrF_ag_adj_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF_adj Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_adj_ag, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETrF_adj_ag_hist_eeflux.pdf")

    ETa_ag_hist = plt.figure()
    aa = ETa_ag_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa_ag_hist Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETa', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_ag, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETa_ag_hist_eeflux.pdf")

    ETa_adj_ag_hist = plt.figure()
    aa = ETa_adj_ag_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa_ag_adj_hist Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETa_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_adj_ag, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETa_adj_ag_hist_eeflux.pdf")

    # NATURAL

    ETrF_nat_hist = plt.figure()
    aa = ETrF_nat_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_nat, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETrF_nat_hist_eeflux.pdf")

    ETrF_nat_adj_hist = plt.figure()
    aa = ETrF_nat_adj_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF_adj Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_adj_nat, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETrF_nat_adj_hist_eeflux.pdf")

    ETa_nat_hist = plt.figure()
    aa = ETa_nat_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa_nat_hist Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETa', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_nat, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETa_nat_hist_eeflux.pdf")

    ETa_adj_nat_hist = plt.figure()
    aa = ETa_adj_nat_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa_nat_adj_hist Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETa_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_adj_nat, bins=20)
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/eeflux/ETa_adj_nat_hist_eeflux.pdf")





def run():

    # TODO - update at each use
    drive_path = os.path.join('/', 'Volumes', 'SeagateExpansionDrive', )
    #tiff_path = os.path.join(drive_path, "jan_metric", 'for_stacking', 'aligned_nlcd_full_warp_near_clip_3336.tif')
    stack_location = os.path.join(drive_path, "jan_metric", 'stacking_histogram_eeflux')



    #x, y = coord_getter(tiff_path)

    # print "x", x
    #
    # print "y", y


    #### find the right window to use.

    # First get the minimum raster extent.
    comparison_list = []
    comparison_dict = {}
    for directory_path, subdir, file in os.walk(stack_location, topdown=False):

        for tf in file:
            if tf.endswith(".tif"):

                tiff_path = os.path.join(directory_path, tf)

                with rasterio.open(tiff_path) as src:
                    ras = src.read(1)

                    # raster.shape -> (###,###)
                    #
                    #     raster.shape[1] raster.shape[0]

                    comparison_list.append(ras.shape[0]*ras.shape[1])

                    comparison_dict["{}".format(ras.shape[0]*ras.shape[1])] = tiff_path


    # get the minimum dimensions raster.
    val = min(comparison_list)
    min_raster_path = comparison_dict["{}".format(val)]

    print (min_raster_path)
    with rasterio.open(min_raster_path) as raster:

        ras = raster.read(1)

        print('ras shape 0', ras.shape[0])

        print('ras shape 1', ras.shape[1])

        window = ((0, ras.shape[0]), (0, ras.shape[1]))

        print("WINDOW", window)
        bounds = raster.window_bounds(window)

        print("BOUNDS", bounds)


    # Take the bounds from the minimum raster and for each raster in the dir,
    # get the correct window to be read in for the dict using the bounds from the min raster.
    raster_dict = {}
    window_lst = []
    for directory_path, subdir, file in os.walk(stack_location, topdown=False):

        for tf in file:
            if tf.endswith(".tif"):
                tiff_path = os.path.join(directory_path, tf)

                with rasterio.open(tiff_path) as r:
                    T0 = r.affine  # upper-left pixel corner affine transform

                    print(T0)

                    window = r.window(*bounds)

                    print("edited window", window)

                    A = r.read(1, window=window)

                print("A", A)
                print("A shape", A.shape)


                raster_dict['{}'.format(tf.split(".")[0])] = (A, tiff_path)



    print('raster dict', raster_dict)

    print("Starting the formatter")

    data_frame_formatter(raster_dict)


if __name__ == "__main__":

    run()