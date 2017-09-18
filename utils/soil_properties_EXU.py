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
input_path = 'G:\\Walnut\\WalnutData\\'
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

############################
from recharge.raster_tools import convert_raster_to_array
import numpy as np
import ternary

#Locations for Walnut Gulch
input_path = 'H:\\NewMexico\\NM_Extracted\\'
sand_tif = 'Merge_percSand_5cm.tif'
clay_tif = 'Merge_percClay_5cm.tif'
#elev_tif = 'Walnut250mDEM_UTM.tif'


#Locations for New Mexico

sand = convert_raster_to_array(input_path, sand_tif)
clay = convert_raster_to_array(input_path, clay_tif)
silt = np.subtract(100,clay+sand)
#elev = convert_raster_to_array(input_path, elev_tif)

sand_1d = sand.flatten()
clay_1d = clay.flatten()
silt_1d = silt.flatten()
#elev_1d = elev.flatten()

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







########################################################
########################################################
#Ksat Comparison
from recharge.raster_tools import convert_raster_to_array
import numpy as np


#Locations for Walnut Gulch
input_wn = 'H:\\Walnut\\WalnutData\\'
sand_wn = 'Merge_percSand_5cm_utm.tif'
clay_wn = 'Merge_percClay_5cm_utm.tif'

#Locations for Walnut Gulch
input_nm = 'H:\\NewMexico\\NM_Extracted\\'
sand_nm = 'Merge_percSand_5cm.tif'
clay_nm = 'Merge_percClay_5cm.tif'


#Locations for New Mexico

sand_wn1 = convert_raster_to_array(input_path, sand_wn)
clay_wn1 = convert_raster_to_array(input_path, clay_wn)

sand_nm1 = convert_raster_to_array(input_path, sand_nm)
clay_nm1 = convert_raster_to_array(input_path, clay_nm)

sand_wn_1d = sand_wn1.flatten()
clay_wn_1d = clay_wn1.flatten()

sand_nm_1d = sand_nm1.flatten()
clay_nm_1d = clay_nm1.flatten()

K_wn = 2.78*10^(-6)
K_nm =
