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
import yaml
import datetime
import numpy as np

# ============= local library imports ===========================
from utils.depletions_modeling.net_cdf_extract_to_tiff import write_raster

def pull_series(data_dict):

    observation_files = data_dict['obs']
    print 'observation files\n ', observation_files

    # get the dates when we have observations
    obs_dates = []
    for obs in observation_files:
        filename = obs.split('/')[-1]
        name = filename.split('.')[0]
        date_components = [int(i) for i in name.split('_')[-3:]]
        dt = datetime.date(year=date_components[2], month=date_components[1], day=date_components[0])
        obs_dates.append(dt)

    print 'the dates we observed \n{}'.format(obs_dates)
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


def get_obs_arr(obs, date):
    """"""

    for observation in obs:
        ending = '{}_{}_{}.npy'.format(date.day, date.month, date.year)
        if observation.endswith(ending):
            arr = np.load(observation)
            return arr

def get_model_arr(model_results, date):

    for result in model_results:
        ending = '{}_{}_{}.npy'.format(date.day, date.month, date.year)
        if result.endswith(ending):
            arr = np.load(result)
            return arr

def get_sse(data_dict, obs_dates, taw_vals):
    """"""

    obs = data_dict['obs']

    # a dictionary to store the residuals indexed by date and sorted by taw
    residual_dict = {}
    chi_dict = {}

    # # FOR TESTING
    # taw_vals = [225, 250]

    for taw in taw_vals:

        print 'taw', taw
        model_results = data_dict['{}'.format(taw)]

        residual_datelist = []
        for date in obs_dates:

            # for a given taw, we have the observed array and the model array here
            obs_arr = get_obs_arr(obs, date)
            model_arr = get_model_arr(model_results, date)

            residual_arr = obs_arr - model_arr

            # store the date and the residual array in a tuple and append to a list.
            store_residual = (date, residual_arr)
            residual_datelist.append(store_residual)

            # get chi (square error)
            chi = residual_arr ** 2
            store_chi = (date, chi)

        # get the date/value in dictionaries
        chi_dict['{}'.format(taw)] = residual_datelist
        residual_dict['{}'.format(taw)] = residual_datelist


    # need residual sum of squares (for each taw), degrees of freedom (number of obs of each taw +1), and taw values
    # taw_list = taw_vals
    rss_list = []
    dof_list = []
    for taw in taw_vals:
        n = 0
        # make a zeros array from the shape of the array in the second place of the first tuple of chi_dict.
        rss = np.zeros(chi_dict['{}'.format(taw)][0][1].shape)
        print 'len chi dict', len(chi_dict["{}".format(taw)])
        for tup in chi_dict['{}'.format(taw)]:
            rss += tup[1]
            n += 1

        # append the sum of each taw's squared errors to
        rss_list.append(rss)
        dof_list.append(n)

    residual_sum_squares_dict = {'taw': taw_vals, 'rss': rss_list, 'dof': dof_list}


    # print 'the rss \n', residual_sum_squares_dict

    return residual_sum_squares_dict, chi_dict, residual_dict

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

    print 'x coordinate array \n', x_coords
    print 'y coordinate array \n', y_coords


    # flatten each array
    flat_x_coords = x_coords.ravel()
    flat_y_coords = y_coords.ravel()
    # convert to list
    x_list = flat_x_coords.tolist()
    y_list = flat_y_coords.tolist()

    print 'about to open file'

    # open a csv file and save the header and lines
    with open('/Users/Gabe/Desktop/rss_array_output.csv', mode='w') as wfile:
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

def numpy_to_geotiff(array, geo_info, output_path):
    """"""

    trans = geo_info['geotransform']



    dim = geo_info['dimensions']
    proj = geo_info['projection']

    print'transform', trans
    print 'dimensions', dim
    print 'projections', proj

    write_raster(array, geotransform=trans, output_path=output_path, output_filename='optimized_taw.tif',
                 dimensions=dim, projection=proj)

def optimize_taw(rss, output_path, geo_info=None, big_arr=False):
    """"""

    print 'optimizing taw'
    # get taw, rss arrays, and degrees of freedom out.
    taw_vals = rss['taw']
    rss_arrs = rss['rss']
    dof_vals = rss['dof']

    # square root of the degrees of freedom
    nu = [(dof - 1) ** 0.5 for dof in dof_vals]
    # square root of the sum of squares
    norm = [rss ** 0.5 for rss in rss_arrs]

    # get the standard deviation from the residuals (I'm not sure what Juliet was using it for)
    s = [norm_val / nu_val for norm_val, nu_val in zip(norm, nu)]

    # before you optimize TAW, store the values in ways that are easy to visualize # todo - write these
    if not big_arr:
        print '\n outputting to csv since file is not so big \n'
        # output each pixel as a separate .csv
        csv_output(taw_vals, rss_arrs, outpath=output_path, geo_info=geo_info)
    # stack into a geo-referrenced net_cdf
    net_cdf_output(taw_vals, rss_arrs, geo_info, output_path)

    # for storing the minimum rss
    rss_tab = np.empty(rss_arrs[0].shape)
    # for storing the minimum taw
    taw_tab = np.empty(rss_arrs[0].shape)
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

    print 'taw tab at the end \n', taw_tab
    # save the optimized_taw as a numpy array and as a geotiff

    numpy_to_geotiff(taw_tab, geo_info, output_path)

    np.save(os.path.join(output_path, 'optimized_taw.npy'), taw_tab)


def main(data_dir, output_path, geo_info):
    """"""

    # open the data
    with open(data_dir, 'r') as yam:
        # load() returns a dict. load_all() returns a yaml object. Usefull if many subfiles are embedded.
        data_dict = yaml.load(yam)
    # pull
    obs_dates, taw_vals = pull_series(data_dict)

    # proceed by date and taw to read each image. Probably won't need chi and residuals but we get them in case we do.
    rss, chi, residuals = get_sse(data_dict, obs_dates, taw_vals)

    # pull out the geo info
    with open(geo_info, mode='r') as geofile:
        geo_dict = yaml.load(geofile)

    print 'testing the geo dict -> ', geo_dict


    # get the square root of the sum of squares
    optimize_taw(rss, output_path, geo_info=geo_dict, big_arr=False)


if __name__ == "__main__":

    # path to the .yml_file
    data_locations_dir = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/get_data_output.yml'
    output_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results'

    # for turning arrays into geotiffs
    geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info.yml'

    # todo - should be a place to get the geotransform here.

    main(data_locations_dir, output_path, geo_info_path)