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

# ============= local library imports ===========================
import yaml
from runners.distributed_daily import dist_daily_run, dist_daily_taw_run
from runners.paths import Paths

def run1(config_dict, config_path):
    """Modifies ETRM_CONFIG.yml to NOT have taw_mod_output_root then runs dist_daily_run."""

    key_to_remove = 'taw_mod_output_root'

    if key_to_remove in config_dict:
        del config_dict[key_to_remove]

    print "run1 dict", config_dict

    print "config path --->{}".format(config_path)
    with open(config_path, 'w') as wfile:
        for key, item in config_dict.iteritems():
            wfile.write('{}: {}\n'.format(key, item))

    dist_daily_run()
    return None

    #dist_daily_run()

    # if dict['taw_mod_output_root'] in dict:
    #
    #     dict['taw_mod_output_root']
    #return None
#
def run2(config_dict, yml_path):
    """Modifies ETRM_CONFIG.yml to have taw_mod_output_root: /Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output
     then runs dist_daily_taw_run."""

    # print config_dict
    #
    # print yml_path

    key_to_add = 'taw_mod_output_root'

    if key_to_add not in config_dict:
        config_dict[key_to_add] = '/Users/Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output'

    print "taw Mod added to dict", config_dict

    with open(yml_path, 'w') as wfile:
        for key, item in config_dict.iteritems():
            wfile.write('{}: {}\n'.format(key, item))

    dist_daily_taw_run()

    return None

def config_format():
    """Makes a dict out of items in ETRM config to begin with and returns the dict."""

    config_path = Paths()

    yml_path = config_path.config

    print "yaml_path", yml_path

    with open(yml_path, 'r') as rfile:
        yaml_thingy = yaml.load(rfile)

    #print yaml_thingy

    return yaml_thingy, yml_path


if __name__ == "__main__":

    config_dict, yml_path = config_format()

    print "dict -> {} \n path -> {}".format(config_dict, yml_path)

    run1(config_dict, yml_path)

    run2(config_dict, yml_path)


#taw_mod_output_root: /Users_Gabe/Desktop/ETRM_Desktop_TAW_Mod_Output