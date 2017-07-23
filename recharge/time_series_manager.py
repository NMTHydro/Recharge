# ===============================================================================
# Copyright 2016 dgketchum
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
from datetime import datetime, timedelta

from numpy import array, nan, loadtxt, append, zeros
from pandas import DataFrame, notnull, to_numeric, concat

from app.paths import paths


def load_df(path):
    """
    :param path: path to csv file

    :returns dataframe of etrm time series input
    """
    print 'reading in csv: {}'.format(path)
    csv = loadtxt(path, dtype=str, delimiter=',')

    # extracts should have headers
    csv = csv[1:]

    try:
        new_ind = [datetime.strptime(row[0], '%Y-%m-%d') for row in csv]
    except ValueError:
        new_ind = [datetime.strptime(row[0], '%Y/%m/%d') for row in csv[1:]]

    arr = array(csv[:, 1:], dtype=float)

    cols = ['kcb', 'rg', 'etrs', 'min_temp', 'max_temp', 'temp', 'precip']

    df = DataFrame(arr, index=new_ind, columns=cols)

    return df


def get_etrm_time_series(input_root, dict_):
    """
    Read pre-extracted data out of a formatted csv.  Use recharge.point_extract_utility.py to do extract.

    :param input_root: path to a folder of csv files.
    :param dict_: dict of point locations

    csv will be in the following format
    ['kcb', 'rg', 'etrs', 'min_temp', 'max_temp', 'temp', 'precip']
    """

    csv_list = [filename for filename in os.listdir(input_root) if filename.endswith('.csv')]

    print 'etrm extract csv list: {}'.format(csv_list)
    for path in csv_list:
        name = os.path.splitext(path)[0]
        df = load_df(os.path.join(input_root, path))

        if dict_:
            for key, val in dict_.iteritems():
                if val['Name'] == name:
                    print 'updating {} number {} with etrm inputs df'.format(name, key)
                    # print 'your df: \n{}'.format(df)
                    dict_[key]['etrm'] = df


def amf_obs_time_series(dict_, save_cleaned_data_path=False, complete_days_only=False,
                        close_threshold=0.20, return_low_err=False):
    """ Analyze, clean and return dict of AmeriFlux sites and relevant data.

    :param dict_: dict object of Ameriflux IDs as keys, nested dict with 'Name', 'Coords' etc
    :param path: string path to AmeriFlux folder containing AmeriFlux csv files
    :param return_low_err: retun dataframe of only low energy balance closure error
    :param close_threshold: threshold of error tolerated
    :param complete_days_only: return only full days of valid data
    :param save_cleaned_data_path: path to save location of output


    #  (year, dtime, H, LE, FG, RN, RG, RGin, RGout)
    # H  = sensible heat flux
    # LE = latent heat flux
    # FG = soil heat flux
    # RN = net radiation
    # RG = incoming shortwave
    # RGout = outgoing shortwave
    # RGL  = incoming longwave
    # RGLout = outgoing longwave
    """
    path = paths.amf_sites
    print path

    def day_fraction_to_hr_min(fractional_day, year):
        """

        :param fractional_day:  100.134
        :param year:
        :return:
        """

        def ext(d, scalar):
            d = str(d)
            a, b = d.split('.')
            aa, bb = int(a), float('.{}'.format(b))
            return aa, bb * scalar

        dec = str(fractional_day)
        day, timepart = ext(dec, 24)
        hour, minpart = ext(timepart, 60)
        minutes = int(minpart)

        # day_part_str = '.{}'.format(dec_split[1])
        # day, day_part_flt = int(dec_split[0]), float(day_part_str)
        # hour_dec = day_part_flt * 24
        # hour_split = str(hour_dec).split('.')
        # hour, hour_part = int(hour_split[0]), float('.{}'.format(hour_split[1]))
        # min_part = str(hour_part * 60).split('.')
        #

        if minutes == 29:
            minutes = 30
        elif minutes == 59:
            minutes = 0

        tup = datetime(year, 1, 1) + timedelta(days=day, hours=hour, minutes=minutes)
        return tup

    arr_cols = [0, 2, 12, 14, 28, 30, 33, 34, 35]
    subset = ['year', 'day', 'H', 'LE', 'RN', 'RG', 'RGout', 'RGL', 'RGLout']
    # ncols = len(arr_cols)

    columns = ['H', 'LE', 'RN', 'RG', 'RGout', 'RGL', 'RGLout']
    for key, val in dict_.iteritems():  # Changes here
        amf_name = val['Name']
        print 'name: {}'.format(amf_name)
        folder = os.path.join(path,'AMF_Data',amf_name)

        folder_contents = os.listdir(folder)
        print "this is the folder contents: {}".format(folder_contents)

        csv_list = [os.path.join(folder, item) for item in folder_contents]
        print "this is the new list: {}".format(csv_list)

        # amf_data = array([]).reshape(0, ncols)

        print 'attempting to fetch headers: {}'.format(subset)
        amf_data = None
        for item in csv_list:
            p = os.path.join(folder, item)
            # if i == 0:
            #     col_check = loadtxt(p, dtype=str, skiprows=0, delimiter=',', usecols=arr_cols)
            #     print 'headers being read: \n {}'.format(col_check[:1, :])

            csv = loadtxt(p, dtype=str, skiprows=3, delimiter=',', usecols=arr_cols)
            if amf_data is None:
                amf_data = csv
            else:
                amf_data = append(amf_data, csv, axis=0)

        new_ind = [day_fraction_to_hr_min(float(row[1]), int(row[0])) for row in amf_data]
        amf_data = amf_data[:, 2:]

        df = DataFrame(amf_data, index=new_ind, columns=columns)
        print 'You have {} rows of --RAW-- data from {}'.format(df.shape[0], amf_name)

        # drop rows with NA values in 'subset'
        df[df == '-9999'] = nan
        df = df[notnull(df)]
        df = df.apply(to_numeric)
        df.dropna(axis=0, how='any', inplace=True)
        print 'You have {} rows of FlUX  data from {}'.format(df.shape[0], amf_name)

        # Find all complete days (48) records with no NULL values,
        if complete_days_only:
            df = df.groupby(lambda xx: xx.date())
            print 'df grouped: {}'.format(df)
            df = df.aggregate(lambda xx: sum(xx) if len(xx) > 23 else nan)

        df.dropna(axis=0, how='any', inplace=True)

        # and convert energy to MJ
        for name, series in df.iteritems():
            if name in columns:
                series *= 0.0864 / 48

        # calculate energy balance error
        calculated_cols = ['rad_err', 'en_bal_err', 'rad_minus_sens_heat', 'amf_ET']
        empty = zeros((df.shape[0], len(calculated_cols)), dtype=float)
        new_df = DataFrame(empty, index=df.index, columns=calculated_cols)
        df = concat([df, new_df], axis=1, join='outer')

        for ind, row in df.iterrows():

            rn = row['RN']
            leg = row['LE'] + row['H']
            rn_leg = rn - leg

            row['rad_err'] = (abs(rn - (row['RG'] - row['RGout'] + row['RGL'] - row['RGLout'])) / rn)
            row['en_bal_err'] = rn_leg / rn
            row['rad_minus_sens_heat'] = rn_leg * 0.0864 / 48
            row['amf_ET'] = (row['LE'] / 2.45)  # convert from MJ/(step * m**2) to mm water

        df_low_err = df[df['en_bal_err'] <= close_threshold]

        print 'You have {} DAYS of CLEAN RN/LE/H/RAD data from {}'.format(df.shape[0], amf_name)
        print 'The mean energy balance closure error is: {}'.format(df['en_bal_err'].mean())
        print 'You have {} DAYS  of [0.0 < CLOSURE ERROR < {}] data from {}'.format(len(df_low_err), close_threshold,
                                                                                    amf_name)

        if save_cleaned_data_path:
            p = os.path.join(save_cleaned_data_path, '{}_cleaned_all.csv'.format(amf_name))
            df.to_csv(p)

            p = os.path.join(save_cleaned_data_path, '{}_cleaned_lowErr.csv'.format(amf_name))
            df_low_err.to_csv(p)

        if return_low_err:
            val['AMF_Data'] = df_low_err
        else:
            val['AMF_Data'] = df_low_err

    return dict_


if __name__ == '__main__':
    pass


# ============= EOF =============================================
