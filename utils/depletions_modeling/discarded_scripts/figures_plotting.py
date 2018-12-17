# ===============================================================================
# Copyright 2018 gabe-parrish
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
from cumulative_depletions import raster_extract
import numpy as np
import numpy.ma as ma
from matplotlib import pyplot as plt
import matplotlib.cm as cm

# ============= local library imports ===========================

def get_cmap(n, name='hsv'):
    """"""
    print 'n is what?', n
    return plt.cm.get_cmap(name, n)


def plot_landcover_type():
    """"""

    land_cover_path = "/Users/Gabe/Desktop/NM_DEM_slope/depletions_work/ETRM_static/nlcd_nm_utm13.tif"

    # depletion from the cum_depletions_neg_mod
    depletion_path = "/Users/Gabe/Desktop/NM_DEM_slope/depletions_work/ETRM_static/max_depletion_2000_2013.tif"

    old_taw_path = "/Users/Gabe/Desktop/NM_DEM_slope/depletions_work/ETRM_static/taw_mod_4_21_10_0.tif"

    # read in the arrays
    landcover_arr, transform, dim, proj, dt = raster_extract(land_cover_path)
    depletion_arr, transform, dim, proj, dt = raster_extract(depletion_path)
    old_taw_arr, transform, dim, proj, dt = raster_extract(old_taw_path)

    # flatten the depletion, old_taw and land_cover arrays
    cover = landcover_arr.flatten().astype(int)
    depletion = depletion_arr.flatten()
    etrm_taw = old_taw_arr.flatten()

    # mask landcover array based on land_types we dont want to visualize.
    # dont want [1, 11, 81, 82, 21, 22, 23, 24, 31]
    undesirable_classes = (1, 11, 81, 82, 21, 22, 23, 24, 31)

    masks = [cover != 1, cover != 11, cover != 81, cover != 82, cover != 21, cover != 22, cover != 23, cover != 24, cover != 31]

    mask_saver = np.zeros(landcover_arr.shape)
    for i in range(1, len(masks) + 1, 1):
        masks[i]


    total_mask = reduce(np.logical_and, masks).astype(int)

    # print 'lc mask', landcover_mask

    print 'tmask len', total_mask.shape

    # we mask out the zeros in the cover class so that they will be the same as the depletions and ETRM TAW
    # todo - fix this here script.
    masked_cover = []

    # apply the mask to depletion and etrm taw and get rid of the zero values

    # testing the lengths of the depletion and etrm_taw prior to masking
    print 'dep len', depletion.shape
    print 'taw len', etrm_taw.shape

    # test whether the total mask is just ones and zeros
    binarylist = np.unique(total_mask).astype(list)
    print 'binary list', binarylist

    # masks out the zero values, they wont be used in calculations or plotting

    # test whether the multiplication changes the number of values
    depletion2 = depletion * total_mask
    print 'len dep 2', depletion2.shape
    etrm_taw2 = etrm_taw * total_mask
    print 'len etrmtaw 2',etrm_taw2.shape

    depletion = np.ma.masked_equal((depletion * total_mask), 0)
    print "len masked dep", depletion.shape
    # print 'depletion sum', np.sum(depletion), depletion.compressed()
    etrm_taw = np.ma.masked_equal((etrm_taw * total_mask), 0)
    print "len masked taw", etrm_taw.shape

    # # if you want to get the array without the mask -- then use .compressed()
    # etrm_taw = etrm_taw.compressed()

    # plot depletion and old taw against each other, and color code based on the land_cover
    # We need to make a list of colors "red", "blue" to correspond with the appropriate land cover class for each pixel

    # get the unique values from the masked landcover array
    class_list = np.unique(masked_cover).astype(list)
    print 'class list', class_list

    # make a color list
    color_dict = {}
    color_list = []
    # the cmap only goes betwen 0 and 7. Higher numbers than seven don't cause an error, they're just the same as 7.
    cmap = get_cmap(len(class_list))

    # make a dictionary relating the class to a color in cmap.
    for i, c in enumerate(class_list):
        color_dict["{}".format(c)] = cmap(i)

    # todo - commented out for testing
    # use the dictionary to assign colors to a list corresponding to the class in masked_cover

    for i in masked_cover.astype(list):
        # the value in masked color selects the appropriate color from the color dict
        color_list.append(color_dict["{}".format(i)])

    print 'color_list is huge', len(color_list)

    facecolor_list = []
    for i in color_list:
        facecolor_list.append('none')

    # todo - commented out for testing
    # === plotting ===
    # you have to increase the chunksize when the dataset is big...
    plt.rcParams['agg.path.chunksize'] = 20000
    plt.scatter(depletion, etrm_taw, facecolors=facecolor_list, edgecolors=color_list)
    # plot a one to one line
    plt.plot([0, 0], [500, 500], 'ro-')





if __name__ == "__main__":

    # TODO - This script sucks and is currently broken.

    plot_landcover_type()

    # # todo - try and determine whether or not the plot is plotting NAN values over the masked arrays.
    #
    # # todo - when we compress the masked data why are the values different if we multiplied through by the same array
    # # of the same length?
    # depletion = depletion.compressed()
    # # d_list = depletion.astype(list)
    # print 'what values are in depletion list', class_list
    # print len(depletion.astype(list))
    # etrm_taw = etrm_taw.compressed()
    # print len(etrm_taw.astype(list))
    #
    # # why does masked cover have the same length as etrm_taw ???? Makes no sense to me...
    #
    # masked_cover = masked_cover.compressed()
    # print len(masked_cover.astype(list))
    #
    # for i in masked_cover.astype(list):
    #     # the value in masked color selects the appropriate color from the color dict
    #     color_list.append(color_dict["{}".format(i)])
    #
    # print 'color_list is huge', len(color_list)
    #
    # facecolor_list = []
    # for i in color_list:
    #     facecolor_list.append('none')
    #
    # # === plotting ===
    # # you have to increase the chunksize when the dataset is big...
    # plt.rcParams['agg.path.chunksize'] = 20000
    # plt.scatter(depletion, etrm_taw, facecolors=facecolor_list, edgecolors=color_list)
    # # plot a one to one line
    # plt.plot([0, 0], [500, 500], 'ro-')
    #
    #
    # plt.show()

    # # ==== saving ====
    #
    # masks = [cover != 1, cover != 11, cover != 81, cover != 82, cover != 21, cover != 22, cover != 23, cover != 24,
    #          cover != 31]
    #
    # # # let's make a list, then of jus the desirable classes
    # # landcover_mask = cover[(cover != 1) & (cover != 11) & (cover != 81) & (cover != 82) & (cover != 21) & (cover != 22)
    # #                        & (cover != 23) & (cover != 24) & (cover != 31)]
    # # landcover_mask = cover[cover =! undesirable_classes.any()]
    # total_mask = reduce(np.logical_and, masks).astype(int)
    #
    # # print 'lc mask', landcover_mask
    #
    # print 'tmask len', len(total_mask.astype(list))
    #
    # # we mask out the zeros in the cover class so that they will be the same as the depletions and ETRM TAW
    # masked_cover = ma.masked_equal((cover * total_mask), 0)
    #
    # # apply the mask to depletion and etrm taw and get rid of the zero values
    #
    # # testing the lengths of the depletion and etrm_taw prior to masking
    # print 'dep len', len(depletion.astype(list))
    # print 'taw len', len(etrm_taw.astype(list))
    #
    # # test whether the total mask is just ones and zeros
    # binarylist = np.unique(total_mask).astype(list)
    # print 'binary list', binarylist
    #
    # # masks out the zero values, they wont be used in calculations or plotting
    #
    # # test whether the multiplication changes the number of values
    # depletion2 = depletion * total_mask
    # print 'len dep 2', len(depletion2.astype(list))
    # etrm_taw2 = etrm_taw * total_mask
    # print 'len etrmtaw 2', len(etrm_taw2.astype(list))
    #
    # depletion = np.ma.masked_equal((depletion * total_mask), 0)
    # print "len masked dep", len(depletion.astype(list))
    # # print 'depletion sum', np.sum(depletion), depletion.compressed()
    # etrm_taw = np.ma.masked_equal((etrm_taw * total_mask), 0)
    # print "len masked taw", len(etrm_taw.astype(list))
    #
    # # # if you want to get the array without the mask -- then use .compressed()
    # # etrm_taw = etrm_taw.compressed()
    #
    # # plot depletion and old taw against each other, and color code based on the land_cover
    # # We need to make a list of colors "red", "blue" to correspond with the appropriate land cover class for each pixel
    #
    # # get the unique values from the masked landcover array
    # class_list = np.unique(masked_cover).astype(list)
    # print 'class list', class_list
    #
    # # make a color list
    # color_dict = {}
    # color_list = []
    # # the cmap only goes betwen 0 and 7. Higher numbers than seven don't cause an error, they're just the same as 7.
    # cmap = get_cmap(len(class_list))
    #
    # # make a dictionary relating the class to a color in cmap.
    # for i, c in enumerate(class_list):
    #     color_dict["{}".format(c)] = cmap(i)


    # ====

    # # let's make a list, then of jus the desirable classes
    # landcover_mask = cover[(cover != 1) & (cover != 11) & (cover != 81) & (cover != 82) & (cover != 21) & (cover != 22)
    #                        & (cover != 23) & (cover != 24) & (cover != 31)]
    # landcover_mask = cover[cover =! undesirable_classes.any()]