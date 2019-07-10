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
import matplotlib.pyplot as plt
import datetime
# ============= standard library imports ========================


if __name__ == "__main__":

    sitename = 'vcm'
    taw = '125'
    root = '/Users/dcadol/Desktop/academic_docs_II/'

    #combined_timeseries_{}_taw{}
    data_location = os.path.join(root, 'combined_timeseries_{}_taw{}.csv'.format(sitename, taw))

    data_df = pd.read_csv(data_location, header=0)


    print type(data_df.columns[0])

    # this is how you rename columns
    data_df.rename(columns={data_df.columns[0]: 'date_string'}, inplace=True)

    # here we make a new datetime column based on by indexing the dataframe, effectively selecting date_string col
    data_df['dt'] = pd.to_datetime(data_df.iloc[:, 0])
    # # we could do:
    # data_df['dt'] = pd.to_datetime(data_df['date_string'])

    # set dt as the index
    data_df.set_index('dt', drop=True, inplace=True)

    data_df.drop(['date_string'], axis=1, inplace=True)

    # trim off the excess where JPL is not good and Amf is not good
    data_df = data_df['2009-02-01': '2012-12-03']
    print data_df

    # data_df[]

    # interpolate smoothly. Now that most errors are gone....
    print 'how many null jpl values there are', pd.isna(data_df['jpl_values']).sum()
    print 'how many null ameriflux eta values are there', pd.isna(data_df['amf_eta_values'])
    # data_df['jpl_akima'] = data_df['jpl_values'].interpolate(method='akima')
    # data_df['amf_akima'] = data_df['amf_eta_values'].interpolate(method='akima')

    print 'saving the interpolated dataset to file'
    data_df.to_csv(os.path.join(root, 'akima_interpolated.csv'))

    # get the cumulative sum of each of the columns. These we will plot
    data_df['etrm_cum'] = data_df['etrm_values'].cumsum()
    data_df['jpl_cum'] = data_df['jpl_values'].cumsum()
    # data_df['jpl_cum_akima'] = data_df['jpl_akima'].cumsum()
    data_df['prism_cum'] = data_df['prism_values'].cumsum()
    # Here we use the akima interpolated AMF just to be extra conservative relative to JPL which we use un-interpolated
    data_df['amf_cum'] = data_df['amf_eta_values'].cumsum()

    # 30% increase in amf to account for possible closure error
    data_df['amf_30perc'] = data_df['amf_eta_values'] + (data_df['amf_eta_values'] * .30)
    data_df['amf_30perc_cum'] = data_df['amf_30perc'].cumsum()

    print 'data df \n', data_df

    # # from the pandas cheatsheet
    # ax = data_df.plot()
    #
    # ax.set_xlabel('time')
    # ax.set_ylabel('mm ET or Precip')


    fig, ax = plt.subplots()
    ax.plot(data_df.index.values, data_df['etrm_cum'], color='black')
    ax.plot_date(data_df.index.values, data_df['etrm_cum'], fillstyle='none', color='black')

    ax.plot(data_df.index.values, data_df['jpl_cum'], color='red')
    ax.plot_date(data_df.index.values, data_df['jpl_cum'], fillstyle='none', color='red')

    ax.plot(data_df.index.values, data_df['prism_cum'], color='blue')
    ax.plot_date(data_df.index.values, data_df['prism_cum'], fillstyle='none', color='blue')

    # Note, amf_cum is filled with akima interpolation
    ax.plot(data_df.index.values, data_df['amf_cum'], color='green')
    ax.plot_date(data_df.index.values, data_df['amf_cum'], fillstyle='none', color='green')

    ax.plot(data_df.index.values, data_df['amf_30perc_cum'], color='yellow')
    ax.plot_date(data_df.index.values, data_df['amf_30perc_cum'], fillstyle='none', color='yellow')

    ax.set_title('Cumulative ETa and Precip Site:{} ETRM TAW:{}'.format(sitename, taw))
    ax.set_ylabel('ETa or Precip in mm H20')
    ax.set_xlabel('Date')
    plt.grid(True)

    plt.grid(True)
    plt.show()

    """fig, ax = plt.subplots()

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

    plt.show()"""