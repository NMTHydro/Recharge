# ===============================================================================
# Copyright 2016 gabe-parrish
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

import pandas as pd
import numpy as np

from app.config import Config
from app.paths import paths
from recharge.etrm_processes import Processes


from utils.pixel_coord_finder import coord_getter


from recharge.raster_tools import tiff_framer, get_mask, convert_array_to_raster, remake_array, get_raster_geo_attributes, apply_mask

# ============= local library imports ===========================

def taw_func(root):
    """Function gets a masked original taw and a masked modified taw"""
    #TODO- maybe just use dict_setup code to read in taw and modify.
    #TODO- make an initialize taw function.

    mask_path = os.path.join(root, 'Mask')
    mask_arr = get_mask(mask_path)

    northing, easting = coord_getter(os.path.join(mask_path, 'unioned_raster_output.tif'))

    home = os.path.expanduser('~')
    #cp1 = os.path.join(home, 'ETRM_CONFIG_TAW.yml') # for a modified taw
    cp1 = os.path.join(home, 'ETRM_CONFIG.yml')  # for an unmodified taw

    # modified taw
    cfg1 = Config(path=cp1)
    runspec1 = cfg1.runspecs[0]
    paths.build(runspec1.input_root, runspec1.output_root)
    etrm_new = Processes(runspec1)
    print 'config taw_mod------->', runspec1.taw_modification
    taw_new = etrm_new.modify_taw(runspec1.taw_modification)
    print 'new taw newwww', taw_new
    taw_new = remake_array(mask_path, taw_new)

    # unmodified taw

    runspec2 = cfg1.runspecs[1]
    etrm_unmod = Processes(runspec2)
    print "etrm taw shape ---->>> ", etrm_unmod.get_taw().shape
    taw_unmod = etrm_unmod.get_taw()
    taw_unmod = remake_array(mask_path, taw_unmod)

    columns = ['x', 'y', 'taw_unmodified', 'taw_new']
    x_list = []
    y_list = []
    taw_unmodified_list = []
    taw_new_list = []
    nrows, ncols = taw_new.shape
    for ri in xrange(nrows):
        for ci in xrange(ncols):
            mask_values = mask_arr[ri, ci]
            if mask_values:
                # print ri, ci, taw[ri,ci], taw_new_masked[ri,ci], taw_new[ri,ci]
                x_list.append('{}'.format(easting[ri, ci]))
                y_list.append('{}'.format(northing[ri, ci]))
                taw_unmodified_list.append('{}'.format(taw_unmod[ri, ci]))
                taw_new_list.append('{}'.format(taw_new[ri, ci]))

    taw_data_dict = {'x': x_list, 'y': y_list, 'taw_unmodified': taw_unmodified_list, 'taw_new': taw_new_list}
    taw_df = pd.DataFrame(taw_data_dict, columns=columns)

    #print 'taw dataframe', taw_df
    return taw_df, taw_data_dict


def rzsm_mapper(depletions, taw, inputs_path, mask_path):
    """Root Zone Soil Mapper, which takes two dataframe objects, depletions, taw and gets soil moiture using
    RZSM = 1- (D/TAW) for each pixel of the model. The RZSM will be converted to an array and refitted into
    a map using convert_array_to_raster()"""

    #de = depletions.as_matrix(columns='de') # why won't this work?

    de = depletions.ix[:, 2]
    de = de.values.tolist()[0:]
    de = np.array(de)
    print 'de shape', de.shape
    print 'de', de

    dr = depletions.ix[:, 3]
    dr = dr.values.tolist()[0:]
    dr = np.array(dr)
    print'dr shape', dr.shape

    drew = depletions.ix[:, 4]
    drew = drew.values.tolist()[0:]
    drew = np.array(drew)
    print'drew shape', drew.shape


    d = de + dr + drew
    print 'depletion ->', d
    print 'depletion shape', d.shape

    # TODO - you don't need an array for this. scalar will work.
    ones = np.ones(d.shape) # was 32787 now 3056 because the mask size changed you dummy!

    taw_unmod = taw.ix[:, 2]
    taw_unmod = taw_unmod.values.tolist()[0:]

    taw_unmod = [float(value) for value in taw_unmod]
    # for value in taw_unmod:
    #     value = int(value)

    taw_unmod = np.array(taw_unmod)
    print 'taw_unmod shape', taw_unmod.shape
    print 'taw_unmod', taw_unmod
    quotient = (d/taw_unmod)
    print 'Quotient', quotient
    unmod_soil_arr = ones - quotient
    print 'unmodified rzsm array', unmod_soil_arr

    #print 'taw shape', taw_unmod.shape

    taw_mod = taw.ix[:, 3]
    taw_mod = taw_mod.values.tolist()[0:]
    taw_mod = [float(value) for value in taw_mod]
    taw_mod = np.array(taw_mod)
    quotient = d/taw_mod
    mod_soil_arr = ones - quotient

    print 'modified rzsm array', mod_soil_arr


    # ---- Get Arrays Back into shape! -----

    #print 'paths.static_inputs',
    # should be able to get the paths thing to work.
    #geo_path = Paths()
    geo_path = os.path.join(inputs_path, 'statics')
    geo_thing = get_raster_geo_attributes(geo_path)
    print 'GEO THING', geo_thing
    print 'unmod shape', unmod_soil_arr.shape
    print unmod_soil_arr
    unmod_soil_arr = remake_array(os.path.dirname(mask_path), unmod_soil_arr)
    convert_array_to_raster('/Users/Gabe/Desktop/gdal_raster_output/newtestfile.tif', unmod_soil_arr, geo_thing)




def run():

    #------PATHS-------
    hard_drive_path = os.path.join('/', 'Volumes', 'Seagate Expansion Drive')
    inputs_path = os.path.join(hard_drive_path, 'ETRM_Inputs')
    root = inputs_path
    inputs_path = os.path.join(hard_drive_path, 'ETRM_inputs')
    mp = os.path.join(inputs_path, 'Mask')
    tiff_root = '/Volumes/Seagate Expansion Drive/ETRM_results/ETRM_Results_2017_03_13/daily_rasters'
    mask_path = os.path.join(mp, 'unioned_raster_output.tif')  # mp, 'zuni_1.tif'
    #tiff_path = os.path.join(mask_path, 'unioned_raster_output.tif')

    # -----DATES-----
    # TODO - get the date list form the config object


    # ----TIFFS----

    # TODO - based on the date list, make a function that formats the tiff list.
    # be mindful that under the new ETRM we don't have multiple depletions....
    tiff_list = ['de_27_12_2013.tif', 'dr_27_12_2013.tif', 'drew_27_12_2013.tif']
    tiff_list = [os.path.join(tiff_root, i) for i in tiff_list]
    tiff_frame = tiff_framer(mask_path, tiff_list)



    # TODO - pull out the dates from the tiff list. or something....

    #---- TAW ----------
    taw_df, taw_data_dict = taw_func(root)

    # ----- Take Stock ----
    #tiff_frame.to_excel('/Users/Gabe/Desktop/tiff_frame.xls')
    #taw_df.to_excel('/Users/Gabe/Desktop/taw_df.xls')

    # ------ RZSM = 1- (D/TAW) -------
    rzsm_mapper(tiff_frame, taw_df, inputs_path, mask_path)


if __name__ == '__main__':
    run()