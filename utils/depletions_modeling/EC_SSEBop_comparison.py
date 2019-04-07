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
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime as dt
from datetime import date

# ============= local library imports ===========================
from utils.pixel_time_series_extractor import run_point_extract, raster_extract, x_y_extract

def monthly_time_parse(timeseries):

    timeseries = pd.to_datetime(timeseries)

    mtime_list = []
    for i in timeseries:
        year = i.year
        month = i.month
        mtime = date(year, month, 1)
        mtime_list.append(mtime)

    # get rid of duplicates.
    mtime_set = set(mtime_list)
    print 'len mtime_set', len(mtime_set)
    print 'mtime set \n', mtime_set
    # change back to a list and sort
    mtime = sorted(list(mtime_set))
    print 'mtime sorted\n ', mtime

    return mtime

def plotter1(x, y, daily_average=False):
    """
    Plots parameters via a timeseries
    :param x:
    :param y:
    :param daily_average:
    :return:
    """

    if daily_average:
        # x = x.values
        y = y.values

        fig, ax = plt.subplots()

        ax.plot_date(x, y, fillstyle='none')

        ax.set_title('Closure Error for Daily Averaged EC')
        ax.set_ylabel('Percent Error')
        ax.set_xlabel('Time')
        plt.show()
    else:
        y = y.values
        fig, ax = plt.subplots()
        ax.plot_date(x, y, fillstyle='none')
        ax.set_title('Closure Error for 30 minute EC')
        ax.set_ylabel('Percent Error')
        ax.set_xlabel('Time')

        plt.show()

def closure_check(ec_dataset, Rn, LE, H, timeseries, daily_average=False):
    """"""
    if not daily_average:
        try:
            G = ec_dataset['FG']
        # TODO - If there is no ground heat flux, average over 24 hours to negate impact of G. Ask Dan the proper way.
        except KeyError:
            print 'No ground heat flux at this station. Consider averaging over a daily period.'
            G = 0
        try:
            stored_H = ec_dataset['SH']
            stored_LE = ec_dataset['SLE']
        except KeyError:
            print 'No sensible or latent heat storage terms'
            stored_H = 0
            stored_LE = 0

        # closure_error = abs((((Rn-G) - (LE + H)) - (stored_H + stored_LE))/Rn) * 100
        closure_error = (((LE + H) - (stored_H + stored_LE)) / (Rn - G)) * 100

        print 'median closure error: {}, average closure error {}'.format(
            np.median(closure_error.values), np.mean(closure_error.values))

        plotter1(timeseries, closure_error)

    else:
        print 'IGNORE G as we are averaging over a daily time period. We wont bother with stored H or stored LE either'
        # closure_error = abs(((Rn) - (LE + H)) / Rn) * 100
        # # after Sung-Ho's thesis Twine et al. 2000
        closure_error = ((LE + H)/Rn) * 100

        print 'median closure error: {}, average closure error {}'.format(
            np.median(closure_error.values), np.mean(closure_error.values))

        plotter1(timeseries, closure_error, daily_average=True)

def check_energybal(ec_dataset, timeseries=None, dailyaverage=False):
    """

    :param ec_dataset: the full dataset from the EC tower
    :param timeseries: a series of datetimes
    :return: a plot of the energy balance closure over time for the Eddy Covariance tower.
    """

    if not dailyaverage:
        Rn = ec_dataset['NETRAD']
        H = ec_dataset['H']
        LE = ec_dataset['LE']
        closure_check(ec_dataset, Rn, H, LE, timeseries)

    # ===== daily averaging =====

    if dailyaverage:
        timeseries = timeseries.values
        Rn = ec_dataset['NETRAD'].values
        H = ec_dataset['H'].values
        LE = ec_dataset['LE'].values
        # indexed_datetimes = pd.DataFrame(pd.DatetimeIndex(timeseries))

        # recreate a dataframe of the variables you want to time average on a dialy timestep
        halfhour_data = pd.DataFrame({'timeseries':timeseries, 'Rn': Rn, 'LE': LE, 'H': H})

        # resample the dataframe by making the timeseries column into the index and using .resample('d') for day
        halfhour_data = halfhour_data.set_index(pd.DatetimeIndex(halfhour_data['timeseries']))
        daily_time = halfhour_data.resample('d').mean()
        # Get the values of the datetime index as an array
        timeseries_daily = daily_time.index.values

        # Net Radiation
        Rn_av = daily_time['Rn']

        # Heat
        H_av = daily_time['H']
        LE_av = daily_time['LE']
        closure_check(ec_dataset, Rn_av, H_av, LE_av, timeseries_daily, daily_average=True)


def analyze(path, x, y):
    """

    :param path: path to a csv containing Ameriflux Dataset
    :param x: string corresponding to a dependent variable, usually a timeseries
    :param y: string corresponding to a dependent variable, usually a timeseries
    :return:
    """
    # Get the data from the path and turn the path into a data frame
    ec_dataset = pd.read_csv(path, header=2)

    # print ec_dataset.head()
    print ec_dataset['LE'].head()
    print ec_dataset[ec_dataset[y] != -9999].head()
    # get rid of no data values in any category of the energy balance
    ec_dataset = ec_dataset[ec_dataset[y] != -9999]
    ec_dataset = ec_dataset[ec_dataset['NETRAD'] != -9999]
    ec_dataset = ec_dataset[ec_dataset['H'] != -9999]
    ec_dataset = ec_dataset[ec_dataset['LE'] != -9999]
    # ec_dataset = ec_dataset[ec_dataset['SH'] != -9999]
    # ec_dataset = ec_dataset[ec_dataset['SLE'] != -9999]

    if x.startswith("TIMESTAMP"):
        a = ec_dataset[x].apply(lambda b: dt.strptime(str(b), '%Y%m%d%H%M'))
    else:
        a = ec_dataset[x]

    b = ec_dataset[y]

    unconverted_LE = ec_dataset[y]
    if y == 'LE':
        # convert latent heat flux into mm h20 by multiplying by the latent heat of vaporization todo - check calc w Dan
        mmh20 = b * 7.962e-4 # 4.09243e-7 <- instantaneous (mm/s)/m^2

    # ===== cumulative monthly =====
    timeseries = a.tolist()
    # print 'timeseries\n', timeseries
    Rn = ec_dataset['NETRAD'].values
    H = ec_dataset['H'].values
    LE = ec_dataset['LE'].values
    # indexed_datetimes = pd.DataFrame(pd.DatetimeIndex(timeseries))

    # recreate a dataframe of the variables you want to time average on a monthly timestep
    halfhour_data = pd.DataFrame({'timeseries': timeseries, 'Rn': Rn, 'LE': LE, 'H': H})

    # set the timeseries column to the index so groupby function can group by year and month of the index.
    halfhour_data = halfhour_data.set_index(pd.DatetimeIndex(halfhour_data['timeseries']))
    halfhour_data['mmh20'] = halfhour_data['LE'] * 7.962e-4

    # ===== Check closure Error ======

    check_energybal(ec_dataset, timeseries=a, dailyaverage=True)

    # check_energybal(ec_dataset, timeseries=a, dailyaverage=False)

    return halfhour_data

def order_satellite_obs(satellite_dict):
    """"""
    ordered_dict = {}
    for k, v in satellite_dict.iteritems():

        unordered_dates = v['date']
        unordered_values = v['value']

        ordered_dates = sorted(unordered_dates)

        ordered_vals = []
        for o_date in ordered_dates:

            for grab_date, grab_val in zip(unordered_dates, unordered_values):

                if o_date == grab_date:
                    ordered_vals.append(grab_val)

        ordered_dict[k] = {'date': ordered_dates, 'value': ordered_vals}


    return ordered_dict


def main(ec_path, sseb_directory, point_shape, ending):
    """Checking Eddy Covariance Data from Ameriflux EC towers and plotting it alongside SSEBop Data"""


    # define variables you want to analyze
    ind_var = 'TIMESTAMP_START'
    dep_var = 'LE'

    # TODO - energy balance closure is quite high. What can be done to fix this? Check Marcy Litvak's publications?
    # parse the ec data. check energy balance closure. Return the data for plotting.
    ec_data = analyze(ec_path, ind_var, dep_var)

    # === accumulate mmh20 to make comparable to SSEBop ===
    timeseries = ec_data.timeseries.tolist()
    monthly_cumulative = ec_data.groupby([lambda x: x.year, lambda x: x.month]).sum()
    # the time series that matches the monthly cumulative dataframe
    monthly_list = monthly_time_parse(timeseries)

    # # try plotting
    # plt.plot(monthly_list, monthly_cumulative.mmh20)
    # plt.scatter(monthly_list, monthly_cumulative.mmh20)
    # plt.show()

    # extract the SSEBop data from the rasters
    sseb_dict = run_point_extract(point_path=point_shape, raster_path=sseb_directory, ending=ending, sseb=True)

    print 'sseb dictionary \n', sseb_dict

    ordered_sseb_dict = order_satellite_obs(sseb_dict)

    fig, ax = plt.subplots()
    ax.plot(monthly_list, monthly_cumulative.mmh20)
    ax.scatter(monthly_list, monthly_cumulative.mmh20)
    ax.plot(ordered_sseb_dict['0']['date'], ordered_sseb_dict['0']['value'], color='red')
    ax.set_title('Comparison of Monthly total ET from SSEB (red) vs EC Flux Tower (Wjs-blue)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Monthly Cumulative ET in mm')
    plt.show()

    # todo - now plot a new pixel time series to compare to the pixel that contains the EC tower



if __name__ == "__main__":

    # get the location of the file containing the EC dataset
    # #Walnut Gulch Kendal Grasslands
    # ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Wkg_BASE-BADM_11-5/AMF_US-Wkg_BASE_HH_11-5.csv'
    # # Sevilleta Grass
    # ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Seg_BASE-BADM_8-5/AMF_US-Seg_BASE_HH_8-5.csv'

    # Valles Caldera Mixed
    # ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Vcm_BASE-BADM_9-5/AMF_US-Vcm_BASE_HH_9-5.csv'
    # ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Vcp_BASE-BADM_6-5/AMF_US-Vcp_BASE_HH_6-5.csv'
    # ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Vcs_BASE-BADM_3-5/AMF_US-Vcs_BASE_HH_3-5.csv'
    # ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Seg_BASE-BADM_8-5/AMF_US-Seg_BASE_HH_8-5.csv'
    # ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Mpj_BASE-BADM_8-5/AMF_US-Mpj_BASE_HH_8-5.csv'
    ec_path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Wjs_BASE-BADM_7-5/AMF_US-Wjs_BASE_HH_7-5.csv'

    # SSEB directory
    sseb_dir = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/SSEBop/SSEBOP_Geotiff'
    # ssebn_dir = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/SSEBop/'

    # SSEB shape dir
    vcm_shape = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/SSEBop/vcm_point_shape/vcm_point.shp'

    # SSEB raster files end with this extension
    ending = '.tif'

    main(ec_path, sseb_dir, point_shape=vcm_shape, ending=ending)