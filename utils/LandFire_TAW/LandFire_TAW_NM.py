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
import numpy as np
from matplotlib import pyplot as plt
# ============= local library imports ===========================
from recharge.raster_tools import convert_raster_to_array
from utils.depletions_modeling.cumulative_depletions import write_raster
from utils.LandFire_TAW.landfire_raster_reclass import get_raster_geo

def get_codes(eco_path):
    """"""
    codes_lst = []
    with open(eco_path, 'r') as rfile:
        for line in rfile:
            # print 'line\n', line

            line_lst = line.split(',')
            if line_lst[0].isdigit():
                codes_lst.append((line_lst[0], line_lst[1], float(line_lst[6])))

    codes = set(codes_lst)
    return codes

def generate_histograms(codes, landfire_arr, ndvi_arr, outinfo):

    print landfire_arr.shape
    print ndvi_arr.shape

    outpath, outname = outinfo

    value_holder = []
    code_holder = []

    for code in codes:

        raster_val = int(code[0])
        eco_name = code[1]

        fig_name = outname.format(raster_val, eco_name)
        print 'fig name: ', fig_name
        fig_output = os.path.join(outpath, fig_name)

        box_name = 'box_{}_{}'.format(raster_val, eco_name)
        box_output = os.path.join(outpath, box_name)

        # landfire_vals = landfire_arr[landfire_arr == raster_val]
        ndvi_vals = ndvi_arr[landfire_arr == raster_val]

        # print landfire_vals
        print ndvi_vals

        hist_bins = []
        start = -0.15
        step = 0.01
        end = 0.85
        steps = int((end - start)/step)
        for i in range(steps + 1):
            hist_bins.append(start + (i * step))

        print 'bins for the histograms \n', hist_bins
        # [-0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.8, 0.9]
        # Make the histogram
        fig1, ax1 = plt.subplots()
        ax1.hist(ndvi_vals, bins=hist_bins, color='green')
        ax1.set_title('NDVI counts {}'.format(eco_name))
        # plt.show()

        fig1.savefig(fig_output)

        # box and whiskers
        fig2, ax2 = plt.subplots()
        ax2.boxplot(ndvi_vals)
        ax2.set_title('NDVI {}'.format(eco_name))
        fig2.savefig(box_output)

        # to plot all the boxplots on the same level, add
        value_holder.append(ndvi_vals)
        code_holder.append(code[0])

    # Plot all boxplots together for direct comparison
    boxfig, box_ax = plt.subplots()
    box_ax.boxplot(value_holder, labels=code_holder)
    box_ax.set_ylim(-.2, .75)
    box_ax.set_title('Ecosystem Boxplots')
    boxfig.savefig('/Users/dcadol/Desktop/academic_docs_II/LandFire/python_plots/histograms/allboxes')

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def get_ndvi_stats(codes, landfire_arr, ndvi_arr, csv=False, threshold_95=False):
    """"""
    ndvi_stats_dict = {}
    # the codes are a list of tuples of ('codestring', 'econame')
    for code in codes:
        print code

        raster_val = int(code[0])
        # print 'raster val', raster_val
        eco_name = code[1]
        # print 'econame', eco_name

        ndvi_vals = ndvi_arr[landfire_arr == raster_val]

        # # only keep vals where the ndvi is positive
        # ndvi_vals = ndvi_vals[ndvi_vals > 0]
        # stats = (np.min(ndvi_vals), np.max(ndvi_vals), np.average(ndvi_vals), eco_name)

        if threshold_95:
            # The upper and lower limit of the boxplots. 95% confidence interval, values within 1.5 * iqr are the whiskers
            upper_95 = np.percentile(ndvi_vals, 95)
            lower_5 = np.percentile(ndvi_vals, 5)

            # stats = (lower_5, upper_95, np.average(ndvi_vals), eco_name)
            stats = (lower_5, upper_95, np.percentile(ndvi_vals, 50), eco_name)
            ndvi_stats_dict['{}'.format(raster_val)] = stats

        else:

            # todo - this old version allows some ecosystems to go above the max where NDVI is overall higher than third quartile at edge of high mountains
            lower_5 = np.percentile(ndvi_vals, 5)
            third_quartile = np.percentile(ndvi_vals, 75)
            stats = (lower_5, third_quartile, np.percentile(ndvi_vals, 50), eco_name)
            ndvi_stats_dict['{}'.format(raster_val)] = stats

            # lower = np.min(ndvi_vals)
            # upper = np.max(ndvi_vals)
            # stats = (lower, upper, np.percentile(ndvi_vals, 50), eco_name)
            # ndvi_stats_dict['{}'.format(raster_val)] = stats

            # lower = np.percentile(ndvi_vals, 5)
            # upper = np.percentile(ndvi_vals, 95)
            # stats = (lower, upper, np.percentile(ndvi_vals, 50), eco_name)
            # ndvi_stats_dict['{}'.format(raster_val)] = stats

    return ndvi_stats_dict


def ndvi_histogramer(eco_path, ndvi_path, lf_path, outinfo):
    """
    Output histograms of the NDVI for every reclassified LandFire ecosystem grouping
    :param eco_path:
    :param lf_path:
    :param outinfo:
    :return:
    """

    # parse the eco path. Get the name and code for each re-classifed ecosystem category. returns a SET object containing unique code and econames tuples
    codes = get_codes(eco_path)

    # read in the ndvi and landfire_images
    landfire_arr = convert_raster_to_array(lf_path)
    ndvi_arr = convert_raster_to_array(ndvi_path)

    # set about generating the histogram, also boxplots
    generate_histograms(codes, landfire_arr, ndvi_arr, outinfo)

    # return (min, max, avg, eco) for each ecosystem in a dict. Key is eco_code
    ndvi_stats_dict = get_ndvi_stats(codes, landfire_arr, ndvi_arr)

    # Output the stats to a .csv
    filename = 'stats_values.csv'
    outpath = outinfo[0]
    stats_path = os.path.join(outpath, filename)
    with open(stats_path, 'w') as wfile:
        for key, val in ndvi_stats_dict.iteritems():
            wfile.write('{},{},{},{},{}\n'.format(key, val[0], val[1], val[2], val[3]))


def sandvig_rootzone_interpolation(avg_rooting_depth, rd_ecotone_1, rd_ecotone2, avg_ndvi, ndvi_high, ndvi_low, ndvi_arr, root_depth_array, landfire_array, ecosystem_code):
    """"""

    print 'Interpolation info for ecosystem {}'.format(ecosystem_code)
    # Set the slope for the linear adjustment for NDVI < avg NDVI AKA m1
    if avg_rooting_depth < rd_ecotone_1:
        print 'slope is negative for rd1 and m1 should be negative'
        m1 = (avg_rooting_depth - rd_ecotone_1)/(avg_ndvi - ndvi_low)
    elif avg_rooting_depth > rd_ecotone_1:
        print 'slope is positive for rd1 and m1 should be positive'
        m1 = (avg_rooting_depth - rd_ecotone_1)/(avg_ndvi - ndvi_low)
    # Set the slope for the linear adjustment for NDVI > avg NDVI AKA m2
    if avg_rooting_depth < rd_ecotone2:
        print 'slope is positive for rd2 and m2 should be positive'
        m2 = (rd_ecotone2 - avg_rooting_depth)/(ndvi_high - avg_ndvi)
    elif avg_rooting_depth > rd_ecotone2:
        print 'slope is negative for rd2 and m2 should be negative'
        m2 = (rd_ecotone2 - avg_rooting_depth) / (ndvi_high - avg_ndvi)


    print 'm1 is {}'.format(m1)
    print 'm2 is {}'.format(m2)

    # initialize rd1 and rd2 to be the changing root_depth array
    # we do this in order to preserve the changes you made in the previous interpolation runs
    # rd1 = root_depth_array
    # rd2 = root_depth_array
    rd1 = np.empty(ndvi_arr.shape)
    rd2 = np.empty(ndvi_arr.shape)
    # rd1 = np.ones(ndvi_arr.shape)
    # rd2 = np.ones(ndvi_arr.shape)

    # rd1[landfire_array == ecosystem_code] = (m1* ndvi_arr[landfire_array == ecosystem_code]) + avg_ndvi
    # rd2[landfire_array == ecosystem_code] = (m2 * ndvi_arr[landfire_array == ecosystem_code]) + avg_ndvi
    print 'rd1 intercept is {}'.format(rd_ecotone_1)
    print 'rd2 intercept is {}'.format(avg_rooting_depth)
    rd1[landfire_array == ecosystem_code] = (m1 * (ndvi_arr[landfire_array == ecosystem_code] - ndvi_low)) + rd_ecotone_1
    rd2[landfire_array == ecosystem_code] = (m2 * (ndvi_arr[landfire_array == ecosystem_code] - avg_ndvi)) + avg_rooting_depth

    root_depth_array[ndvi_arr < avg_ndvi] = rd1[ndvi_arr < avg_ndvi]
    root_depth_array[ndvi_arr > avg_ndvi] = rd2[ndvi_arr > avg_ndvi]

    return root_depth_array


def ndvi_rootzone_interpolation(taw_arr, stats_dict, codes, landfire_arr, ndvi_arr, porosity, tew_arr):
    """

    :param max_taw_arr:
    :param stats_dict:
    :param codes:
    :param landfire_arr:
    :param ndvi_arr:
    :return:
    """

    # convert tew to meters
    tew_arr = tew_arr/1000

    for code in codes:
        print 'code is {} for ecosystem {} and has rooting value of {}'.format(code[0], code[1], code[2])
        stats_key = code[0]
        econame = code[1]
        landfire_code = int(code[0])

        eco_root_depth = code[2]

        # check to make sure that the maxTAW > TEW else TAW = TEW

        max_taw = eco_root_depth * porosity
        print 'max taw val', max_taw

        print landfire_arr.shape

        max_taw_arr = np.zeros(landfire_arr.shape)
        max_taw_arr = max_taw_arr + max_taw

        print 'average', np.median(max_taw_arr)

        # We set the max_taw = tew when the TEW (lower limit) > MAX_TAW(upper limit)
        max_taw_arr[(landfire_arr == landfire_code) & (max_taw_arr < tew_arr)] = tew_arr[(landfire_arr == landfire_code) & (max_taw_arr < tew_arr)]
        print max_taw_arr.shape

        ndvi_stats_tuple = stats_dict[stats_key]

        ndvi_max_stat = ndvi_stats_tuple[1]
        ndvi_min_stat = ndvi_stats_tuple[0]

        # # testing
        # ndvi_max_stat = 0.75
        # ndvi_min_stat = 0.01

        ## deprecated.
        # root_depth_arr[landfire_arr == landfire_code] = ((ndvi_max_stat - ndvi_arr[landfire_arr==landfire_code])/(ndvi_max_stat - ndvi_min_stat)) * (eco_root_depth)

        print ndvi_arr.shape, max_taw_arr.shape, tew_arr.shape, landfire_arr.shape, tew_arr.shape

        # keep Dan's code, but subtract NDVI - NDVI min statistic in numerator instead of subtracting from the max.
        # scale TAW based on NDVI
        taw_arr[landfire_arr == landfire_code] = ((ndvi_arr[landfire_arr == landfire_code] - ndvi_min_stat) / (ndvi_max_stat - ndvi_min_stat))\
                                                 * (max_taw_arr[landfire_arr == landfire_code] - tew_arr[landfire_arr == landfire_code]) \
                                                 + tew_arr[landfire_arr == landfire_code]

        # Limit TAW values to the maximum if NDVI > Max Statistic
        taw_arr[(landfire_arr == landfire_code) & (ndvi_arr > ndvi_max_stat)] = max_taw_arr[(landfire_arr == landfire_code) & (ndvi_arr > ndvi_max_stat)]

        # Limit TAW values to the minimum if NDVI < Min Statistic
        taw_arr[(landfire_arr == landfire_code) & (ndvi_arr < ndvi_min_stat)] = tew_arr[(landfire_arr == landfire_code) & (ndvi_arr < ndvi_min_stat)]


    return taw_arr


def sandvig_phillips_root_zone(lf_path, ndvi_path, eco_path=None, outinfo=None, landfire_geo=None):
    """"""
    # read in the ndvi and landfire_images
    landfire_arr = convert_raster_to_array(lf_path)
    ndvi_arr = convert_raster_to_array(ndvi_path)

    codes = get_codes(eco_path)
    # function that determines NDVI stats (average, 3rd quartile high and 1st quartile low) for each ecosysetm
    stats_dict = get_ndvi_stats(codes, landfire_arr, ndvi_arr, threshold_95=True)

    # root_zone_arr = np.empty(landfire_arr.shape)
    root_zone_arr = np.zeros(landfire_arr.shape)

    # The rooting depths for the neighboring ecosystems
    bare_rd = 0.0
    creosote_rd = 3.0
    grass_rd = 2.0
    pj_rd = 4.0
    ponderosa_fir_rd = 3.0
    mountain_grass_rd = 2.0

    # === Riparian Zone ===
    # Riparian zones, wetlands and ag are assigned an arbitrarily large root zone.
    root_zone_arr[landfire_arr == 7] = 9.0

    # === interpolate between Bare, Creosote_shrub and Grass ===

    # ecosystem codes for each ecosystem.
    creosote_shrubs_code = '2'
    print 'stats dict\n', stats_dict
    creosote_shrubs_stats = stats_dict[creosote_shrubs_code]
    creosote_ndvi_low = creosote_shrubs_stats[0]
    creosote_ndvi_high = creosote_shrubs_stats[1]
    creosote_ndvi_avg = creosote_shrubs_stats[2]

    print 'creosote low {}, creosote high {}, creosote average {}'.format(creosote_ndvi_low, creosote_ndvi_high,
                                                                          creosote_ndvi_avg)

    root_zone_arr = sandvig_rootzone_interpolation(avg_rooting_depth=creosote_rd, rd_ecotone_1=bare_rd, rd_ecotone2=grass_rd,
                                                   avg_ndvi=creosote_ndvi_avg, ndvi_high=creosote_ndvi_high,
                                                   ndvi_low=creosote_ndvi_low, ndvi_arr=ndvi_arr,
                                                   root_depth_array=root_zone_arr, landfire_array=landfire_arr,
                                                   ecosystem_code=2)

    write_raster(root_zone_arr, landfire_geo['geotransform'], outinfo[0], outinfo[1].format(creosote_shrubs_code),
                 (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])

    # === interpolate between Creosote_shrub, Grass and PJ ===


    grass_code = '3'
    grass_stats = stats_dict[grass_code]
    grass_ndvi_low = grass_stats[0]
    grass_ndvi_high = grass_stats[1]
    grass_ndvi_avg = grass_stats[2]

    print 'grass low {}, grass high {}, grass average {}'.format(grass_ndvi_low, grass_ndvi_high,
                                                                          grass_ndvi_avg)

    root_zone_arr = sandvig_rootzone_interpolation(avg_rooting_depth=grass_rd, rd_ecotone_1=creosote_rd, rd_ecotone2=pj_rd,
                                                   avg_ndvi=grass_ndvi_avg, ndvi_high=grass_ndvi_high,
                                                   ndvi_low=grass_ndvi_low, ndvi_arr=ndvi_arr,
                                                   root_depth_array=root_zone_arr, landfire_array=landfire_arr, ecosystem_code=3)
    write_raster(root_zone_arr, landfire_geo['geotransform'], outinfo[0], outinfo[1].format(grass_code),
                 (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])

    # === interpolate between Grass, PJ and Ponderosa/Fir ===
    pj_code = '4'
    pj_stats = stats_dict[pj_code]
    pj_ndvi_low = pj_stats[0]
    pj_ndvi_high = pj_stats[1]
    pj_ndvi_avg = pj_stats[2]

    root_zone_arr = sandvig_rootzone_interpolation(avg_rooting_depth=pj_rd, rd_ecotone_1=grass_rd, rd_ecotone2=ponderosa_fir_rd,
                                                   avg_ndvi=pj_ndvi_avg, ndvi_high=pj_ndvi_high,
                                                   ndvi_low=pj_ndvi_low, ndvi_arr=ndvi_arr,
                                                   root_depth_array=root_zone_arr, landfire_array=landfire_arr, ecosystem_code=4)
    write_raster(root_zone_arr, landfire_geo['geotransform'], outinfo[0], outinfo[1].format(pj_code),
                 (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])

    # === interpolate between PJ, Ponderosa/Fir and mountain_grass ===
    ponderosa_fir_code = '5'
    ponderosa_fir_stats = stats_dict[ponderosa_fir_code]
    ponderosa_fir_ndvi_low = ponderosa_fir_stats[0]
    ponderosa_fir_ndvi_high = ponderosa_fir_stats[1]
    ponderosa_fir_ndvi_avg = ponderosa_fir_stats[2]

    root_zone_arr = sandvig_rootzone_interpolation(avg_rooting_depth=ponderosa_fir_rd, rd_ecotone_1=pj_rd, rd_ecotone2=mountain_grass_rd,
                                                   avg_ndvi=ponderosa_fir_ndvi_avg, ndvi_high=ponderosa_fir_ndvi_high,
                                                   ndvi_low=ponderosa_fir_ndvi_low, ndvi_arr=ndvi_arr,
                                                   root_depth_array=root_zone_arr, landfire_array=landfire_arr, ecosystem_code=5)
    write_raster(root_zone_arr, landfire_geo['geotransform'], outinfo[0], outinfo[1].format(ponderosa_fir_code),
                 (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])

    # === interpolate between bare, mountain_grass and ponderosa_fir ===
    # (the order is changed to account for least to greatest NDVI)
    mountain_grass_code = '6'
    mountain_grass_stats = stats_dict[mountain_grass_code]
    mountain_grass_ndvi_low = mountain_grass_stats[0]
    mountain_grass_ndvi_high = mountain_grass_stats[1]
    mountain_grass_ndvi_avg = mountain_grass_stats[2]

    root_zone_arr = sandvig_rootzone_interpolation(avg_rooting_depth=mountain_grass_rd, rd_ecotone_1=bare_rd,
                                                   rd_ecotone2=ponderosa_fir_rd,
                                                   avg_ndvi=mountain_grass_ndvi_avg, ndvi_high=mountain_grass_ndvi_high,
                                                   ndvi_low=mountain_grass_ndvi_low, ndvi_arr=ndvi_arr,
                                                   root_depth_array=root_zone_arr, landfire_array=landfire_arr, ecosystem_code=6)
    write_raster(root_zone_arr, landfire_geo['geotransform'], outinfo[0], outinfo[1].format(mountain_grass_code),
                 (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])

    return root_zone_arr


def ndvi_taw_scaling(lf_path=None, ndvi_path=None, eco_path=None, tew_path=None, outinfo=None, landfire_geo=None, porosity=0.2, output_path=None):
    """

    :param lf_path:
    :param ndvi_path: All time 13 year average ndvi statistic starting in the year 2000 from modis
    :param eco_path: configuration file defining ranges of values for reclassified LandFire Raster eco-parameters
     (effective rooting depth from chloride concentration SandvigPhillips)
    :param outinfo:
    :param landfire_geo:
    :return:
    """

    # read in the ndvi and landfire_images
    landfire_arr = convert_raster_to_array(lf_path)
    ndvi_arr = convert_raster_to_array(ndvi_path)

    codes = get_codes(eco_path)
    # function that determines NDVI stats (average, 3rd quartile high and 1st quartile low) for each ecosysetm
    stats_dict = get_ndvi_stats(codes, landfire_arr, ndvi_arr)

    print 'stats dict \n', stats_dict

    taw_arr = np.zeros(landfire_arr.shape)

    # read in the tew array (total EVAPORABLE water)
    tew_arr = convert_raster_to_array(tew_path)

    # do a linear interpolation of root zone based on ndvi statistics (total AVAILABLE water)
    taw_arr = ndvi_rootzone_interpolation(taw_arr, stats_dict, codes, landfire_arr, ndvi_arr, porosity, tew_arr)

    # output the array as a raster
    output_name = 'taw_linear_ecomodel.tif'

    write_raster(taw_arr, landfire_geo['geotransform'], output_path, output_name, (landfire_geo['cols'],
                                                                                   landfire_geo['rows']),
                 landfire_geo['projection'])



if __name__ == "__main__":

    # # path to the codes, counts and ecosystem names for the Landfire Dataset.
    # # ...File produced by Landfire_Eco_Stringparse.py
    # eco_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/grouped_lf_rasters/landfire_reclassification/LandFire_Reclass_Combine_Sandvig_config.csv'
    #
    # # path to the 13 year average NDVI. Produced by ndvi_processing.py -> then warped using nearest neighbor to LandFire extent and resolution (30x30)
    # ndvi_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/NDVI_parameters/all_time_avg_ndvi_warp.tif'
    #
    # # path to the re-classified raster produced by landfire_raster_reclass.py
    # lf_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/grouped_lf_rasters/grouped_landfire_rasters/gabe_reclass_march_2.tif'
    # # get the geo information for the raster
    # landfire_geo = get_raster_geo(lf_path)
    #
    # # ====== User-Defined Output path ======
    # outpath = '/Users/dcadol/Desktop/academic_docs_II/LandFire/python_plots/histograms'
    # # to add the ecosystem number code and name from the .csv
    # outname = 'ndvi_hist_{}_{}'
    #
    # # outfile = os.path.join(outpath, outname)
    # outinfo = [outpath, outname]
    #
    # # ndvi_histogramer(eco_path, ndvi_path, lf_path, outinfo)
    # # # Todo - make box and whisker plots for the elevations of each eco-class
    #
    # # TODO - come up with algorithm to scale rooting depth by NDVI based on avg ndvi between adjoining ecotones
    # # first, plot where the averages are in relation to each other, are they distinct?
    #
    # # Do a simpler algorithm where min, max and avg rooting depth from the literature are scaled by min, max, avg NDVI
    #
    # outinfo = [outpath, 'sandvig_phillips_rd_{}.tif']
    #
    # root_zone_array = sandvig_phillips_root_zone(lf_path, ndvi_path, eco_path=eco_path, outinfo=outinfo, landfire_geo=landfire_geo)

    # path to the codes, counts and ecosystem names for the Landfire Dataset.
    # ...File produced by Landfire_Eco_Stringparse.py

    eco_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/grouped_lf_rasters/landfire_reclassification/LandFire_Reclass_Combine_Sandvig_config.csv'

    # path to the 13 year average NDVI. Produced by ndvi_processing.py -> then warped using nearest neighbor to LandFire extent and resolution (30x30)
    ndvi_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/NDVI_parameters/all_time_avg_ndvi_warp.tif'

    # path to the re-classified raster produced by landfire_raster_reclass.py
    lf_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/grouped_lf_rasters/grouped_landfire_rasters/gabe_reclass_march_2.tif'
    # get the geo information for the raster
    landfire_geo = get_raster_geo(lf_path)

    # tew for lower evap limit layer
    tew_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/tew_warp/tew_warp.tif'

    # ====== User-Defined Output path ======
    outpath = '/Users/dcadol/Desktop/academic_docs_II/LandFire/python_plots/histograms'
    # to add the ecosystem number code and name from the .csv
    outname = 'ndvi_hist_{}_{}'

    # outfile = os.path.join(outpath, outname)
    outinfo = [outpath, outname]

    raster_output = '/Users/dcadol/Desktop/academic_docs_II/LandFire/ndvi_linear'


    ndvi_taw_scaling(lf_path, ndvi_path, eco_path=eco_path, outinfo=outinfo, tew_path=tew_path, landfire_geo=landfire_geo, output_path=raster_output)

    # write_raster(root_zone_array, landfire_geo['geotransform'], outinfo[0], outinfo[1],
    #              (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])

