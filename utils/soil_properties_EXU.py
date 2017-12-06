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
#Locations for Walnut Gulch
input_path = 'H:\\Walnut\\WalnutSoilProperties\\'
sand_tif = 'Merged_percSand.tif'
clay_tif = 'Merged_percClay.tif'
silt_tif = 'Merged_percSilt.tif'
BD_w_tif = 'Merged_gcmBD3rdbar.tif'
Ksat_tif = 'Merged_umsKsat.tif'
OM_tif = 'Merged_OrgMatter.tif'
WC_tif = 'Merged_WC3rdbar.tif'

sand = convert_raster_to_array(input_path, sand_tif)
clay = convert_raster_to_array(input_path, clay_tif)
silt_e = convert_raster_to_array(input_path, silt_tif)
#elev = convert_raster_to_array(input_path, elev_tif)
BD_w = convert_raster_to_array(input_path, BD_w_tif)#wet bulk density
Ksat = convert_raster_to_array(input_path, Ksat_tif)#extracted
OM = convert_raster_to_array(input_path, OM_tif)
WC = convert_raster_to_array(input_path, WC_tif)

sand_1d = sand.flatten()
clay_1d = clay.flatten()
silt_e_1d = silt_e.flatten()
silt_s_1d = np.subtract(100,clay_1d+sand_1d)
#elev_1d = elev.flatten()
BD_w_1d = BD_w.flatten()
Ksat_1d = Ksat.flatten()
OM_1d = OM.flatten()
WC_1d = WC.flatten()

points_e = []
for i in range(len(sand_1d)):
    z = sand_1d[i]
    y = clay_1d[i]
    x = silt_e_1d[i]
    points_e.append((x,y,z))

points_s = []
for i in range(len(sand_1d)):
    z = sand_1d[i]
    y = clay_1d[i]
    x = silt_s_1d[i]
    points_s.append((x,y,z))

#for study, this is a way to combine points as [[],[]]
#soil_content = np.dstack((sand_1d, clay_1d, silt_1d))
def ternary_plot(points,title):
    import ternary
    #tax is the axes object
    #For more information please vist https://github.com/marcharper/python-ternary
    figure, tax = ternary.figure(scale =100)
    # Remove default Matplotlib Axes
    tax.clear_matplotlib_ticks()
    #formatting the ternary diagram
    left_kwargs = {'color': 'blue'}
    right_kwargs = {'color': 'red'}
    tax.set_title(title, fontsize=20)
    tax.boundary(linewidth=2.0)
    tax.gridlines(color="black", multiple=5, left_kwargs=left_kwargs,right_kwargs=right_kwargs)
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
#compare two silt
import matplotlib.pyplot as plt
plt.scatter(silt_s_1d, silt_e_1d)
plt.ylabel('Extracted perc Silt')
plt.xlabel('Substracted perc Silt')
plt.title('perc Silt comparison')
plt.show()

#now make ternary plot for Extracted and Subtracted Silt data for Walnut Gulch
title = "Soil Content in Walnut Gulch, Extracted"
ternary_plot(points_e,title)
title = "Soil Content in Walnut Gulch, Subtracted"
ternary_plot(points_s,title)

#Calculate Ksat
#Ksat Comparison, Loosvelt
#Ksat from PTF = cm/s = 10^4 um/s
#bulk density = tho_d = g/cm^3
def PTF(Sand,Clay,OM,rho_d,P):
    #Extracted
    Ksat = Ksat_1d * 86.4#um/s to mm/day
    #Loosvelt et al, 2011, PTFa
    #Vereecken et al 1989&1990
    PTF_a = 1.1574*10**(-5)*np.exp(20.62-0.96*np.log(Clay)-0.66*np.log(Sand)-0.46*np.log(OM)-8.43*rho_d)#cm/s
    Ksat_a = PTF_a * 864000#mm/day
    # Loosvelt et al, 2011, PTFb
    #Rawls and Brakensiek[1985, 1989].
    PTF_b = 2.78*10**(-6)*np.exp(19.52*P - 8.97 - 2.82*10**(-2)*Clay+1.81*10**(-4)*(Sand**2) - 9.41*10**(-3)*(Clay**2) - 8.40*(P**2) + 7.77*10**(-2)*(Sand*P) - 2.98*10**(-3)*(Sand**2)*(P**2) - 1.95**10**(-2)*(Clay**2)*(P**2) + 1.73*10**(-5)*(Sand**2)*Clay + 2.73*10**(-2)*(Clay**2)*P + 1.43*10**(-3)*(Sand**2)*P - 3.5*10**(-6)*(Clay**2)*Sand)#cm/s
    Ksat_b = PTF_b*864000#mm/day
    #Cosby et al, 1984 from Julia, 2004 and Abdelbaki,2009 agreed
    Ksat_c = 25.4 * 10 ** (-0.6 + 0.012 * Sand - 0.0064 * Clay)  #mm/h
    Ksat_c = Ksat_c * 24#mm/day
    #Saxton et al, 1986,from Julia, 2004 corrected by Abdelbaki,2009
    Ksat_s = 10 * np.exp(12.01 - 0.0755 * Sand + (
    (-3.895 + 0.03671 * Sand - 0.1103 * Clay + 0.00087546 * Clay ** 2) / (0.33 - 0.000751 * Sand + 0.176 * np.log10(Clay))))#mm/h
    Ksat_s = Ksat_s * 24  # mm/day
    #Juliet_A,2004
    Ksat_ja = 0.920 * np.exp(0.0491 * Sand)#mm/h
    Ksat_ja = Ksat_ja * 24  # mm/day
    # Juliet_B,2004
    Ksat_jb = -4.994+0.56728*Sand -0.131*Clay-0.0127*OM#mm/h
    Ksat_jb = Ksat_jb * 24  # mm/day
    #Nemes et al, 2005
    x1=-3.663+0.046*Sand
    x2=-0.887+0.083*Clay
    x3=-9.699+6.451*rho_d
    x4=-0.807+1.263*OM
    z1=-0.428+0.998*x1+0.651*x1**2+0.130*x1**3
    z2=0.506*x1 - 0.188*x2 - 0.327*x3 - 0.094*x4
    z3=-0.268+0.885*z1+0.544*z1**2-0.682*z1**3+0.320*z2-0.134*z1*z2+1.119*z1**2*z2+0.050*z2**2-0.645*z1*z2**2+0.160*z2**3+0.126*x4-0.144*z1*x4-0.372*z2**2*x4+0.247*z2*x4+0.795*z1*z2*x4-0.344*z2**2*x4+0.038*x4**2-0.071*z1*x4**4+0.050*z2*x4**2-0.015*x4**3
    z4=0.102+1.383*z3+0.302*z3**2+0.103*z3**3+0.331*x2+0.693*z3*x2+0.541*z3**2*x2+0.198*x2**2+0.429*z3*x2**2+0.092*x2**3+0.929*z3*x2*x3+0.319*x2**2*x3+0.026*x3**2+0.094*z3*x3**2+0.116*x2*x3**2
    Ksat_n = 10**(0.571+0.956*z4)#cm/day
    Ksat_n = Ksat_n*10#mm/day
    return Ksat,Ksat_a,Ksat_b,Ksat_c,Ksat_s,Ksat_ja,Ksat_jb,Ksat_n


[Ksat,Ksat_a,Ksat_b,Ksat_c,Ksat_s,Ksat_ja,Ksat_jb,Ksat_n]=PTF(Sand,Clay,OM,rho_d,P)


#Calculation
Sand = sand_1d
Clay = clay_1d
OM = OM_1d
rho_d = BD_w_1d - WC_1d * 0.01  # UNIT g/cm^3
rho_s = 2.65#unit g/cm^3
P = 1 - rho_d/rho_s
WC = WC_1d

from recharge.raster_tools import convert_array_to_raster
from recharge.raster_tools import get_raster_geo_attributes
root = "H:\\Walnut\\WalnutSoilProperties\\"
geo = get_raster_geo_attributes(root)
output_path = "H:\\Walnut\\Ksat.tif"
Ksat_c =Ksat_c*0.0115741
arr = Ksat_c.reshape(74,243)
convert_array_to_raster(output_path, arr, geo, output_band=1)

a=convert_raster_to_array("H:\\Walnut\\Ksat.tif")




0.0864
plt.scatter(Ksat_a, Ksat_b)
plt.ylabel('PTF_b')
plt.xlabel('PTF_a')
plt.title('Ksat comparison between PTFs')
plt.show()

plt.scatter(Ksat_a, Ksat)
plt.ylabel('Extracted')
plt.xlabel('PTF_A')
plt.title('Ksat comparison - A and Extracted')
plt.show()

plt.scatter(Ksat_b, Ksat)
plt.ylabel('Extracted')
plt.xlabel('PTF_B')
plt.title('Ksat comparison - B and Extracted')
plt.show()



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
#Silt Comparison
plt.scatter(Silt_s, Silt_e)
plt.ylabel('Extracted perc Silt')
plt.xlabel('Substracted perc Silt')
plt.title('perc Silt comparison')
plt.show()
#Call ternary function from previous section
title = "Soil Content in New Mexico"
ternary_plot(points,title)

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
#==================================================================
from recharge.raster_tools import convert_raster_to_array
import numpy as np
import matplotlib.pyplot as plt
input_path = 'H:\\NewMexico\\DirectSoilData\\Merge_Fin\\'
sand_tif = 'Merged_percSand_5cm_Raster.tif'
clay_tif = 'Merged_percClay_5cm_Raster.tif'
Ksat_tif = 'Merged_umsKsat_5cm_Raster.tif'
Ksat_D = 'H:\\ETRM_inputs\\statics\\Soil_Ksat_15apr.tif'

sand = convert_raster_to_array(input_path, sand_tif)
clay = convert_raster_to_array(input_path, clay_tif)
Ksat_e = convert_raster_to_array(input_path, Ksat_tif)#extracted
Ksat_d = convert_raster_to_array(Ksat_D[0:-19],Ksat_D[23:49])#come from David's
NoData = -9999.0
NoData_d = -999.0
s_idx = sand > NoData
c_idx = clay > NoData
Total_idx = []
for s in s_idx:
    if s in c_idx:
        Total_idx.append(s)

from recharge.raster_tools import convert_array_to_raster
from recharge.raster_tools import get_raster_geo_attributes
root = "H:\\NewMexico\\DirectSoilData\\Merge_Fin\\"
geo = get_raster_geo_attributes(root)
output_path = "H:\\NewMexico\\Ksat_Esther_1129.tif"
Ksat_c = np.ones((geo['rows'],geo['cols']))*-999
Ksat_c[Total_idx] = 25.4 * 10 ** (-0.6 + 0.012 * sand[Total_idx] - 0.0064 * clay[Total_idx])  # mm/h
Ksat_c[Total_idx] = Ksat_c[Total_idx] * 60/1000  # mm/day
#Ksat_c[Ksat_c==-999]= np.nan
arr = Ksat_c


convert_array_to_raster(output_path, arr, geo, output_band=1)
output = "H:\\NewMexico\\Test.tif"
os.system(
        'python D:\Anaconda2\Scripts\gdal_merge.py -n -999 -a_nodata -999  -of GTiff -o {a} {b} {c}'.format(a=output,
                                                                                                              c=output_path,
                                                                                                              b=Ksat_D))