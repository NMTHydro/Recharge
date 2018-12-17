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
import fiona
import rasterio
import rasterio.mask
import matplotlib.pyplot as plt
import numpy as np

# ============= local library imports ===========================

def xy_plotter(array_dictionary, plot_output):
    """"""

    for k, v in array_dictionary.iteritems():
        max_dep = np.max(v[0])
        max_taw = np.max(v[1])

        limit = max(max_dep, max_taw)

        plt.style.use('ggplot')

        fig, ax = plt.subplots(1, 1)

        ax.set_title("study area: {}".format(k))
        ax.set_xlabel("max depletion corrected (+ and -) (mm)")
        ax.set_ylabel('nrcs taw (mm)')
        ax.plot([0, limit], [0, limit])
        ax.scatter(v[0], v[1], facecolors='none', edgecolors='b')

        plt.savefig(os.path.join(plot_output, '{}.png'.format(k)))




def shapefile_extract(shapefile_pd, max_depletion, nrcs_taw):
    """"""
    array_dictonary = {}
    for k, v in shapefile_pd.iteritems():
        print 'shapefile {}'.format(k)

        with fiona.open(v) as shp:
            geometry = [feature['geometry'] for feature in shp]


        with rasterio.open(max_depletion) as max_dep:
            max_dep_image, max_dep_transform = rasterio.mask.mask(max_dep, geometry, crop=True)
            # print 'this is the image for max dep :', max_dep_image
            # print 'type {}'.format(type(max_dep_image))
            # print 'shape {}'.format(max_dep_image.shape)


        with rasterio.open(nrcs_taw) as taw:
            taw_image, taw_transform = rasterio.mask.mask(taw, geometry, crop=True)

        tup = (max_dep_image.ravel(), taw_image.ravel())

        array_dictonary[k] = tup

    return array_dictonary



def main(shpfile_pd, max_depletion, nrcs_taw, plot_output):
    """"""

    # return dict of -> 'shapefile_name': (depletion_arr, nrcs_taw_arr)
    print 'extracting'
    array_dictionary = shapefile_extract(shpfile_pd, max_depletion, nrcs_taw)

    # take the dict into a plotter that makes plots for each one...
    xy_plotter(array_dictionary, plot_output=plot_output)


if __name__ == "__main__":

    root = "/Volumes/Seagate_Expansion_Drive"
    # get paths to all the shapefiles, package in dictionary
    shapefile_root = os.path.join(root, 'SSEBop_research/xy_plotting_polygons')

    shapefile_dict = {}
    for file in os.listdir(shapefile_root):
        print 'file', file
        if file.endswith('.shp'):
            path = os.path.join(shapefile_root, file)
            name = file.split('.')[0]
            shapefile_dict[name] = path

    # # get path to the max_depletion raster
    # max_dep_neg_corr = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/cum_depletions_neg_mod/' \
    #                    'max_depletion_2000_2013.tif'
    # # this one only is positive depletions for ETRM
    # max_dep_neg_corr = '/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/' \
    #                    'ETRM_cumulative_depletions_research/ETRM_WA_pos_only/pyrana_max_depletion_2001_2013.tif'
    # this one is for positive depletions from 1.25*NDVI
    max_dep_neg_corr = '/Volumes/Seagate_Expansion_Drive/Esther_Results_mult_runs_monthly_annually/' \
                       'ETRM_cumulative_depletions_research/ndvi_WA/ndvi_WA_pos_only/' \
                       'alfalfa_positive_max_depletion_2000_2013.tif'


    # get path to the NRCS TAW raster
    nrcs_taw_path = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/statics/taw_mod_4_21_10_0.tif'

    # where to output plots
    plot_output = os.path.join(shapefile_root, 'plots_alfalfa')


    main(shapefile_dict, max_dep_neg_corr, nrcs_taw_path, plot_output=plot_output)