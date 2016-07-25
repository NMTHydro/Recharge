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
"""
The purpose of this module is update the etrm master dict daily.

returns dict with all rasters under keys of etrm variable names

dgketchum 24 JUL 2016
"""

from numpy import ones, zeros, maximum, minimum, where, isnan, exp

from recharge.master_dict import initialize_master_dict
from recharge.user_constants import set_constants


class Processes(object):
    def __init__(self, static_dictionary, raster_shape):
        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered
        constants = set_constants(soil_evap_depth=40, et_depletion_factor=0.4, min_basal_crop_coef=0.15,
                                  max_ke=1.0, min_snow_albedo=0.45, max_snow_albedo=0.90)

        empty_array_list = ['albedo', 'de', 'dp_r', 'dr', 'drew', 'eta', 'etrs', 'evap', 'fs1', 'infil', 'kcb',
                            'kr', 'ks', 'max_temp', 'min_temp', 'pde', 'pdr', 'pdrew', 'pkr', 'pks', 'ppt',
                            'precip', 'rg', 'runoff', 'swe', 'temp', 'transp']

        master = initialize_master_dict(empty_array_list, raster_shape)

        self._ones = ones(raster_shape)
        self._zeros = zeros(raster_shape)

        self._master = master
        self._static = static_dictionary
        self._constants = constants

    def get_master(self):
        """
        get the master dictionary
        :return: master dictionary
        :rtype: dict
        """
        return self._master

    def do_dual_crop_coefficient(self):
        """
        calculate dual crop coefficient

        :return:
        """

        m = self._master
        s = self._static
        c = self._constants
        _ones = self._ones
        _zeros = self._zeros

        nlcd_plt_hgt = s['plant_height'] * 0.5 + 1
        numr = maximum(m['kcb'] - c['kc_min'], _ones * 0.001)
        denom = maximum((c['kc_max'] - c['kc_min']), _ones * 0.001)
        fcov_ref = (numr / denom) ** nlcd_plt_hgt
        fcov_min = minimum(fcov_ref, _ones)
        fcov = maximum(fcov_min, _ones * 0.001)
        few = maximum(1 - fcov, 0.01)  # exposed ground

        pkr = m['kr']
        kr = minimum(((s['tew'] - m['de']) / (s['tew'] - s['rew'])), _ones)
        kr = where(isnan(kr) == True, pkr, kr)

        pks = m['ks']
        ks_ref = where(((s['taw'] - m['pdr']) / (0.6 * s['taw'])) < _ones, _ones * 0.001,
                       ((s['taw'] - m['pdr']) / ((1 - c['p']) * s['taw'])))
        ks_ref = where(isnan(m['ks']) == True, pks, ks_ref)
        m['ks'] = minimum(ks_ref, _ones)

        # Ke evaporation reduction coefficient; stage 1 evaporation
        fsa = where(isnan((s['rew'] - m['drew']) / (c['ke_max'] * m['etrs'])) == True, _zeros,
                    (s['rew'] - m['drew']) / (c['ke_max'] * m['etrs']))
        fsb = minimum(fsa, _ones)
        fs1 = maximum(fsb, _zeros)
        ke = where(m['drew'] < s['rew'], minimum((fs1 + (1 - fs1) * kr) * (c['kc_max'] - m['ks'] * m['kcb']),
                                                 few * c['kc_max']), _zeros)

        m['transp'] = (m['ks'] * m['kcb']) * m['etrs']
        et_init = (m['ks'] * m['kcb'] + ke) * m['etrs']
        m['eta'] = maximum(et_init, _zeros)
        evap_init = ke * m['etrs']
        evap_min = maximum(evap_init, _zeros)
        m['evap'] = minimum(evap_min, c['kc_max'])

    def do_snowmelt(self):
        m = self._master
        c = self._constants
        _ones = self._ones
        _zeros = self._zeros

        temp = m['temp']

        snow_fall = where(temp <= 0.0, m['ppt'], _zeros)
        m['rain'] = where(temp >= 0.0, m['ppt'], _zeros)

        palb = m['albedo']

        alb = where(snow_fall > 3.0, _ones * c['a_max'], palb)
        alb = where(snow_fall <= 3.0, c['a_min'] + (palb - c['a_min']) * exp(-0.12), alb)
        alb = where(snow_fall == 0.0, c['a_min'] + (palb - c['a_min']) * exp(-0.05), alb)
        m['albedo'] = alb = where(alb < c['a_min'], c['a_min'], alb)

        # m['albedo'] = where(snow_fall > 3.0, _ones * c['a_max'], m['albedo'])
        # m['albedo'] = where(snow_fall <= 3.0, c['a_min'] + (palb - c['a_min']) * exp(-0.12), m['albedo'])
        # m['albedo'] = where(snow_fall == 0.0, c['a_min'] + (palb - c['a_min']) * exp(-0.05), m['albedo'])
        # m['albedo'] = where(m['albedo'] < c['a_min'], c['a_min'], m['albedo'])

        m['swe'] += snow_fall

        mlt_init = maximum(((1 - alb) * m['rg'] * 0.2) + (temp - 1.8) * 11.0, _zeros)
        mlt = minimum(m['swe'], mlt_init)

        m['swe'] -= mlt

    def do_soil_moisture_depletion(self):
        self._master['pdr'] = self._master['dr']
        self._master['pde'] = self._master['de']
        self._master['pdrew'] = self._master['drew']

        watr = self._master['rain'] + self._master['mlt']
        deps = self._master['dr'] + self._master['de'] + self._master['drew']

        ro = self._zeros
        ro = where(watr > self._master['ksat'] + deps, watr - self._master['ksat'] - deps, ro)
        self._master['ro'] = maximum(ro, self._zeros)

        dp_r = self._zeros
        id1 = where(watr > deps, self._ones, self._zeros)
        id2 = where(self._master['ksat'] > watr - deps, self._ones, self._zeros)
        dp_r = where(id1 + id2 > 1.99, maximum(watr - deps, self._zeros), dp_r)
        dp_r = where(watr > self._master['ksat'] + deps, self._master['ksat'], dp_r)
        self._master['dp_r'] = maximum(dp_r, self._zeros)

        drew_1 = minimum((self._master['pdrew'] + self._master['ro'] + (
        self._master['evap'] - (self._master['rain'] + self._master['mlt']))),
                         s['rew'])
        drew = maximum(drew_1, self._zeros)
        diff = maximum(self._master['pdrew'] - self._master['drew'], self._zeros)

        de_1 = minimum(
            (self._master['pde'] + (self._master['evap'] - (self._master['rain'] + self._master['mlt'] - diff))),
            self._static['tew'])
        self._master['de'] = maximum(de_1, self._zeros)
        diff = maximum(((self._master['pdrew'] - self._master['drew']) + (self._master['pde'] - self._master['de'])),
                       self._zeros)

        dr_1 = minimum((self._master['pdr'] + (
        (self._master['transp'] + self._master['dp_r']) - (self._master['rain'] + self._master['mlt'] - diff))),
                       self._static['taw'])
        self._master['dr'] = maximum(dr_1, self._zeros)
        # dr = (pdr + dr_2) / 2.

        return None

    def do_accumulations(self):
        self._master['infil'] += self._master['dp_r']
        self._master['infil'] = maximum(self._master['infil'], self._zeros)

        prev_et = self._master['et']
        self._master['cum_ref_et'] += self._master['etrs']
        self._master['eta'] = et + evap + transp
        et_ind = et / ref_et
        et = where(isnan(et) == True, prev_et, et)
        et = where(et > ref_et, ref_et / 2., et)
        et = maximum(et, ones_shaped * 0.001)

        precip = precip + rain + snow_fall
        precip = maximum(precip, zeros_shaped)

        runoff += ro
        runoff = maximum(runoff, zeros_shaped)

        snow_ras = swe + snow_fall - mlt
        snow_ras = maximum(snow_ras, zeros_shaped)

        tot_snow += snow_fall

# ============= EOF =============================================
