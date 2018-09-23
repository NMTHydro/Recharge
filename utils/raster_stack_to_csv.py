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


def data_frame_formatter(x_list, y_list, raster_dictionary):

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

        print("v[0]")
        print(v[0])

        print('lenght of ravel v[0] for k = {}'.format(k))

        print(len(v[0].ravel().tolist()))

        ras_dict["{}".format(k)] = v[0].ravel().tolist()

    print("Done wi kv loop")

    # col_list = ["x", "y"]

    # add x_list and y_list to raster dict

    ras_dict["northings"] = y_list
    ras_dict["eastings"] = x_list

    # make col_list to store the columns in a list so you can make a dataframe out of the raster dictionary.
    col_list = []

    for key in ras_dict.keys():

        col_list.append(key)

    df = pd.DataFrame(ras_dict, columns=col_list)

    # todo - change or turn on/off as needed
    # This way you get rid of the zero values associated with the unmasked areas.
    df = df[df['new_ag_aoi_rast_clip_13N_LST_gr']>0] # ag_aoi_raster_05_phx_2, aoi_alfalfa_mask_phx_2010, new_ag_aoi_rast_clip_13N_LST_gr

    # Filter out slope values greater than two
    df = df[df['slope_janmetric_20110818_align']<3]

    # Just for ETrF's where the ag mask covers NODATA values
    # todo - change or turn on/off as needed
    #df = df[df['LT50370372005195PAC01_ETrF']!=0]

    # TODO - change each time
    df.to_excel("/Volumes/SeagateExpansionDrive/jan_metric_PHX_GR/green_river_stack/stack_output/20150728_ETrF_NDVI_gr_coords.xls")

    return df

def grapher(df):

    # for the ideal NDVI ETrF = 1.25 * NDVI unless NDVI is above 0.8 where ETrF == 1
    ideal_ndvi = []
    for col in df.columns:

        print(col)

        if str(col).endswith("NDVI"):

            print(df[col])

            for row in df[col]:
                if row >= 0.8:
                    ideal_ndvi.append(1)

                elif row < 0.8:
                    ideal_ndvi.append(row * 1.25)

    df['ideal_ETrF'] = ideal_ndvi

    print("enhanced dataframe", df)


    # now plot ideal ETrf vs normal ETRF and dont forget small gridlines for Jan.
    # empty = []

    # for col in df.columns:
    #     if str(col).endswith("NDVI"):
    #         empty.append(col)
    ndvi_string = [col for col in df.columns if str(col).endswith("NDVI")]
    etrf_string = [col for col in df.columns if str(col).endswith("ETrF")]
    etrf_ideal = df.ix[:,"ideal_ETrF"]
    etrf = df.ix[:, etrf_string[0]]
    ndvi = df.ix[:, ndvi_string[0]]


    ETrF_vs_NDVI = plt.figure()
    aa = ETrF_vs_NDVI.add_subplot(111)
    aa.set_title('ETrF vs NDVI', fontweight='bold')
    aa.set_xlabel('NDVI - {}'.format(ndvi_string), style='italic')
    aa.set_ylabel('ETrF-{}'.format(etrf_string), style='italic')
    aa.scatter(ndvi, etrf_ideal, facecolors= 'none', edgecolors = 'blue')
    aa.scatter(ndvi, etrf, facecolors= 'none', edgecolors= 'red')
    plt.minorticks_on()
    #aa.grid(b=True, which='major', color='k')
    aa.grid(b=True, which='minor', color='white')
    plt.tight_layout()
    # plt.savefig(
    #      "/Volumes/SeagateExpansionDrive/jan_metric_PHX_GR/green_river_stack/stack_output/20150728_ETrF_NDVI_gr.pdf")
    #plt.show()


def run():

    # TODO - update at each use
    # drive_path = os.path.join('/', 'Volumes', 'SeagateExpansionDrive', )
    # #tiff_path = os.path.join(drive_path, "jan_metric", 'for_stacking', 'aligned_nlcd_full_warp_near_clip_3336.tif')
    # stack_location = os.path.join(drive_path, "jan_metric_PHX_GR", 'green_river_stack', 'stack_20150728_ETrF_NDVI')
    drive_path = os.path.join('/', 'Users', 'Gabe', 'Desktop', 'juliet_problem')
    # tiff_path = os.path.join(drive_path, "jan_metric", 'for_stacking', 'aligned_nlcd_full_warp_near_clip_3336.tif')
    stack_location = os.path.join(drive_path, 'juliet_stack')

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

                    print("Here is T0", T0)

                    window = r.window(*bounds)

                    print("edited window", window)

                    top_left = [bounds[0], bounds[-1]]


                    print("Here is top left", top_left)

                    print('r.window', r.window)

                    A = r.read(1, window=window)

                print("A", A)
                print("A shape", A.shape)



                # top left x and top left y coord from bounds of window
                tlx = bounds[0]
                tly = bounds[-1]
                geotransform = (tlx, T0[0], 0.0, tly, 0.0, T0[4])

                # make an Affine transformation matrix out of the geotransform
                fwd = Affine.from_gdal(*geotransform)
                # use the affine matrix to shift half a raster over.
                T1 = fwd * Affine.translation(0.5, 0.5)
                print(" The new T1 ", T1)
                # make a grid to hold the columns and rows based on the shape of the raster you read in.
                col, row = np.meshgrid(np.arange(A.shape[1]), np.arange(A.shape[0]))
                # convert col and row to UTM centroids using translated affine matrix
                x, y = T1 * (col, row)

                # add the rasters to a raster dict.
                raster_dict['{}'.format(tf.split(".")[0])] = (A, tiff_path)


    # make the list of northings y and eastings x

    x_list = x.ravel().tolist()

    y_list = y.ravel().tolist()

    print("Starting the formatter")
    # add the raster dict and the list of x and y coordinates separately.
    df = data_frame_formatter(x_list, y_list, raster_dict)

    #graph ETrF vs NDVI and ideal ETrF vs NDVI
    grapher(df)


if __name__ == "__main__":

    run()

# NLCD FIltering code

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
    # y = df.ix[:, 'ETrF_20110818_eeflux_align'] # LT50350312011230PAC01_ETrF
    #
    # x = df.ix[:, "NDVI_20110818_eeflux_align"]

