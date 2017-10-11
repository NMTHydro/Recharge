# ===============================================================================
# Copyright 2017 EXu
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
# ==============================================================================

"""
The purpose of this module is to study soil properties of desired region.

The program haven't been cleaned for all, yet.

First section: ternary plot for NM
Second section: ternary plot for Walnut
Third section: PTF calculation (not finished)
Fourth section: comparisons including K comparision, silt comparison, etc.

EXu 13 SEP 2017
"""


from recharge.raster_tools import convert_raster_to_array
import numpy as np
import ternary

#Locations for Walnut Gulch
input_path = 'H:\\Walnut\\WalnutData\\'
sand_tif = 'Merge_percSand_5cm_utm.tif'
clay_tif = 'Merge_percClay_5cm_utm.tif'
elev_tif = 'Walnut250mDEM_UTM.tif'


#Locations for New Mexico

sand = convert_raster_to_array(input_path, sand_tif)
clay = convert_raster_to_array(input_path, clay_tif)
silt = np.subtract(100,clay+sand)
elev = convert_raster_to_array(input_path, elev_tif)

sand_1d = sand.flatten()
clay_1d = clay.flatten()
silt_1d = silt.flatten()
elev_1d = elev.flatten()

points = []
for i in range(len(sand_1d)):
    z = sand_1d[i]
    y = clay_1d[i]
    x = silt_1d[i]
    points.append((x,y,z))


#for study, this is a way to combine points as [[],[]]
#soil_content = np.dstack((sand_1d, clay_1d, silt_1d))



#tax is the axes object
#For more information please vist https://github.com/marcharper/python-ternary
figure, tax = ternary.figure(scale =100)

# Remove default Matplotlib Axes
tax.clear_matplotlib_ticks()

#formatting the ternary diagram
left_kwargs = {'color': 'blue'}
right_kwargs = {'color': 'red'}

tax.set_title("Soil Content in Walnut Gulch", fontsize=20)
tax.boundary(linewidth=2.0)
tax.gridlines(color="black", multiple=5, left_kwargs=left_kwargs,
                         right_kwargs=right_kwargs)

#should be three stack of three different lines
tax.scatter(points,linewidth=1)

#axis settings
fontsize = 10
tax.left_axis_label("%Clay", fontsize=fontsize)
tax.right_axis_label("%Silt", fontsize=fontsize)
tax.bottom_axis_label("%Sand", fontsize=fontsize)

tax.ticks(axis='lbr', linewidth=1, multiple= 10,clockwise= True)
tax.get_axes().axis('off')
#present
ternary.plt.show()

############################New Mexico
from recharge.raster_tools import convert_raster_to_array
import numpy as np
import ternary
import matplotlib.pyplot as plt

#Locations for New Mexico
input_path = 'H:\\NewMexico\\DirectSoilData\\Merge_Fin\\'
sand_tif = 'Merged_percSand_5cm_Raster.tif'
clay_tif = 'Merged_percClay_5cm_Raster.tif'
silt_tif = 'Merged_percSilt_5cm_Raster.tif'
BD_w_tif = 'Merged_gcmBD3rdbar_5cm_Raster.tif'
Ksat_tif = 'Merged_umsKsat_5cm_Raster.tif'
Ksat_D = 'H:\\ETRM_inputs\\statics\\Bedrock_Ksat_Ras_15apr.tif'#come from David
OM_tif = 'Merged_OrgMatter_5cm_Raster.tif'
WC_tif = 'Merged_WC3rdbar_5cm_Raster.tif'
#elev_tif = 'Walnut250mDEM_UTM.tif'

#Conversions
sand = convert_raster_to_array(input_path, sand_tif)
clay = convert_raster_to_array(input_path, clay_tif)
silt_e = convert_raster_to_array(input_path, silt_tif)#extracted
#silt_s: below
BD_w = convert_raster_to_array(input_path, BD_w_tif)#wet bulk density
Ksat_e = convert_raster_to_array(input_path, Ksat_tif)#extracted
Ksat_d = convert_raster_to_array(Ksat_D[0:-26],Ksat_D[23:49])#come from David's
OM = convert_raster_to_array(input_path, OM_tif)
WC = convert_raster_to_array(input_path, WC_tif)
#elev = convert_raster_to_array(input_path, elev_tif)

sand_1d = sand.flatten()
clay_1d = clay.flatten()
silt_e_1d = silt_e.flatten()

#elev_1d = elev.flatten()

BD_w_1d = BD_w.flatten()
Ksat_e_1d = Ksat_e.flatten()
Ksat_d_1d = Ksat_d.flatten()
OM_1d = OM.flatten()
WC_1d = WC.flatten()

noData = -9999.0
noData_d = -999.0

sand_n = []
silt_n = []
clay_n = []
BD_w_n = []
Ksat_d_n = []
OM_n = []
WC_n = []
for i in range(len(sand_1d)):
    z = sand_1d[i]
    y = clay_1d[i]
    x = silt_e_1d[i]
    BD_w = BD_w_1d[i]
    Ksat_d = Ksat_d_1d[i]
    OM = OM_1d[i]
    WC = WC_1d[i]
    if Ksat_d != noData_d and x != noData and y != noData and z != noData and z != 0 and x != 0 and y != 0:
        sand_n.append(z)
        silt_n.append(x)
        clay_n.append(y)
        BD_w_n.append(BD_w)
        Ksat_d_n.append(Ksat_d)
        OM_n.append(OM)
        WC_n.append(WC)

Sand = np.asarray(sand_n)
Clay = np.asarray(clay_n)
Silt_e = np.asarray(silt_n)
Silt_s = np.subtract(100,Sand+Clay)

BD_w = np.asarray(BD_w_n)
Ksat_d = np.asarray(Ksat_d_n)
OM = np.asarray(OM_n)
WC = np.asarray(WC_n)

points = []
for i in range(len(sand)):
    z = sand[i]
    y = clay[i]
    x = silt_e[i]
    points.append((x,y,z))


plt.scatter(Silt_s, Silt_e)
plt.ylabel('Extracted perc Silt')
plt.xlabel('Substracted perc Silt')
plt.title('perc Silt comparison')
plt.show()


#Build ternary plot

#for study, this is a way to combine points as [[],[]]
#soil_content = np.dstack((sand_1d, clay_1d, silt_1d))
#tax is the axes object
#For more information please vist https://github.com/marcharper/python-ternary
figure, tax = ternary.figure(scale =100)
# Remove default Matplotlib Axes
tax.clear_matplotlib_ticks()
#formatting the ternary diagram
left_kwargs = {'color': 'blue'}
right_kwargs = {'color': 'red'}
tax.set_title("Soil Content in New Mexico", fontsize=20)
tax.boundary(linewidth=2.0)
tax.gridlines(color="black", multiple=5, left_kwargs=left_kwargs,
                         right_kwargs=right_kwargs)
#should be three stack of three different lines
tax.scatter(points,linewidth=1)
#axis settings
fontsize = 10
tax.left_axis_label("%Clay", fontsize=fontsize)
tax.right_axis_label("%Silt", fontsize=fontsize)
tax.bottom_axis_label("%Sand", fontsize=fontsize)
tax.ticks(axis='lbr', linewidth=1, multiple= 10,clockwise= True)
tax.get_axes().axis('off')
#present
ternary.plt.show()

######################################################################################
#Ksat Comparison
rho_d = BD_w - WC*0.01 #UNIT G/CM^3
rho_s = 2650
P = 1 - rho_d/rho_s
PTF_a = 1.1574*10**(-5)*np.exp(20.62-0.96*np.log(Clay)-0.66*np.log(Sand)-0.46*np.log(OM)-8.43*rho_d)
PTF_b = 2.78*10**(-6)*np.exp(19.52*P-8.97-2.82*10**(-2)*Clay+1.81*10**(-4)*Sand**2-9.41*10**(-3)*Clay**2-8.40*P**2+7.77*10**(-2)*Sand*P-2.98*10**(-3)*Sand**2*P**2-1.95**10**(-2)*Clay**2*P**2+1.73*10**(-5)*Sand**2*Clay+2.73*10**(-2)*Clay**2*P+1.43*10**(-3)*Sand**2*P-3.5*10**(-6)*Clay**2*Sand)

import plotly.figure_factory as ff
import pandas as pd
import plotly.plotly as py

dataframe = pd.DataFrame({'Davids': Ksat_d, 'A': PTF_a, 'B': PTF_b})
fig = ff.create_scatterplotmatrix(dataframe, diag='box',
                                  colormap_type='cat',
                                  height=800, width=800)
py.iplot(fig, filename = 'Colormap as a Dictionary')

plt.scatter(PTF_a, PTF_b)
plt.ylabel('PTF_a')
plt.xlabel('PTF_b')
plt.title('comparison between PTF K')
plt.show()

plt.scatter(PTF_a*10**(3), Ksat_d)
plt.ylabel('Davids')
plt.xlabel('PTF_a')
plt.title('A')
plt.show()

plt.scatter(PTF_b*10**(3), Ksat_d)
plt.ylabel('Davids')
plt.xlabel('PTF_b')
plt.title('B')
plt.show()