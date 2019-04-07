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
import shutil
import yaml
import datetime
import numpy as np
from matplotlib import pyplot as plt

# ============= local library imports ===========================
from utils.depletions_modeling.net_cdf_extract_to_tiff import write_raster
from recharge.raster_tools import convert_raster_to_array


# ===== GLOBAL VARIABLES =====
eeflux = False
jpl = True


def pull_series(data_dict):

    observation_files = data_dict['obs']
    # print 'observation files\n ', observation_files

    # get the dates when we have observations for synthetic data
    obs_dates = []
    for obs in observation_files:
        filename = obs.split('/')[-1]
        name = filename.split('.')[0]
        date_components = [int(i) for i in name.split('_')[-3:]]
        dt = datetime.date(year=date_components[2], month=date_components[1], day=date_components[0])
        obs_dates.append(dt)

    # print 'the dates we observed \n{}'.format(obs_dates)
    print len(obs_dates)

    taw_vals = []
    for k in data_dict.iterkeys():
        if k != 'obs':
            taw_vals.append(int(k))

    print 'values of taw that need to be tested \n', sorted(taw_vals)

    # sort both of them
    taw_vals = sorted(taw_vals)
    obs_dates = sorted(obs_dates)

    return obs_dates, taw_vals

def pull_series_jpl(data_dict):
    observation_files = data_dict['obs']
    obs_dates = []

    for obs in observation_files:
        filename = obs.split('/')[-1]
        file_lst = filename.split('.')
        # print file_lst[0]
        y = int(file_lst[0])
        m = int(file_lst[1])
        d = int(file_lst[2])

        jpl_date = datetime.date(y, m, d)

        # print 'eeflux_date', eeflux_date
        obs_dates.append(jpl_date)

    taw_vals = []
    for k in data_dict.iterkeys():
        if k != 'obs':
            taw_vals.append(int(k))

    # sort both of them
    taw_vals = sorted(taw_vals)
    obs_dates = sorted(obs_dates)

    return obs_dates, taw_vals

def pull_series_eeflux(data_dict):
    """"""

    observation_files = data_dict['obs']
    # print 'observation files\n ', observation_files

    # get dates when we have observations for eeflux
    obs_dates = []
    for obs in observation_files:
        filename = obs.split('/')[-1]
        name = filename.split('_')[0]
        year = name[9:13]
        j_date = name[13:16]

        eeflux_date = datetime.datetime.strptime('{}{}'.format(year, j_date), '%Y%j').date()
        # print 'date: ', eeflux_date
        obs_dates.append(eeflux_date)

    taw_vals = []
    for k in data_dict.iterkeys():
        if k != 'obs':
            taw_vals.append(int(k))

    # sort both of them
    taw_vals = sorted(taw_vals)
    obs_dates = sorted(obs_dates)

    return obs_dates, taw_vals


def get_obs_arr(obs, date):
    """"""

    for observation in obs:
        ending = '{}_{}_{}.npy'.format(date.day, date.month, date.year)
        if observation.endswith(ending):
            arr = np.load(observation)
            return arr


def get_obs_arr_jpl(obs, date):
    """"""

    for observation in obs:
        name = observation.split('/')[-1]
        file_lst = name.split('.')
        y = int(file_lst[0])
        m = int(file_lst[1])
        d = int(file_lst[2])

        jpl_date = datetime.date(y, m, d)

        if '{}_{}_{}'.format(jpl_date.year, jpl_date.month, jpl_date.day) == '{}_{}_{}'.format(date.year,
                                                                                                        date.month,
                                                                                                        date.day):
            arr = convert_raster_to_array(observation)
            # print 'shape', arr.shape

            return arr


def get_obs_arr_eeflux(obs, date):
    """"""

    for observation in obs:
        # print 'I observe: ', observation

        obsfile = observation.split('/')[-1]
        obsname = obsfile.split('_')[0]
        # print 'obsname: ', obsname
        year = obsname[9:13]
        j_date = obsname[13:16]

        eeflux_date = datetime.datetime.strptime('{}{}'.format(year, j_date), '%Y%j').date()

        if '{}_{}_{}'.format(eeflux_date.year, eeflux_date.month, eeflux_date.day) == '{}_{}_{}'.format(date.year,
                                                                                                        date.month,
                                                                                                        date.day):
            arr = convert_raster_to_array(observation)
            # print 'shape', arr.shape

            return arr



def get_model_arr(model_results, date):

    for result in model_results:
        # TODO - when did this get fucked up?
        ending = '{}_{}_{}.npy'.format(date.day, date.month, date.year)
        ending = '{}_{}_{}.npy'.format(date.year, date.month, date.day)
        if result.endswith(ending):
            arr = np.load(result)
            # print 'model shape', arr.shape
            return arr

def save_to_temp(squared_residual_datelist, taw):
    """"""

    read_list = []

    temp_location = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_temp/'
    temp_location ='/Users/dcadol/Desktop/desktop_taw_optimization_temp/'

    for tup in squared_residual_datelist:
        resid_date = tup[0]
        sq_resid_arr = tup[1]

        # print 'taw tup[0', taw
        # print 'sq resid arr tup[1', sq_resid_arr



        temp_name = '{}_{}_{}_{}.npy'.format(taw, resid_date.year, resid_date.month, resid_date.day)

        # print temp_location
        # print temp_name

        file_address = os.path.join(temp_location, temp_name)

        # file_address = "{}/{}".format(temp_location, temp_name)

        # save the locations of the temp squared residual files
        read_list.append(file_address)

        if not os.path.isfile(file_address):
            np.save(file_address, sq_resid_arr)

    return read_list



def get_sse(data_dict, obs_dates, taw_vals, read_eeflux_tiff=False, read_jpl_tiff=False, read_numpy=False):
    """"""
    print 'true false eef {}, jpl {}, numpy, {}'.format(read_eeflux_tiff, read_jpl_tiff, read_numpy)
    obs = data_dict['obs']

    # a dictionary to store the residuals indexed by date and sorted by taw
    residual_dict = {}

    # we should store the squared residuals in the chi dict
    chi_dict = {}

    # # FOR TESTING
    # taw_vals = [225, 250]
    # ==== MEMORY INTENSIVE  (we avoid serious memory leaks by writing to files...)====
    new_obs_dates = []
    for taw in taw_vals:

        print 'taw', taw
        model_results = data_dict['{}'.format(taw)]

        # we store tuples of dates and residuals in this
        residual_datelist = []
        # store tuples of dates and squared residuals here
        squared_residual_datelist = []

        read_list = []

        for i, resid_date in enumerate(obs_dates):

            # for a given taw, we have the observed array and the model array here

            # # TODO get rid of this 'if' statement to calibrate to dates not in the growing season...
            # if resid_date > datetime.date(resid_date.year, 6, 1) and resid_date < datetime.date(resid_date.year, 9, 30):

            if read_eeflux_tiff:
                obs_arr = get_obs_arr(obs, resid_date)
            elif read_numpy:
                obs_arr = get_obs_arr_eeflux(obs, resid_date)

            elif read_jpl_tiff:
                obs_arr = get_obs_arr_jpl(obs, resid_date)

            if np.isnan(obs_arr).all():
                print 'WARNING \n {} \n obs arr is nan for {}'.format(obs_arr, resid_date)

            # get the ETRM modeled array that matches the observation.
            model_arr = get_model_arr(model_results, resid_date)

            if np.isnan(model_arr).all():
                print 'WARNING \n {} \n model arr is nan for {}'.format(model_arr, resid_date)

            # the residuals are the observed values - modeled values
            # GET RID of NaN values for both obs and modeled [by turning them both to zero] (GELP March 2, 2019)
            obs_arr = np.nan_to_num(obs_arr)
            model_arr = np.nan_to_num(model_arr)
            # calculate the residual array
            residual_arr = obs_arr - model_arr # todo - divide by uncertainty to normalize

            if np.isnan(residual_arr).all():
                print 'WARNING \n {} \n residual arr is nan for {}'.format(residual_arr, resid_date)

            # # store the date and the residual array in a tuple and append to a list.
            # store_residual = (date, residual_arr)
            # residual_datelist.append(store_residual)

            # get chi (square error)
            chi = residual_arr ** 2
            # store_chi = (date, chi)

            if np.isnan(chi).all():
                print 'WARNING \n {} \n chi arr is nan for {}'.format(chi, resid_date)

            if not np.isnan(chi).all():

                # get new observation dates
                new_obs_dates.append(resid_date)

                # these you can use to generate a time series analysis of the root squared error.
                temp_name = '{}_{}_{}_{}.npy'.format(taw, resid_date.year, resid_date.month, resid_date.day)

                read_list.append('/Users/dcadol/Desktop/desktop_taw_optimization_temp/{}'.format(temp_name))

                np.save('/Users/dcadol/Desktop/desktop_taw_optimization_temp/{}'.format(temp_name), chi)


        chi_dict['{}'.format(taw)] = read_list


    # need residual sum of squares (for each taw), degrees of freedom (number of obs of each taw +1), and taw values
    # taw_list = taw_vals
    rss_list = []
    dof_list = []
    test_list = []
    for taw in taw_vals:
        print 'were on taw {}'.format(taw)
        n = 0
        # make a zeros array from the shape of one of the arrays in the chi_dict.
        sample_path = chi_dict['{}'.format(taw)][0]
        sample_arr = np.load(sample_path)

        # print 'the sample array'
        # plt.imshow(sample_arr)
        # plt.show()
        # zeros array:
        rss = np.zeros(sample_arr.shape)
        print 'len chi dict', len(chi_dict["{}".format(taw)])

        # print 'the zero array'
        # plt.imshow(rss)
        # plt.show()
        # the rss list is getting the squared value of the residual
        for i, file_address in enumerate(chi_dict['{}'.format(taw)]):

            # add up all the squared residuals and that's the sum of squared residuals
            squared_resid_arr = np.load(file_address)

            squared_resid_arr = np.nan_to_num(squared_resid_arr)

            rss += squared_resid_arr

            n += 1

        # # append the sum of each taw's squared errors to
        print 'final rss for taw {}'.format(taw)
        print 'rss', rss
        rss_list.append(rss)
        dof_list.append(n)

    residual_sum_squares_dict = {'taw': taw_vals, 'rss': rss_list, 'dof': dof_list}


    # print 'the rss \n', residual_sum_squares_dict

    return residual_sum_squares_dict #chi_dict, residual_dict

def csv_output(taw_vals, rss_arrs, outpath, geo_info=None):
    """"""

    # first get the coordinates of the array into an array of the same size
    basic_arr = rss_arrs[0]
    x_coords = np.empty(basic_arr.shape)
    y_coords = np.empty(basic_arr.shape)
    # coord_arr =

    # get x, and y origin from the transform
    geotrans = geo_info['geotransform']
    xOrigin = geotrans[0]
    yOrigin = geotrans[3]
    width_of_pixel = geotrans[1]
    height_of_pixel = geotrans[5]

    # shape is (rows, cols) i.e. (y, x) spatially
    print 'shape', basic_arr.shape

    # xs change along the columns
    for i in range(basic_arr.shape[1]):
        x_coord = (i * width_of_pixel) + xOrigin
        # ys change along the rows
        for j in range(basic_arr.shape[0]):
            y_coord = yOrigin - (j * height_of_pixel)

            # put em in as (rows, cols)
            x_coords[j, i] = x_coord
            y_coords[j, i] = y_coord

    # print 'x coordinate array \n', x_coords
    # print 'y coordinate array \n', y_coords


    # flatten each array
    flat_x_coords = x_coords.ravel()
    flat_y_coords = y_coords.ravel()
    # convert to list
    x_list = flat_x_coords.tolist()
    y_list = flat_y_coords.tolist()

    print 'about to open file'

    # open a csv file and save the header and lines
    with open('{}/rss_array_output.csv'.format(output_path), mode='w') as wfile:
        print 'file opened'

        # header
        head = 'x, y, taw, pixel_rss\n'
        wfile.write(head)

        for value, rss_arr in zip(taw_vals, rss_arrs):
            # make value a list the same size as the x_coords/y_coords
            value_arr = np.full(flat_x_coords.shape, value).tolist()

            # flatten rss_arr
            flat_rss_list = rss_arr.ravel().tolist()

            for i , value, in enumerate(value_arr):

                ln = '{}, {}, {}, {}\n'.format(x_list[i], y_list[i], value, flat_rss_list[i])

                wfile.write(ln)
    print 'done writing to csv'


def geotiff_output(taw_vals, rss_arrs, geo_info, outpath):
    """"""
    for arr, taw_val in zip(rss_arrs, taw_vals):
        outname = 'rss_image_taw_{}.tif'.format(taw_val)
        numpy_to_geotiff(arr, geo_info, outpath, outname)

def numpy_to_geotiff(array, geo_info, output_path, output_name):
    """"""

    trans = geo_info['geotransform']

    dim = geo_info['dimensions']
    proj = geo_info['projection']

    print'transform', trans
    print 'dimensions', dim
    print 'projections', proj

    write_raster(array, geotransform=trans, output_path=output_path, output_filename=output_name,
                 dimensions=dim, projection=proj)

def optimize_taw(rss, output_path, geo_info=None, big_arr=False):
    """"""

    print 'optimizing taw'
    # get taw, rss arrays, and degrees of freedom out.
    taw_vals = rss['taw']
    rss_arrs = rss['rss']
    dof_vals = rss['dof']

    # degrees of freedom (m-n) where n=1 in this case ... (n - parameters, m - observations)
    df = [(dof - 1) for dof in dof_vals]
    # square root of the degrees of freedom
    nu = [(dof - 1) ** 0.5 for dof in dof_vals]
    # square root of the sum of squares
    norm = [rss ** 0.5 for rss in rss_arrs]

    # get the standard deviation from the residuals (I'm not sure what Juliet was using it for)
    s = [norm_val / nu_val for norm_val, nu_val in zip(norm, nu)]

    # before you optimize TAW, store the values in ways that are easy to visualize
    if not big_arr:
        print '\n outputting to csv since file is not so big \n'
        # output each pixel as a separate .csv
        csv_output(taw_vals, rss_arrs, outpath=output_path, geo_info=geo_info)

    # output this into a group of GeoTiffs
    geotiff_output(taw_vals, rss_arrs, geo_info, output_path)

    # ====== FIND the TAW vals that correspond to min root sum squared error ======

    # for storing the minimum rss
    rss_tab = np.empty(rss_arrs[0].shape)
    # for storing the minimum taw
    taw_tab = np.empty(rss_arrs[0].shape)
    # to store the passing 95% confidence array (0/1)
    threshold_95_tab = np.zeros(rss_arrs[0].shape)

    count = 0
    for taw, rss_array in zip(taw_vals, rss_arrs):

        print 'checking rss for taw: {}'.format(taw)

        # make each taw into an array so we can index it
        taw_arr = np.full(rss_array.shape, taw, dtype='float64')

        # i want rss_tab to be set equal to the first array and then take the minimum rss value after that with each successive array.
        if count == 0:
            rss_tab = rss_array
            taw_tab = np.full(rss_array.shape, taw, dtype='float64')

        else:
            # get the boolean where rss_array is smaller than rss_tab
            smaller_than = rss_array < rss_tab
            print'smaller than array \n', smaller_than

            # copy the rss over to rss tab where the new rss array is smaller
            np.copyto(rss_tab, rss_array, where=smaller_than)

            # copy in the taws to the taw_tab where the rss is smaller
            np.copyto(taw_tab, taw_arr, where=smaller_than)
        # keep the counter going
        count += 1

    print 'the minimum rss tab at the end of the loop \n', rss_tab

    # ====== CALCULATE the Minimum CHI SQUARE and 95% confidence ======

    # calculate the smallest residual sum of squares (I don't understand how this is different from the RSS)
    smin = (rss_tab ** (0.5)) / (df[0] ** (0.5))
    # I feel like the only reason we calculate smin is to get chimin and c...
    sq = smin ** 2

    # calculate the smallest Chi square in order to display it later
    # ERROR
    chimin = rss_tab / sq

    print 'this is the chimin array \n', chimin

    # calculate the 95% confidence interval from chi-square table with degrees of freedom of 1
    c = chimin + 3.841459

    # normalize the (minimum) sum of squares by dividing the sum by the sq. of the smin(for direct comparison w chimin?)
    # if this array exceeds the 95% conf int raster, we pass the chi squared test
    # ERROR
    t = rss_tab / sq

    # give the empty array a value of 1 if the normalized min sum of squares exceeds the chi square confidence interval
    threshold_bool = t > c
    print 'threshold bool\n', threshold_bool
    threshold_95_tab[threshold_bool] = 1
    print 'threshold_95 tab \n', threshold_95_tab

    print 'taw tab at the end \n', taw_tab


    # ====== OUTPUT arrays as rasters for optimized TAW and confidence interval ======
    # save the optimized_taw as a numpy array and as a geotiff

    # SAVE the optimized TAWs to a tiff file
    numpy_to_geotiff(taw_tab, geo_info, output_path, output_name='optimized_taw.tif')
    np.save(os.path.join(output_path, 'optimized_taw.npy'), taw_tab)

    # output the 95% confidence interval as a raster
    numpy_to_geotiff(c, geo_info, output_path, output_name='95_confidence_lvl.tif')

    #if this raster exceeds the 95% conf int raster, we pass the chi squared test
    numpy_to_geotiff(t, geo_info, output_path, output_name='norm_min_rss.tif')

    # output the binary array as a raster indicating where the parametrized TAW would be passing the Chi2 95% C.I.
    numpy_to_geotiff(threshold_95_tab, geo_info, output_path, output_name='95_pass.tif')


def main(data_dir, output_path, geo_info, eeflux=False, jpl=False):
    """"""

    # open the data
    with open(data_dir, 'r') as yam:
        # load() returns a dict. load_all() returns a yaml object. Usefull if many subfiles are embedded.
        data_dict = yaml.load(yam)
    # pull
    if eeflux:
        obs_dates, taw_vals = pull_series_eeflux(data_dict)
    elif jpl:
        obs_dates, taw_vals = pull_series_jpl(data_dict)
    else:
        obs_dates, taw_vals = pull_series(data_dict)

    # proceed by date and taw to read each image. Probably won't need chi and residuals but we get them in case we do.
    if eeflux:
        read_ee_tiff = True
        read_jpl_tiff = False
        numpy = False
    elif jpl:
        read_jpl_tiff = True
        read_ee_tiff = False
        numpy = False
    else:
        numpy = True
        read_jpl_tiff = False
        read_ee_tiff = False

    rss = get_sse(data_dict, obs_dates, taw_vals, read_eeflux_tiff=read_ee_tiff,
                                  read_jpl_tiff=read_jpl_tiff, read_numpy=numpy)

    # pull out the geo info
    with open(geo_info, mode='r') as geofile:
        geo_dict = yaml.load(geofile)

    # print 'testing the geo dict -> ', geo_dict


    # get the square root of the sum of squares
    optimize_taw(rss, output_path, geo_info=geo_dict, big_arr=False)

    # alternate TAW optimization routine.
    optimize_taw_disaggregate(rss, output_path, geo_info=geo_dict, big_arr=False)

def optimize_taw_disaggregate(rss, output_path, geo_info, big_arr=False, test_mode=False):
    """

    :param rss:
    :param output_path:
    :param geo_info:
    :param big_arr:
    :param test_mode:
    :return:
    """


    if test_mode:

        test_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/taw_calibration_disaggregated/grassland_test.csv'

        with open(test_path, 'r') as rfile:

            taw_vals = []
            rss_vals = []

            for line in rfile:
                taw_rss = line.split(',')
                taw = int(taw_rss[0])
                rss = float(taw_rss[1])

                taw_vals.append(taw)
                rss_vals.append(rss)

        # get the average daily rss in mm
        rss_vals_avg_daily = [((rss / 11.0) / 365.0) for rss in rss_vals]

        print 'the rss avg daily error \n', rss_vals_avg_daily

        error_reduced_lst = []
        for i in range(len(rss_vals_avg_daily)):
            # print 'i', i
            if i == 0:
                error_reduced_lst.append('')

            elif i > 0:
                # calculate the error reduced by each taw step
                error_reduced = rss_vals_avg_daily[i] - rss_vals_avg_daily[i-1]
                error_reduced_lst.append(error_reduced)

            # elif i == len(rss_vals_avg_daily)
        print 'the error reduced list \n', error_reduced_lst

        # set the first value of the list to the second value
        error_reduced_lst[0] = error_reduced_lst[1]
        print 'the error reduced list \n', error_reduced_lst

        # round the values to the 2nd decimal place
        error_reduced_lst= [round(i, 2) for i in error_reduced_lst]

        # # select the TAW after which error reduced is no longer greater than 0.01
        # for taw, reduced_error in zip(taw_vals, error_reduced_lst):
        #     print 'taw {}, re {}'.format(taw, reduced_error)
        indx_lst = []
        for i, re in enumerate(error_reduced_lst):
            if abs(re) <= 0.01:
                indx_lst.append(i)

        print 'the index list\n', indx_lst
        consecutives = []
        for i in range(len(indx_lst)+1):

            if i > 0 and i < (len(indx_lst)-1):
                print i
                if indx_lst[i + 1] == indx_lst[i] + 1:
                    consecutives.append(indx_lst[i])
            elif i == len(indx_lst)-1:
                if indx_lst[i] -1 == indx_lst[i-1]:
                    consecutives.append(indx_lst[i-1])
                    consecutives.append(indx_lst[i])

        print 'consecutives \n', consecutives

        # take the first index after which the reduced error is consistently less than or equal to 0.01

        target_index = consecutives[0]

        # taw at the target index is the optimum taw

        optimum_taw = taw_vals[target_index]

        print 'optimum taw', optimum_taw

    else:

        # # Save the rss dict as a .yml to be tested with disagg_tester.py
        # test_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/taw_calibration_disaggregated/rss.yml'
        # with open(test_path, 'w') as wfile:
        #     yaml.dump(rss, wfile)

        print 'optimizing taw'
        # get taw, rss arrays out.
        taw_vals = rss['taw']
        rss_arrs = rss['rss']




        print 'len of rss arrs', len(rss_arrs)

        # get the average daily rss in mm
        rss_vals_avg_daily = [((rss / 11.0) / 365.0) for rss in rss_arrs]

        print 'the rss avg daily error \n', len(rss_vals_avg_daily)

        error_reduced_lst = []
        for i in range(len(rss_vals_avg_daily)):
            print 'i', i
            if i == 0:
                error_reduced_lst.append('')

            elif i > 0:
                # calculate the error reduced by each taw step
                error_reduced = rss_vals_avg_daily[i] - rss_vals_avg_daily[i - 1]
                error_reduced_lst.append(error_reduced)

            # elif i == len(rss_vals_avg_daily)
        print 'the error reduced list \n', error_reduced_lst

        # set the first value of the list to the second value
        error_reduced_lst[0] = error_reduced_lst[1]
        print 'the error reduced list \n', error_reduced_lst

        # make all errors positive by taking the absolute value
        error_reduced_lst = [np.absolute(i) for i in error_reduced_lst]

        # round the values to the 2nd decimal place FOR AN ARRAY
        error_reduced_lst = [np.round(i, 2) for i in error_reduced_lst]

        # # select the TAW after which error reduced is no longer greater than 0.01

        # prepare to store three dimensional arrays with dstack
        value_shape = rss_arrs[0].shape
        three_d_shape = (value_shape[0], value_shape[1], 0)
        # for storing the rss value < 0.01

        # todo - should this be np.zeros or is np.empty better?
        # reduced_error_tab = np.zeros(three_d_shape, dtype=bool)
        reduced_error_tab = np.empty(three_d_shape)

        # for storing the minimum taw
        taw_tab = np.empty(three_d_shape)

        for taw, error_array in zip(taw_vals, error_reduced_lst):

            print 'checking rss for taw: {}'.format(taw)

            # make each taw into an array so we can index it
            taw_arr = np.full(error_array.shape, taw, dtype='float64')

            # we only want to store values that are less than or equal to 0.01 when rounded (rounding handled earlier)

            # get the boolean where error array is less than 0.01
            smaller_than = error_array <= 0.01
            print'smaller than array \n', smaller_than

            # append the smaller than array to reduced error tab with dstack
            reduced_error_tab = np.dstack((reduced_error_tab, smaller_than))

            # append the taw array to a 3d array
            taw_tab = np.dstack((taw_tab, taw_arr))

        print '3d array True for error values less than or equal to 0.01 otherwise, False \n', reduced_error_tab

        # 1) go through the 3d array of true false from start to finish, extract true/false as list along 3rd dimension
        # 2) go through that list and get the indices of the true values
        # 3) get the indices that are consecutive
        # 4) take the first of the consecutive indices and grab the corresponding TAW.
        # 5) put the TAW back in a 2d array where it belongs.

        # This will hold the optimized TAW (2d array)
        optimum_taw_disagg = np.empty(rss_arrs[0].shape)

        # iterate through the 3d array
        cols, rows, vals = reduced_error_tab.shape
        for i in range(cols):
            for j in range(rows):

                true_indices = []
                taw_lst = []

                for k in range(vals):
                    taw = taw_tab[i, j, k]
                    taw_lst.append(taw)
                    if reduced_error_tab[i, j, k]:
                        true_indices.append(k)

                consecutives = []
                for i in range(len(true_indices) + 1):

                    if i > 0 and i < (len(true_indices) - 1):
                        if true_indices[i + 1] == true_indices[i] + 1:
                            consecutives.append(true_indices[i])
                    elif i == len(true_indices) - 1:
                        if true_indices[i] - 1 == true_indices[i - 1]:
                            consecutives.append(true_indices[i - 1])
                            consecutives.append(true_indices[i])

                print 'consecutives \n', consecutives

                # take the first index after which the reduced error is consistently less than or equal to 0.01

                try:
                    target_index = consecutives[0]
                except IndexError:
                    target_index = 0

                # taw at the target index is the optimum taw

                optimum_taw = taw_lst[target_index]
                # when we have the taw value put it back in the 2d array
                optimum_taw_disagg[i, j] = optimum_taw

    # # # todo - output the rasters
    numpy_to_geotiff(optimum_taw_disagg, geo_info, output_path, output_name='optimized_taw_disagg.tif')



if __name__ == "__main__":

    # # FOR SYNTHETIC DATA
    # # path to the .yml_file
    # data_locations_dir = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/get_data_output.yml'
    # output_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results'
    # geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info.yml'
    # main(data_locations_dir, output_path, geo_info_path)

    # # EEFLUX paths
    # data_locations_dir = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/get_data_output_eeflux.yml'
    # output_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results_eeflux'
    #
    # # for turning arrays into geotiffs
    # geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info.yml'
    #
    # # todo - should be a place to get the geotransform here.

    # JPL paths (make sure global 'eeflux' variable set to False and 'jpl' is set to True)
    data_locations_dir = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/get_data_output_jpl.yml'
    output_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results_jpl_03_28_19'
    geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'


    main(data_locations_dir, output_path, geo_info_path, jpl=True) #eeflux=True

    # # for testing
    # optimize_taw_disaggregate(rss=None, output_path=None, geo_info=None, big_arr=False, test_mode=True)