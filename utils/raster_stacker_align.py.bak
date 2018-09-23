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

# ============= local library imports ===========================


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

    print "x, y is done. Starting k, v loop"

    for k, v in raster_dictionary.iteritems():

        #=======
        #print v[0]

        #index = np.argwhere(v[0]==0)

        #non_zero_vals = v[0][v[0] != 0] #v[0].delete(0, index)

        #print y
        #========

        ras_dict["{}".format(k)] = v[0].ravel().tolist() #v[0].tolist()

    print "Done wi kv loop"

    # col_list = ["x", "y"]

    col_list = []

    for key in ras_dict.keys():

        col_list.append(key)

    df = pd.DataFrame(ras_dict, columns=col_list)

    #df.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/full_aligned_dataset.csv")

    print "Done with main Dataframe"

    return df

def ag(df):

    # This way you get rid of the zero values associated with the unmasked areas.
    df_ag = df[df['ag_raster_mask_align']>0]

    # Filter out slope values greater than three
    df_ag = df_ag[df_ag['slope_janmetric_20110818_align']<3]

    print "Done writing ag data frame"
    return df_ag


def natural(df):

    # NATURAL AREAS
    # This way you get rid of the zero values associated with the unmasked areas.
    df_nat = df[df['natural_raster_mask_align']>0]

    # Filter out slope values greater than three
    df_nat = df_nat[df_nat['slope_janmetric_20110818_align']<3]

    #df_nat.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/jan_comparison_nat.csv")

    print "Done writing natural data frame"

    return df_nat

def histogram_gen(ag_df, nat_df):


    ### BREAK out the appropriate Data

    # AGRICULTURAL EEFLUX
    ETrF_ag_ee = ag_df.ix[:, "ETrF_20110818_eeflux_align"]
    ETrF_ag_adj_ee = ag_df.ix[:, "adjusted_etrf_test_2_align"]
    ETa_ag_ee = ag_df.ix[:, "ETa_20110818_eeflux_align"]
    ETa_ag_adj_ee = ag_df.ix[:, "ETa_adj_20110818_eeflux_align"]

    # NATURAL EEFLUX
    ETrF_nat_ee = nat_df.ix[:, "ETrF_20110818_eeflux_align"]
    ETrF_nat_adj_ee = nat_df.ix[:, "adjusted_etrf_test_2_align"]
    ETa_nat_ee = nat_df.ix[:, "ETa_20110818_eeflux_align"]
    ETa_nat_adj_ee = nat_df.ix[:, "ETa_adj_20110818_eeflux_align"]


    # AGRICULTURAL Jan Metric
    ETrF_ag_jan = ag_df.ix[:, "etrf24_janmetric_20110818_unmasked_align"]
    ETa_ag_jan = ag_df.ix[:, "et24_janmetric_20110818_align"]

    # NATURAL Jan Metric
    ETrF_nat_jan = nat_df.ix[:, "etrf24_janmetric_20110818_unmasked_align"]
    ETa_nat_jan = nat_df.ix[:, "et24_janmetric_20110818_align"]




    #========================================================

    # AGRICULTURE EEFLUX HISTOGRAMS

    ETrF_ag_ee_hist = plt.figure()
    aa = ETrF_ag_ee_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_ag_ee, bins=20, color='r')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETrF_ag_hist_eefl.png")

    ETa_ag_ee_hist = plt.figure()
    aa = ETa_ag_ee_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETa', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_ag_ee, bins=20, color='m')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETa_ag_hist_eefl.png")

    ETrF_ag_adj_ee_hist = plt.figure()
    aa = ETrF_ag_adj_ee_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF Adjusted Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_ag_adj_ee, bins=20, color='r')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETrF_adj_ag_hist_eefl.png")

    ETa_adj_ag_ee_hist = plt.figure()
    aa = ETa_adj_ag_ee_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa Adjusted Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETa_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_ag_adj_ee, bins=20, color='m')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETa_adj_ag_hist_eefl.png")


    # NATURAL EEFLUX HISTOGRAMS

    ETrF_nat_ee_hist = plt.figure()
    aa = ETrF_nat_ee_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_nat_ee, bins=20, color='g')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETrF_nat_hist_eefl.png")

    ETrF_nat_adj_ee_hist = plt.figure()
    aa = ETrF_nat_adj_ee_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETrF Adjusted Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_nat_adj_ee, bins=20, color='g')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETrF_nat_adj_hist_eefl.png")

    ETa_nat_hist = plt.figure()
    aa = ETa_nat_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETa', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_nat_ee, bins=20, color='c')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETa_nat_hist_eefl.png")

    ETa_adj_nat_hist = plt.figure()
    aa = ETa_adj_nat_hist.add_subplot(111)
    aa.set_title('EE FLUX 2011 August 18 - ETa Adjusted Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETa_adj', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_nat_adj_ee, bins=20, color='c')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/eeflux/ETa_adj_nat_hist_eefl.png")

    # =================================================================================================================
    # =================================================================================================================
    # =================================================================================================================
    # =================================================================================================================

    # AGRICULTURE Jan Metric HISTOGRAMS
    ETrF_ag_jan_hist = plt.figure()
    aa = ETrF_ag_jan_hist.add_subplot(111)
    aa.set_title('Hendrickx Metric 2011 August 18 - ETrF Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_ag_jan, bins=20, color='r')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/janmetric/ETrF_ag_hist_janmetr.png")

    ETa_ag_jan_hist = plt.figure()
    aa = ETa_ag_jan_hist.add_subplot(111)
    aa.set_title('Hendrickx Metric 2011 August 18 - ETa Agricultural Pixels', fontweight='bold')
    aa.set_xlabel('ETa', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_ag_jan, bins=20, color='m')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/janmetric/ETa_ag_hist_janmetr.png")



    # NATURAL Jan Metric HISTOGRAMS

    ETrF_nat_jan_hist = plt.figure()
    aa = ETrF_nat_jan_hist.add_subplot(111)
    aa.set_title('Hendrickx Metric 2011 August 18 - ETrF Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETrF', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETrF_nat_jan, bins=20, color='g')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/janmetric/ETrF_nat_hist_janmetr.png")

    ETa_nat_jan_hist = plt.figure()
    aa = ETa_nat_jan_hist.add_subplot(111)
    aa.set_title('Hendrickx Metric 2011 August 18 - ETa Natural Pixels', fontweight='bold')
    aa.set_xlabel('ETa', style='italic')
    aa.set_ylabel('Frequency', style='italic')
    aa.hist(ETa_nat_jan, bins=20, color='c')
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/Histograms/janmetric/ETa_nat_hist_janmetr.png")


def one_to_one_plotter(ag_df, nat_df):

    """
    This function takes the ag pixels dataframe and makes matplotlib plots comparing Jan's data to
     adjusted and non-adjusted ETrFs

    :param ag_df:
    :param nat_df:
    :return:
    """

    # AGRICULTURAL EEFLUX
    ETrF_ag_ee = ag_df.ix[:, "ETrF_20110818_eeflux_align"]
    ETrF_ag_adj_ee = ag_df.ix[:, "adjusted_etrf_test_2_align"]
    ETa_ag_ee = ag_df.ix[:, "ETa_20110818_eeflux_align"]
    ETa_ag_adj_ee = ag_df.ix[:, "ETa_adj_20110818_eeflux_align"]

    # NATURAL EEFLUX
    ETrF_nat_ee = nat_df.ix[:, "ETrF_20110818_eeflux_align"]
    ETrF_nat_adj_ee = nat_df.ix[:, "adjusted_etrf_test_2_align"]
    ETa_nat_ee = nat_df.ix[:, "ETa_20110818_eeflux_align"]
    ETa_nat_adj_ee = nat_df.ix[:, "ETa_adj_20110818_eeflux_align"]

    # AGRICULTURAL Jan Metric
    ETrF_ag_jan = ag_df.ix[:, "etrf24_janmetric_20110818_unmasked_align"]
    ETa_ag_jan = ag_df.ix[:, "et24_janmetric_20110818_align"]

    # NATURAL Jan Metric
    ETrF_nat_jan = nat_df.ix[:, "etrf24_janmetric_20110818_unmasked_align"]
    ETa_nat_jan = nat_df.ix[:, "et24_janmetric_20110818_align"]



    # ==================================================
    # ==================================================
    # ==================================================
    #AGRICULTURAL

    # one to one ee ETrF to Jan Metric ETrf
    ETrF_ag = plt.figure()
    aa = ETrF_ag.add_subplot(111)
    aa.set_title('EE FLUX vs Hendrickx Agricultural ETrF 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETrF', style='italic')
    aa.set_ylabel('ETrF EE Flux', style='italic')
    plt.xlim(-.5, 2)
    plt.ylim(-.5, 2)
    aa.scatter(ETrF_ag_jan, ETrF_ag_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/agricultural/et.png")

    # adjusted
    ETrF_adj_ag = plt.figure()
    aa = ETrF_adj_ag.add_subplot(111)
    aa.set_title('Adjusted EE FLUX vs Hendrickx Agricultural ETrF 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETrF', style='italic')
    aa.set_ylabel('ETrF adj EE Flux', style='italic')
    plt.xlim(-.5, 2)
    plt.ylim(-.5, 2)
    aa.scatter(ETrF_ag_jan, ETrF_ag_adj_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/agricultural/etrf_a.png")

    # one to one EE ETa to Jan Metric ETa
    ETa_ag = plt.figure()
    aa = ETa_ag.add_subplot(111)
    aa.set_title('EE FLUX vs Hendrickx Agricultural ETa 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETa', style='italic')
    aa.set_ylabel('ETa EE Flux', style='italic')
    plt.xlim(-2, 15)
    plt.ylim(-2, 15)
    aa.scatter(ETa_ag_jan, ETa_ag_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/agricultural/e.png")
    #adjusted
    ETa_adj_ag = plt.figure()
    aa = ETa_adj_ag.add_subplot(111)
    aa.set_title('Adjusted EE FLUX vs Hendrickx Agricultural ETa 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETa', style='italic')
    aa.set_ylabel('ETa Adj EE Flux', style='italic')
    plt.xlim(-2, 15)
    plt.ylim(-2, 15)
    aa.scatter(ETa_ag_jan, ETa_ag_adj_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/agricultural/eta_a.png")

    # adj to not adjusted

    ETrF_self_ag = plt.figure()
    aa = ETrF_self_ag.add_subplot(111)
    aa.set_title('EE FLUX vs Adjusted EE FLUX Agricultural Areas ETrF 2011 August 18', fontweight='bold')
    aa.set_xlabel('EE FLUX ETrF', style='italic')
    aa.set_ylabel('ETrF Adj EE FLUX', style='italic')
    # plt.xlim(-2, 15)
    # plt.ylim(-2, 15)
    aa.scatter(ETrF_ag_ee, ETrF_ag_adj_ee, color='blue')
    # aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/agricultural/etrf_a_self.png")



    # ==================================================
    # ==================================================
    # ==================================================
    # Natural

    # one to one ee ETrF to Jan Metric ETrf
    ETrF_nat = plt.figure()
    aa = ETrF_nat.add_subplot(111)
    aa.set_title('EE FLUX vs Hendrickx Natural ETrF 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETrF', style='italic')
    aa.set_ylabel('ETrF EE Flux', style='italic')
    plt.xlim(-.5, 2)
    plt.ylim(-.5, 2)
    aa.scatter(ETrF_nat_jan, ETrF_nat_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/natural/et.png")
    # adjusted
    ETrF_adj_nat = plt.figure()
    aa = ETrF_adj_nat.add_subplot(111)
    aa.set_title('Adjusted EE FLUX vs Hendrickx Natural ETrF 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETrF', style='italic')
    aa.set_ylabel('ETrF adj EE Flux', style='italic')
    plt.xlim(-.5, 2)
    plt.ylim(-.5, 2)
    aa.scatter(ETrF_nat_jan, ETrF_nat_adj_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/natural/etrf_a.png")

    # one to one EE ETa to Jan Metric ETa
    ETa_nat = plt.figure()
    aa = ETa_nat.add_subplot(111)
    aa.set_title('EE FLUX vs Hendrickx Natural ETa 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETa', style='italic')
    aa.set_ylabel('ETa EE Flux', style='italic')
    plt.xlim(-2, 15)
    plt.ylim(-2, 15)
    aa.scatter(ETa_nat_jan, ETa_nat_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/natural/e.png")
    # adjusted

    ETa_adj_nat = plt.figure()
    aa = ETa_adj_nat.add_subplot(111)
    aa.set_title('Adjusted EE FLUX vs Hendrickx Natural ETa 2011 August 18', fontweight='bold')
    aa.set_xlabel('Jan Metric ETa', style='italic')
    aa.set_ylabel('ETa Adj EE Flux', style='italic')
    plt.xlim(-2, 15)
    plt.ylim(-2, 15)
    aa.scatter(ETa_nat_jan, ETa_nat_adj_ee, color='blue')
    aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/natural/eta_a.png")

    ETrF_self_nat = plt.figure()
    aa = ETrF_self_nat.add_subplot(111)
    aa.set_title('EE FLUX vs EE FLUX Adjusted Natural Areas ETrF 2011 August 18', fontweight='bold')
    aa.set_xlabel('EE FLUX ETrF', style='italic')
    aa.set_ylabel('ETrF Adj EE FLUX', style='italic')
    # plt.xlim(-2, 15)
    # plt.ylim(-2, 15)
    aa.scatter(ETrF_nat_ee, ETrF_nat_adj_ee, color='blue')
    # aa.plot(aa.get_xlim(), aa.get_ylim(), ls="--")
    plt.tight_layout()
    plt.savefig(
        "/Volumes/SeagateExpansionDrive/jan_metric/plots/aligned_plots/one_to_one_plots/natural/etrf_a_self.png")


def run():

    # TODO - update at each use
    drive_path = os.path.join('/', 'Volumes', 'SeagateExpansionDrive', )
    #tiff_path = os.path.join(drive_path, "jan_metric", 'for_stacking', 'aligned_nlcd_full_warp_near_clip_3336.tif')
    stack_location = os.path.join(drive_path, "jan_metric", 'stacking_histogram_align')


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

        print 'ras shape 0', ras.shape[0]

        print 'ras shape 1', ras.shape[1]

        window = ((0, ras.shape[0]), (0, ras.shape[1]))

        print "WINDOW", window
        bounds = raster.window_bounds(window)

        print "BOUNDS", bounds


    # Take the bounds from the minimum raster and for each raster in the dir,
    # get the correct window to be read in for the dict using the bounds from the min raster.
    raster_dict = {}
    window_lst = []
    for directory_path, subdir, file in os.walk(stack_location, topdown=False):

        for tf in file:
            if tf.endswith(".tif") or tf.endswith(".img"):
                tiff_path = os.path.join(directory_path, tf)

                #print 'path', tiff_path

                with rasterio.open(tiff_path) as r:
                    T0 = r.affine  # upper-left pixel corner affine transform

                    print T0

                    window = r.window(*bounds)

                    print "edited window", window

                    A = r.read(1, window=window)

                print "A", A
                print "A shape", A.shape
                print 'path', tiff_path


                raster_dict['{}'.format(tf.split(".")[0])] = (A, tiff_path)



    print 'raster dict', raster_dict

    print "Starting the formatter"

    df = data_frame_formatter(raster_dict)

    ag_df = ag(df)

    nat_df = natural(df)

    # Total Histogram for Analysis (for Juliet)
    # Here we simpy take the ag_df and nat_df and export them into .csv files

    ag_df.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/full_aligned_dataset_ag.csv")

    nat_df.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/full_aligned_dataset_nat.csv")

    histogram_gen(ag_df, nat_df)

    one_to_one_plotter(ag_df, nat_df)


if __name__ == "__main__":

    run()

# # AGRICULTURE
#     # This way you get rid of the zero values associated with the unmasked areas.
#     df_ag = df[df['jan_ag_mask_from_maskjanaoi_20110818']>0]
#
#     # Filter out slope values greater than three
#     df_ag = df_ag[df_ag['slope_degree_20110818']<3]
#
#     df_ag.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/jan_comparison_ag.csv")
#
#     print "Done writing ag data frame"
#
#     # NATURAL AREAS
#     # This way you get rid of the zero values associated with the unmasked areas.
#     df_nat = df[df['jan_natural_mask_from_naturalareasmask_20110818']>0]
#
#     # Filter out slope values greater than three
#     df_nat = df_nat[df_nat['slope_degree_20110818']<3]
#
#     df_nat.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/jan_comparison_nat.csv")
#
#     print "Done writing natural data frame"
#
#
#     #============================
#     # TODO - Fix hard-coding here
#     # df_filter = df.loc[df['nlcd_align_path35_dixon_wy'].isin([81, 80])]
#     # df_filter.to_csv("/Volumes/SeagateExpansionDrive/jan_metric/for_stacking/stack_csv.csv")
#
#     # TODO - and here
#     # y = df_filter.ix[:, 'LT50350312011166PAC01_ETrF']
#     # x = df_filter.ix[:, "LT50350312011166PAC01_NDVI"]
#
#     ### IF doing at-large NLCD filtering
#     # df = df[df['aligned_nlcd_full_warp_near_clip_3336']>80 | df['aligned_nlcd_full_warp_near_clip_3336']< 81]
#     # ============================
#
#
#     # TODO - comment out if using nlcd filter at-large
#
#     # AGRICULTURAL
#     ETrF_ag = df_ag.ix[:, "etrf24_20110818"]
#
#     ETa_ag = df_ag.ix[:, "et24_20110818"]
#
#     # NATURAL
#     ETrF_nat = df_nat.ix[:, "etrf24_20110818"]
#
#     ETa_nat = df_nat.ix[:, "et24_20110818"]
#
#
#     # =======GRAPHING PORTION=======
#
#     # AGRICULTURAL
#     ETrF_ag_hist = plt.figure()
#     aa = ETrF_ag_hist.add_subplot(111)
#     aa.set_title('EE FLUX 2011 August 18 - ETrF Agricultural Pixels', fontweight='bold')
#     aa.set_xlabel('ETrF', style='italic')
#     aa.set_ylabel('Frequency', style='italic')
#     aa.hist(ETrF_ag, bins=20)
#     plt.tight_layout()
#     plt.savefig(
#         "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/janmetric/ETrF_ag_hist_janmetr.png")
#
#
#     ETa_ag_hist = plt.figure()
#     aa = ETa_ag_hist.add_subplot(111)
#     aa.set_title('EE FLUX 2011 August 18 - ETa_ag_hist Agricultural Pixels', fontweight='bold')
#     aa.set_xlabel('ETa', style='italic')
#     aa.set_ylabel('Frequency', style='italic')
#     aa.hist(ETa_ag, bins=20)
#     plt.tight_layout()
#     plt.savefig(
#         "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/janmetric/ETa_ag_hist_janmetr.png")
#
#     # NATURAL
#
#     ETrF_nat_hist = plt.figure()
#     aa = ETrF_nat_hist.add_subplot(111)
#     aa.set_title('EE FLUX 2011 August 18 - ETrF Natural Pixels', fontweight='bold')
#     aa.set_xlabel('ETrF', style='italic')
#     aa.set_ylabel('Frequency', style='italic')
#     aa.hist(ETrF_nat, bins=20)
#     plt.tight_layout()
#     plt.savefig(
#         "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/janmetric/ETrF_nat_hist_janmetr.png")
#
#     ETa_nat_hist = plt.figure()
#     aa = ETa_nat_hist.add_subplot(111)
#     aa.set_title('EE FLUX 2011 August 18 - ETa_nat_hist Natural Pixels', fontweight='bold')
#     aa.set_xlabel('ETa', style='italic')
#     aa.set_ylabel('Frequency', style='italic')
#     aa.hist(ETa_nat, bins=20)
#     plt.tight_layout()
#     plt.savefig(
#         "/Volumes/SeagateExpansionDrive/jan_metric/plots/non_aligned_plots/Histograms/janmetric/ETa_nat_hist_janmetr.png")