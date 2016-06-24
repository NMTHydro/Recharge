# ===============================================================================
# Copyright 2016 ross
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

# Modified from ETRM_distributed/ETRM_savAnMo_5MAY16.py
# Developed by David Ketchum NMT 2016

# ============= standard library imports ========================
import calendar
import logging
import os
from datetime import datetime, timedelta, time
from math import isnan
from dateutil import rrule
from numpy import ones, where, zeros
from numpy.ma import maximum, minimum, exp
from osgeo import gdal

# ============= local library imports  ==========================
from recharge.etrm_funcs import tif_params, tif_to_array, clean, InvalidDataSourceException, write_tiff
from recharge.model import BaseModel

YEARS = (2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013)
KE_MAX = 1.0
S = 480
E = 940

logging.basicConfig(filename='etrm.log', level=logging.DEBUG)


class ETRM(BaseModel):
    """
    ETRM: EvapoTranspiration Recharge Model

    """
    _runtime = None

    _current_use_root = None
    _array_results_root = None
    _ndvi_root = None
    _prism_root = None
    _prism_min_temp_root = None
    _prism_max_temp_root = None
    _pm_data_root = None

    _min_val = None
    _shape = None
    _qDeps = None
    _taw = None
    _nlcd_rt_z = None
    _nlcd_plt_hgt = None
    _ksat = None
    _tew = None
    _dr = None
    _de = None
    _drew = None

    _output_tag = None
    _dataset_params = None

    _annual_results_root = None
    _monthly_results_root = None

    def initialize(self):
        """
        Initialize the model

        :return:
        """
        self.load_current_use()
        self.load_array_results()

        return True

    def run_model(self):
        """
        Run the model

        :return:
        """

        shape = self._shape
        tew = self._tew
        taw = self._taw

        start_time = datetime.now()

        pkcb = zeros(shape)
        swe = zeros(shape)
        tot_snow = zeros(shape)

        tot_mass = zeros(shape)
        cum_mass = zeros(shape)
        ref_et = zeros(shape)
        a_min = ones(shape) * 0.45
        a_max = ones(shape) * 0.90
        a = a_max
        pA = a_min

        days = list(rrule.rrule(rrule.DAILY, dtstart=self._start, until=self._end))
        nsteps = len(days)
        plt_day = zeros(nsteps)
        plt_rain = zeros(nsteps)
        plt_eta = zeros(nsteps)
        plt_snow_fall = zeros(nsteps)
        plt_ro = zeros(nsteps)
        plt_dr = zeros(nsteps)
        plt_de = zeros(nsteps)
        plt_drew = zeros(nsteps)
        plt_temp = zeros(nsteps)
        plt_dp_r = zeros(nsteps)
        plt_ks = zeros(nsteps)
        plt_pdr = zeros(nsteps)
        plt_etrs = zeros(nsteps)
        plt_kcb = zeros(nsteps)
        plt_ppt = zeros(nsteps)
        plt_ke = zeros(nsteps)
        plt_kr = zeros(nsteps)
        plt_mlt = zeros(nsteps)
        plt_swe = zeros(nsteps)
        plt_tempm = zeros(nsteps)
        plt_fs1 = zeros(nsteps)
        plt_mass = zeros(nsteps)

        p_mo_et = zeros(shape)
        p_mo_precip = zeros(shape)
        p_mo_ro = zeros(shape)
        p_mo_deps = self._dr + self._de + self._drew
        p_mo_infil = zeros(shape)
        p_mo_etrs = zeros(shape)

        p_yr_et = zeros(shape)
        p_yr_precip = zeros(shape)
        p_yr_ro = zeros(shape)
        p_yr_deps = self._dr + self._de + self._drew
        p_yr_infil = zeros(shape)
        p_yr_etrs = zeros(shape)

        start_month = self._start_month
        end_month = self._end_month

        for i, dday in enumerate(days):
            if i > 0:
                pkcb = kcb
            doy = dday.timetuple().tm_yday
            year = dday.year
            month = dday.month
            day = dday.day

            msg = 'Time : {} day {}_{}'.format(datetime.now() - start_time, doy, year)
            logging.debug(msg)

            # --------------  kcb -------------------
            if year == 2000:
                ndvi = self.calculate_ndvi_2000(doy)
            elif year == 2001:
                ndvi = self.calculate_ndvi_2001(doy)
            else:
                ndvi = self.calculate_ndvi(year, doy)

            kcb = ndvi * 1.25
            kcb = maximum(kcb, self._min_val)
            kcb = where(isnan(kcb), pkcb, kcb)

            # -------------- PRISM -------------------
            ppt, ppt_tom, max_temp, min_temp, mid_temp = self.load_prism(dday)

            # -------------- PM -------------------
            # PM data to etrs
            name = os.path.join('PM{}'.format(year),
                                'PM_NM_{}_{:03n}'.format(year, doy))
            etrs = tif_to_array(self._pm_data_root, name)
            etrs = maximum(etrs, self._min_val)

            name = os.path.join('PM{}'.format(year),
                                'RLIN_NM_{}_{:03n}'.format(year, doy))
            rlin = tif_to_array(self._pm_data_root, name)
            rlin = maximum(rlin, zeros(shape))

            name = os.path.join('rad{}'.format(year),
                                'RTOT_{}_{:03n}'.format(year, doy))
            rg = tif_to_array(self._pm_data_root, name)
            rg = maximum(rg, zeros(shape))

            if i == 0:
                #  Total evaporable water is depth of water in the evaporable
                #  soil layer, i.e., the water available to both stage 1 and 2 evaporation
                rew = minimum((2 + (tew / 3.)), 0.8 * tew)
                # del tew1, tew2

                # you should have all these from previous model runs
                pDr = self._dr
                pDe = self._de
                pDrew = self._drew
                dr = self._dr
                de = self._de
                drew = self._drew

            nom = 2 if start_month <= doy <= end_month else 6
            ksat = self._ksat * nom / 24.

            kc_max_1 = kcb + 0.0001
            min_val = ones(shape) * 0.0001
            kc_max = maximum(min_val, kc_max_1)

            self._nlcd_plt_hgt = self._nlcd_plt_hgt * 0.5 + 1
            numr = maximum(kcb - self._kc_min, min_val * 10)
            denom = maximum((kc_max - self._kc_min), min_val * 10)
            fcov_ref = (numr / denom) ** self._nlcd_plt_hgt
            fcov_min = minimum(fcov_ref, ones(shape))
            fcov = maximum(fcov_min, min_val * 10)
            few = maximum(1 - fcov, 0.01)  # exposed ground

            pKr = kr
            kr = minimum(((tew - de) / (tew - rew)), ones(shape))
            kr = where(isnan(kr), pKr, kr)

            pKs = ks
            ks_ref = where(((taw - pDr) / (0.6 * taw)) < zeros(shape), ones(shape) * 0.001,
                           ((taw - pDr) / (0.6 * taw)))
            ks_ref = where(isnan(ks), pKs, ks_ref)
            ks = minimum(ks_ref, ones(shape))

            # Ke evaporation reduction coefficient; stage 1 evaporation
            fsa = where(isnan((rew - drew) / (KE_MAX * etrs)), zeros(shape),
                        (rew - drew) / (KE_MAX * etrs))
            fsb = minimum(fsa, ones(shape))
            fs1 = maximum(fsb, zeros(shape))
            ke = where(drew < rew, minimum((fs1 + (1 - fs1) * kr) * (kc_max - ks * kcb), few * kc_max),
                       zeros(shape))

            transp = (ks * kcb) * etrs
            et_init = (ks * kcb + ke) * etrs
            eta = maximum(et_init, zeros(shape))
            evap_init = ke * etrs
            evap_min = maximum(evap_init, zeros(shape))
            evap = minimum(evap_min, kc_max)

            # Load temp, find swe, melt, and precipitation, load Ksat
            # Use SNOTEL data for precip and temps:
            # df_snow : (stel_date, stel_snow, stel_precip, stel_tobs, stel_tmax, stel_tmin, stel_tavg, stel_snwd)

            snow_fall = where(mid_temp <= 0.0, ppt, zeros(shape))
            rain = where(mid_temp >= 0.0, ppt, zeros(shape))

            pA = a
            a = where(snow_fall > 3.0, ones(shape) * a_max, a)
            a = where(snow_fall <= 3.0, a_min + (pA - a_min) * exp(-0.12), a)
            a = where(snow_fall == 0.0, a_min + (pA - a_min) * exp(-0.05), a)
            a = where(a < a_min, a_min, a)

            swe += snow_fall

            mlt_init = maximum(((1 - a) * rg * 0.2) + (mid_temp - 1.8) * 11.0,
                               zeros(shape))  # use calibrate coefficients
            mlt = minimum(swe, mlt_init)

            swe -= mlt

            # Find depletions
            pDr = dr
            pDe = de
            pDrew = drew
            watr = rain + mlt
            deps = dr + de + drew

            ro = zeros(shape)
            ro = where(watr > ksat + deps, watr - ksat - deps, ro)
            ro = maximum(ro, zeros(shape))

            dp_r = zeros(shape)
            id1 = where(watr > deps, ones(shape), zeros(shape))
            id2 = where(ksat > watr - deps, ones(shape), zeros(shape))
            dp_r = where(id1 + id2 > 1.99, maximum(watr - deps, zeros(shape)), dp_r)

            dp_r = where(watr > ksat + deps, ksat, dp_r)
            dp_r = maximum(dp_r, zeros(shape))

            drew_1 = minimum((pDrew + ro + (evap - (rain + mlt))), rew)
            drew = maximum(drew_1, zeros(shape))
            diff = maximum(pDrew - drew, zeros(shape))

            de_1 = minimum((pDe + (evap - (rain + mlt - diff))), tew)
            de = maximum(de_1, zeros(shape))
            diff = maximum(((pDrew - drew) + (pDe - de)), zeros(shape))

            dr_1 = minimum((pDr + ((transp + dp_r) - (rain + mlt - diff))), taw)
            dr = maximum(dr_1, zeros(shape))

            # Create cumulative rasters to show net over entire run

            infil += dp_r
            infil = maximum(infil, zeros(shape))

            prev_et = et
            ref_et += etrs
            et = et + evap + transp
            et_ind = et / ref_et
            et = where(isnan(et) == True, prev_et, et)
            et = where(et > ref_et, ref_et / 2., et)
            et = maximum(et, ones(shape) * 0.001)

            precip = precip + rain + snow_fall
            precip = maximum(precip, zeros(shape))

            runoff += ro
            runoff = maximum(runoff, zeros(shape))

            snow_ras = swe + snow_fall - mlt
            snow_ras = maximum(snow_ras, zeros(shape))

            tot_snow += snow_fall

            mo_date = calendar.monthrange(year, month)
            if day == mo_date[1]:
                infil_mo = infil - p_mo_infil
                infil_mo = maximum(infil_mo, zeros(shape))

                ref_et_mo = etrs - p_mo_etrs
                et_mo = et - p_mo_et
                et_mo = where(isnan(et_mo) == True, p_mo_et, et_mo)
                et_mo = where(et_mo > ref_et, ref_et / 2., et_mo)
                et_mo = maximum(et_mo, ones(shape) * 0.001)

                precip_mo = precip - p_mo_precip
                precip_mo = maximum(precip_mo, zeros(shape))

                runoff_mo = ro - p_mo_ro
                runoff_mo = maximum(runoff_mo, zeros(shape))

                snow_ras_mo = swe
                snow_ras_mo = maximum(snow_ras_mo, zeros(shape))

                deps_mo = drew + de + dr
                delta_s_mo = p_mo_deps - deps_mo

                outputs = (('infil', infil_mo), ('et', et_mo), ('precip', precip_mo), ('runoff', runoff_mo),
                           ('snow_ras', snow_ras_mo), ('delta_s_mo', delta_s_mo), ('deps_mo', deps_mo))

                self.save_month_step(outputs, month, year)

                p_mo_et = et
                p_mo_precip = precip
                p_mo_ro = ro
                p_mo_deps = deps_mo
                p_mo_infil = infil
                p_mo_etrs = etrs

            if day == 31 and month == 12:
                infil_yr = infil - p_yr_infil
                infil_yr = maximum(infil_yr, zeros(shape))

                ref_et_yr = etrs - p_yr_etrs
                et_yr = et - p_yr_et
                et_yr = where(isnan(et_yr) == True, p_yr_et, et_yr)
                et_yr = where(et_yr > ref_et, ref_et / 2., et_yr)
                et_yr = maximum(et_yr, ones(shape) * 0.001)

                precip_yr = precip - p_yr_precip
                precip_yr = maximum(precip_yr, zeros(shape))

                runoff_yr = ro - p_yr_ro
                runoff_yr = maximum(runoff_yr, zeros(shape))

                snow_ras_yr = swe
                snow_ras_yr = maximum(snow_ras_yr, zeros(shape))

                deps_yr = drew + de + dr
                delta_s_yr = p_yr_deps - deps_yr

                outputs = (('infil', infil_yr), ('et', et_yr), ('precip', precip_yr), ('runoff', runoff_yr),
                           ('snow_ras', snow_ras_yr), ('delta_s_yr', delta_s_yr), ('deps_yr', deps_yr))

                p_yr_et = et
                p_yr_precip = precip
                p_yr_ro = ro
                p_yr_deps = deps_yr  # this was originally p_mo_deps = deps_yr im assuming this is a typo
                p_yr_infil = infil
                p_yr_etrs = etrs

                self.save_year_step(outputs, month, year)

            # Check MASS BALANCE for the love of WATER!!!
            mass = rain + mlt - (ro + transp + evap + dp_r + ((pDr - dr) + (pDe - de) + (pDrew - drew)))
            tot_mass += abs(mass)
            cum_mass += mass

            plt_day[i] = dday

            plt_rain[i] = rain[S, E]
            plt_eta[i] = eta[S, E]
            plt_snow_fall[i] = snow_fall[S, E]
            plt_ro[i] = ro[S, E]
            plt_dr[i] = dr[S, E]
            plt_de[i] = de[S, E]
            plt_drew[i] = drew[S, E]
            plt_temp[i] = mid_temp[S, E]
            plt_dp_r[i] = dp_r[S, E]
            plt_ks[i] = ks[S, E]
            plt_pdr[i] = pDr[S, E]
            plt_etrs[i] = etrs[S, E]
            plt_kcb[i] = kcb[S, E]
            plt_ppt[i] = ppt[S, E]
            plt_ke[i] = ke[S, E]
            plt_kr[i] = kr[S, E]
            plt_mlt[i] = mlt[S, E]
            plt_swe[i] = swe[S, E]
            plt_tempm[i] = max_temp[S, E]
            plt_fs1[i] = fs1[S, E]
            plt_mass[i] = mass[S, E]

    def save_year_step(self, outputs, month, year):
        """

        :param year:
        :param month:
        :param outputs:
        :return:
        """
        basename = os.path.join(self._annual_results_root, '{name}_{year}_{tag}.tif')
        savemsg = 'Saving name={name} year={year}'
        self.save_step(outputs, basename, savemsg, month, year)

    def save_month_step(self, outputs, month, year):
        """
        :param year:
        :param month:
        :param outputs:
        :return:
        """
        basename = os.path.join(self._monthly_results_root, '{name}_{month}_{year}_{tag}.tif')
        savemsg = 'Saving name={name} month={month}, year={year}'
        self.save_step(outputs, basename, savemsg, month, year)

    def save_step(self, outputs, basename, savemsg, month, year):
        """

        :param outputs:
        :param basename:
        :param savemsg:
        :param month:
        :param year:
        :return:
        """
        driver = gdal.GetDriverByName('GTiff')

        params = self._dataset_params

        for name, data in outputs:
            if self._verbose:
                logging.debug(savemsg.format(name=name, month=month, year=year))
            path = basename.format(name=name, month=month, year=year, tag=self._output_tag)

            write_tiff(path, params, data, driver=driver)

    def load_prism(self, d):
        """
        load prism data for this day

        :param d:
         :type d: datetime
        :return:
        """

        year = d.year
        month = d.month
        day = d.day

        shape = self._shape

        prism_base = 'PRISMD2_NMHW2mi_{}{:02n}{:02n}'
        name = prism_base.format(year, month, day)
        ppt = tif_to_array(self._prism_root, name)
        tom = d + timedelta(days=1)
        name = prism_base.format(year, tom.month, tom.day)
        ppt_tom = tif_to_array(self._prsim_root, name)
        ppt = maximum(ppt, zeros(shape))
        ppt_tom = maximum(ppt_tom, zeros(shape))
        # PRISM to mintemp, maxtemp, temp
        if year in YEARS:
            name = 'cai_tmin_us_us_30s_{}{:02n}{:02n}'.format(year, month, day)
            min_temp = tif_to_array(self._prism_min_temp_root, name)
        else:
            name = 'TempMin_NMHW2Buff_{}{:02n}{:02n}'.format(year, month, day)
            min_temp = tif_to_array(self._prism_min_temp_root, name)
        name = 'TempMax_NMHW2Buff_{}{:02n}{:02n}'.format(year, month, day)
        max_temp = tif_to_array(self._prism_max_temp_root, name)
        mid_temp = (min_temp + max_temp) / 2

        return ppt, ppt_tom, max_temp, min_temp, mid_temp

    # private
    def _default_config(self):
        input_root = os.path.join('F:', 'ETRM_Inputs')
        results_root = os.path.join('F:', 'ETRM_Results')
        cfg = {'current_use': os.path.join('C:', 'Recharge_GIS', 'OSG_Data', 'current_use'),
               'array_results': os.path.join('C:', 'Recharge_GIS', 'Array_Results', 'initialize'),
               'ndvi': os.path.join(input_root, 'NDVI', 'NDVI_std_all'),
               'prism': os.path.join(input_root, 'PRISM', 'Precip', '800m_std_all'),
               'prism_min_temp': os.path.join(input_root, 'PRISM', 'Temp', 'Minimum_standard'),
               'prism_max_temp': os.path.join(input_root, 'PRISM', 'Temp', 'Maximum_standard'),
               'pm_data': os.path.join(input_root, 'PM_RAD'),
               'annual_results': os.path.join(results_root, 'Annual_results'),
               'monthly_results': os.path.join(results_root, 'Monthly_results'),
               'output_tag': '23MAY',
               'start': '2000-1-1',
               'end': '2000-12-31',
               'start_month': 6,
               'end_month': 10,
               }
        return cfg

    def _load_config(self, cfg):
        self._current_use_root = cfg['current_use']
        self._array_results_root = cfg['array_results']
        self._ndvi_root = cfg['ndvi']
        self._prism_root = cfg['prism']
        self._prism_min_temp_root = cfg['prism_min_temp']
        self._prism_max_temp_root = cfg['prism_max_temp']
        self._pm_data_root = cfg['pm_data']
        self._annual_results_root = cfg['annual_results']
        self._monthly_results_root = cfg['monthly_results']

        self._output_tag = cfg['output_tag']

        self._load_start_end(cfg)

    def load_current_use(self):
        """

        :return:
        """
        root = self._current_use_root
        qDeps = tif_to_array(root, 'Q_deps_std')

        min_val = ones(qDeps.shape) * 0.001
        qDeps = maximum(qDeps, min_val)

        aws = tif_to_array(root, 'aws_mod_4_21_10_0')
        aws = maximum(aws, min_val)
        self._dataset_params = tif_params(root, 'aws_mod_4_21_10_0')

        nlcd_rt_z = tif_to_array(root, 'nlcd_root_dpth_15apr')
        nlcd_rt_z = maximum(nlcd_rt_z, min_val)

        nlcd_plt_hgt = tif_to_array(root, 'nlcd_plnt_hgt1_250_m_degraded1')
        nlcd_plt_hgt = maximum(nlcd_plt_hgt, min_val)

        ksat = tif_to_array(root, 'Soil_Ksat_15apr')
        ksat = maximum(ksat, min_val)

        tew = tif_to_array(root, 'tew_250_15apr')
        tew = maximum(tew, min_val)

        self._qDeps = qDeps
        self._taw = aws
        self._nlcd_rt_z = nlcd_rt_z
        self._nlcd_plt_hgt = nlcd_plt_hgt
        self._ksat = ksat
        self._tew = tew

        self._min_val = min_val
        self._shape = aws.shape

    def load_array_results(self):
        """

        :return:
        """
        root = self._array_results_root

        tag = '4_19_23_11'
        de1 = tif_to_array(root, 'de_{}'.format(tag))
        de1 = clean(de1)
        self._de = de1

        dr1 = tif_to_array(root, 'dr_{}'.format(tag))
        dr1 = clean(dr1)
        self._dr = dr1

        drew = tif_to_array(root, 'drew_{}'.format(tag))
        drew = clean(drew)
        self._drew = drew

    def calculate_ndvi_2000(self, doy):
        """

        :param doy:
        :return:
        """
        base_name = 'T{:03n}_{:03n}_2000_etrf_subset_001_048_ndvi_daily'
        if doy < 49:
            a = 1
            b = 48
            name = base_name.format(a, b)
            if self._verbose:
                logging.debug('calculate 1 {}'.format(name))
            ndvi = tif_to_array(self._ndvi_root, name, band=doy)
        else:
            obj = [1, 49, 81, 113, 145, 177, 209, 241, 273, 305, 337]

            idx = next((num for num in obj[1:] if 0 <= doy - num <= 31))

            diff = doy - idx
            offset = 29 if idx == 337 else 31

            strt = idx
            nd = idx + offset

            name = base_name.format(strt, nd)
            if self._verbose:
                logging.debug('calculate 2 {}'.format(name))

            ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)

        return ndvi

    def calculate_ndvi_2001(self, doy):
        """

        :param doy:
        :return:
        """
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        idx = next((num for num in obj[1:] if 0 <= doy - num <= 15))

        diff = doy - idx
        offset = 12 if idx == 353 else 15

        strt = idx
        nd = idx + offset

        name = '2001_{}_{}'.format(strt, nd)
        if self._verbose:
            logging.debug('calculate 3 {}'.format(name))

        ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)
        return ndvi

    def calculate_ndvi(self, year, doy):
        """

        :param year:
        :param doy:
        :return:
        """
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        idx = next((num for num in obj[1:] if 0 <= doy - num <= 15))

        diff = doy - idx
        name = '{}_{}'.format(year, obj.index(idx) + 1)
        if self._verbose:
            logging.debug('calculate 4 {}'.format(name))

        ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)
        return ndvi


if __name__ == '__main__':
    e = ETRM()
    config = '../example_configuration.yml'
    e.run(config, verbose=True)

# ============= EOF =============================================
