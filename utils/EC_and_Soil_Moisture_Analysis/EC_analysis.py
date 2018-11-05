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

# ============= local library imports ===========================
"""5) VARIABLE LIST

-- TIMEKEEPING
TIMESTAMP_START (YYYYMMDDHHMM): ISO timestamp start of averaging period - short format [YEAR, DTIME, DOY, HRMIN]
TIMESTAMP_END   (YYYYMMDDHHMM): ISO timestamp end of averaging period - short format [YEAR, DTIME, DOY, HRMIN]

-- GASES
CO2_1 (umolCO2 mol-1): Carbon Dioxide (CO2) mole fraction (CO2 layer 1 - Top) [CO2top]
CO2_2 (umolCO2 mol-1): Carbon Dioxide (CO2) mole fraction (CO2 layer 2) [CO2]
H2O   (mmolH2O mol-1): Water (H2O) vapor mole fraction [H2O]
FC    (umolCO2 m-2 s-1): Carbon Dioxide (CO2) flux [FC]
SC    (umolCO2 m-2 s-1): Carbon Dioxide (CO2) storage flux [SFC]

-- HEAT
G   (W m-2): Soil heat flux [FG]
H   (W m-2): Sensible heat flux [H]
LE  (W m-2): Latent heat flux [LE]
SH  (W m-2): Heat storage in the air [SH]
SLE (W m-2): Latent heat storage flux [SLE]

-- MET_WIND
WD    (Decimal degrees): Wind direction [WD]
WS    (m s-1): Wind speed [WS]
USTAR (m s-1): Friction velocity [UST]
ZL    (adimensional): Stability parameter [ZL]

-- MET_ATM
PA     (kPa): Atmospheric pressure [PRESS]
RH     (%): Relative humidity, range 0-100 [RH]
TA     (deg C): Air temperature [TA]
VPD_PI (hPa): Vapor Pressure Deficit (as measured/calculated by tower teams) [VPD]

-- MET_SOIL
SWC_1 (%): Soil water content (volumetric), range 0-100 (SWC layer 1 - upper) [SWC1]
SWC_2 (%): Soil water content (volumetric), range 0-100 (SWC layer 2 - lower) [SWC2]
TS_1  (deg C): Soil temperature (TS layer 1 - upper) [TS1]
TS_2  (deg C): Soil temperature (TS layer 2 - lower) [TS2]

-- MET_RAD
APAR     (umol m-2 s-1): Absorbed PAR [APAR]
FAPAR    (%): Fraction of absorbed PAR, range 0-100 [APARpct]
NETRAD   (W m-2): Net radiation [Rn]
PPFD_IN  (umolPhoton m-2 s-1): Photosynthetic photon flux density, incoming [PAR]
PPFD_OUT (umolPhoton m-2 s-1): Photosynthetic photon flux density, outgoing [PARout]
PPFD_DIF (umolPhoton m-2 s-1): Photosynthetic photon flux density, diffuse incoming [PARdif]
SW_IN    (W m-2): Shortwave radiation, incoming [Rg]
SW_OUT   (W m-2): Shortwave radiation, outgoing [RgOut]
SW_DIF   (W m-2): Shortwave radiation, diffuse incoming [Rgdif]
LW_IN    (W m-2): Longwave radiation, incoming [Rgl]
LW_OUT   (W m-2): Longwave radiation, outgoing [RglOut]

-- MET_PRECIP
P      (mm): Precipitation [PREC]

-- PRODUCTS
NEE_PI  (umolCO2 m-2 s-1): Net Ecosystem Exchange (as measured/calculated by tower teams) [NEE]
RECO_PI (umolCO2 m-2 s-1): Ecosystem Respiration (as measured/calculated by tower teams) [RE]
GPP_PI  (umolCO2 m-2 s-1): Gross Primary Productivity (as measured/calculated by tower teams) [GPP]"""

def closure_check(ec_dataset, Rn, LE, H, timeseries, daily_average=False):
    """"""
    if not daily_average:
        try:
            G = ec_dataset['FG']
        # TODO - If there is no ground heat flux, average over 24 hours to negate impact of G. Ask Dan the proper way.
        except:
            KeyError
            print 'No ground heat flux at this station. Consider averaging over a daily period.'
            G = 0
        try:
            stored_H = ec_dataset['SH']
            stored_LE = ec_dataset['SLE']
        except:
            KeyError
            print 'No sensible or latent heat storage terms'
            stored_H = 0
            stored_LE = 0

        # Todo - Get Dan's help with this.
        closure_error = abs((((Rn-G) - (LE + H)) - (stored_H + stored_LE))/Rn) * 100

        print 'median closure error: {}, average closure error {}'.format(
            np.median(closure_error.values), np.mean(closure_error.values))

        plotter1(timeseries, closure_error)

    else:
        print 'IGNORE G as we are averaging over a daily time period. We wont bother with stored H or stored LE either'
        closure_error = abs(((Rn) - (LE + H)) / Rn) * 100

        print 'median closure error: {}, average closure error {}'.format(
            np.median(closure_error.values), np.mean(closure_error.values))

        plotter1(timeseries, closure_error, daily_average=True)


def plotter1(x, y, daily_average=False):
    """
    Plots parameters via a timeseries
    :param x:
    :param y:
    :param daily_average:
    :return:
    """

    if not daily_average:
        x = x.values
        y = y.values

        plt.plot_date(x, y, fillstyle='none')
        plt.show()
    else:
        y = y.values

        plt.plot_date(x, y, fillstyle='none')
        plt.show()

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

    #===== daily averaging =====

    else:
        timeseries = timeseries.values
        Rn = ec_dataset['NETRAD'].values
        H = ec_dataset['H'].values
        LE = ec_dataset['LE'].values
        # indexed_datetimes = pd.DataFrame(pd.DatetimeIndex(timeseries))

        # recreate a dataframe of the variables you want to time average on a dialy timestep
        halfhour_data = pd.DataFrame({'timeseries':timeseries, 'Rn':Rn, 'LE':LE, 'H':H})

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
    print ec_dataset[ec_dataset[y] != -9999].head()
    ec_dataset = ec_dataset[ec_dataset[y] != -9999]

    if x.startswith("TIMESTAMP"):
        a = ec_dataset[x].apply(lambda b: dt.strptime(str(b), '%Y%m%d%H%M'))
    else:
        a = ec_dataset[x]

    b = ec_dataset[y]

    unconverted_LE = ec_dataset[y]
    if y == 'LE':
        # convert latent heat flux into mm h20 by multiplying by the latent heat of vaporization todo - check calc w Dan
        mmh20 = b * 7.962e-4 # 4.09243e-7 <- instantaneous (mm/s)/m^2

    print mmh20.head()

    # # check energy balance closure
    # check_energybal(ec_dataset, timeseries=a)

    check_energybal(ec_dataset, timeseries=a, dailyaverage=True)

    # plot the variables
    plotter1(a, mmh20)

    plotter1(a, unconverted_LE)



if __name__ == '__main__':
    def main():
        """We are reading in and plotting Eddy Covariance Data from Ameriflux EC towers"""
        # get the location of the file containing the EC dataset
        # #Walnut Gulch Kendal Grasslands
        # path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Wkg_BASE-BADM_11-5/AMF_US-Wkg_BASE_HH_11-5.csv'
        # # path = 'C:\Users\Mike\Downloads\AMF_US-Wkg_BASE_HH_11-5.csv' # Dan's computer
        # todo - there seems to be a bias in the closure error of Sevilleta Grass. WHY?!
        # Sevilleta Grass
        path = '/Users/Gabe/Desktop/thesiscomposition/fluxnet_EC/AMF_US-Seg_BASE-BADM_8-5/AMF_US-Seg_BASE_HH_8-5.csv'

        # define variables you want to analyze
        ind_var = 'TIMESTAMP_START'
        dep_var = 'LE'

        analyze(path, ind_var, dep_var)

        # todo - create a function that measures energy balance closure error


if __name__ == "__main__":

    main()