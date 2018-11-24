# ===============================================================================
# Copyright 2018 gabe-parrish
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
import datetime
from dateutil.relativedelta import relativedelta
import random
import yaml

# ============= local library imports ===========================

def get_synthetics(list_of_taws, list_of_dates, synpath):
    """"""

    # pick a random taw
    n_taws = len(list_of_taws)

    random_index = random.randint(0, n_taws)

    rand_taw = list_of_taws[random_index]

    synthetic_file_list = []
    for date in list_of_dates:
        file_name = 'synthetic_rzswf_obs_taw_{}_{}_{}_{}.npy'.format(rand_taw, date.day, date.month, date.year)
        file_path = os.path.join(synpath, file_name)
        synthetic_file_list.append(file_path)

    print 'the synthetic file list \n', synthetic_file_list

    return synthetic_file_list

def get_results(list_of_taws, list_of_dates, results_path, rzsm):
    """"""

    # go through the admittedyl weird data structure of the output files and append things to a dictionary based on the
    #  TAW value
    results_dictionary = {}
    for i, taw in enumerate(list_of_taws):
        level1_dir = os.listdir(results_path)[i]
        level2_dir = os.listdir(os.path.join(results_path, level1_dir))[0]
        dir_path = os.path.join(results_path, level1_dir, level2_dir, 'numpy_arrays')
        # print 'level 1: {}, level 2: {}'.format(level1_dir, level2_dir)
        print 'directory path: {}'.format(dir_path)
        sample_file = os.listdir(dir_path)[0]

        print 'sample file: {}'.format(sample_file)
        taw = sample_file.split("_")[-4]
        print 'taw: {}'.format(taw)

        results_list = []
        if rzsm:
            for date in list_of_dates:
                file_name = 'ETRM_daily_rzsm_taw_{}_{}_{}_{}.npy'.format(taw, date.day, date.month, date.year)
                file_path = os.path.join(dir_path, file_name)
                results_list.append(file_path)

        else:
            for date in list_of_dates:
                file_name = 'ETRM_daily_eta_taw_{}_{}_{}_{}.npy'
                file_path = os.path.join(dir_path, file_name)
                results_list.append(file_path)

        # put the results files in a dictionary indexed by the taw
        results_dictionary[taw] = results_list

    print 'this is the results dictionary \n\n', results_dictionary
    return results_dictionary

def get_taw(config):
    """
    Gets all the TAW values from the ETRM run
    :param config: yaml file
    :return: list of TAW values
    """
    with open(config, 'r') as cfg:
        doclist = [doc for doc in yaml.load_all(cfg)]
        # print 'doclist'
    # print ' the doclist   \n', doclist
    taw_list = [doc['uniform_taw'] for doc in doclist]

    print 'the taw list ', taw_list
    return taw_list

def random_date(start_date, end_date):
    """

    :param start_date: datetime date object of the start of the growing season.
    :param end_date: datetime date object of the end of the growing season.
    :return: random datetime object between start and end.
    """

    # subtract start from end. Get the time difference. Multiply by a random number between 0-1. Add the product to the
    #  start date. Return the sum: a random date within the growing season for a given year.

    date_diff = end_date - start_date

    rand_num = random.random()

    rand_date = start_date + datetime.timedelta(seconds=date_diff.total_seconds() * rand_num)

    print 'random date', rand_date

    return rand_date

def run_synthetic(synpath, results_path, n, config, rzsm=False):
    """
    Gathers data from a synthetic dataset.
    :param synpath: the path to the synthetic data
    :param results_path: the path to the etrm results
    :param n:
    :param config: the path to the config file used to complete the model run that developed the outputs.
    :param rzsm: if True, the program is grabbing rzsm files from the synthetic data and getting corresponding data from
     the model results.
    :return: the paths of the files to be used in statistical analysis for the observations and for the modeled results.
    """

    # ***** todo - we need to load the config file and get all the taws out to load in the model results. For the
    # observations, we'll need to randomly pick one TAW from the list and pull all of those. This way we'll know what
    # the 'right' answer should be for the optimized pixels *****

    list_of_taws = get_taw(config)

    # we want images in the growing season, so for each year we want between April 1 and October 31

    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2013, 12, 31)

    dates_to_get = []
    for i in range((end_date.year - start_date.year) + 1):
        year = start_date + relativedelta(years=i)
        print 'year', year.year

        grow_season_start = datetime.date(year.year, 4, 1)
        grow_season_end = grow_season_start + relativedelta(months=7)

        print "start -> {} |-|-| end -> {}".format(grow_season_start, grow_season_end)

        # get n random dates for each years growing season.
        for i in range(n):
            r_date = random_date(grow_season_start, grow_season_end)
            dates_to_get.append(r_date)

    print "we must retreive the images from these dates: \n", dates_to_get

    synthetic_observations = get_synthetics(list_of_taws, dates_to_get, synpath)

    etrm_results = get_results(list_of_taws, dates_to_get, results_path, rzsm)

    return synthetic_observations, etrm_results



def run():
    """"""
    pass


synthetic_mode = True
rzsm = True
if __name__ =="__main__":

    # the path to the results dataset
    results_path = "/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/taw_optimization_etrm_outputs"

    # the path to the synthetic dataset
    synpath = "/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/taw_optimization_synthetic_observations"
    # the path to the config file used to run the model
    config = '/Users/Gabe/ETRM_CONFIG.yml'
    # the number of days we want from each growing season
    n = 5
    if synthetic_mode:
        synthetic_obs, pyrana_results = run_synthetic(synpath, results_path, n, config, rzsm)

    else:
        # todo - make run once we have real results.
        run()
    # put the observations in the results dictionary
    pyrana_results['obs'] = synthetic_obs

    # output the dictionary to a .yml file
    gather_data_output_path = "/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/get_data_output.yml"

    with open(gather_data_output_path, 'w') as wfile:
        yaml.dump(pyrana_results, wfile)

    print 'DONE-ZO'