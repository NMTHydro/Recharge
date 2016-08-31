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
The purpose of this module is update the etrm master dict daily.  It should work for both point and
distributed model runs

returns dict with all rasters under keys of etrm variable names

dgketchum 24 JUL 2016
"""

from numpy import ones, zeros, maximum, minimum, where, isnan, exp
from datetime import datetime, timedelta
from dateutil import rrule

from recharge.dict_setup import initialize_master_dict, initialize_static_dict, initialize_initial_conditions_dict,\
    initialize_tracker, set_constants
from recharge.raster_manager import ManageRasters
from recharge.raster_finder import get_penman, get_prism, get_ndvi


class Processes(object):

    _tracker = None

    def __init__(self, static_inputs=None, initial_inputs=None, point_dict=None, raster_point=None):

        self._raster = ManageRasters()

        self._raster_point = raster_point

        self._point_dict = point_dict
        self._outputs = ['cum_ref_et', 'cum_eta', 'cum_precip', 'cum_ro', 'tot_snow']
        self._output_an = {}
        self._output_mo = {}
        self._last_mo = {}
        self._last_yr = {}
        for key in self._outputs:
            self._output_an.update({key: []})
            self._output_mo.update({key: []})
            self._last_mo.update({key: []})
            self._last_yr.update({key: []})

        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered
        self._constants = set_constants()

        if point_dict:
            self._static = initialize_static_dict(static_inputs, point_dict)
            print 'intitialized static dict:\n{}'.format(self._static)
            self._initial = initialize_initial_conditions_dict(initial_inputs, point_dict)
            print 'intitialized initial conditions dict:\n{}'.format(self._initial)

        else:
            self._static = initialize_static_dict(static_inputs)
            self._initial = initialize_initial_conditions_dict(initial_inputs)

        self._shape = self._static['taw'].shape
        self._master = initialize_master_dict()

        if point_dict:
            self._zeros, self._ones = 0.0, 1.0
        else:
            self._ones, self._zeros = ones(self._shape), zeros(self._shape)

    def run(self, date_range, out_pack=None, ndvi_path=None, prism_path=None, penman_path=None,
            point_dict=None):

        m = self._master
        s = self._static
        c = self._constants
        _zeros = self._zeros
        start_date, end_date = date_range
        start_monsoon, end_monsoon = c['s_mon'], c['e_mon']
        start_time = datetime.now()
        print 'start time :{}'.format(start_time)
        for day in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
            if not point_dict:
                print "Time : {a} day {b}_{c}".format(a=str(datetime.now() - start_time),
                                                      b=day.timetuple().tm_yday, c=day.year)

            if day == start_date:
                m['ke'] = 0.5
                m['ks'] = 0.5
                m['kr'] = 0.5
                m['pkcb'] = _zeros
                m['tot_mass'] = _zeros
                m['cum_mass'] = _zeros
                m['albedo'] = 0.45
                m['swe'] = _zeros  # this should be initialized correctly using simulation results
                rew = minimum((2 + (s['tew'] / 3.)), 0.8 * s['tew'])
                s.update({'rew': rew})
                m['pdr'] = self._initial['dr']
                m['pde'] = self._initial['de']
                m['pdrew'] = self._initial['drew']
                m['dr'] = m['pdr']
                m['de'] = m['pde']
                m['drew'] = m['pdrew']

            if self._point_dict:
                self._do_daily_point_load(point_dict, day)
            else:
                self._do_daily_raster_load(ndvi_path, prism_path, penman_path, day)

            if start_monsoon.timetuple().tm_yday <= day.timetuple().tm_yday <= end_monsoon.timetuple().tm_yday:
                s['soil_ksat'] = s['soil_ksat'] * 2 / 24.
            else:
                s['soil_ksat'] = s['soil_ksat'] * 6 / 24.

            self._do_dual_crop_coefficient()

            self._do_snow()

            self._do_soil_water_balance(day)

            self._do_mass_balance()

            if day == start_date:
                self._tracker = initialize_tracker(self._master)

            if not point_dict:
                self._raster.update_save_raster(m, self._output_an, self._output_mo, self._last_yr,
                                                self._last_mo, self._outputs, day, out_pack, save_dates=None,
                                                save_outputs=None)
                if self._raster_point:
                    self._update_point_tracker(day, self._raster_point)

            else:
                self._update_point_tracker(day)

            if point_dict and day == end_date:
                return self._tracker

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

        plant_exponent = s['plant_height'] * 0.5 + 1
        numerator_term = maximum(m['kcb'] - c['kc_min'], _ones * 0.001)
        denominator_term = maximum((c['kc_max'] - c['kc_min']), _ones * 0.001)
        cover_fraction_unbound = (numerator_term / denominator_term) ** plant_exponent
        cover_fraction_upper_bound = minimum(cover_fraction_unbound, _ones)
        cover_fraction = maximum(cover_fraction_upper_bound, _ones * 0.001)
        uncovered_fraction = maximum(1 - cover_fraction, 0.01)
        m['pke'] = m['ke']
        m['pks'] = m['ks']
        m['pkr'] = m['kr']

        if self._point_dict:

            ####
            # transpiration
            if ((s['taw'] - m['pdr']) / (0.6 * (s['taw']) - m['tew'] - m['rew'])) < _ones:
                ks_ref = _ones * 0.001
            else:
                ks_ref = ((s['taw'] - m['pdr']) / ((1 - c['p']) * s['taw']))
            m['ks'] = minimum(ks_ref, _ones)
            m['transp'] = (m['ks'] * m['kcb']) * m['etrs']

            ####
            # check for stage 1 evaporation, i.e. drew < rew
            # this evaporation rate is limited only by available energy
            k_stage_one = (s['rew'] - m['drew']) / (c['ke_max'] * m['etrs'])
            k_stage_one = minimum(k_stage_one, _ones)
            m['k_stage_one'] = maximum(k_stage_one, _zeros)
            if m['drew'] < s['rew']:
                m['ke'] = min((m['k_stage_one'] + (1 - m['k_stage_one']) * m['kr']) * (c['kc_max'] - m['ks'] * m['kcb']),
                              uncovered_fraction * c['kc_max'])
                evap_init = m['ke'] * m['etrs']
                m['evap'] = maximum(evap_init, _zeros)

            ####
            # if rew == drew, stage 1 evaporation is over, and stage 2 continues at a slower rate
            else:
                m['kr'] = minimum(((s['tew'] - m['de']) / (s['tew'] - s['rew'])), _ones)
                if isnan(m['kr']):
                    m['kr'] = m['pkr']




        else:
            pkr = m['kr']
            kr = minimum(((s['tew'] - m['de']) / (s['tew'] - s['rew'])), _ones)
            kr = where(isnan(kr) == True, pkr, kr)

            pks = m['ks']
            ks_ref = where(((s['taw'] - m['pdr']) / (0.6 * s['taw'])) < _ones, _ones * 0.001,
                           (s['taw'] - m['pdr']) / ((1 - c['p']) * s['taw']))
            ks_ref = where(isnan(m['ks']) == True, pks, ks_ref)

            k_stage_one = where(isnan((s['rew'] - m['drew']) / (c['ke_max'] * m['etrs'])) == True, _zeros,
                                (s['rew'] - m['drew']) / (c['ke_max'] * m['etrs']))
            k_stage_one = minimum(k_stage_one, _ones)
            m['k_stage_one'] = maximum(k_stage_one, _zeros)
            m['ke'] = where(m['drew'] < s['rew'], minimum((m['k_stage_one'] + (1 - m['k_stage_one']) * kr) * (c['kc_max'] - m['ks'] * m['kcb']),
                                                     uncovered_fraction * c['kc_max']), _zeros)


        et_init = (m['ks'] * m['kcb'] + m['ke']) * m['etrs']
        m['eta'] = maximum(et_init, _zeros)

        # m['evap'] = minimum(evap_min, c['kc_max'])  ## where did this mistake come from???

    def _do_snow(self):
        m = self._master
        c = self._constants
        _ones = self._ones
        _zeros = self._zeros

        temp = m['temp']
        palb = m['albedo']

        if self._point_dict:
            if temp < 0.0 < m['ppt']:
                # print 'producing snow fall'
                m['snow_fall'] = m['ppt']
                m['rain'] = 0.0
            else:
                m['rain'] = m['ppt']
                m['snow_fall'] = 0.0

            if m['snow_fall'] > 3.0:
                # print 'snow: {}'.format(m['snow_fall'])
                m['albedo'] = c['a_max']
            elif 0.0 < m['snow_fall'] < 3.0:
                # print 'snow: {}'.format(m['snow_fall'])
                m['albedo'] = c['a_min'] + (palb - c['a_min']) * exp(-0.12)
            else:
                m['albedo'] = c['a_min'] + (palb - c['a_min']) * exp(-0.05)

            if m['albedo'] < c['a_min']:
                m['albedo'] = c['a_min']
        else:
            m['snow_fall'] = where(temp < 0.0, m['ppt'], _zeros)
            m['rain'] = where(temp >= 0.0, m['ppt'], _zeros)
            alb = where(m['snow_fall'] > 3.0, _ones * c['a_max'], palb)
            alb = where(m['snow_fall'] <= 3.0, c['a_min'] + (palb - c['a_min']) * exp(-0.12), alb)
            alb = where(m['snow_fall'] == 0.0, c['a_min'] + (palb - c['a_min']) * exp(-0.05), alb)
            alb = where(alb < c['a_min'], c['a_min'], alb)
            m['albedo'] = alb

        m['swe'] += m['snow_fall']

        mlt_init = maximum(((1 - m['albedo']) * m['rg'] * c['snow_alpha']) + (temp - 1.8) * c['snow_beta'], _zeros)
        m['mlt'] = minimum(m['swe'], mlt_init)

        m['swe'] -= m['mlt']

    def _do_soil_water_balance(self, date):
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
        ro = where(watr > s['soil_ksat'] + deps, watr - s['soil_ksat'] - deps, ro)
        m['ro'] = maximum(ro, _zeros)

        if self._point_dict:
            dp_r = _zeros
            if watr > deps and s['soil_ksat'] > watr - deps:
                dp_r = max(watr - deps, zeros)
            elif watr > s['soil_ksat'] + deps:
                dp_r = s['soil_ksat']
            m['dp_r'] = max(dp_r, _zeros)

        else:
            dp_r = _zeros
            id1 = where(watr > deps, _ones, _zeros)
            id2 = where(s['soil_ksat'] > watr - deps, _ones, _zeros)
            dp_r = where(id1 + id2 > 1.99, maximum(watr - deps, _zeros), dp_r)
            dp_r = where(watr > s['soil_ksat'] + deps, s['soil_ksat'], dp_r)
            m['dp_r'] = maximum(dp_r, _zeros)

        # it is difficult to ensure mass balance in the following code: do not touch it #
        drew_1 = minimum((m['pdrew'] + (m['evap'] * m['k_stage_one']) - m['rain'] - m['mlt'] + m['ro']), s['rew'])
        m['drew'] = maximum(drew_1, _zeros)
        diff = maximum(m['pdrew'] - m['drew'], _zeros)

        de_1 = m['pde'] + (m['evap'] * (1 - m['k_stage_one'])) - m['rain'] - m['mlt'] - diff
        de_2 = minimum(de_1, s['tew'])
        if de_1 > s['tew']:
            print 'evaporation is over available stage one and two on {}'.format(date)
            m['evap'] -= de_1 - s['tew']
        m['de'] = maximum(de_2, _zeros)
        diff = maximum(((m['pdrew'] - m['drew']) + (m['pde'] - m['de'])), _zeros)

        dr_1 = minimum((m['pdr'] + ((m['transp'] + m['dp_r']) - (m['rain'] + m['mlt'] - diff))), s['taw'])
        m['dr'] = maximum(dr_1, _zeros)

        return None

    def _do_accumulations(self):
        m = self._master
        _ones = self._ones
        _zeros = self._zeros

        m['cum_infil'] += m['dp_r']
        m['cum_infil'] = maximum(m['infil'], _zeros)

        prev_et = m['cum_eta']
        m['cum_ref_et'] += m['etrs']
        m['cum_eta'] = m['cum_eta'] + m['evap'] + m['transp']
        m['et_ind'] = m['cum_eta'] / m['cum_ref_et']
        m['cum_eta'] = where(isnan(m['cum_eta']) == True, prev_et, m['cum_eta'])
        m['cum_eta'] = where(m['cum_eta'] > m['cum_ref_et'], m['cum_ref_et'] / 2., m['cum_eta'])
        m['cum_eta'] = maximum( m['cum_eta'], _ones * 0.001)

        m['cum_precip'] = m['precip'] + m['rain'] + m['snow_fall']
        m['cum_precip'] = maximum(m['precip'], _zeros)

        m['cum_ro'] += m['ro']
        m['cum_ro'] = maximum(m['cum_ro'], _zeros)

        m['cum_swe'] += m['swe']

        m['tot_snow'] += m['snow_fall']

    def _do_mass_balance(self):

        m = self._master
        m['mass'] = m['rain'] + m['mlt'] - (m['ro'] + m['transp'] + m['evap'] + m['dp_r'] +
                                            ((m['pdr'] - m['dr']) + (m['pde'] - m['de']) +
                                            (m['pdrew'] - m['drew'])))
        m['tot_mass'] += abs(m['mass'])
        m['cum_mass'] += m['mass']

    def _update_point_tracker(self, date, raster_point=None):

        m = self._master

        master_keys_sorted = m.keys()
        master_keys_sorted.sort()
        # print 'master keys sorted: {}, length {}'.format(master_keys_sorted, len(master_keys_sorted))
        tracker_from_master = [m[key] for key in master_keys_sorted]
        # print 'tracker from master, list : {}, length {}'.format(tracker_from_master, len(tracker_from_master))

        # remember to use loc. iloc is to index by integer, loc can use a datetime obj.
        if raster_point:
            list_ = []
            for item in tracker_from_master:
                list_.append(item[raster_point])
            self._tracker.loc[date] = list_

        else:
            # print 'master: {}'.format(m)
            self._tracker.loc[date] = tracker_from_master

    def _do_daily_raster_load(self, ndvi_path, prism_path, penman_path, date):

        m = self._master

        m['pkcb'] = m['kcb']
        m['kcb'] = get_ndvi(ndvi_path, m['pkcb'], date)
        self._print_check(m['kcb'], 'daily kcb')
        m['min_temp'] = get_prism(prism_path, date, variable='min_temp')
        self._print_check(m['min_temp'], 'daily min_temp')
        m['max_temp'] = get_prism(prism_path, date, variable='max_temp')
        self._print_check(m['max_temp'], 'daily max_temp')
        m['temp'] = (m['min_temp'] + m['max_temp']) / 2
        self._print_check(m['temp'], 'daily temp')
        m['ppt'], m['ppt_tom'] = get_prism(prism_path, date, variable='precip')
        self._print_check(m['ppt'], 'daily ppt')
        m['etrs'] = get_penman(penman_path, date, variable='etrs')
        self._print_check(m['etrs'], 'daily etrs')
        m['rg'] = get_penman(penman_path, date, variable='rg')
        self._print_check(m['rg'], 'daily rg')
        return None

    def _do_daily_point_load(self, point_dict, date):
        m = self._master
        ts = point_dict['etrm']
        m['kcb'] = ts['kcb'][date]
        m['min_temp'] = ts['min temp'][date]
        m['max_temp'] = ts['max temp'][date]
        m['temp'] = (m['min_temp'] + m['max_temp']) / 2
        m['ppt'], m['ppt_tom'] = ts['precip'][date], ts['precip'][date + timedelta(days=1)]
        m['etrs'] = ts['etrs_pm'][date]
        m['rg'] = ts['rg'][date]

    def _cells(self, raster):
        return raster[480:485, 940:945]

    def _print_check(self, variable, category):
        print 'raster is {}'.format(category)
        print 'example values from data: {}'.format(self._cells(variable))
        print ''

# ============= EOF =============================================
