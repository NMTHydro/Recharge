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

import yaml

# ============= local library imports ===========================

"""
This script may be useful to format the ETRM config file ETRM_CONFIG.yml You should be able to generate a yml file
for a given number of runs, with certain specs. Default specs can be selected.
"""

def run():
    """Here we basically take an ETRM_CONFIG file and edit it to our specifications."""

    # path to the file
    config_path = "/Users/Gabe/ETRM_CONFIG_25_juliet.yml"

    # read in the file as a dict
    with open("{}".format(config_path), 'r') as config:
        try:
            # makes a list of all the configs for a given run. (List of dictionaries)
            doclist = [doc for doc in yaml.load_all(config)]
            #print doclist
            #print len(doclist)
        except yaml.YAMLError as exc:
            print(exc)

    # now that we have the list of dictionaries, lets store the list in a dict where the key
    # is the number of the nth run, and the value is the config dict.
    run_dict = {}

    for i, dic in enumerate(doclist):
        run_dict["{}".format(i)] = dic

    #print run_dict

    # test
    print("TAW of third run", run_dict['2']['uniform_taw'])

    # TODO - edit the 'uniform_taw' value of all the docs in the config.
    taw = 25
    for i in range(0, len(doclist)):
        for key, value in run_dict["{}".format(i)].iteritems():
            #print value
            if key == "uniform_taw":
                run_dict["{}".format(i)]["{}".format(key)] = taw
                taw += 45
                #print "TAW", taw

    # did it work?
    # for k, v in run_dict.iteritems():
    #     for key, value in v.iteritems():
    #         if key == "uniform_taw":
    #             print value

    # YAY it works now...

    print(run_dict)

    # TODO - rewrite the config file.

    # need to make the dict back into a list of dicts

    doclist_new = []
    for i in range (0, len(doclist)):
        doclist_new.append(run_dict["{}".format(i)])

    print("new edited doclist", doclist_new)

    # Maybe just rewrite the config file old-school
    with open('/Users/Gabe/ETRM_CONFIG_45_gabe_2.yml', 'w') as writefile:
        for doc in doclist_new:
            # print doc
            writefile.write("---\n")
            for k, v in doc.iteritems():
                writefile.write("{}: {}\n".format(k, v))
                # success

    # ANOTHER WAY TO DO IT BUT WITH A FLAW FOR THE LISTED ITEMS COME OUT AS TIC MARKED BITS.
    # got this part from: https://stackoverflow.com/questions/12470665/how-can-i-write-data-in-yaml-format-in-a-file
    # with open('/Users/Gabe/new_ETRM_CONFIG.yml', 'w') as writefile:
    #     for doc in doclist_new:
    #         writefile.write("---\n")
    #         yaml.dump(doc, writefile, default_flow_style=False)

# Boilerplate
if __name__ == "__main__":

    run()