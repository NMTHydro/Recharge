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
from numpy import linspace, array, insert, ones, divide
from pandas import DataFrame
from ogr import Open
from datetime import datetime

from recharge.time_series_manager import get_etrm_time_series
from recharge.etrm_processes import Processes


# Set start datetime object
SIMULATION_PERIOD = datetime(2000, 1, 1), datetime(2013, 12, 31)

FACTORS = ['Temperature', 'Precipitation', 'Reference ET', 'Total Available Water (TAW)',
           'Vegetation Density (NDVI)', 'Soil Ksat']


def round_to_value(number, roundto):
    return round(number / roundto) * roundto


def get_sensitivity_analysis(extracts, points, statics, initials, pickle=None):

    temps = range(-5, 6)
    all_pct = [x * 0.1 for x in range(5, 16)]
    ndvi_range = linspace(0.9, 1.7, 11)
    ndvi_range = array([round_to_value(x, 0.05) for x in ndvi_range])
    var_arrs = []
    y = 0
    for x in range(0, 6):
        ones_ = ones((5, 11), dtype=float)
        zeros = [x * 0.0 for x in range(5, 16)]
        norm_ndvi = array([1.25 for x in zeros])
        if y == 0:
            arr = insert(ones_, y, temps, axis=0)
            arr = insert(arr, 4, norm_ndvi, axis=0)
            arr = arr[0:6]
            var_arrs.append(arr)
            arr = []
        elif y == 4:
            arr = insert(ones_, 0, zeros, axis=0)
            arr = insert(arr, y, ndvi_range, axis=0)
            arr = arr[0:6]
            var_arrs.append(arr)
            print('shape arr: {}'.format(arr.shape))
            arr = []
        elif y == 5:
            arr = insert(ones_, 0, zeros, axis=0)
            arr = insert(arr, 4, norm_ndvi, axis=0)
            arr = arr[0:5]
            arr = insert(arr, y, all_pct, axis=0)
            var_arrs.append(arr)
            arr = []
        else:
            arr = insert(ones_, 0, zeros, axis=0)
            arr = insert(arr, y, all_pct, axis=0)
            arr = insert(arr, 4, norm_ndvi, axis=0)
            arr = arr[0:6]
            var_arrs.append(arr)
            arr = []
        y += 1

    print('variable arrays: {}'.format(var_arrs))
    normalize_list = [2, 0.20, 0.20, 2, 0.20, 0.50]

    # site_list = ['Bateman', 'Navajo_Whiskey_Ck', 'Quemazon', 'Sierra_Blanca', 'SB_1', 'SB_2', 'SB_4', 'SB_5', 'VC_1',
    #              'VC_2', 'VC_3', 'CH_1', 'CH_3', 'MG_1', 'MG_2', 'WHLR_PK', 'LP', 'South_Baldy',
    #              'Water_Canyon', 'La_Jencia', 'Socorro']

    site_list = ['Sierra_Blanca', 'Great_Western_Mine', 'Bonito', 'Nogal']
    df = DataFrame(columns=FACTORS, index=site_list)
    df_norm = DataFrame(columns=FACTORS, index=site_list)

    site_dict = {'Sierra_Blanca': {}, 'Great_Western_Mine': {}, 'Bonito': {}, 'Nogal': {}}
    ds = Open(points)
    lyr = ds.GetLayer()
    # defs = lyr.GetLayerDefn()

    for j, feat in enumerate(lyr):
        name = feat.GetField("Name")
        name = name.replace(' ', '_')
        geom = feat.GetGeometryRef()
        mx, my = int(geom.GetX()), int(geom.GetY())
        site_dict[name]['Coords'] = '{} {}'.format(mx, my)
        file_name = os.path.join(extracts, '{}.csv'.format(name))
        print(file_name)
        site_dict[name]['etrm'] = get_etrm_time_series(file_name, single_file=True)

    # print 'site dict before running etrm: {}'.format(site_dict)

    for i, var_arr in enumerate(var_arrs):
        factor = FACTORS[i]
        print('running modified factor: {}'.format(factor))
        print('')
        for key, val in site_dict.iteritems():
            print('\n site: {} \n '.format(key))
            results = []
            for col in var_arr.T:
                etrm = Processes(SIMULATION_PERIOD, static_inputs=statics, initial_inputs=initials,
                                 output_root=pickle, point_dict=site_dict)
                tracker = etrm.run(point_dict=site_dict, point_dict_key=key, sensitivity_matrix_column=col,
                                   sensitivity=True)

                # print 'tracker: {}'.format(tracker)
                results.append(tracker['tot_infil'][-1])
                print('total infil: {} \n results: {}'.format(tracker['tot_infil'][-1], results))

            df.iloc[site_list.index(key), FACTORS.index(factor)] = divide(array(results), 14.0)
        print('df after site {}: \n {}'.format(key, df))
    print('df: {}'.format(df))

    # tot_data : precip, et, tot_transp, tot_evap, infil, runoff, snow_fall, cum_mass, end_mass

    # "SI = [Q(Po + delP] -Q(Po - delP] / (2 * delP)"
    # where SI = Sensitivity Index, Q = recharge, Po = base value of input parameter,
    # delP = change in value input
    # find sensitivity index

    xx = 0
    for param in df.iteritems():
        data_cube = param[1]
        var_arr = var_arrs[xx]
        yy = 0
        for site in data_cube:
            site_name = site_list[yy]
            normal = normalize_list[xx]
            site_obj = [x for x in site]
            sens_list = []
            zz = 0
            for var in var_arr[xx]:
                if var != var_arr[xx][5]:
                    base = var_arr[xx][5]
                    deltap = var - base
                    obj = site_obj[zz]
                    sen = ((obj * (base + deltap) - obj * (base - deltap)) / (2 * deltap)) * normal
                    sens_list.append(sen)
                    zz += 1
            sens_list = array(sens_list)
            df_norm.iloc[site_list.index(site_name), FACTORS.index(param[0])] = sens_list
            if yy == 20:
                print('done')
                break
            yy += 1
        xx += 1

    # why not save the data as pickle, so we don't have to do the analysis each time
    # we debug the plotting

    df.to_pickle(os.path.join(pickle, '_basic_sensitivity_2.pkl'))
    df_norm.to_pickle(os.path.join(pickle, 'norm_sensitivity_2.pkl'))

    # make_spider_plot(df_norm, ndvi_range=ndvi_range, all_pct=all_pct, temps=temps, fig_path=None,
    #                  show=True)
    # make_tornado_plot(df_norm, FACTORS, show=True, fig_path=None)


if __name__ == '__main__':
    root = os.path.join('F:\\', 'ETRM_Inputs')
    sensitivity = os.path.join(root, 'sensitivity_analysis')
    extract_files = os.path.join(sensitivity, 'SA_extracts')
    sa_locations = os.path.join(sensitivity, 'sensitivity_points', 'SA_pnts_SierBlanca_18OCT16.shp')
    initial_conditions_path = os.path.join(root, 'initialize')
    static_inputs_path = os.path.join(root, 'statics')
    pickles = os.path.join(sensitivity, 'pickled')
    get_sensitivity_analysis(extract_files, sa_locations,
                             statics=static_inputs_path,
                             initials=initial_conditions_path, pickle=pickles)

# ==========================  EOF  ==============================================
