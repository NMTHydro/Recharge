# ===============================================================================
# Copyright 2017 ross
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

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
import sys
import os
pp = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(pp)))

from app.paths import paths
from config import Config, check_config
from recharge.dataset import generate_dataset
from recharge.etrm_processes import Processes
from recharge.preprocessing import generate_rew_tiff
from recharge.raster_tools import make_results_dir

CLI_ENABLED = False


def run_dataset():
    print 'Running Dataset'

    cfg = Config()
    for runspec in cfg.runspecs:
        paths.build(runspec.input_root, runspec.output_root)
        paths.set_mask_path(runspec.mask)

        generate_dataset(runspec.date_range, runspec.output_root)


# def run_model(cfg_path=None):
#     print 'Running Model'
#     print 'this is the cfg_path {}'.format(cfg_path)
#     cfg = Config(cfg_path)
#     for runspec in cfg.runspecs:
#         print runspec.input_root
#         print runspec.output_root
#         paths.build(runspec.input_root, runspec.output_root)
#         print '1'
#         etrm = Processes(runspec)
#         etrm.configure_run(runspec)
#         etrm.run()

# This version if you have lots of runs.
def run_model(cfg_path=None):
    print 'Running Model'
    print 'this is the cfg_path {}'.format(cfg_path)
    cfg = Config(cfg_path)
    print cfg
    for i, runspec in enumerate(cfg.runspecs):
        runspec.output_root = '{}{:03n}'.format(runspec.output_root, i)
        # TODO - make a modified make_results_dir to only create of the 'outer' folder.
        make_results_dir(runspec.output_root)
        paths.build(runspec.input_root, runspec.output_root)
        etrm = Processes(runspec)
        etrm.configure_run(runspec)
        etrm.run()


def run_rew():
    print 'Running REW'
    generate_rew_tiff()


def run_help():
    print 'help'


def run_commands():
    keys = ('model', 'rew', 'help')
    print 'Available Commands: {}'.format(','.join(keys))


def welcome():
    print '''====================================================================================
 _______  _______  ______    __   __
|    ___||       ||    _ |  |  |_|  |
|   |___ |_     _||   |_||_ |       |
|    ___|  |   |  |    __  ||       |
|   |___   |   |  |   |  | || ||_|| |
|_______|  |___|  |___|  |_||_|   |_|
====================================================================================
Developed by David Ketchum, Jake Ross 2016
New Mexico Tech/New Mexico Bureau of Geology


Available commands are enumerated using "commands"

For more information regarding a specific command use "help <command>". Replace <command> with the command of interest
'''


def run(cfg_path=None):
    # check for a configuration file
    check_config(cfg_path)

    cmds = {'model': run_model, 'rew': run_rew,
            'help': run_help, 'commands': run_commands,
            'dataset':run_dataset}

    # run_dataset()
    # return

    welcome()

    if CLI_ENABLED:
        while 1:
            cmd = raw_input('>>> ')
            try:
                func = cmds[cmd]
            except KeyError:
                continue

            func()
    else:
        run_model(cfg_path)


if __name__ == '__main__':
    # # print sys.argv[1]
    if len(sys.argv) == 1:
        run()
    else:
        run(cfg_path=sys.argv[1])
    # run(cfg_path=None)

# ============= EOF =============================================
