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
# ===============================================================================

import os
from subprocess import call
import fnmatch



'''For downloading data, please use the pyModis script:
        modis_download.py
    It is very easy to operate.'''

'''Note:
        There is no G:\\Modis\\ anymore         
'''
# rename the files
folder = 'G:\\Modis\\'
output_folder = 'G:\\Modis\\'

os.chdir(folder)
files = os.listdir(folder)
for it in files:
    if it.startswith("MOD13Q1"):
        name = it[9:16] + it[-4:]
        os.rename(it, name)

for mo in files:
    if mo.startswith('20'):
        name = mo[0:7]
        i_file = folder + name + '.hdf'
        o_file = output_folder + name
        print(name,i_file,o_file)
        os.system('python E:\\PythonGit\\Recharge\\pyModis-2.0.5\\scripts\\modis_convert.py -s "( 1 0 )" -g 250 -r {c} -o {a} -e 26913 {b}'.format(a = o_file,b = i_file, c = 'AVERAGE' ))


h8v5 =  'G:\\Modis\\h8\\'
h9v5 =  'G:\\Modis\\h9\\'
folder_o = 'G:\\Modis\\'
os.chdir(h8v5)
files = os.listdir(h8v5)
for haha in files:
    name = haha[0:7]
    file_a = h8v5 + name + '_250m 16 days NDVI.tif'
    file_b = h9v5 + name + '_250m 16 days NDVI.tif'
    file_o = folder_o + name + '_250m 16 days NDVI.tif'
    os.system('python D:\Anaconda2\Scripts\gdal_merge.py -n -3000 -a_nodata -3000 -of GTiff -o "{a}" "{b}" "{c}"'.format(a= file_o, b= file_a, c= file_b))


folder_o = 'G:\\Modis\\'
os.chdir(folder_o)
files = os.listdir(folder_o)
for haha in files:
    if haha.startswith('20'):
        name = haha[0:-4]
        file_o = 'G:\\Modis\\' + name + '.tif'
        output_w = 'G:\\Walnut\\Modis\\' + name[0:7] + '.tif'
        output_nm = 'G:\\NewMexico\\Modis\\' + name[0:7] + '.tif'
        WGEW = 'gdalwarp -overwrite -s_srs EPSG:26913 -t_srs EPSG:26912 -te 576863 3501109 637613 3519609 -tr 250 250 -r {c} -of GTiff "{a}" {b}'.format(a=file_o, b=output_w,c = 'average')
        call(WGEW)
        NM = 'gdalwarp  -overwrite -s_srs EPSG:26913 -te 107500 3470500 683500 4259000 -tr 250 250 -r {c} -of GTiff "{a}" {b}'.format(a=file_o, b=output_nm,c = 'average')
        call(NM)
        print "Done processing {a}".format(a=name)



#Reproject interpolated wrong-projected Modis Data

# folder_o = 'G:\\Walnut\\Modis\\'
# os.chdir(folder_o)
# files = os.listdir(folder_o)
# for haha in files:
#     if haha.startswith('20'):
#         name = haha[0:-4]
#         file_o = 'G:\\Walnut\\Modis\\' + name + '.tif'
#         output_w = 'G:\\Walnut\\Modis\\R' + name[0:7] + '.tif'
#
#         repro = 'gdalwarp -overwrite -s_srs EPSG:26712 -t_srs EPSG:26912 -of GTiff "{a}" {b}'.format(a=file_o, b=output_w)
#         call(repro)
#
#         print "Done processing {a}".format(a=name)


folder_o = 'H:\\Walnut\\Modis\\'
os.chdir(folder_o)
files = os.listdir(folder_o)
for haha in files:
    if haha.startswith('20'):
        name = haha[0:-4]
        file_o = 'H:\\Walnut\\Modis\\' + name + '.tif'
        output_w = 'H:\\Walnut\\Modis\\RR' + name[0:7] + '.tif'

        repro = 'gdalwarp -overwrite -s_srs EPSG:26712 -t_srs EPSG:26912 -srcnodata -3000 -dstnodata -999 -of GTiff -te 576863 3501109 637613 3519609 -tr 250 250 "{a}" {b}'.format(a=file_o, b=output_w)
        call(repro)

        print "Done processing {a}".format(a=name)
