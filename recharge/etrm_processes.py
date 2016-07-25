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


class Processes(object):
    
    def __init__(self, master_dictionary, static_dictionary, constants_dictionary, raster_shape):

        self._ones = ones(raster_shape)
        self._zeros = zeros(raster_shape)
        self._m = master_dictionary
        self._s = static_dictionary
        self._c = constants_dictionary

    def do_dual_crop_coefficient(self):

        nlcd_plt_hgt = self._s['plant_height'] * 0.5 + 1
        numr = maximum(self._m['kcb'] - self._c['kc_min'], self._ones * 0.001)
        denom = maximum((self._c['kc_max'] - self._c['kc_min']), self._ones * 0.001)
        fcov_ref = (numr / denom) ** nlcd_plt_hgt
        fcov_min = minimum(fcov_ref, self._ones)
        fcov = maximum(fcov_min, self._ones * 0.001)
        few = maximum(1 - fcov, 0.01)  # exposed ground

        pkr = self._m['kr']
        kr = minimum(((self._s['tew'] - self._m['de']) / (self._s['tew'] - self._s['rew'])), self._ones)
        kr = where(isnan(kr) == True, pkr, kr)

        pks = self._m['ks']
        ks_ref = where(((self._s['taw'] - self._m['pdr']) / (0.6 * self._s['taw'])) < self._ones, self._ones * 0.001,
                       ((self._s['taw'] - self._m['pdr']) / ((1 - self._c['p']) * self._s['taw'])))
        ks_ref = where(isnan(self._m['ks']) == True, pks, ks_ref)
        self._m['ks'] = minimum(ks_ref, self._ones)

        # Ke evaporation reduction coefficient; stage 1 evaporation
        fsa = where(isnan((self._s['rew'] - self._m['drew']) / (self._c['ke_max'] * self._m['etrs'])) == True, self._zeros,
                    (self._s['rew'] - self._m['drew']) / (self._c['ke_max'] * self._m['etrs']))
        fsb = minimum(fsa, self._ones)
        fs1 = maximum(fsb, self._zeros)
        ke = where(self._m['drew'] < self._s['rew'], minimum((fs1 + (1 - fs1) * kr) * (self._c['kc_max'] - self._m['ks'] * self._m['kcb']),
                                       few * self._c['kc_max']), self._zeros)

        self._m['transp'] = (self._m['ks'] * self._m['kcb']) * self._m['etrs']
        et_init = (self._m['ks'] * self._m['kcb'] + ke) * self._m['etrs']
        self._m['eta'] = maximum(et_init, self._zeros)
        evap_init = ke * self._m['etrs']
        evap_min = maximum(evap_init, self._zeros)
        self._m['evap'] = minimum(evap_min, self._c['kc_max'])

        return None

    def do_snowmelt(self):

        snow_fall = where(self._m['temp'] <= 0.0, self._m['ppt'], self._zeros)
        self._m['rain'] = where(self._m['temp'] >= 0.0, self._m['ppt'], self._zeros)
    
        palb = self._m['albedo']
        self._m['albedo'] = where(snow_fall > 3.0, self._ones * self._c['a_max'], self._m['albedo'])
        self._m['albedo'] = where(snow_fall <= 3.0, self._c['a_min'] + (palb - self._c['a_min']) * exp(-0.12), self._m['albedo'])
        self._m['albedo'] = where(snow_fall == 0.0, self._c['a_min'] + (palb - self._c['a_min']) * exp(-0.05), self._m['albedo'])
        self._m['albedo'] = where(self._m['albedo'] < self._c['a_min'], self._c['a_min'], self._m['albedo'])
    
        self._m['swe'] += snow_fall
    
        mlt_init = maximum(((1 - self._m['albedo']) * self._m['rg'] * 0.2) + (self._m['temp'] - 1.8) * 11.0, self._zeros)
        mlt = minimum(self._m['swe'], mlt_init)

        self._m['swe'] -= mlt

        return None

    def do_soil_moisture_depletion(self):

        self._m['pdr'] = self._m['dr']
        self._m['pde'] = self._m['de']
        self._m['pdrew'] = self._m['drew']

        watr = self._m['rain'] + self._m['mlt']
        deps = self._m['dr'] + self._m['de'] + self._m['drew']

        ro = self._zeros
        ro = where(watr > self._m['ksat'] + deps, watr - self._m['ksat'] - deps, ro)
        self._m['ro'] = maximum(ro, self._zeros)

        dp_r = self._zeros
        id1 = where(watr > deps, self._ones, self._zeros)
        id2 = where(self._m['ksat'] > watr - deps, self._ones, self._zeros)
        dp_r = where(id1 + id2 > 1.99, maximum(watr - deps, self._zeros), dp_r)
        dp_r = where(watr > self._m['ksat'] + deps, self._m['ksat'], dp_r)
        self._m['dp_r'] = maximum(dp_r, self._zeros)

        drew_1 = minimum((self._m['pdrew'] + self._m['ro'] + (self._m['evap'] - (self._m['rain'] + self._m['mlt']))),
                         s['rew'])
        drew = maximum(drew_1, self._zeros)
        diff = maximum(self._m['pdrew'] - self._m['drew'], self._zeros)

        de_1 = minimum((self._m['pde'] + (self._m['evap'] - (self._m['rain'] + self._m['mlt'] - diff))), self._s['tew'])
        self._m['de'] = maximum(de_1, self._zeros)
        diff = maximum(((self._m['pdrew'] - self._m['drew']) + (self._m['pde'] - self._m['de'])), self._zeros)

        dr_1 = minimum((self._m['pdr'] + ((self._m['transp'] + self._m['dp_r']) - (self._m['rain'] + self._m['mlt'] - diff))), self._s['taw'])
        self._m['dr'] = maximum(dr_1, self._zeros)
        # dr = (pdr + dr_2) / 2.

        return None

    def do_accumulations(self):

        self._m['infil'] += self._m['dp_r']
        self._m['infil'] = maximum(self._m['infil'], self._zeros)

        prev_et = self._m['et']
        self._m['cum_ref_et'] += self._m['etrs']
        self._m['eta'] = et + evap + transp
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
