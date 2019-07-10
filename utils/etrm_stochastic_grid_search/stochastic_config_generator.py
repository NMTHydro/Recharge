# ===============================================================================
# Copyright 2019 Jan Hendrickx and Gabriel Parrish
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
import sys
import yaml

# ============= local library imports ===========================

"""

========== STOCHASTIC VERSION =======================

In the stochastic version we also seed the runs and do a custom number of runs for each TAW (SWHC) that is simulated in
 the grid search

This script may be useful to format the ETRM config file ETRM_CONFIG.yml You should be able to generate a yml file
for a given number of runs, with certain specs. Default specs can be selected.

1) Start with a config file. The options available in the config file that you select will be the config options
available for modification (this particular script only formats the taw of the config).

2) Provide the program with the path to the config file. Give a starting uniform taw, give an ending uniform taw and
 give a step interval

3) The taw_grid_search function will build out a config file that has all the same config parameters but repeats with
 TAW increasing by the step interval provided by the user.

NOTE: It would be good for the config file to look something like this:
---
input_root: /Volumes/Seagate_Expansion_Drive/ETRM_inputs_test_tiny_AOI
output_root: /Volumes/Seagate_Expansion_Drive/ETRM_test_output
# === START (No earlier than year 2000) ===
start_day: 1
start_month: 1
start_year: 2000
# === Finish (No later than year 2013) ===
end_day: 29
end_month: 12
end_year: 2000
# === MASKS ===
mask: Mask/mask_reduced.tif  #Mask/Landsat_test_tiny_AOI_mask.tif  #Mask/mask_reduced.tif
#binary_shapefile: binary_shapefile/Landsat_test_tiny_AOI_mask.tif
tiff_shape: 21,13
#  === Saving specific dates as rasters ===
save_dates: [] # list in format -> 'mm/dd/YYY' such as ['mm/dd/YYY', 'mm/dd/YYY', 'mm/dd/YYY']
write_freq: daily
daily_outputs: ['rzsm', 'eta', 'etrs']
# === Misc settings ===
is_reduced: True #False
winter_evap_limiter: 0.3  # (default)
polygons: Blank_Geo # (default)
evap_ceff: 1.0 # (default)
ro_reinf_frac: 0.0 # (default) Runoff Reinfiltration Fraction. To increase runoff into soil.
rew_ceff: 1.0 # (default)
output_units: mm # (default) OPTIONS -> mm|acre-ft|?
winter_end_day: 92 # (default)
winter_start_day: 306 # (default)
use_individual_kcb: True # (default)
new_mexico_extent: False #True
# === Don't Change ===
swb_mode: fao # FAO 56 Water Balance Method
use_verify_paths: True
# === individual pixel tracker related ===
plot_output: /Users/Gabe/Desktop/time_series_figs # (for plots of the binary shapefile pixel tracker time series)
xplot: ['Date'] # (default)
yplot: ['rain', 'eta', 'rzsm'] # (default) OPTIONS -> anything in master dict.
# === TAW parametrization (default is commented out) ====
taw_modification: 1.0 # (default) Will increase TAW by a specified factor.
uniform_taw: 25  # changes entire raster to a given TAW value
use_walnut_gulch_ro = True
seed = 123456789
use_monsoon_precip_correction = False
use_mountain_precip_correction = False

"""

def stochastic_taw_grid_search(config_path, output_path, begin_taw, end_taw, taw_step, runs, yaml_name):

    # test if the grid search bounds and step size are appropriate
    if ((end_taw - begin_taw) % taw_step) != 0:
        print 'taw step size has to divide evenly into end_taw - begin_taw'
        sys.exit()

    # we'll want to generate a list of the order that the config file was in so that the output config file will be nice
    #  and legible with everything in the same order as the first config file.
    config_param_order = []
    try:
        with open(config_path, 'r') as config:
            for line in config:
                print 'line', line
                # skip the comments right away.
                if not line.startswith('#'):
                    # and skip blank lines
                    if line != '\n':
                        # append the line but cut off any comments next to the lines...
                        config_param_order.append(line.split('#')[0])
    except:
        print 'something messed up and we couldnt open the file and make the list'

    print 'config parameter order', config_param_order

    # get rid of the \n at the end
    config_param_order = [i[:-2] for i in config_param_order]

    # get just the parameters, bc we'll use them to get them out of the dictionaries...
    config_param_order = [i.split(':')[0] for i in config_param_order]

    print 'no nubs', config_param_order

    # todo - Dan don't worry about the formatting just use yaml.load_all() and yaml.dump() with dictionaries
    # read in the configuration file as a dict
    with open("{}".format(config_path), 'r') as config:
        try:
            # makes a list of all the configs for a given run. (List of dictionaries)
            doclist = [doc for doc in yaml.load_all(config)]
            # print doclist
            # print len(doclist)
        except yaml.YAMLError as exc:
            print(exc)

    print 'the doclist', doclist

    config_dict = doclist[0]

    configuration_container = []
    current_taw = begin_taw

    for j in range(runs):
        for i in range(0, ((end_taw - begin_taw) / taw_step)):
            param_list = []
            for param in config_param_order:

                if param == "uniform_taw":
                    if i == 0:
                        current_taw = begin_taw
                    else:
                        current_taw += taw_step
                    param_list.append("{}: {}".format(param, current_taw))

                # set the seed
                if param == 'seed':
                    seed = config_dict[param] + j
                    param_list.append("{}: {}".format(param, seed))

                elif param == "--":
                    param_list.append('---') #param)
                elif param != 'uniform_taw':
                    val = config_dict[param]
                    param_list.append("{}: {}".format(param, val))

            print 'param list', param_list
            configuration_container.append(param_list)

        file_path = os.path.join(output_path, '{}.yml'.format(yaml_name))
        print file_path
        # Re-Write the config file old-school
        with open(file_path, 'w') as writefile:
            for doc in configuration_container:
                # print doc
                # writefile.write("---\n")
                for param in doc:
                    writefile.write("{}\n".format(param))
                # success

    # # now that we have the list of dictionaries, lets store the list in a dict where the key
    # # is the number of the nth run, and the value is the config dict.
    # run_dict_list = []
    # current_taw = begin_taw
    # # get the first value from the doclist is all you'll need
    # config_dict = doclist[0]
    # for i in range(0, ((end_taw - begin_taw) / taw_step)):
    #     run_dict = {}
    #     for param in config_param_order:
    #         if param == 'uniform_taw':
    #             current_taw += taw_step
    #             run_dict['{}'.format(i)] = config_dict[param]
    #         else:
    #             run_dict['{}'.format(i)] = config_dict[param]
    #     run_dict_list.append(run_dict)
    #
    # print 'run dict list: \n ', run_dict_list


        # for key, value in run_dict["{}".format(i)].iteritems():
        #     print value
        #     if key == "uniform_taw":
        #         run_dict["{}".format(i)]["{}".format(key)] = begin_taw
        #         current_taw += taw_step


    # # need to make the dict back into a list of dicts
    #
    # doclist_new = []
    # for i in range(0, ((end_taw - begin_taw) / taw_step)):
    #     doclist_new.append(run_dict["{}".format(i)])
    #
    # print "new edited doclist", doclist_new
    #




def run():
    """Here we basically take an ETRM_CONFIG file and edit it to our specifications."""

    # path to the file
    # config_path = "/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/ETRM_CONFIG_statewide.yml"
    # config_path = "/Users/dcadol/Desktop/academic_docs_II/ameriflux_aoi_qgis/ETRM_CONFIG_ameriflux_aoi.yml"
    # config_path = '/Users/dcadol/Desktop/academic_docs_II/ameriflux_aoi_qgis/ETRM_CONFIG_ameriflux_aoi_ceff_06.yml'
    config_path = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_configs/Wjs_config.yml'

    # path to directory where output config will go:
    output_path = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_configs'
    # name of output yaml
    yaml_name = 'Wjs_stochastic_6runs'
    # starting TAW value
    begin_taw = 25
    # ending TAW value
    end_taw = 925
    # grid search step size. Each ETRM run will increase the uniform TAW of the RZSW holding capacity by this many mm.
    taw_step = 25

    # number of runs to do for the stochastic runs each time. Determines the seed by adding an interger to the original
    #  config, giving each taw x-number of seeds
    runs = 6



    # format and output a config file to generate ETRM outputs based on a changing TAW value.
    stochastic_taw_grid_search(config_path, output_path, begin_taw, end_taw, taw_step, runs, yaml_name)

# Boilerplate
if __name__ == "__main__":

    run()