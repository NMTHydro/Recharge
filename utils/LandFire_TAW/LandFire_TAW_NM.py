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
                # codes_lst.append((line_lst[0], line_lst[1], float(line_lst[6])))
                codes_lst.append((line_lst[0], line_lst[5], float(line_lst[6])))

    codes = set(codes_lst)
    return codes


def generate_swhc_histograms(codes, landfire_arr, swhc_arr, outinfo):
    """"""
    print landfire_arr.shape
    print swhc_arr.shape

    outpath, outname = outinfo
    outname = 'swhc'

    value_holder = []
    code_holder = []

    for code in codes:
        raster_val = int(code[0])
        eco_name = code[1]
        swhc_vals = swhc_arr[landfire_arr == raster_val]

        swhc_vals[swhc_vals <= 0] = 0

        value_holder.append(swhc_vals)
        code_holder.append(code[0])

    names = []

    for code in code_holder:

        if code == 1 or code == '1':
            n = 'Bare'
        elif code == 2 or code == '2':
            n = 'Shrub'
        elif code == 3 or code == '3':
            n = 'Grass'
        elif code == 4 or code == '4':
            n = 'Pinyon-Juniper'
        elif code == 5 or code == '5':
            n = 'Ponderosa-Mixed Conifer'
        elif code == 6 or code == '6':
            n = 'Mountain Grass'
        elif code == 7 or code == '7':
            n = 'Ag-R-Wet'
        elif code == 8 or code == '8':
            n = 'Prairie'
        elif code == 9 or code == '9':
            n = 'Creosotebush'
        else:
            n = code

        names.append(n)

    # Plot all boxplots together for direct comparison
    boxfig, box_ax = plt.subplots()
    box_ax.boxplot(value_holder, labels=names)
    # box_ax.set_ylim(0, 10000)
    box_ax.set_title('Ecosystem SWHC')
    box_ax.set_ylabel('Ecosystem SWHC (mm)')
    plt.show()
    boxfig.savefig('/Users/dcadol/Desktop/academic_docs_II/LandFire/python_plots/histograms/allboxes')


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

        ndvi_vals = ndvi_arr[landfire_arr == raster_val]

        value_holder.append(ndvi_vals)
        code_holder.append(code[0])

    names = []

    for code in code_holder:

        if code == 1 or code == '1':
            n = 'Bare'
        elif code == 2 or code == '2':
            n = 'Shrub'
        elif code == 3 or code == '3':
            n = 'Grass'
        elif code == 4 or code == '4':
            n = 'Pinyon-Juniper'
        elif code == 5 or code == '5':
            n = 'Ponderosa-Mixed Conifer'
        elif code == 6 or code == '6':
            n = 'Mountain Grass'
        elif code == 7 or code == '7':
            n = 'Ag-R-Wet'
        elif code == 8 or code == '8':
            n = 'Prairie'
        elif code == 9 or code == '9':
            n = 'Creosotebush'
        else:
            n = code

        names.append(n)

    # Plot all boxplots together for direct comparison
    boxfig, box_ax = plt.subplots()
    box_ax.boxplot(value_holder, labels=names)
    box_ax.set_ylim(-.2, .75)
    box_ax.set_title('Ecosystem NDVI Boxplots')
    box_ax.set_ylabel('Ecosystem NDVI')
    plt.show()
    boxfig.savefig('/Users/dcadol/Desktop/academic_docs_II/LandFire/python_plots/histograms/allboxes')

    return codes, names, value_holder

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

        if threshold_95:
            # The upper and lower limit of the boxplots. 95% confidence interval, values within 1.5 * iqr are the whiskers
            upper_95 = np.percentile(ndvi_vals, 95)
            lower_5 = np.percentile(ndvi_vals, 5)

            # stats = (lower_5, upper_95, np.average(ndvi_vals), eco_name)
            stats = (lower_5, upper_95, np.percentile(ndvi_vals, 50), eco_name)
            ndvi_stats_dict['{}'.format(raster_val)] = stats

        else:

            # this version allows some ecosystems to go above the max where NDVI is overall higher than third quartile at edge of high mountains
            lower_5 = np.percentile(ndvi_vals, 5)
            third_quartile = np.percentile(ndvi_vals, 75)
            stats = (lower_5, third_quartile, np.percentile(ndvi_vals, 50), np.percentile(ndvi_vals, 1), eco_name)
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
    codes, names, value_holder = generate_histograms(codes, landfire_arr, ndvi_arr, outinfo)

    # return (min, max, avg, eco) for each ecosystem in a dict. Key is eco_code
    ndvi_stats_dict = get_ndvi_stats(codes, landfire_arr, ndvi_arr)

    # Output the stats to a .csv
    filename = 'stats_values.csv'
    outpath = outinfo[0]
    stats_path = os.path.join(outpath, filename)
    with open(stats_path, 'w') as wfile:
        for key, val in ndvi_stats_dict.iteritems():
            wfile.write('{},{},{},{},{}\n'.format(key, val[0], val[1], val[2], val[3]))

    return codes, names, value_holder



def ndvi_rootzone_interpolation(taw_arr, stats_dict, codes, landfire_arr, ndvi_arr, porosity, tew_arr):
    """

    :param taw_arr:
    :param stats_dict:
    :param codes:
    :param landfire_arr:
    :param ndvi_arr:
    :return:
    """

    # initialize the fractional term array to hold fraction values to show reduction of max TAW by NDVI
    fraction_arr = np.ones(landfire_arr.shape)


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

        # We set the max_taw = tew when the TEW (lower limit) > MAX_TAW(upper limit)
        max_taw_arr[(landfire_arr == landfire_code) & (max_taw_arr < tew_arr)] = tew_arr[(landfire_arr == landfire_code) & (max_taw_arr < tew_arr)]
        print max_taw_arr.shape

        ndvi_stats_tuple = stats_dict[stats_key]

        # TODO - This is a major adjustment that can change how the TAW modeled with Landfire Behaves.
        # 75th percentile
        ndvi_max_stat = ndvi_stats_tuple[1]
        # # 5th percentile
        # ndvi_min_stat = ndvi_stats_tuple[0]

        ## ==== Specialized stats settings Dan and Gabe July 29 to boost TAW in certain areas especially Creosote
        # ndvi_min_stat = 0.1
        # refers to the 1 percentile instead of fifth percentile
        ndvi_min_stat = ndvi_stats_tuple[3]


        ## deprecated.
        # root_depth_arr[landfire_arr == landfire_code] = ((ndvi_max_stat - ndvi_arr[landfire_arr==landfire_code])/(ndvi_max_stat - ndvi_min_stat)) * (eco_root_depth)

        print ndvi_arr.shape, max_taw_arr.shape, tew_arr.shape, landfire_arr.shape, tew_arr.shape

        # We treat Creosote as special and we linearly interpolate to median instead of 75th percentile
        if landfire_code == 9:

            ndvi_max_stat = ndvi_stats_tuple[2]


        # keep Dan's code, but subtract NDVI - NDVI min statistic in numerator instead of subtracting from the max.
        # scale TAW based on NDVI
        taw_arr[landfire_arr == landfire_code] = ((ndvi_arr[landfire_arr == landfire_code] - ndvi_min_stat) / (ndvi_max_stat - ndvi_min_stat))\
                                                 * (max_taw_arr[landfire_arr == landfire_code] - tew_arr[landfire_arr == landfire_code]) \
                                                 + tew_arr[landfire_arr == landfire_code]

        # Limit TAW values to the maximum if NDVI > Max Statistic
        taw_arr[(landfire_arr == landfire_code) & (ndvi_arr > ndvi_max_stat)] = max_taw_arr[(landfire_arr == landfire_code) & (ndvi_arr > ndvi_max_stat)]

        # Limit TAW values to the minimum if NDVI < Min Statistic
        taw_arr[(landfire_arr == landfire_code) & (ndvi_arr < ndvi_min_stat)] = tew_arr[(landfire_arr == landfire_code) & (ndvi_arr < ndvi_min_stat)]

        fraction_arr[landfire_arr == landfire_code] = (ndvi_arr[landfire_arr == landfire_code] - ndvi_min_stat) / (ndvi_max_stat - ndvi_min_stat)

    return taw_arr, fraction_arr


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

    print 'codes \n', codes

    # function that determines NDVI stats (average, 3rd quartile high and 1st quartile low) for each ecosysetm
    stats_dict = get_ndvi_stats(codes, landfire_arr, ndvi_arr)

    print 'stats dict \n', stats_dict

    taw_arr = np.zeros(landfire_arr.shape)

    # read in the tew array (total EVAPORABLE water)
    tew_arr = convert_raster_to_array(tew_path)

    # do a linear interpolation of root zone based on ndvi statistics (total AVAILABLE water)
    taw_arr, fraction_arr = ndvi_rootzone_interpolation(taw_arr, stats_dict, codes, landfire_arr, ndvi_arr, porosity, tew_arr)

    # output the array as a raster
    output_name = 'taw_linear_ecomodel_DG.tif'

    write_raster(taw_arr, landfire_geo['geotransform'], output_path, output_name, (landfire_geo['cols'],
                                                                                   landfire_geo['rows']),
                 landfire_geo['projection'])

    write_raster(fraction_arr, landfire_geo['geotransform'], output_path, '{}.tif'.format(output_name.split('.')[0]), (landfire_geo['cols'],
                                                                                   landfire_geo['rows']),
                 landfire_geo['projection'])

    generate_swhc_histograms(codes, landfire_arr, taw_arr, outinfo=outinfo)



if __name__ == "__main__":

    # path to the grouped Landfire ecosystems (full filepaths)
    eco_path = '/Volumes/Seagate_Blue/LandFire/grouped_lf_rasters/landfire_reclassification/LandFire_Reclass_Combine_Sandvig_config_DGedit.csv'

    # path to the 13 year average NDVI. Produced by ndvi_processing.py -> then warped using nearest neighbor to LandFire extent and resolution (30x30)
    ndvi_path = 'Volumes/Seagate_Blue/LandFire/NDVI_parameters/all_time_avg_ndvi_warp.tif'

    # path to the re-classified raster produced by landfire_raster_reclass.py
    lf_path = 'Volumes/Seagate_Blue/LandFire/grouped_lf_rasters/grouped_landfire_rasters/gabe_reclass_july_24.tif'
    # get the geo information for the raster
    landfire_geo = get_raster_geo(lf_path)

    # tew for lower evap limit layer
    tew_path = 'Volumes/Seagate_Blue/LandFire/tew_warp/tew_warp.tif'

    # ====== User-Defined Output path ======
    outpath = 'Volumes/Seagate_Blue/LandFire/python_plots/histograms'
    # to add the ecosystem number code and name from the .csv
    outname = 'ndvi_hist_{}_{}'

    # outfile = os.path.join(outpath, outname)
    outinfo = [outpath, outname]

    raster_output = 'Volumes/Seagate_Blue/LandFire/thesis_res'
    if not os.path.exists(raster_output):
        os.mkdir(raster_output)

    codes, names, value_holder = ndvi_histogramer(eco_path, ndvi_path, lf_path, outinfo)


    ndvi_taw_scaling(lf_path, ndvi_path, eco_path=eco_path, outinfo=outinfo, tew_path=tew_path, landfire_geo=landfire_geo, output_path=raster_output)

