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
import numpy as np

# ============= local library imports ===========================
from utils.EC_and_Soil_Moisture_Analysis.hendrickx_soil_moisture_model import stress_function

def process_eta(array_path, out_root, start_date, end_date):
    """"""

    # todo - finish this function

    pass

def create_rzsmf_obs(array_path, out_root, start_date, end_date):
    """"""

    # make a series of datetimes to move through a daily timestep from start to end
    start_date = datetime.date(start_date[2], start_date[1], start_date[0])
    end_date = datetime.date(end_date[2], end_date[1], end_date[0])
    date_delta = end_date - start_date
    total_days = date_delta.days

    print 'total_days', total_days

    # find the taw value of this set

    output_string = os.listdir(array_path)[0]
    taw = output_string.split("_")[-4]

    # get eta and etrs

    for i in range(total_days):
        current_date = start_date + datetime.timedelta(days=i)
        print 'day is', current_date

        # print 'current date', current_date
        # # === This method for generating rzsmf from Jan's model. May not make sense for synthetic data. ===
        # eta = "ETRM_daily_eta_taw_{}_{}_{}_{}.npy".format(taw, current_date.day, current_date.month, current_date.year)
        # etrs = "ETRM_daily_etrs_taw_{}_{}_{}_{}.npy".format(taw, current_date.day, current_date.month,
        #                                                     current_date.year)
        # # read the arrays,
        # eta_arr = np.load(os.path.join(array_path, eta))
        # etrs_arr = np.load(os.path.join(array_path, etrs))
        #
        # # add progressive noise to eta_arr. Sigma = 0.02
        # normal_eta_noise_array = np.random.normal(0.00, 0.02, eta_arr.shape)
        # eta_noise = eta_arr * normal_eta_noise_array
        # eta_arr_noise_added = eta_arr + eta_noise
        #
        # # make the etrf array
        # etrf_arr = eta_arr_noise_added / etrs_arr
        #
        # # apply Jan's stress function
        # rzswf = stress_function(ETrF=etrf_arr)

        rzsm = "ETRM_daily_rzsm_taw_{}_{}_{}_{}.npy".format(taw, current_date.day, current_date.month, current_date.year)

        # keep rzsmf naming convention instead of rzsm to distinguish
        rzswf_arr = np.load(os.path.join(array_path, rzsm))

        # add 'progressive' noise to rzswf. Sigma = 0.02
        normal_noise_array = np.random.normal(0.00, 0.02, rzswf_arr.shape)
        noise = rzswf_arr * normal_noise_array
        rzswf_error_added = rzswf_arr + noise

        rzswf_name = "synthetic_rzswf_obs_taw_{}_{}_{}_{}.npy".format(taw, current_date.day, current_date.month,
                                                                      current_date.year)
        rzswf_save_path = os.path.join(out_root, rzswf_name)

        # output the data to a file
        np.save(rzswf_save_path, rzswf_error_added, allow_pickle=True)

def data_finder(etrm_root, runs, year, out_root, start_date, end_date, rzsm=False):
    """"""

    for file in os.listdir(etrm_root):
        # print 'file', file
        etrm_run = os.path.join(etrm_root, file)
        for run_dir in os.listdir(etrm_run):
            # print 'run dir', run_dir
            if run_dir.startswith(year):
                # print 'file we want', run_dir
                r_d = os.path.join(etrm_run, run_dir)
                for dir in os.listdir(r_d):
                    if dir == 'numpy_arrays':
                        array_path = os.path.join(r_d, dir)
                        if rzsm:
                            # print 'array path', array_path
                            create_rzsmf_obs(array_path, out_root, start_date, end_date)
                        else:
                            # todo - finish this function
                            process_eta(array_path, out_root, start_date, end_date)

def main():

    etrm_root = "/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/" \
                "taw_optimization_etrm_outputs_nov_28_2percent"

    output_root = "/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/" \
                  "taw_optimization_synthetic_observations_nov_28_2percent"

    # if rzsm is true we create ETrF and convert to RZSM using Jan Hendrickx's stress function. If false or not
    # specified, we generate synthetic ETa observations.
    rzsm = True

    start_date = (1, 1, 2000)
    end_date = (31, 12, 2013)

    runs = 80

    # last two digits of the current year to get results
    year = str(datetime.datetime.today().year)[-2:]
    print 'this is the year the results were run', year

    data_finder(etrm_root, runs, year, output_root, start_date, end_date, rzsm=rzsm)


if __name__ == '__main__':

    main()

    # # to test for zero arrays
    # output_root = "/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/" \
    #               "taw_optimization_synthetic_observations_nov_27_2percent"
    #
    # for file in os.listdir(output_root):
    #
    #     arr = np.load(os.path.join(output_root, file))
    #
    #     print 'this is the array \n', arr
    #
    #     print 'this is the average value: {}'.format(np.average(arr))
