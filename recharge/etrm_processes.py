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
import os
from datetime import datetime
from dateutil import rrule

from recharge.master_dict import initialize_master_dict
from recharge.user_constants import set_constants
from recharge.raster_manager import ManageRasters
from recharge.raster_finder import get_penman, get_prism, get_ndvi


class Processes(object):

    def __init__(self, static_inputs, initial_inputs):

        self._raster = ManageRasters()

        outputs = ['cum_ref_et', 'cum_et', 'cum_precip', 'cum_ro', 'cur_swe', 'tot_snow']
        self._output_an = {}
        self._output_mo = {}
        for key in outputs:
            self._output_an.update({key: []})
            self._output_mo.update({key: []})

        # build list of static rasters from current use file
        statics = [filename for filename in os.listdir(static_inputs) if filename.endswith('.tif')]
        statics = sorted(statics, key=lambda s: s.lower())
        # convert rasters to arrays
        static_arrays = [self._raster.convert_raster_to_array(static_inputs, filename) for filename in statics]
        # give variable names to each raster
        static_keys = ['bedksat', 'plant_height', 'quat_deposits', 'root_z', 'soilksat', 'taw', 'tew']
        static = {}
        for key, data in zip(static_keys, static_arrays):
            self._print_check(key, 'static')
            static.update({key: data})

        self._shape = static['taw'].shape

        # read in initial soil moisture conditions from spin up, put in dict
        initial_cond = [filename for filename in os.listdir(initial_inputs) if filename.endswith('.tif')]
        initial_cond.sort()
        initial_cond_arrays = [self._raster.convert_raster_to_array(initial_inputs, filename) for filename in statics]
        initial_cond_keys = ['de', 'dr', 'drew']
        initial_cond_dict = {}
        for key, data in zip(initial_cond_keys, initial_cond_arrays):
            self._print_check(key, 'initial conditions')
            initial_cond_dict.update({key: data})

        # Create indices to plot point time series, these are empty lists that will
        # be filled as the simulation progresses
        tracker = {}
        tracker_keys = ['rain', 'eta', 'snowfall', 'runoff', 'dr', 'pdr', 'de', 'pde', 'drew',
                        'pdrew', 'temp', 'max_temp', 'recharge', 'ks', 'pks', 'etrs', 'kcb', 'ke', 'pke', 'melt',
                        'swe', 'fs1', 'precip', 'kr', 'pkr', 'mass']
        for key in tracker_keys:
            tracker.update({key: []})

        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered
        constants = set_constants(soil_evap_depth=40, et_depletion_factor=0.4, min_basal_crop_coef=0.15,
                                  max_ke=1.0, min_snow_albedo=0.45, max_snow_albedo=0.90)

        empty_array_list = ['albedo', 'cum_eta', 'cur_swe', 'de', 'dp_r', 'dr', 'drew', 'et_ind', 'eta', 'etrs', 'evap',
                            'fs1', 'infil', 'kcb', 'kr', 'ks', 'max_temp', 'min_temp', 'pde', 'pdr', 'pdrew', 'pkr',
                            'pks', 'ppt', 'precip', 'rain', 'rg', 'runoff', 'snow_fall', 'swe', 'temp', 'transp']

        master = initialize_master_dict(empty_array_list, self._shape)

        self._ones = ones(self._shape)
        self._zeros = zeros(self._shape)

        self._master = master
        self._static = static
        self._initial_conditions = initial_cond_dict
        self._constants = constants

    def run(self, start_date, end_date, ndvi_path, prism_path, penman_path, start_monsoon, end_monsoon):
        m = self._master
        s = self._static

        start_time = datetime.now()
        print start_time
        for day in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
            print "Time : {a} day {b}_{c}".format(a=str(datetime.datetime.now() - start_time),
                                                  b=day.timetuple().tm_yday, c=day.year)

            if day != start_date:
                pkcb = m['kcb']
            m['kcb'] = get_ndvi(ndvi_path, pkcb, self._shape)
            self._print_check(m['kcb'], 'daily kcb')
            m['min_temp'] = get_prism(prism_path, day, variable='min_temp')
            self._print_check(m['min_temp'], 'daily min_temp')
            m['max_temp'] = get_prism(prism_path, day, variable='max_temp')
            self._print_check(m['max_temp'], 'daily max_temp')
            m['temp'] = (m['min_temp'] + m['max_temp']) / 2
            self._print_check(m['temp'], 'daily temp')
            m['ppt'] = get_prism(prism_path, day, variable='precip')
            self._print_check(m['ppt'], 'daily ppt')
            m['etrs'] = get_penman(penman_path, day, variable='etrs')
            self._print_check(m['etrs'], 'daily etrs')
            m['rg'] = get_penman(penman_path, day, variable='rg')
            self._print_check(m['rg'], 'daily rg')

            if day == start_date:

                rew = minimum((2 + (s['tew'] / 3.)), 0.8 * s['tew'])
                m.update({'rew': rew})
                #  should have all these from previous model runs
                m['pdr'] = self._initial_conditions['dr']
                m['pde'] = self._initial_conditions['de']
                m['pdrew'] = self._initial_conditions['drew']
                dr = m['pdr']
                de = m['pde']
                drew = m['pdrew']

            if start_monsoon.timetuple().tm_yday <= day.timetuple().tm_yday <= end_monsoon.timetuple().tm_yday:
                s['ksat'] = s['ksat'] * 2 / 24.
            else:
                s['ksat'] = s['ksat'] * 6 / 24.

            self._do_dual_crop_coefficient()

            self._do_snowmelt()

            self._do_soil_moisture_depletion()

            self._raster.update(m)

            self._raster.save_raster(m, day)

    def get_master(self):
        """
        get the master dictionary
        :return: master dictionary
        :rtype: dict
        """
        return self._master

    def _do_dual_crop_coefficient(self):
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

    def _do_snowmelt(self):
        m = self._master
        c = self._constants
        _ones = self._ones
        _zeros = self._zeros

        temp = m['temp']

        m['snow_fall'] = where(temp <= 0.0, m['ppt'], _zeros)
        m['rain'] = where(temp >= 0.0, m['ppt'], _zeros)

        palb = m['albedo']

        alb = where(m['snow_fall'] > 3.0, _ones * c['a_max'], palb)
        alb = where(m['snow_fall'] <= 3.0, c['a_min'] + (palb - c['a_min']) * exp(-0.12), alb)
        alb = where(m['snow_fall'] == 0.0, c['a_min'] + (palb - c['a_min']) * exp(-0.05), alb)
        m['albedo'] = alb = where(alb < c['a_min'], c['a_min'], alb)

        m['swe'] += m['snow_fall']

        mlt_init = maximum(((1 - alb) * m['rg'] * 0.2) + (temp - 1.8) * 11.0, _zeros)
        m['mlt'] = minimum(m['swe'], mlt_init)

        m['swe'] -= m['mlt']

    def _do_soil_moisture_depletion(self):
        m = self._master
        s = self._static
        _ones = self._ones
        _zeros = self._zeros

        m['pdr'] = m['dr']
        m['pde'] = m['de']
        m['pdrew'] = m['drew']

        watr = m['rain'] + m['mlt']
        deps = m['dr'] + m['de'] + m['drew']

        ro = _zeros
        ro = where(watr > m['ksat'] + deps, watr - m['ksat'] - deps, ro)
        m['ro'] = maximum(ro, _zeros)

        dp_r = _zeros
        id1 = where(watr > deps, _ones, _zeros)
        id2 = where(m['ksat'] > watr - deps, _ones, _zeros)
        dp_r = where(id1 + id2 > 1.99, maximum(watr - deps, _zeros), dp_r)
        dp_r = where(watr > m['ksat'] + deps, m['ksat'], dp_r)
        m['dp_r'] = maximum(dp_r, _zeros)

        drew_1 = minimum((m['pdrew'] + m['ro'] + (m['evap'] - (m['rain'] + m['mlt']))),
                         s['rew'])
        m['drew'] = maximum(drew_1, _zeros)
        diff = maximum(m['pdrew'] - m['drew'], _zeros)

        de_1 = minimum(
            (m['pde'] + (m['evap'] - (m['rain'] + m['mlt'] - diff))),
            s['tew'])
        m['de'] = maximum(de_1, _zeros)
        diff = maximum(((m['pdrew'] - m['drew']) + (m['pde'] - m['de'])),
                       _zeros)

        dr_1 = minimum((m['pdr'] + ((m['transp'] + m['dp_r']) - (m['rain'] + m['mlt'] - diff))),
                       s['taw'])
        m['dr'] = maximum(dr_1, _zeros)
        # dr = (pdr + dr_2) / 2.

        return None

    def _do_accumulations(self):
        m = self._master
        _ones = self._ones
        _zeros = self._zeros

        m['cum_infil'] += m['dp_r']
        m['cum_infil'] = maximum(m['infil'], _zeros)

        prev_et = m['cum_et']
        m['cum_ref_et'] += m['etrs']
        m['cum_et'] = m['cum_et'] + m['evap'] + m['transp']
        m['et_ind'] = m['cum_et'] / m['cum_ref_et']
        m['cum_et'] = where(isnan(m['cum_et']) == True, prev_et, m['cum_et'])
        m['cum_et'] = where(m['cum_et'] > m['cum_ref_et'], m['cum_ref_et'] / 2., m['cum_et'])
        m['cum_et'] = maximum( m['cum_et'], _ones * 0.001)

        m['cum_precip'] = m['precip'] + m['rain'] + m['snow_fall']
        m['cum_precip'] = maximum(m['precip'], _zeros)

        m['cum_ro'] += m['ro']
        m['cum_ro'] = maximum(m['cum_ro'], _zeros)

        m['cur_swe'] = m['swe'] + m['snow_fall'] - m['mlt']
        m['cur_swe'] = maximum(m['cur_swe'], _zeros)

        m['tot_snow'] += m['snow_fall']

    def do_mass_balance(self):

        m = self._master
        m['mass'] = m['rain'] +m['mlt'] - (m['ro'] + m['transp'] + m['evap'] + m['dp_r'] +
                                           ((m['pdr'] - m['dr']) + (m['pde'] - m['de']) +
                                            (m['pdrew'] - m['drew'])))
        m['tot_mass'] += abs(m['mass'])
        m['cum_mass'] += m['mass']

    def _cells(self, raster):
        window = raster[480:485, 940:945]
        return window

    def _print_check(self, variable, category):
        print 'raster is {}'.format(category)
        print 'example values from data: {}'.format(self._cells(variable))
        print ''
# ============= EOF =============================================
