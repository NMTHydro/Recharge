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
import pandas as pd
from datetime import datetime as dt
from datetime import date
import yaml
import numpy as np
from matplotlib import pyplot as plt

# ============= standard library imports ========================
from utils.TAW_optimization_subroutine.non_normalized_hist_analysis import geospatial_array_extract
from utils.TAW_optimization_subroutine.chisquare_timeseries_analyst import x_y_extract, raster_extract


"""This script will plot EC, PRISM, JPL and ETRM data for a point for a time series."""

def get_jpl_results(jpl_path):
    """

    :param jpl_path:
    :return:
    """

    all_data_dict = {}

    for path, dirs, files in os.walk(jpl_path, topdown=False):
        # print 'path', path
        # print 'dirs', dirs
        # print 'files', files

        them_dates = []
        them_files = []
        for f in files:
            if f.endswith('.tif'):
                flist = f.split('.')

                # print flist

                if len(flist[0])>0:
                    yr = int(flist[0])
                    mnth = int(flist[1])
                    dy = int(flist[2])

                f_date = date(yr, mnth, dy)
                them_dates.append(f_date)

                f_path = os.path.join(path, f)
                them_files.append(f_path)

        sorted_files = [f for _, f in sorted(zip(them_dates, them_files))]
        sorted_dates = sorted(them_dates)

        all_data_dict['dates'] = sorted_dates
        all_data_dict['etas'] = sorted_files

    return all_data_dict


def get_prism_results(prism_path):
    """

    :param prism_path:
    :return:
    """

    all_data_dict = {}
    for path, dirs, files in os.walk(prism_path, topdown=False):
        # print 'path', path
        # print 'dirs', dirs
        # print 'files', files

        them_dates = []
        them_files = []
        for f in files:

            # format ex 'precip_20000101.tif'
            fname = f.split('.')[0]
            f_time = fname.split('_')[-1]

            # print f_time
            f_datetime = dt.strptime(f_time, '%Y%m%d')

            f_date = date(f_datetime.year, f_datetime.month, f_datetime.day)
            them_dates.append(f_date)

            f_path = os.path.join(path, f)
            them_files.append(f_path)

        sorted_files = [f for _, f in sorted(zip(them_dates, them_files))]
        sorted_dates = sorted(them_dates)

        all_data_dict['dates'] = sorted_dates
        all_data_dict['precips'] = sorted_files

    return all_data_dict


def get_monthly_etrm_outputs(output_path, output_type):
    """
    For getting the paths and time series for monthly data outputs from ETRM
    :param output_path:
    :param output_type:
    :return:
    """
    all_data_dict = {}

    # for path, dirs, files in os.walk(output_path, topdown=False):
    #     if path.endswith('numpy_arrays') and len(files) > 0:
    #         # print 'path', path
    #         # print 'dirs', dirs
    #         # print 'files', files
    #
    #         example_file = files[0]
    #
    #         taw = example_file.split('_')[4]
    #         print 'ex taw: ', taw

    for path, dirs, files in os.walk(output_path, topdown=False):
        if path.endswith('monthly_rasters') and len(files) > 0:

            print 'path', path

            # get the TAW value from the numpy arrays
            results_path = os.path.split(path)[0]
            numpy_path = os.path.join(results_path, 'numpy_arrays')
            example_file = os.listdir(numpy_path)[0]
            print example_file
            taw = example_file.split('_')[4]
            print 'ex taw: ', taw

            print 'the taw of the monthly {}'.format(taw)

            # if output_type == 'eta':

            # NOW, get the files and timeseries for the monthlies from monthly_rasters
            timeseries = []
            fileseries = []

            for f in files:
                fname = f.split('.')[0]
                flist = fname.split('_')

                # to get the kind of monthly output you want i.e 'eta', or 'rzsm'
                if flist[0] == output_type:

                    yr = int(flist[-2])
                    mnth = int(flist[-1])
                    # set day to the first of the month automatically for monthly datasets so they can be put together with
                    #  daily timeseries
                    dy = 1


                    first_of_the_month = date(yr, mnth, dy)

                    first_of_next = first_of_the_month + relativedelta(months=+1)

                    last_of_month = first_of_next - timedelta(days=1)


                    timeseries.append(last_of_month)

                    filepath = os.path.join(path, f)
                    fileseries.append(filepath)

            # do a nifty sort of file paths based on the dates
            sorted_files = [f for _, f in sorted(zip(timeseries, fileseries))]

            sorted_dates = sorted(timeseries)
            print 'len sorted files {}, len sorted dates {}, taw {}'.format(len(sorted_files), len(sorted_dates), taw)

            all_data_dict[taw] = (sorted_files, sorted_dates)

    return all_data_dict


# etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results_ceff_06'
# etrm_taw = '425'
#
# geo_info_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder/geo_info_ameriflux.yml'
# with open(geo_info_path, mode='r') as geofile:
#     geo_dict = yaml.load(geofile)
#
# shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mpj_point_extract.shp'
#
# # get the x and y from the shapefile in order to extract
# # ... from rasters raster_extract() and geospatial arrays geospatial_array_extract()
# feature_dictionary = x_y_extract(shape_path)
# # Use the feature dictionary to extract data from the rasters.
# for feature, tup in feature_dictionary.iteritems():
#     # Get the X and Y coords from the dictionary and unpack them
#     x, y = tup
#     print x, y
#
#
# monthly_etrm_outputs = get_monthly_etrm_outputs(etrm_path, output_type='eta')

# print 'outputs \n', monthly_etrm_outputs[etrm_taw]

def get_etrm_results(etrm_results_path, rzsm=False, observation_dates=None):
    """

    :param etrm_results_path:
    :param rzsm:
    :param observation_dates:
    :return:
    """

    all_data_dict = {}

    for path, dirs, files in os.walk(etrm_results_path, topdown=False):

        if path.endswith('numpy_arrays') and len(files) > 0:
            # print 'path', path
            # print 'dirs', dirs
            # print 'files', files

            example_file = files[0]

            taw = example_file.split('_')[4]
            print 'ex taw: ', taw

            them_dates = []
            them_files = []

            # collect date objects for each file. Then use the dates to order the files - then tack on the path
            for f in files:

                fname = f.split('.')[0]
                flist = fname.split('_')

                yr = int(flist[-3])
                mnth = int(flist[-2])
                dy = int(flist[-1])

                if rzsm:

                    if flist[2] == 'rzsm':

                        if observation_dates != None:
                            file_date = date(yr, mnth, dy)
                            if file_date in observation_dates:
                                them_dates.append(file_date)
                                f_path = os.path.join(path, f)
                                them_files.append(f_path)

                        else:
                            file_date = date(yr, mnth, dy)
                            them_dates.append(file_date)
                            f_path = os.path.join(path, f)
                            them_files.append(f_path)


                else:

                    if flist[2] == 'eta':

                        if observation_dates != None:
                            file_date = date(yr, mnth, dy)


                            if file_date in observation_dates:
                                them_dates.append(file_date)
                                f_path = os.path.join(path, f)
                                them_files.append(f_path)

                        else:
                            file_date = date(yr, mnth, dy)
                            them_dates.append(file_date)

                            f_path = os.path.join(path, f)
                            them_files.append(f_path)

            # do a nifty sort of file paths based on the dates
            sorted_files = [f for _, f in sorted(zip(them_dates, them_files))]

            sorted_dates = sorted(them_dates)
            print 'len sorted files {}, len sorted dates {}'.format(len(sorted_files), len(sorted_dates))

            all_data_dict[taw] = (sorted_files, sorted_dates)

    return all_data_dict


def daily_time_parse(timeseries):

    timeseries = pd.to_datetime(timeseries)

    daily_time_list = []
    for i in timeseries:
        year = i.year
        month = i.month
        day = i.day
        daily_time = date(year, month, day)
        daily_time_list.append(daily_time)

    # get rid of duplicates.
    daily_time_set = set(daily_time_list)
    print 'len mtime_set', len(daily_time_set)
    print 'mtime set \n', daily_time_set
    # change back to a list and sort
    daily_time = sorted(list(daily_time_set))
    print 'mtime sorted\n ', daily_time

    return daily_time

# old version of ec_data_processor
# def ec_data_processor(path, x='TIMESTAMP_START', y='LE', daily=True, cumulative_days=None):
#     """
#
#     :param path: path to a csv containing Ameriflux Dataset
#     :param x: default is the header string for the timestamps
#     :param y: default is Latent Heat LE
#     :param daily: if true, we convert the Eddy Covariance to a daily total
#     :param cumulative_days: an interger number of days to be accumulated based on the daily total
#     :return: a timeseries of
#     """
#     # Get the data from the path and turn the path into a data frame
#     # ec_dataset = pd.read_csv(path, header=2)
#     ec_dataset = pd.read_csv(path, header=2, engine='python')
#
#     # print ec_dataset.head()
#     print ec_dataset['LE'].head()
#     print ec_dataset[ec_dataset[y] != -9999].head()
#     # === get rid of no data values in any category of the energy balance ===
#     ec_dataset = ec_dataset[ec_dataset[y] != -9999]
#     ec_dataset = ec_dataset[ec_dataset['NETRAD'] != -9999]
#     ec_dataset = ec_dataset[ec_dataset['H'] != -9999]
#     ec_dataset = ec_dataset[ec_dataset['LE'] != -9999]
#     # ec_dataset = ec_dataset[ec_dataset['P'] != -9999]
#     # # You probably won't need these because Marcy Doesn't think they are valid for her towers
#     # ec_dataset = ec_dataset[ec_dataset['SH'] != -9999]
#     # ec_dataset = ec_dataset[ec_dataset['SLE'] != -9999]
#
#     if x.startswith("TIMESTAMP"):
#         a = ec_dataset[x].apply(lambda b: dt.strptime(str(b), '%Y%m%d%H%M'))
#     else:
#         a = ec_dataset[x]
#
#     # ===== Time Series Processing =====
#
#     timeseries = a.tolist()
#     # print 'timeseries\n', timeseries
#     Rn = ec_dataset['NETRAD'].values
#     H = ec_dataset['H'].values
#     LE = ec_dataset['LE'].values
#     # P = ec_dataset['P']
#     # indexed_datetimes = pd.DataFrame(pd.DatetimeIndex(timeseries))
#
#     # recreate a dataframe of the variables you want to time average on a monthly timestep
#     halfhour_data = pd.DataFrame({'timeseries': timeseries, 'Rn': Rn, 'LE': LE, 'H': H}) # took out precip. no good vals? 'P': P
#
#     # set the timeseries column to the index so groupby function can group by year and month of the index.
#     halfhour_data = halfhour_data.set_index(pd.DatetimeIndex(halfhour_data['timeseries']))
#     halfhour_data['mmh20'] = halfhour_data['LE'] * 7.962e-4
#
#     # # ===== Check closure Error ======
#     #
#     # check_energybal(ec_dataset, timeseries=a, dailyaverage=True)
#     #
#     # # check_energybal(ec_dataset, timeseries=a, dailyaverage=False)
#
#     if daily:
#         # # === an example of # === accumulate mmh20 to make comparable to SSEBop ===
#         #     timeseries = ec_data.timeseries.tolist()
#         #     monthly_cumulative = ec_data.groupby([lambda x: x.year, lambda x: x.month]).sum()
#         #     # the time series that matches the monthly cumulative dataframe
#         #     monthly_list = monthly_time_parse(timeseries)arse(timeseries)
#         daily_cum_data = halfhour_data.groupby([lambda x: x.year, lambda x: x.month, lambda x: x.day]).sum()
#
#         daily_cum_time = daily_time_parse(timeseries)
#
#         # # testing
#         # daily_cum_data.to_csv('/Users/dcadol/Desktop/daily_cumulative_df.csv')
#
#         # format daily_cum_data to have datetimes
#         daily_cum_data['date'] = daily_cum_time
#
#         # # testing
#         # daily_cum_data.to_csv('/Users/dcadol/Desktop/daily_cumulative_df.csv')
#
#         return daily_cum_data
#
#     else:
#         return halfhour_data

# new version of ec_data_processor
def ec_data_processor(path, x='TIMESTAMP_START', y='LE', daily=True):
    """

    :param path: path to a csv containing Ameriflux Dataset
    :param x: default is the header string for the timestamps
    :param y: default is Latent Heat LE
    :param daily: if true, we convert the Eddy Covariance to a daily total
    :param cumulative_days: an interger number of days to be accumulated based on the daily total
    :return: a timeseries of
    """
    # old version of ec_data_processor
    # def ec_data_processor(path, x='TIMESTAMP_START', y='LE', daily=True, cumulative_days=None):
    #     """
    #
    #     :param path: path to a csv containing Ameriflux Dataset
    #     :param x: default is the header string for the timestamps
    #     :param y: default is Latent Heat LE
    #     :param daily: if true, we convert the Eddy Covariance to a daily total
    #     :param cumulative_days: an interger number of days to be accumulated based on the daily total
    #     :return: a timeseries of
    #     """
    #     # Get the data from the path and turn the path into a data frame
    #     # ec_dataset = pd.read_csv(path, header=2)
    #     ec_dataset = pd.read_csv(path, header=2, engine='python')
    #
    #     # print ec_dataset.head()
    #     print ec_dataset['LE'].head()
    #     print ec_dataset[ec_dataset[y] != -9999].head()
    #     # === get rid of no data values in any category of the energy balance ===
    #     ec_dataset = ec_dataset[ec_dataset[y] != -9999]
    #     ec_dataset = ec_dataset[ec_dataset['NETRAD'] != -9999]
    #     ec_dataset = ec_dataset[ec_dataset['H'] != -9999]
    #     ec_dataset = ec_dataset[ec_dataset['LE'] != -9999]
    #     # ec_dataset = ec_dataset[ec_dataset['P'] != -9999]
    #     # # You probably won't need these because Marcy Doesn't think they are valid for her towers
    #     # ec_dataset = ec_dataset[ec_dataset['SH'] != -9999]
    #     # ec_dataset = ec_dataset[ec_dataset['SLE'] != -9999]
    #
    #     if x.startswith("TIMESTAMP"):
    #         a = ec_dataset[x].apply(lambda b: dt.strptime(str(b), '%Y%m%d%H%M'))
    #     else:
    #         a = ec_dataset[x]
    #
    #     # ===== Time Series Processing =====
    #
    #     timeseries = a.tolist()
    #     # print 'timeseries\n', timeseries
    #     Rn = ec_dataset['NETRAD'].values
    #     H = ec_dataset['H'].values
    #     LE = ec_dataset['LE'].values
    #     # P = ec_dataset['P']
    #     # indexed_datetimes = pd.DataFrame(pd.DatetimeIndex(timeseries))
    #
    #     # recreate a dataframe of the variables you want to time average on a monthly timestep
    #     halfhour_data = pd.DataFrame({'timeseries': timeseries, 'Rn': Rn, 'LE': LE, 'H': H}) # took out precip. no good vals? 'P': P
    #
    #     # set the timeseries column to the index so groupby function can group by year and month of the index.
    #     halfhour_data = halfhour_data.set_index(pd.DatetimeIndex(halfhour_data['timeseries']))
    #     halfhour_data['mmh20'] = halfhour_data['LE'] * 7.962e-4
    #
    #     # # ===== Check closure Error ======
    #     #
    #     # check_energybal(ec_dataset, timeseries=a, dailyaverage=True)
    #     #
    #     # # check_energybal(ec_dataset, timeseries=a, dailyaverage=False)
    #
    #     if daily:
    #         # # === an example of # === accumulate mmh20 to make comparable to SSEBop ===
    #         #     timeseries = ec_data.timeseries.tolist()
    #         #     monthly_cumulative = ec_data.groupby([lambda x: x.year, lambda x: x.month]).sum()
    #         #     # the time series that matches the monthly cumulative dataframe
    #         #     monthly_list = monthly_time_parse(timeseries)arse(timeseries)
    #         daily_cum_data = halfhour_data.groupby([lambda x: x.year, lambda x: x.month, lambda x: x.day]).sum()
    #
    #         daily_cum_time = daily_time_parse(timeseries)
    #
    #         # # testing
    #         # daily_cum_data.to_csv('/Users/dcadol/Desktop/daily_cumulative_df.csv')
    #
    #         # format daily_cum_data to have datetimes
    #         daily_cum_data['date'] = daily_cum_time
    #
    #         # # testing
    #         # daily_cum_data.to_csv('/Users/dcadol/Desktop/daily_cumulative_df.csv')
    #
    #         return daily_cum_data
    #
    #     else:
    #         return halfhour_data




    # Get the data from the path and turn the path into a data frame
    # ec_dataset = pd.read_csv(path, header=2)

    ec_dataset = pd.read_csv(path, header=2, engine='python')

    # print ec_dataset.head()
    print ec_dataset['LE'].head()
    print ec_dataset[ec_dataset[y] != -9999].head()
    # === get rid of no data values in any category of the energy balance ===
    ec_dataset = ec_dataset[ec_dataset[y] != -9999]
    ec_dataset = ec_dataset[ec_dataset['NETRAD'] != -9999]
    ec_dataset = ec_dataset[ec_dataset['H'] != -9999]
    ec_dataset = ec_dataset[ec_dataset['LE'] != -9999]
    # ec_dataset = ec_dataset[ec_dataset['P'] != -9999]
    # # You probably won't need these because Marcy Doesn't think they are valid for her towers
    # ec_dataset = ec_dataset[ec_dataset['SH'] != -9999]
    # ec_dataset = ec_dataset[ec_dataset['SLE'] != -9999]

    if x.startswith("TIMESTAMP"):
        a = ec_dataset[x].apply(lambda b: dt.strptime(str(b), '%Y%m%d%H%M'))
    else:
        a = ec_dataset[x]

    # ===== Time Series Processing =====

    timeseries = a.tolist()
    # print 'timeseries\n', timeseries
    Rn = ec_dataset['NETRAD'].values
    H = ec_dataset['H'].values
    LE = ec_dataset['LE'].values
    # P = ec_dataset['P']
    # indexed_datetimes = pd.DataFrame(pd.DatetimeIndex(timeseries))

    # recreate a dataframe of the variables you want to time average on a monthly timestep
    halfhour_data = pd.DataFrame({'timeseries': timeseries, 'Rn': Rn, 'LE': LE, 'H': H}) # took out precip. no good vals? 'P': P

    # set the timeseries column to the index so groupby function can group by year and month of the index.
    halfhour_data = halfhour_data.set_index(pd.DatetimeIndex(halfhour_data['timeseries']))
    # convert latent heat to mmH2O by multiplying by latent heat of vaporization.
    halfhour_data['mmh20'] = halfhour_data['LE'] * 7.962e-4

    if daily:

        # # === an example of # === accumulate mmh20 to make comparable to SSEBop ===
        #     timeseries = ec_data.timeseries.tolist()
        #     monthly_cumulative = ec_data.groupby([lambda x: x.year, lambda x: x.month]).sum()
        #     # the time series that matches the monthly cumulative dataframe
        #     monthly_list = monthly_time_parse(timeseries)arse(timeseries)

        daily_cum_data = halfhour_data.groupby([lambda x: x.year, lambda x: x.month, lambda x: x.day]).sum()

        # get each day in the timeseries. there are duplicates from the groupby function, so use set() to get rid of
        #  duplicates
        daily_cum_time = daily_time_parse(timeseries)

        # # testing
        # daily_cum_data.to_csv('/Users/dcadol/Desktop/daily_cumulative_df.csv')

        # format daily_cum_data to have datetimes
        daily_cum_data['date'] = daily_cum_time

        # # testing
        # daily_cum_data.to_csv('/Users/dcadol/Desktop/daily_cumulative_df.csv')


        return daily_cum_data

    else:
        return halfhour_data


def dataset_plot(shape_path, ameriflux_df, raster_datasets, geo_info, taw, sitename=None):
    """

    :param shape_path: path to a shapefile where the values will be read from
    :param ameriflux_df: ameriflux tower corresponding to the shapefile or nearby to the shapefile ideally
    :param raster_datasets: a dictionary of the raster datasets containing date objects and filepaths for timeseries
    :param geo_info: dictionary containing info for georefferencing .npy files
    :return:
    """

    # get the x and y from the shapefile in order to extract
    # ... from rasters raster_extract() and geospatial arrays geospatial_array_extract()
    feature_dictionary = x_y_extract(shape_path)

    print "feature dictionary", feature_dictionary

    # Use the feature dictionary to extract data from the rasters.
    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

    # ====== Unpack the different raster datasets

    etrm_dict = raster_datasets['etrm']
    jpl_dict = raster_datasets['jpl']
    prism_dict = raster_datasets['prism']

    print 'processing ETRM'
    # ====== select etrm dataset based on TAW =======
    etrm_eta_tup = etrm_dict[taw]

    etrm_eta = etrm_eta_tup[0]
    etrm_dates = etrm_eta_tup[1]

    # GET THE ETRM VALUES from the numpy array
    etrm_values = []
    for etrm_rast in etrm_eta:
        etrm_arr = np.load(etrm_rast)
        etrm_val = geospatial_array_extract(geo_dict, etrm_arr, (x, y))
        etrm_values.append(etrm_val)


    print 'processing jpl'
    # ====== select jpl from dict =====
    jpl_eta = jpl_dict['etas']
    jpl_dates = jpl_dict['dates']

    # GET the JPL VALUES from the .tif
    jpl_values = []
    for jpl_rast in jpl_eta:
        if jpl_rast.endswith('.tif'):
            jpl_val = raster_extract(jpl_rast, x, y)
            jpl_values.append(jpl_val)


    print 'processing prism'
    # ====== select precip from prism ====
    prism_precip = prism_dict['precips']
    prism_dates = prism_dict['dates']

    # GET the PRISM VALUES from the .tif
    prism_values = []
    for prism_rast in prism_precip:
        prism_val = raster_extract(prism_rast, x, y)
        prism_values.append(prism_val)


    # ====== GET the timeseries from the AMERIFLUX DATAFRAME ========
    ameriflux_values = ameriflux_df.mmh20
    ###ameriflux_precip_values = ameriflux_df.P
    ameriflux_dates = ameriflux_df.date

    print 'plotting'
    fig, ax = plt.subplots()

    ax.plot(ameriflux_dates, ameriflux_values, color='green')
    ax.plot_date(ameriflux_dates, ameriflux_values, fillstyle='none', color='green')

    ax.plot(prism_dates, prism_values, color='blue')
    ax.plot_date(prism_dates, prism_values, fillstyle='none', color='blue')

    ax.plot(jpl_dates, jpl_values, color='red')
    ax.plot_date(jpl_dates, jpl_values, fillstyle='none', color='red')

    ax.plot(etrm_dates, etrm_values, color='black')
    ax.plot_date(etrm_dates, etrm_values, fillstyle='none', color='black')

    ax.set_title('Comprehensive ETa and Precip Site:{} TAW:{}'.format(sitename, taw))
    ax.set_ylabel('ETa or Precip in mm H20')
    ax.set_xlabel('Date')
    plt.grid(True)

    plt.show()

    # todo - removed the precip values. appear to be dysfunctional.
    # ax.plot(ameriflux_dates, ameriflux_precip_values, color='purple')
    # ax.plot_date(ameriflux_dates, ameriflux_precip_values, fillstyle='none', color='purple')


if __name__ == '__main__':

    # intput parameters

    # ===== Point Info - UTM Shapefile) =====

    # shapefile
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Vcp_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Ss_point_extract.shp'
    # shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Mjs_point_extract.shp'
    shape_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/Sg_point_extract.shp'


    # ===== Precip Time Series =====

    # PRISM - format = 'precip_YYYYjjj.tif' where jjj is three digit day of year
    prism_path = '/Volumes/Seagate_Blue/ameriflux_aoi/PRISM/precip/800m_std_all'

    # dict with keys 'dates' for date objs and 'precips' for filepaths
    prism_dict = get_prism_results(prism_path)


    # TODO - ADD in a RefET time series here
    # ===== GADGET RefET Time Series =====

    # TODO - ADD in FluxTower daily RefET timeseries here
    # ===== FluxTower daily PM RefET ======


    # ===== Observational ETa Time Series =====

    # JPL - format = 'YYYY.mm.dd.PTJPL.ET_daily_kg.MODISsin1km_etrm.tif' [using full ETRM dataset so you can plot
    # against Ameriflux that is outside of Study area]
    jpl_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'

    # dict with keys 'dates' for date objs and 'etas' for filepaths
    jpl_data_dict = get_jpl_results(jpl_path)


    # Ameriflux
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcm_BASE_HH_9-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Mpj_BASE_HH_8-5.csv'
    ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Seg_BASE_HH_10-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Ses_BASE_HH_8-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Vcp_BASE_HH_6-5.csv'
    # ameriflux_path = '/Users/dcadol/Desktop/academic_docs_II/Ameriflux_data/AMF_US-Wjs_BASE_HH_7-5.csv'

    # get a dataframe of daily cumulative ETa values in mm/day for the ameriflux path
    daily_cum_ameriflux = ec_data_processor(ameriflux_path)

    # ETRM - get it from the original output files
    # etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results'
    etrm_path = '/Volumes/Seagate_Blue/ameriflux_aoi_etrm_results_ceff_06'

    # returns a dictionary where key = 'taw'. Key returns a tuple (date_objs, files) in chronological order.
    etrm_dict = get_etrm_results(etrm_path)

    # get geo-info path to handle importing numpy files
    # geo_info_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info_espanola.yml'
    geo_info_path = '/Volumes/Seagate_Blue/taw_optimization_work_folder/geo_info_ameriflux.yml'
    with open(geo_info_path, mode='r') as geofile:
        geo_dict = yaml.load(geofile)

    raster_datasets = {'prism': prism_dict, 'jpl': jpl_data_dict, 'etrm': etrm_dict}



    dataset_plot(shape_path, ameriflux_df=daily_cum_ameriflux, raster_datasets=raster_datasets, geo_info=geo_dict, taw='225', sitename='Seg')





