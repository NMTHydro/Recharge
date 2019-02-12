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

        # TODO get rid of this if statement to calibrate to dates not in the growing season...
        if resid_date > datetime.date(resid_date.year, 4, 1) and resid_date < datetime.date(resid_date.year, 10, 31):

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

    # # FOR TESTING (Wait... what does this test?!?!?)
    # taw_vals = [225, 250]
    # ==== MEMORY INTENSIVE  (we avoid serious memory leaks by writing to files...)====
    new_obs_dates = []
    for taw in taw_vals[0:1]:

        print 'taw', taw
        model_results = data_dict['{}'.format(taw)]

        # we store tuples of dates and residuals in this
        residual_datelist = []
        # store tuples of dates and squared residuals here
        squared_residual_datelist = []

        read_list = []

        for i, date in enumerate(obs_dates):

            # for a given taw, we have the observed array and the model array here
            if read_eeflux_tiff:
                obs_arr = get_obs_arr(obs, date)
            elif read_numpy:
                obs_arr = get_obs_arr_eeflux(obs, date)

            elif read_jpl_tiff:
                obs_arr = get_obs_arr_jpl(obs, date)

            if np.isnan(obs_arr).all():
                print 'WARNING \n {} \n obs arr is nan for {}'.format(obs_arr, date)

            # get the ETRM modeled array that matches the observation.
            model_arr = get_model_arr(model_results, date)

            if np.isnan(model_arr).all():
                print 'WARNING \n {} \n model arr is nan for {}'.format(model_arr, date)

            # the residuals are the observed values - modeled values
            residual_arr = obs_arr - model_arr

            if np.isnan(residual_arr).all():
                print 'WARNING \n {} \n residual arr is nan for {}'.format(residual_arr, date)

            # # store the date and the residual array in a tuple and append to a list.
            # store_residual = (date, residual_arr)
            # residual_datelist.append(store_residual)

            # get chi (square error)
            chi = residual_arr ** 2
            # store_chi = (date, chi)

            # TODO - Make a NEW array to keep track of the good values from each pixel to modify the Chi SQ where NANs occur.
            # TODO - For NAN pixels, filter them and set them to zero. Track zeros for appropriate quantification of 95% confidence.

            if np.isnan(chi).all():
                print 'WARNING \n {} \n chi arr is nan for {}'.format(chi, date)

            if not np.isnan(chi).all():

                # get new observation dates
                new_obs_dates.append(date)

                temp_name = '{}_{}_{}_{}.npy'.format(taw, date.year, date.month, date.day)

                read_list.append('/Users/dcadol/Desktop/desktop_taw_optimization_temp/{}'.format(temp_name))

                np.save('/Users/dcadol/Desktop/desktop_taw_optimization_temp/{}'.format(temp_name), chi)


        chi_dict['{}'.format(taw)] = read_list


    # need residual sum of squares (for each taw), degrees of freedom (number of obs of each taw +1), and taw values
    # taw_list = taw_vals
    rss_list = []
    dof_list = []
    test_list = []
    for taw in taw_vals[0:1]:
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

            # # TODO - Make an animation of the RSS accumulating for every TAW image. MIGHT be pretty cool.
            # plt.imshow(rss)
            # plt.show()

            # degrees of freedom accumulate
            n += 1

        # # append the sum of each taw's squared errors to
        print 'final rss for taw {}'.format(taw)
        print 'rss', rss
        plt.imshow(rss)
        plt.show()
        # print 'new final rss for taw {}'.format(taw)
        # # rss = np.load('/Users/dcadol/Desktop/desktop_taw_optimization_temp/rss_temp{}.npy'.format(
        # #     len(chi_dict['{}'.format(taw)])-1))
        # plt.imshow(rss)
        # plt.show()
        rss_list.append(rss)
        dof_list.append(n)

    # ===============``````````````````````===================
    # for rss, test in zip(rss_list, test_list):
    #     print 'this is the rss loop', rss
    #     print test
    #     plt.imshow(rss)
    #     plt.show()
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


def net_cdf_output(taw_vals, rss_arrs, geo_info, outpath):
    """"""
    pass

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

    # stack into a geo-referrenced net_cdf TODO - Write this function (currently will 'pass')
    net_cdf_output(taw_vals, rss_arrs, geo_info, output_path)

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
    output_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results_jpl'
    geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'


    main(data_locations_dir, output_path, geo_info_path, jpl=True) #eeflux=True