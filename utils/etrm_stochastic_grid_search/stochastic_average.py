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
import os
import numpy as np
from datetime import date, datetime
import yaml
import scandir
import time

# ============= standard library imports ========================

"""
In this script we grab all the .npy arrays generated in the stochastic grid search ETRM run. They are formatted as
ETRM_daily_eta_taw_150_seed_0_2000_1_1.npy where the last 3 are year month day. The numpy arrays of different seeds with
 matching TAWs need to be averaged together to get the stochastic average. Then the stochastic average numpy arrays are
  output with the format ETRM_daily_eta_taw_150_2000_1_1.npy, note the seed value will no longer be in there. This must
   be done for each kind of daily output that has been generated by the ETRM
"""


def list_output(taw_list, taw_sorted, output_root, outname):
    """

    :param taw_list:
    :param rzsm_taw_sorted:
    :param output_root:
    :param outname:
    :return:
    """
    print 'outname is {}'.format(outname)
    for t, tlist in zip(taw_list, taw_sorted):
        print 'saving t {} to file'.format(t)
        save_start = time.time()
        with open(os.path.join(output_root, outname.format(t)), 'w') as wfile:

            # firstseed = tlist[0]
            # secondseed = tlist[1]
            # thirdseed = tlist[2]
            # fourthseed = tlist[3]
            # fifthseed = tlist[4]
            # sixthseed = tlist[5]

            seeds = tlist[:6]

            header = ','.join(['seed{}file,seed{}val,seed{}date'.format(i, i, i) for i in range(6)])
            wfile.write('{}\n'.format(header))

            # wfile.write('seed0file,seed0val,seed0date,seed1file,seed1val,seed1date,seed2file,seed2val,seed2date,'
            #             'seed3file,seed3val,seed3date,seed4file,seed4val,seed4date,seed5file,seed5val,seed5date\n')
            ost = time.time()
            nseed = len(seeds[0])
            adur = 0
            for j, paths in enumerate(zip(*seeds)):
                # print(j, len(paths))

            # for j, paths in enumerate(tlist):
                # for one, two, three, four, five, six in zip(firstseed, secondseed, thirdseed, fourthseed, fifthseed,
                #                                             sixthseed):

                # one_arr = np.load(one[0])
                # one_val = one_arr[1, 1]
                # two_arr = np.load(two[0])
                # two_val = two_arr[1, 1]
                # three_arr = np.load(three[0])
                # three_val = three_arr[1, 1]
                # four_arr = np.load(four[0])
                # four_val = four_arr[1, 1]
                # five_arr = np.load(five[0])
                # five_val = five_arr[1, 1]
                # six_arr = np.load(six[0])
                # six_val = six_arr[1, 1]

                # row = []
                # for path, date_val in paths:
                #     arr = np.load(path)
                #     row.extend((path, arr[1, 1], date_val))
                st = time.time()

                row = [i for p,d in paths for i in (os.path.basename(p), str(np.load(p)[1,1]), d.isoformat())]
                row = ','.join(row)

                wfile.write('{}\n'.format(row))
                dur = time.time()-st
                # # print('writing row {}, et={}, adur={},'
                #       'timeleft={} t2={}'.format(j, dur, adur,
                #                                  adur*nseed-(time.time()-ost),
                #                                  adur*(nseed -j)
                #                                  ))
                adur = (dur+adur)/2.
                # wfile.write('{},{},{},'.format(one[0], one_val, one[1]))
                #
                # wfile.write('{},{},{},'.format(two[0], two_val, two[1]))
                #
                # wfile.write('{},{},{},'.format(three[0], three_val, three[1]))
                #
                # wfile.write('{},{},{},'.format(four[0], four_val, four[1]))
                #
                # wfile.write('{},{},{},'.format(five[0], five_val, five[1]))
                #
                # wfile.write('{},{},{}\n'.format(six[0], six_val, six[1]))

                # wfile.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(one[0], one[1], two[0], two[1], three[0],
                #                                                            three[1], four[0], four[1], five[0], five[1],
                #                                                            six[0], six[1]))
        save_elapsed = (time.time() - save_start)
        print 'the elapsed time to write the csv {}'.format(save_elapsed)


def taw_sort(file_date_list, runs, taw_list):
    taw_run_list = []

    for taw in taw_list:
        print 'taw {}'.format(taw)
        taw_start = time.time()
        taw_lst = []
        for run in range(runs):
            runlist = []

            for f in file_date_list:

                fpath, fdate = f

                numpy_filename = os.path.split(fpath)[1]

                numpy_seed = numpy_filename.split('_')[6]
                numpy_taw = numpy_filename.split('_')[4]

                if int(numpy_seed) == int(run) and int(numpy_taw) == int(taw):
                    runlist.append(f)

            taw_lst.append(runlist)

        taw_run_list.append(taw_lst)
        taw_elapsed = (time.time() - taw_start)
        print 'taw elapsed {}'.format(taw_elapsed)

    return taw_run_list


def make_taw_list(taw_tup):
    """
    makes a list of all the taws used
    :param taw_tup: (begin_taw, end_taw, taw_step)
    :return:
    """
    # upack
    begin_taw, end_taw, taw_step = taw_tup
    taw_list = []
    for i in range(0, ((end_taw - begin_taw) / taw_step)):
        taw = begin_taw + (i * taw_step)
        taw_list.append(taw)

    return taw_list


def stochastic_filesort(stochastic_file_csv, taw_tup, var_list, model_dates, runs, output_root):
    """
    This function will sort the numpy files saved by stochastic_file_finder into directories of time series of a given taw
    :param stochastic_file_csv: csv created by stochastic file finder with path to each numpy file for a given model run
    formatted as numpypath, date\n
    :return:
    """

    print 'doing a file sort on the csv created by stochastic file finder'

    main_dictionary = {}

    taw_list = make_taw_list(taw_tup)

    open_read = time.time()
    rzsm_lst = []
    ro_lst = []
    eta_lst = []
    infil_lst = []
    print 'opening'
    with open(stochastic_file_csv, 'r') as rfile:
        print 'iterating on lines'
        line_start = time.time()

        for j, line in enumerate(rfile):
            line_item = line.split(',')

            numpy_path = line_item[0]
            string_date = line_item[1][:-1]
            numpy_date = datetime.strptime(string_date, '%Y-%m-%d')

            numpy_filename = os.path.split(numpy_path)[1]
            # print numpy_filename
            # print j, line
            if 'rzsm' in numpy_filename:
                rzsm_lst.append((numpy_path, numpy_date))
            elif 'ro' in numpy_filename:
                ro_lst.append((numpy_path, numpy_date))
            elif 'eta' in numpy_filename:
                eta_lst.append((numpy_path, numpy_date))
            elif 'infil' in numpy_filename:
                infil_lst.append((numpy_path, numpy_date))

            # if j > 1000000:
            #     break
            if not j%10000:
                print j
        print('file line count {}'.format(j))
        line_end = (time.time() - line_start)
        print 'line time elapsed {}'.format(line_end)
    elapsed = (time.time() - open_read)
    print 'time elapsed to parse {}'.format(elapsed)

    # TODO now use sorted(list5, key=lambda vertex: (degree(vertex), vertex)) (firstkey, secondkey) tuple to sort by seed then TAW

    # sorting by a tuple of first, second and third criteria (seed, taw, date)
    def keyfunc(x):
        return os.path.split(x[0])[1].split('_')[6], os.path.split(x[0])[1].split('_')[4], x[1]

    rzsm_lst.sort(key=keyfunc)
    ro_lst.sort(key=keyfunc)
    eta_lst.sort(key=keyfunc)
    infil_lst.sort(key=keyfunc)

    print 'starting the taw sort'
    sort_start = time.time()
    ro_taw_sorted = taw_sort(ro_lst, runs, taw_list)
    sort_elapsed = (time.time() - sort_start)
    print 'sort elapsed {}'.format(sort_elapsed)

    eta_taw_sorted = taw_sort(eta_lst, runs, taw_list)
    sort_elapsed = (time.time() - sort_start)
    print 'sort elapsed {}'.format(sort_elapsed)

    infil_taw_sorted = taw_sort(infil_lst, runs, taw_list)
    sort_elapsed = (time.time() - sort_start)
    print 'sort elapsed {}'.format(sort_elapsed)

    rzsm_taw_sorted = taw_sort(rzsm_lst, runs, taw_list)
    sort_elapsed = (time.time() - sort_start)
    print 'sort elapsed {}'.format(sort_elapsed)

    # outname = '{}.csv'.format()

    list_output(taw_list, ro_taw_sorted, output_root, outname='ro_taw_{}.csv')
    list_output(taw_list, eta_taw_sorted, output_root, outname='eta_taw_{}.csv')
    list_output(taw_list, infil_taw_sorted, output_root, outname='infil_taw_{}.csv')
    list_output(taw_list, rzsm_taw_sorted, output_root, outname='rzsm_taw_{}.csv')

    # todo - finish out this so you can extract the value by loading the array and multiplying through each seed by each taw.


def stochastic_file_finder(output_name, base_dir, output_dir, taw_tup, runs, arr_shape, output_vars):
    """

    :param output_name:
    :param base_dir:
    :param output_dir:
    :param taw_tup:
    :param runs:
    :param arr_shape:
    :param output_vars:
    :return:
    """

    # upack
    begin_taw, end_taw, taw_step = taw_tup

    taw_list = []
    for i in range(0, ((end_taw - begin_taw) / taw_step)):
        taw = begin_taw + (i * taw_step)
        taw_list.append(taw)

    print 'taw list', taw_list

    # # find which params there are
    # swhc_dict = {}
    #
    # for swhc in taw_list:
    #     print 'swhc from list {}'.format(swhc)
    #
    #     for seed in range(runs):
    #
    #         print 'seed of run {}'.format(seed)
    #
    #         seed_dict = {}
    #
    #         for output_var in output_vars:
    #
    #             print 'output var {}'.format(output_var)
    #
    #             print ' making lists'
    #
    #             lst_dates = []
    #             lst_files = []
    #
    #             for path, dirs, files in os.walk(base_dir, topdown=False):
    #
    #                 if path.endswith('numpy_arrays') and len(files) > 0:
    #
    #                     print 'searching'
    #
    #
    #                     for f in files:
    #
    #                         ex_taw = f.split('_')[4]
    #
    #                         # ex) infil, eta, ro etc.
    #                         outvar = f.split('_')[2]
    #
    #                         # stochastic seed
    #                         stoch_seed = f.split('_')[6]
    #
    #                         fname = f.split('.')[0]
    #                         flist = fname.split('_')
    #
    #                         yr = int(flist[-3])
    #                         mnth = int(flist[-2])
    #                         dy = int(flist[-1])
    #
    #                         if int(ex_taw) == swhc:
    #
    #                             if int(stoch_seed) == seed:
    #
    #                                 if output_var == outvar:
    #
    #                                     lst_dates.append(date(yr, mnth, dy))
    #                                     lst_files.append(os.path.join(path, f))
    #
    #             seed_dict[output_var] = (lst_dates, lst_files)
    #
    #         print 'testing seed dict \n', seed_dict['infil'][0]
    #         print 'testing seed dict \n', seed_dict['infil'][1]
    #
    #         print 'populating swhc dict with seed dict for given seed {}'.format(seed)
    #         swhc_dict['{}'.format(seed)] = seed_dict
    #
    #
    # print 'testing \n', swhc_dict['0']['ro'][0]
    #
    # yaml_path = os.path.join(output_dir, '{}_files.yml'.format(output_name))
    #
    # with open(yaml_path, 'w') as wfile:
    #
    #     yaml.dump(swhc_dict, wfile)
    #
    # return yaml_path

    for path, dirs, files in scandir.walk(base_dir, topdown=False):
        walk_start = time.time()
        # print 'walking {}'.format(time.localtime(walk_start))
        if path.endswith('numpy_arrays') and len(files) > 0:
            print 'path \n {}'.format(path)

            start_path = time.time()
            # print 'start searching {}'.format(start_path)

            print 'searching {}'.format(time.localtime(start_path))

            all_files = []
            all_dates = []

            for f in files:
                fname = f.split('.')[0]
                flist = fname.split('_')

                yr = int(flist[-3])
                mnth = int(flist[-2])
                dy = int(flist[-1])

                all_files.append(os.path.join(path, f))
                all_dates.append(date(yr, mnth, dy))

            # print 'the length', len(all_files)

            if os.path.isfile(os.path.join(output_dir, '{}_appended.csv'.format(output_name))):
                start = time.time()
                # print 'start writing {}'.format(start)
                with open(os.path.join(output_dir, '{}_appended.csv'.format(output_name)), 'a') as wfile:
                    for f, d in zip(all_files, all_dates):
                        wfile.write('{},{}\n'.format(f, d))
                elapsed = (time.time() - start)
                # print 'write time: {}'.format(elapsed)
            else:
                start = time.time()
                # print 'start writing {}'.format(start)
                with open(os.path.join(output_dir, '{}_appended.csv'.format(output_name)), 'w') as wfile:
                    for f, d in zip(all_files, all_dates):
                        wfile.write('{},{}\n'.format(f, d))
                elapsed = (time.time() - start)
                # print 'write time: {}'.format(elapsed)

            elapsed_path = (time.time() - start_path)
            # print 'search time: {}'.format(elapsed_path)
            # print 'done searching at {}'.format(time.localtime(time.time()))

        walk_elapsed = time.time() - walk_start
        # print 'walktime {}'.format(walk_elapsed)
    print 'done {}'.format(datetime.now())
    # print 'file read now making dict'
    # swhc_dict = {}
    # for taw in taw_list:
    #     print 'taw {}'.format(taw)
    #     seed_dict = {}
    #     for seed in range(runs):
    #
    #         for outvar in output_vars:
    #
    #             lst_dates = []
    #             lst_files = []
    #
    #             # Tip: Just GET all the files together. Don't search over and over...
    #             # Do the sorting once all strings and dates are obtained.
    #
    #             with open(os.path.join(output_dir, '{}.csv'.format(output_name)), 'r') as rfile:
    #                 print 'reading'
    #
    #                 for line in rfile:
    #
    #                     line_lst = line.split(',')
    #
    #                     f = line_lst[0]
    #                     d = line_lst[1]
    #
    #                     filename = os.path.split(f)[1]
    #
    #                     ex_taw = filename.split('_')[4]
    #
    #                     # ex) infil, eta, ro etc.
    #                     otvar = filename.split('_')[2]
    #
    #                     # stochastic seed
    #                     stoch_seed = filename.split('_')[6]
    #
    #                     if int(ex_taw) == taw:
    #
    #                         if int(stoch_seed) == seed:
    #
    #                             if outvar == otvar:
    #                                 lst_files.append(f)
    #
    #                                 lst_dates.append(d)
    #
    #
    #             # for f, d in zip(all_files, all_dates):
    #             #
    #             #     filename = os.path.split(f)[1]
    #             #
    #             #     ex_taw = filename.split('_')[4]
    #             #
    #             #     # ex) infil, eta, ro etc.
    #             #     otvar = filename.split('_')[2]
    #             #
    #             #     # stochastic seed
    #             #     stoch_seed = filename.split('_')[6]
    #             #
    #             #     if int(ex_taw) == taw:
    #             #
    #             #         if int(stoch_seed) == seed:
    #             #
    #             #             if outvar == otvar:
    #             #
    #             #                 lst_files.append(f)
    #             #
    #             #                 lst_dates.append(d)
    #
    #         seed_dict[outvar] = (lst_dates, lst_files)
    #
    # swhc_dict['{}'.format(seed)] = seed_dict
    #
    # yaml_path = os.path.join(output_dir, '{}_files_speedtest.yml'.format(output_name))
    #
    # with open(yaml_path, 'w') as wfile:
    #
    #     yaml.dump(swhc_dict, wfile)
    #
    # return yaml_path


if __name__ == '__main__':

    # ================================= File Sorter ========================================

    stochastic_csv_file = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_III/wjs/wjs_appended.csv'

    # starting TAW value
    begin_taw = 25
    # ending TAW value
    end_taw = 925
    # grid search step size. Each ETRM run will increase the uniform TAW of the RZSW holding capacity by this many mm.
    taw_step = 25
    taw_tup = (begin_taw, end_taw, taw_step)
    # taw_tup = (25, 50, 25)
    start_date = date(2000, 1, 1)

    end_date = date(2013, 12, 30)

    model_dates = (start_date, end_date)

    # list of variables
    var_list = ['rzsm', 'ro', 'eta', 'infil']

    runs = 6

    output = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_III/wjs'

    stochastic_filesort(stochastic_csv_file, taw_tup, var_list, model_dates, runs, output)

    # ###### ========================== File Finder ===========================================
    # print datetime.now()
    # output_name = 'wjs'
    #
    # print 'DOING {}'.format(output_name)
    #
    # # base_dir = '/Users/dcadol/Desktop/mini_model_rsync/ses'
    # # output_dir = '/Users/dcadol/Desktop/mini_model_rsync/ses'
    # base_dir = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_III/wjs'
    # output_dir = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_III/wjs'
    #
    # print base_dir
    # print output_dir
    #
    # # starting TAW value
    # begin_taw = 25
    # # ending TAW value
    # end_taw = 925
    # # grid search step size. Each ETRM run will increase the uniform TAW of the RZSW holding capacity by this many mm.
    # taw_step = 25
    #
    # taw_tup = (begin_taw, end_taw, taw_step)
    #
    # # number of the stochastic runs each time. Determines the seed by adding an interger to the original
    # #  config, giving each taw 10 seeds
    # runs = 6
    #
    # # shape of the array
    # arr_shape = (3, 3)
    #
    # output_vars = ['eta', 'rzsm', 'ro', 'infil']
    #
    # yaml_path = stochastic_file_finder(output_name, base_dir, output_dir, taw_tup, runs, arr_shape, output_vars)
