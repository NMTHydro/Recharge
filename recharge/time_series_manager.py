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
from pandas import DataFrame, notnull, to_numeric, concat
from numpy import array, nan, loadtxt, append, zeros
from datetime import datetime, timedelta


def get_etrm_time_series(inputs_path, dict_=None, single_file=False):
    """
    Read pre-extracted data out of a formatted csv.  Use recharge.point_extract_utility.py to do extract.

    :param inputs_path: path to a folder of csv files.
    :param dict_: dict of point locations
    :param single_file: if the inputs path is a single file path
    :returns dataframe of etrm time series input

    csv will be in the following format
    ['kcb', 'rg', 'etrs', 'min_temp', 'max_temp', 'temp', 'precip']
    """

    if single_file:

        csv = loadtxt(inputs_path, dtype=str, delimiter=',')
        print 'inputs path: {}'.format(inputs_path)
        name = inputs_path.replace('.csv', '')
        print 'reading in csv for {}'.format(name)

        try:
            new_ind = [datetime.strptime(row[0], '%Y-%m-%d') for row in csv[1:]]  # extracts should have headers

        except ValueError:
            new_ind = [datetime.strptime(row[0], '%Y/%m/%d') for row in csv[1:]]  # extracts should have headers

        arr = array(csv[1:, 1:], dtype=float)

        cols = ['kcb', 'rg', 'etrs', 'min_temp', 'max_temp', 'temp', 'precip']

        df = DataFrame(arr, index=new_ind, columns=cols)

        return df

    else:
        csv_list = os.listdir(inputs_path)
        csv_list = [filename for filename in csv_list if filename.endswith('.csv')]

    print 'etrm extract csv list: \n{}'.format(csv_list)
    for file_ in csv_list:

        csv = loadtxt(os.path.join(inputs_path, file_), dtype=str, delimiter=',')
        name = file_.replace('.csv', '')
        print 'reading in csv for {}'.format(name)

        new_ind = [datetime.strptime(row[0], '%Y-%m-%d') for row in csv[1:]]  # extracts should have headers

        arr = array(csv[1:, 1:], dtype=float)

        cols = ['kcb', 'rg', 'etrs', 'min_temp', 'max_temp', 'temp', 'precip']

        df = DataFrame(arr, index=new_ind, columns=cols)
        if dict_:
            for key, val in dict_.iteritems():
                if val['Name'] == name:
                    print 'updating {} number {} with etrm inputs df'.format(name, key)
                    # print 'your df: \n{}'.format(df)
                    dict_[key]['etrm'] = df

    return None


def amf_obs_time_series(dict_, path, save_cleaned_data_path=False, complete_days_only=False,
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

    def day_fraction_to_hr_min(fractional_day, year):
        dec = str(fractional_day)
        dec_split = dec.split('.')
        day_part_str = '.{}'.format(dec_split[1])
        day, day_part_flt = int(dec_split[0]), float(day_part_str)
        hour_dec = day_part_flt * 24
        hour_split = str(hour_dec).split('.')
        hour, hour_part = int(hour_split[0]), float('.{}'.format(hour_split[1]))
        min_part = str(hour_part * 60).split('.')
        min_ = int(min_part[0])
        if min_ == 29:
            min_ = 30
        if min_ == 59:
            min_ = 0
        tup = datetime(year, 1, 1) + timedelta(days=day, hours=hour, minutes=min_)
        return tup

    for key, val in dict_.iteritems(): # Changes here
        amf_name = val['Name']
        print '\n name: {}'.format(amf_name)
        folder = os.path.join(path, amf_name)
        print path
        print amf_name
        folder_list = os.listdir(folder)
        new_list = []
        for item in folder_list:
            new_list.append(os.path.join(path, amf_name, item))
        print "this is the folder list: {}".format(folder_list)
        print "this is the new list: {}".format(new_list)
        csv_list = new_list
        print folder
        print 'csv list: \n{}'.format(csv_list)
        arr_cols = [0, 2, 12, 14, 28, 30, 33, 34, 35]
        amf_data = array([]).reshape(0, len(arr_cols))
        subset = ['year', 'day', 'H', 'LE', 'RN', 'RG', 'RGout', 'RGL', 'RGLout']

        print 'attempting to fetch headers:\n{}'.format(subset)
        first = True
        for item in csv_list:
            if first:
                col_check = loadtxt(os.path.join(folder, item), dtype=str, skiprows=0, delimiter=',', usecols=arr_cols)
                print 'headers being read: \n {}'.format(col_check[:1, :])
                first = False
            csv = loadtxt(os.path.join(folder, item), dtype=str, skiprows=3, delimiter=',', usecols=arr_cols)
            amf_data = append(amf_data, csv, axis=0)

        new_ind = [day_fraction_to_hr_min(float(row[1]), int(row[0])) for row in amf_data]
        amf_data = amf_data[:, 2:]

        columns = ['H', 'LE', 'RN', 'RG', 'RGout', 'RGL', 'RGLout']
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
            row['rad_err'] = (abs((row['RN']) - (row['RG'] - row['RGout'] + row['RGL'] - row['RGLout'])) / row['RN'])
            row['en_bal_err'] = ((row['RN'] - (row['LE'] + row['H'])) / row['RN'])
            row['rad_minus_sens_heat'] = (row['RN'] - (row['LE'] + row['H'])) * 0.0864 / 48
            row['amf_ET'] = (row['LE'] / 2.45)  # convert from MJ/(step * m**2) to mm water

        df_low_err = df[df['en_bal_err'] <= close_threshold]

        print 'You have {} DAYS of CLEAN RN/LE/H/RAD data from {}'.format(df.shape[0], amf_name)
        print 'The mean energy balance closure error is: {}'.format(df['en_bal_err'].mean())
        print 'You have {} DAYS  of [0.0 < CLOSURE ERROR < {}] data from {}'.format(len(df_low_err), close_threshold,
                                                                                    amf_name)

        if save_cleaned_data_path:
	        df.to_csv(os.path.join('{}'.format(save_cleaned_data_path),'{}_cleaned_all.csv'.format(amf_name)))
            #df.to_csv('{}\\{}_cleaned_all.csv'.format(save_cleaned_data_path, amf_name))
	        df_low_err.to_csv(os.path.join('{}'.format(save_cleaned_data_path), '{}_cleaned_lowErr.csv'.format(amf_name)))
            df_low_err.to_csv('{}\\{}_cleaned_lowErr.csv'.format(save_cleaned_data_path, amf_name))

        if return_low_err:
            val['AMF_Data'] = df_low_err
        else:
            val['AMF_Data'] = df_low_err

    return dict_


if __name__ == '__main__':
    pass


# ============= EOF =============================================
