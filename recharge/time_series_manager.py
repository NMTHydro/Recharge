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


def get_etrm_time_series(dict_, inputs_path=None, get_from_point=False):
    """# csv should be in the following format:
# ['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
# 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z']"""

    folder = os.path.join(inputs_path)
    os.chdir(folder)
    csv_list = os.listdir(folder)
    csv_list = [filename for filename in csv_list if filename.endswith('.csv')]
    print 'csv list: \n{}'.format(csv_list)
    for file_ in csv_list:
        csv = loadtxt(os.path.join(folder, file_), dtype=str, delimiter=',')
        name = file_.strip('AMF').strip('_extract.csv')
        try:
            new_ind = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in csv]
        except ValueError:
            new_ind = [datetime.strptime(row[0], '%Y/%m%d') for row in csv]
        arr = array(csv[:, 1:], dtype=float)
        cols = ['bed_ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_pm', 'plant height', 'min temp',
                'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z']
        df = DataFrame(arr, index=new_ind, columns=cols)
        dict_[name].update({'etrm': df})
        return None


def amf_obs_time_series(dict_, path, save_cleaned_data_path=False, complete_days_only=False):

    """read in data from an extract file
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
        min = int(min_part[0])
        if min == 29:
            min = 30
        if min == 59:
            min = 0
        tup = datetime(year, 1, 1) + timedelta(days=day, hours=hour, minutes=min)
        return tup

    for key, val in dict_.iteritems():
        amf_name = val['Name']
        print '\nname: {}'.format(amf_name)
        folder = os.path.join(path, amf_name)
        os.chdir(folder)
        csv_list = os.listdir(folder)
        print 'csv list: \n{}'.format(csv_list)
        arr_cols = [0, 2, 12, 14, 28, 30, 33, 34, 35]
        amf_data = array([]).reshape(0, len(arr_cols))
        subset = ['year', 'day', 'H', 'LE', 'RN', 'RG', 'RGout', 'RGL', 'RGLout']

        print 'attempting to fetch headers:\n{}'.format(subset)
        first = True
        for item in csv_list:
            if first:
                col_check = loadtxt(item, dtype=str, skiprows=0, delimiter=',', usecols=arr_cols)
                print 'headers being read: \n {}'.format(col_check[:1, :])
                first = False
            csv = loadtxt(item, dtype=str, skiprows=3, delimiter=',', usecols=arr_cols)
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
            df = df.groupby(lambda xx: xx.date()).aggregate(lambda xx: sum(xx) if len(xx) > 10 else nan)
        df.dropna(axis=0, how='any', inplace=True)

        # and convert energy to MJ
        for name, series in df.iteritems():
            if name in columns:
                series *= 0.0864 / 48

        # calculate energy balance error
        calculated_cols = ['rad_err', 'en_bal_err', 'rad_minus_heat', 'amf_ET']
        empty = zeros((df.shape[0], len(calculated_cols)), dtype=float)
        new_df = DataFrame(empty, index=df.index, columns=calculated_cols)
        df = concat([df, new_df], axis=1, join='outer')
        for ind, row in df.iterrows():
            row['rad_err'] = (abs((row['RN']) - (row['RG'] - row['RGout'] + row['RGL'] - row['RGLout'])) / row['RN'])
            row['en_bal_err'] = ((row['RN'] - (row['LE'] + row['H'])) / row['RN'])
            row['rad_minus_heat'] = (row['RN'] - (row['LE'] + row['H'])) * 0.0864 / 48
            row['amf_ET'] = (row['LE'] / 2.45)  # convert from MJ/(step * m**2) to mm water

        df_low_err = df[df['en_bal_err'] <= 0.20]
        print 'You have {} DAYS of CLEAN RN/LE/H/RAD data from {}'.format(df.shape[0], amf_name)
        print 'The mean energy balance closure error is: {}'.format(df['en_bal_err'].mean())
        print 'You have {} DAYS  of [0.0 < CLOSURE ERROR < 0.10] data from {}'.format(len(df_low_err), amf_name)
        if save_cleaned_data_path:
            df.to_csv('{}\\{}_cleaned_all.csv'.format(save_cleaned_data_path, amf_name))
            df_low_err.to_csv('{}\\{}_cleaned_lowErr.csv'.format(save_cleaned_data_path, amf_name))

        val.update({'Dataframe': df})

    return dict_


if __name__ == '__main__':
    pass

# ============= EOF =============================================