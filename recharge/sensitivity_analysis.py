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
from numpy import linspace, array, insert, sum, divide
from pandas import DataFrame
from ogr import Open
from datetime import datetime

from recharge.time_series_manager import get_etrm_time_series
from recharge.etrm_processes import Processes
from utils.spiderPlot_SA import make_spider_plot
from utils.tornadoPlot_SA import make_tornado_plot

# Set start datetime object
SIMULATION_PERIOD = datetime(2000, 1, 1), datetime(2013, 12, 31)

FACTORS = ['Temperature', 'Precipitation', 'Reference ET', 'Total Water Storage (TAW)',
           'Vegetation Density (NDVI)', 'Soil Ksat']


def get_sensitivity_analysis(extracts, points, statics, initials, save_plot=None):

    def round_to_value(number, roundto):
        return round(number / roundto) * roundto

    temps = range(-5, 6)
    all_pct = [x * 0.1 for x in range(5, 16)]
    ndvi_range = linspace(0.9, 1.7, 11)
    ndvi_range = array([round_to_value(x, 0.05) for x in ndvi_range])
    var_arrs = []
    y = 0
    for x in range(0, 6):
        ones = ones((5, 11), dtype=float)
        zeros = [x * 0.0 for x in range(5, 16)]
        norm_ndvi = array([1.25 for x in zeros])
        if y == 0:
            arr = insert(ones, y, temps, axis=0)
            arr = insert(arr, 4, norm_ndvi, axis=0)
            arr = arr[0:6]
            var_arrs.append(arr)
            arr = []
        elif y == 4:
            arr = insert(ones, 0, zeros, axis=0)
            arr = insert(arr, y, ndvi_range, axis=0)
            arr = arr[0:6]
            var_arrs.append(arr)
            arr = []
        elif y == 5:
            arr = insert(ones, 0, zeros, axis=0)
            arr = insert(arr, 4, norm_ndvi, axis=0)
            arr = arr[0:5]
            arr = insert(arr, y, all_pct, axis=0)
            var_arrs.append(arr)
            arr = []
        else:
            arr = insert(ones, 0, zeros, axis=0)
            arr = insert(arr, y, all_pct, axis=0)
            arr = insert(arr, 4, norm_ndvi, axis=0)
            arr = arr[0:6]
            var_arrs.append(arr)
            arr = []
        y += 1

    normalize_list = [2, 0.20, 0.20, 2, 0.20, 0.50]

    site_list = ['Bateman', 'Navajo_Whiskey_Ck', 'Quemazon', 'Sierra_Blanca', 'SB_1', 'SB_2', 'SB_4', 'SB_5', 'VC_1',
                 'VC_2', 'VC_3', 'CH_1', 'CH_3', 'MG_1', 'MG_2', 'WHLR_PK', 'LP', 'South_Baldy',
                 'Water_Canyon', 'La_Jencia', 'Socorro']

    df = DataFrame(columns=FACTORS, index=site_list)
    df_norm = DataFrame(columns=FACTORS, index=site_list)

    for i, var_arr in enumerate(var_arrs):
        factor = FACTORS[i]
        print factor
        print ''
        ds = Open(points)
        lyr = ds.GetLayer()
        # defs = lyr.GetLayerDefn()
        for feat in lyr:
            name = feat.GetField("Name")
            name = name.replace(' ', '_')
            # geom = feat.GetGeometryRef()
            # mx, my = geom.GetX(), geom.GetY()
            file_name = os.path.join(extracts, '{}_extract.csv'.format(name))
            print file_name
            extract_data = get_etrm_time_series(file_name)
            rslts = []
            for col in var_arr.T:
                etrm = Processes(SIMULATION_PERIOD, static_inputs=statics, initial_inputs=initials)
                tracker = etrm.run(sensitivity_matrix_column=col)
                print 'tracker: {}'.format(tracker)
                rech = sum(tracker[:, 9])
                rslts.append(rech)

            df.iloc[site_list.index(name), FACTORS.index(factor)] = divide(array(rslts), 14.0)
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
                print 'done'
                break
            yy += 1
        xx += 1

        make_spider_plot(df_norm, ndvi_range=ndvi_range, all_pct=all_pct, temps=temps, fig_path=None,
                         show=True)
        make_tornado_plot(df_norm, FACTORS, show=True, fig_path=None)

if __name__ == '__main__':
    root = os.path.join('F:\\', 'ETRM_Inputs')
    sensitivity = os.path.join(root, 'sensitivity_analysis')
    extract_files = os.path.join(sensitivity, 'SA_extracts')
    sa_locations = os.path.join(sensitivity, 'sensitivity_points', 'SA_pnts29APR16_UTM.shp')
    initial_conditions_path = os.path.join(root, 'initialize')
    static_inputs_path = os.path.join(root, 'statics')
    figures_path = os.path.join(sensitivity, 'figures')
    get_sensitivity_analysis(extract_files, sa_locations,
                             statics=static_inputs_path,
                             initials=initial_conditions_path, save_plot=figures_path)

# ==========================  EOF  ==============================================
