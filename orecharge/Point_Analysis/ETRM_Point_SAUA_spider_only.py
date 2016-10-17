from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import rc
from osgeo import ogr
import etrm_daily_SA_2MAY16
import extract_readIn
import numpy as np
import pandas

rc('mathtext', default='regular')

save_path = 'C:\\Users\\David\\Documents\\ArcGIS\\results\\Sensitivity_analysis\\data'

pandas.set_option('display.max_rows', 3000)
pandas.set_option('display.max_columns', 3000)
pandas.set_option('display.width', 10000)
pandas.set_option('display.precision', 3)
pandas.options.display.float_format = '${:,.2f}'.format
np.set_printoptions(threshold=3000, edgeitems=5000, precision=3)
pandas.set_option('display.height', 5000)
pandas.set_option('display.max_rows', 5000)
startTime = datetime.now()
print startTime


def print_full(x):
    pandas.set_option('display.max_rows', len(x))
    print(x)
    pandas.reset_option('display.max_rows')
    print (x)


def round_to_value(number, roundto):
    return round(number / roundto) * roundto


def dfv(begin_ind, end_ind):
    return df.iloc[begin_ind, end_ind]


def save_df(df, save_path):
    df.to_csv('{}\\data1.csv'.format(save_path), sep=',')


np.set_printoptions(linewidth=700, precision=2, threshold=2500)

# Set start datetime object
start, end = datetime(2000, 1, 1), datetime(2013, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime(start.year, 11, 1), datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime(start.year, 6, 1), datetime(start.year, 10, 1)

temps = range(-5, 6)
all_pct = [x * 0.1 for x in range(5, 16)]
ndvi_range = np.linspace(0.9, 1.7, 11)
ndvi_range = np.array([round_to_value(x, 0.05) for x in ndvi_range])
var_arrs = []
y = 0
for x in range(0, 6):
    ones = np.ones((5, 11), dtype=float)
    zeros = [x * 0.0 for x in range(5, 16)]
    norm_ndvi = np.array([1.25 for x in zeros])
    if y == 0:
        arr = np.insert(ones, y, temps, axis=0)
        arr = np.insert(arr, 4, norm_ndvi, axis=0)
        arr = arr[0:6]
        var_arrs.append(arr)
        arr = []
    elif y == 4:
        arr = np.insert(ones, 0, zeros, axis=0)
        arr = np.insert(arr, y, ndvi_range, axis=0)
        arr = arr[0:6]
        var_arrs.append(arr)
        arr = []
    elif y == 5:
        arr = np.insert(ones, 0, zeros, axis=0)
        arr = np.insert(arr, 4, norm_ndvi, axis=0)
        arr = arr[0:5]
        arr = np.insert(arr, y, all_pct, axis=0)
        var_arrs.append(arr)
        arr = []
    else:
        arr = np.insert(ones, 0, zeros, axis=0)
        arr = np.insert(arr, y, all_pct, axis=0)
        arr = np.insert(arr, 4, norm_ndvi, axis=0)
        arr = arr[0:6]
        var_arrs.append(arr)
        arr = []
    y += 1

factors = ['Temperature', 'Precipitation', 'Reference ET', 'Total Water Storage (TAW)',
           'Vegetation Density (NDVI)', 'Soil Evaporation Depth']

normalize_list = [2, 0.20, 0.20, 2, 0.20, 0.50]
normalize_list = [1 for x in range(0, len(normalize_list) + 1)]

site_list = ['Bateman', 'Navajo_Whiskey_Ck', 'Quemazon', 'Sierra_Blanca', 'SB_1', 'SB_2', 'SB_4', 'SB_5', 'VC_1',
             'VC_2', 'VC_3', 'CH_1', 'CH_3', 'MG_1', 'MG_2', 'WHLR_PK', 'LP', 'South_Baldy',
             'Water_Canyon', 'La_Jencia', 'Socorro']

df = pandas.DataFrame(columns=factors, index=site_list)
df_norm = pandas.DataFrame(columns=factors, index=site_list)

yy = 0
for var_arr in var_arrs:
    factor = factors[yy]
    print factor
    print ''
    shp_filename = 'C:\\Recharge_GIS\\qgis_layers\\sensitivity_points\\SA_pnts29APR16_UTM.shp'
    ds = ogr.Open(shp_filename)
    lyr = ds.GetLayer()
    defs = lyr.GetLayerDefn()
    for feat in lyr:
        name = feat.GetField("Name")
        name = name.replace(' ', '_')
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()
        path = 'C:\Users\David\Documents\Recharge\Sensitivity_analysis\SA_extracts'
        file_name = '{}\\{}_extract.csv'.format(path, name)
        print file_name
        extract_data = extract_readIn.read_std_extract_csv(file_name)
        rslts = []
        for col in var_arr.T:
            pt_data, tot_data, mass_data = etrm_daily_SA_2MAY16.run_daily_etrm(start, end, extract_data,
                                                                               sMon, eMon, col)
            rech = np.sum(pt_data[:, 9])
            rslts.append(rech)

        df.iloc[site_list.index(name), factors.index(factor)] = np.divide(np.array(rslts), 14.0)
        # tot_data : precip, et, tot_transp, tot_evap, infil, runoff, snow_fall, cum_mass, end_mass
    yy += 1

# "SI = [Q(Po + delP] -Q(Po - delP] / (2 * delP)"
# where SI = Sensitivity Index, Q = recharge, Po = base value of input parameter, delP = change in value of input var
# find sensitivity index

xx = 0
for param in df.iteritems():
    data_cube = param[1]
    var_arr = var_arrs[xx]
    yy = 0
    for site in data_cube:
        print site
        site_name = site_list[yy]
        normal = normalize_list[xx]
        site_obj = [x for x in site]
        sens_list = []
        zz = 0
        for var in var_arr[xx]:
            if var != var_arr[xx][5]:
                base = var_arr[xx][5]
                deltaP = var - base
                obj = site_obj[zz]
                sen = ((obj * (base + deltaP) - obj * (base - deltaP)) / (2 * deltaP)) * normal
                sens_list.append(sen)
                zz += 1
            else:
                sens_list.append(site_obj[zz])
                zz += 1
        sens_list = np.array(sens_list)
        df_norm.iloc[site_list.index(site_name), factors.index(param[0])] = sens_list
        if yy == 20:
            print 'done'
            break
        yy += 1
    xx += 1

fig_path = 'C:\\Users\\David\\Documents\\ArcGIS\\results\\Sensitivity_analysis\\normalized'

disp_pct = [(int(x)) for x in np.add(np.multiply(all_pct, 100.0), -100)]
# disp_pct.remove(0)
temps = range(-5, 6)
# temps.remove(0)
all_pct = [x * 0.1 for x in range(5, 16)]
# all_pct.remove(1.0)
ndvi_range = np.linspace(0.9, 1.7, 11)
ndvi_range = [round_to_value(x, 0.05) for x in ndvi_range]
# ndvi_range.remove(1.3)
ndvi_range = np.array(ndvi_range)

for index, row in df_norm.iterrows():

    if row.name == 'La_Jencia':  # ['South_Baldy', 'Water_Canyon', 'La_Jencia', 'Socorro']:
        print index, row
        fig = plt.figure(xx, figsize=(20, 10))
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twiny()
        ax3 = ax1.twiny()
        fig.subplots_adjust(bottom=0.2)
        ax2.plot(temps, row[0], 'k', marker='x', label='Temperature (+/- 5 deg C)')
        ax1.plot(disp_pct, row[1], 'blue', marker='o', label='Precipitation (+/- 50%)')
        ax1.plot(disp_pct, row[2], 'purple', marker='^', label='Reference Evapotranspiration (+/- 50%)')
        ax1.plot(disp_pct, row[3], 'brown', marker='h', label='Total Available Water (+/- 50%)')
        ax3.plot(ndvi_range, row[4], 'green', marker='s', linestyle='-.', label='Normalized Density Vegetation\n'
                                                                                ' Index Conversion Factor (0.9 - 1.8)')
        ax1.plot(disp_pct, row[5], 'red', marker='*', label='Soil Evaporation Layer Thickness (+/- 50%)')
        ax1.set_xlabel(r"Parameter Change (%)", fontsize=16)
        ax1.set_ylabel(r"Total Recharge per Year (mm)", fontsize=16)

        ax2.set_xlabel(r"Temperature Change (C)", fontsize=16)
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax2.spines["bottom"].set_position(("axes", -0.15))
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        for sp in ax2.spines.itervalues():
            sp.set_visible(False)
        ax2.spines['bottom'].set_visible(True)

        ax3.set_xlabel(r"NDVI to Crop Coefficient Conversion Factor", fontsize=16)
        ax3.xaxis.set_ticks_position("bottom")
        ax3.xaxis.set_label_position("bottom")
        ax3.spines["bottom"].set_position(("axes", -0.3))
        ax3.set_frame_on(True)
        ax3.patch.set_visible(False)
        for sp in ax3.spines.itervalues():
            sp.set_visible(False)
        ax3.spines['bottom'].set_visible(True)
        plt.title('Variation of ETRM Physical Parameters at {}'.format(index.replace('_', ' ')), y=1.08, fontsize=20)
        handle1, label1 = ax1.get_legend_handles_labels()
        handle2, label2 = ax2.get_legend_handles_labels()
        handle3, label3 = ax3.get_legend_handles_labels()
        handles, labels = handle1 + handle2 + handle3, label1 + label2 + label3
        ax1.legend(handles, labels, loc=0)
        plt.show()
        plt.savefig('{}\\{}_spider_10JUL16_2'.format(fig_path, index), ext='png', figsize=(20, 10))
        plt.close(fig)
