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
from collections import defaultdict
import datetime
# from datetime import datetime
import numpy as np
# import seaborn as sns
# import matplotlib.pyplot as plt
import pandas as pd
import gdal

from bokeh.plotting import figure
from bokeh.io import output_file, show

# ============= local library imports ===========================

"""
All this script will do is read in data from ETrF and NDVI and make plots.

"""





def convert_raster_to_array(input_raster_path, raster=None, band=1):
    """
    Convert .tif raster into a numpy numerical array.

    :param input_raster_path: Path to raster.
    :param raster: Raster name with \*.tif
    :param band: Band of raster sought.

    :return: Numpy array.
    """
    # print "input raster path", input_raster_path
    # print "raster", raster
    p = input_raster_path
    if raster is not None:
        p = os.path.join(p, raster)

    # print "filepath", os.path.isfile(p)
    # print p
    if not os.path.isfile(p):
        print('Not a valid file: {}'.format(p))

    raster_open = gdal.Open(p)
    ras = np.array(raster_open.GetRasterBand(band).ReadAsArray(), dtype=float)
    return ras



def run():

    sh_path_ETrF_06_13 = "/Volumes/SeagateExpansionDrive/SEBAL_Data_Sung-ho/SH_warp/sh_ETRF_ag_filtered/ETrF_sh_2004_06_13_ag.tif"

    sh_path_ndvi_06_13 = "/Volumes/SeagateExpansionDrive/ee_images_corrto_sungho/images_filtered_agricultural/sh_ndvi_warped_ag_filtered/ndvi_2004_06_13_wrp_ag.tif"

    #sh_path_ETrF_09_17 = "/Volumes/SeagateExpansionDrive/SEBAL_Data_Sung-ho/SH_warp/sh_ETRF_ag_filtered/ETrF_sh_2004_09_17_ag.tif"

    ee_path_ETrF_06_13 = "/Volumes/SeagateExpansionDrive/ee_images_corrto_sungho/unfiltered_ee_images/filtered_images/ee_ETrF_2004_06_13_ag.tif"

    ee_path_ndvi_06_13 = "/Volumes/SeagateExpansionDrive/ee_images_corrto_sungho/unfiltered_ee_images/filtered_images/ee_ndvi_2004_06_13_ag.tif"

    sh_ETrF_06_13_arr = convert_raster_to_array(sh_path_ETrF_06_13)

    sh_ndvi_06_13_arr = convert_raster_to_array(sh_path_ndvi_06_13)

    ee_ETrF_06_13_arr = convert_raster_to_array(ee_path_ETrF_06_13)

    ee_ndvi_06_13_arr = convert_raster_to_array(ee_path_ndvi_06_13)

    # how do i make a 2d array 1-d???
    # numpy.ndarray.flatten

    sh_ndvi_06_13_flat = np.ndarray.flatten(sh_ndvi_06_13_arr)

    sh_ETrF_06_13_flat = np.ndarray.flatten(sh_ETrF_06_13_arr)

    fig1 = figure(title="sH 06_13")
    fig1.xaxis.axis_label = "NDVI"
    fig1.yaxis.axis_label = "ETrf"
    fig1.circle(sh_ndvi_06_13_flat, sh_ETrF_06_13_flat)

    show(fig1)

    # fig1 = plt.figure()
    # aa = fig1.add_subplot(111)
    # aa.set_title('SH 06 13', fontweight='bold')
    # aa.set_xlabel('NDVI', style='italic')
    # aa.set_ylabel('ETrF', style='italic')
    # aa.scatter(sh_ndvi_06_13_arr, sh_ETrF_06_13_arr)
    # aa.legend(loc='upper right', frameon=True, prop={'size': 10})
    # plt.tight_layout()
    # # plt.savefig('/Users/Gabe/Desktop/time_series_figs/{}_together.png'.format(x_item))
    # # plt.savefig('{}/{}_together.pdf'.format(output_path, x_item[0:7]))
    # plt.show()
    #
    # fig2 = plt.figure()
    # ab = fig2.add_subplot(111)
    # ab.set_title('EE 06 13', fontweight='bold')
    # ab.set_xlabel('NDVI', style='italic')
    # ab.set_ylabel('ETrF', style='italic')
    # ab.scatter(ee_ndvi_06_13_arr, ee_ETrF_06_13_arr)
    # ab.legend(loc='upper right', frameon=True, prop={'size': 10})
    # plt.tight_layout()
    # # plt.savefig('/Users/Gabe/Desktop/time_series_figs/{}_together.png'.format(x_item))
    # # plt.savefig('{}/{}_together.pdf'.format(output_path, x_item[0:7]))
    # plt.show()





if __name__ == "__main__":

    run()