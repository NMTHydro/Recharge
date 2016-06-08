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

# ============= standard library imports ========================
import calendar
from math import isnan
from numpy import array, ones, where, zeros
from numpy.ma import maximum, minimum, exp
from osgeo import gdal
from dateutil import rrule
from datetime import datetime, timedelta
import os

# ============= local library imports  ==========================

# Modified from ETRM_distributed/ETRM_savAnMo_5MAY16.py
# Developed by David Ketchum NMT 2016


YEARS = (2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013)
KE_MAX = 1.0
S = 480
E = 940


def tif_to_array(root, name, band=1):
    path = os.path.join(root, '{}.tif'.format(name))
    rband = gdal.Open(path).GetRasterBand(band)
    return array(rband.ReadAsArray(), dtype=float)


def clean(d, shape):
    return where(isnan(d) == True, zeros(shape), d)


class ETRM:
    _ndvi_root = 'F:\\ETRM_Inputs\\NDVI\\NDVI_std_all'
    _prism_root = 'F:\\ETRM_Inputs\\PRISM\Precip\\800m_std_all'
    _prism_min_temp_root = 'F:\\ETRM_Inputs\\PRISM\\Temp\\Minimum_standard'
    _prism_max_temp_root = 'F:\\ETRM_Inputs\\PRISM\\Temp\\Maximum_standard'
    _pm_data_root = 'F:\\ETRM_Inputs\\PM_RAD'

    _min_val = None
    _shape = None
    _qDeps = None
    _taw = None
    _nlcd_rt_z = None
    _nlcd_plt_hgt = None
    _ksat = None
    _tew = None
    _dr1 = None
    _de1 = None
    _drew = None

    _verbose = True

    def run(self):

        self._load_current_use()
        self._load_array_results()

        shape = self._shape

        start_time = datetime.datetime.now()
        start = datetime.datetime(2000, 1, 1)
        end = datetime.datetime(2000, 12, 31)
        sMon = datetime.datetime(start.year, 6, 1).timetuple().tm_yday
        eMon = datetime.datetime(start.year, 10, 1).timetuple().tm_yday
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

        days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
        nsteps = len(days)
        pltDay = zeros(nsteps)
        pltRain = zeros(nsteps)
        pltEta = zeros(nsteps)
        pltSnow_fall = zeros(nsteps)
        pltRo = zeros(nsteps)
        pltDr = zeros(nsteps)
        pltDe = zeros(nsteps)
        pltDrew = zeros(nsteps)
        pltTemp = zeros(nsteps)
        pltDp_r = zeros(nsteps)
        pltKs = zeros(nsteps)
        pltPdr = zeros(nsteps)
        pltEtrs = zeros(nsteps)
        pltKcb = zeros(nsteps)
        pltPpt = zeros(nsteps)
        pltKe = zeros(nsteps)
        pltKr = zeros(nsteps)
        pltMlt = zeros(nsteps)
        pltSwe = zeros(nsteps)
        pltTempM = zeros(nsteps)
        pltFs1 = zeros(nsteps)
        pltMass = zeros(nsteps)

        for i, dday in enumerate(days):
            if i > 0:
                pkcb = kcb
            doy = dday.timetuple().tm_yday
            year = dday.year
            month = dday.month
            day = dday.day

            msg = 'Time : {a} day {b}_{c}'.format(datetime.now() - start_time, doy, )
            print msg

            # --------------  kcb -------------------
            if year == 2000:
                ndvi = self._calculate_ndvi_2000(doy)
            elif year == 2001:
                ndvi = self._calculate_ndvi_2001(year, doy)
            else:
                ndvi = self._calculate_ndvi(year)

            kcb = ndvi * 1.25
            kcb = maximum(kcb, self._min_val)
            kcb = where(isnan(kcb) == True, pkcb, kcb)

            # -------------- PRISM -------------------
            prism_base = 'PRISMD2_NMHW2mi_{}{:02n}{:02n}'
            name = prism_base.format(year, month, day)
            ppt = tif_to_array(self._prism_root, name)

            tom = dday + timedelta(days=1)
            name = prism_base.format(year, tom.month, tom.day)
            ppt_tom = tif_to_array(self._prsim_root, name)

            ppt = maximum(ppt, zeros(shape))
            ppt_tom = maximum(ppt_tom, zeros(shape))

            # PRISM to mintemp, maxtemp, temp
            if dday.year in YEARS:
                name = 'cai_tmin_us_us_30s_{}{:02n}{:02n}'.format(year, month, day)
                min_temp = tif_to_array(self._prism_min_temp_root, name)
            else:
                name = 'TempMin_NMHW2Buff_{}{:02n}{:02n}'.format(year, month, day)
                min_temp = tif_to_array(self._prism_min_temp_root, name)

            name = 'TempMax_NMHW2Buff_{}{:02n}{:02n}'.format(year, month, day)
            max_temp = tif_to_array(self._prism_max_temp_root, name)

            temp = (min_temp + max_temp) / 2

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

            tew = self._tew
            taw = self._taw
            if i == 0:
                #  Total evaporable water is depth of water in the evaporable
                #  soil layer, i.e., the water available to both stage 1 and 2 evaporation
                rew = minimum((2 + (tew / 3.)), 0.8 * tew)
                # del tew1, tew2

                # you should have all these from previous model runs
                pDr = self._dr1
                pDe = self._de1
                pDrew = self._drew1
                dr = self._dr1
                de = self._de1
                drew = self._drew1

            nom = 2 if sMon <= doy <= eMon else 6
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
            kr = where(isnan(kr) == True, pKr, kr)

            pKs = ks
            ks_ref = where(((taw - pDr) / (0.6 * taw)) < zeros(shape), ones(shape) * 0.001,
                           ((taw - pDr) / (0.6 * taw)))
            ks_ref = where(isnan(ks) == True, pKs, ks_ref)
            ks = minimum(ks_ref, ones(shape))

            # Ke evaporation reduction coefficient; stage 1 evaporation
            fsa = where(isnan((rew - drew) / (KE_MAX * etrs)) == True, zeros(shape),
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

            snow_fall = where(temp <= 0.0, ppt, zeros(shape))
            rain = where(temp >= 0.0, ppt, zeros(shape))

            pA = a
            a = where(snow_fall > 3.0, ones(shape) * a_max, a)
            a = where(snow_fall <= 3.0, a_min + (pA - a_min) * exp(-0.12), a)
            a = where(snow_fall == 0.0, a_min + (pA - a_min) * exp(-0.05), a)
            a = where(a < a_min, a_min, a)

            swe += snow_fall

            mlt_init = maximum(((1 - a) * rg * 0.2) + (temp - 1.8) * 11.0,
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
                # this needs to be copied from original
                pass

            if day == 31 and month == 12:
                # this needs to be copied from original
                pass

            # Check MASS BALANCE for the love of WATER!!!
            mass = rain + mlt - (ro + transp + evap + dp_r + ((pDr - dr) + (pDe - de) + (pDrew - drew)))
            tot_mass += abs(mass)
            cum_mass += mass

            pltDay[i] = dday

            pltRain[i] = rain[S, E]
            pltEta[i] = eta[S, E]
            pltSnow_fall[i] = snow_fall[S, E]
            pltRo[i] = ro[S, E]
            pltDr[i] = dr[S, E]
            pltDe[i] = de[S, E]
            pltDrew[i] = drew[S, E]
            pltTemp[i] = temp[S, E]
            pltDp_r[i] = dp_r[S, E]
            pltKs[i] = ks[S, E]
            pltPdr[i] = pDr[S, E]
            pltEtrs[i] = etrs[S, E]
            pltKcb[i] = kcb[S, E]
            pltPpt[i] = ppt[S, E]
            pltKe[i] = ke[S, E]
            pltKr[i] = kr[S, E]
            pltMlt[i] = mlt[S, E]
            pltSwe[i] = swe[S, E]
            pltTempM[i] = max_temp[S, E]
            pltFs1[i] = fs1[S, E]
            pltMass[i] = mass[S, E]

    # private
    def _load_current_use(self):
        root = 'C:\\Recharge_GIS\\OSG_Data\\current_use'
        qDeps = tif_to_array(root, 'Q_deps_std')

        min_val = ones(qDeps.shape) * 0.001
        qDeps = maximum(qDeps, min_val)

        aws = tif_to_array(root, 'aws_mod_4_21_10_0')
        aws = maximum(aws, min_val)

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

    def _load_array_results(self):
        shape = self._shape

        root = 'C:\\Recharge_GIS\\Array_Results\\initialize'

        tag = '4_19_23_11'
        de1 = tif_to_array(root, 'de_{}'.format(tag))
        de1 = clean(de1, shape)
        self._de1 = de1

        dr1 = tif_to_array(root, 'dr_{}'.format(tag))
        dr1 = clean(dr1, shape)
        self._dr1 = dr1

        drew = tif_to_array(root, 'drew_{}'.format(tag))
        drew = clean(drew, shape)
        self._drew = drew

    def _calculate_ndvi_2000(self, doy):

        base_name = 'T{:03n}_{:03n}_2000_etrf_subset_001_048_ndvi_daily'
        if doy < 49:
            a = 1
            b = 48
            name = base_name.format(a, b)
            if self._verbose:
                print 'calculate 1 {}'.format(name)
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
                print 'calculate 2 {}'.format(name)

            ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)

        return ndvi

    def _calculate_ndvi_2001(self, year, doy):
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        idx = next((num for num in obj[1:] if 0 <= doy - num <= 15))

        diff = doy - idx
        offset = 12 if idx == 353 else 15

        strt = idx
        nd = idx + offset

        name = '{}_{}_{}'.format(year, strt, nd)
        if self._verbose:
            print 'calculate 3 {}'.format(name)

        ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)
        return ndvi

    def _calculate_ndvi(self, year, doy):
        obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
               225, 241, 257, 273, 289, 305, 321, 337, 353]
        idx = next((num for num in obj[1:] if 0 <= doy - num <= 15))

        diff = doy - idx
        name = '{}_{}'.format(year, obj.index(idx) + 1)
        if self._verbose:
            print 'calculate 4 {}'.format(name)

        ndvi = tif_to_array(self._ndvi_root, name, band=diff + 1)
        return ndvi


if __name__ == '__main__':
    e = ETRM()
    e.run()
# ============= EOF =============================================
