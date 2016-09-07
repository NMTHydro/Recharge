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


from numpy import ones, zeros, maximum, minimum, where, isnan, exp
from datetime import datetime, timedelta
from dateutil import rrule

from recharge.dict_setup import initialize_master_dict, initialize_static_dict, initialize_initial_conditions_dict,\
    initialize_tracker, set_constants
from recharge.raster_manager import ManageRasters
from recharge.raster_finder import get_penman, get_prism, get_ndvi


class Processes(object):
    """
    The purpose of this class is update the etrm master dict daily.  It should work for both point and
    distributed model runs
    See functions for explanations.

    Returns dict with all rasters under keys of etrm variable names.

    dgketchum 24 JUL 2016
    """
    _tracker = None
    _point_dict_key = None

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
            point_dict=None, point_dict_key=None):
        """
        Perform all ETRM functions for each time step, updating master dict and saving data as specified.

        :param date_range:
        :param out_pack:
        :param ndvi_path:
        :param prism_path:
        :param penman_path:
        :param point_dict:
        :param point_dict_key:
        :return:
        """
        self._point_dict_key = point_dict_key
        m = self._master
        s = self._static
        if point_dict:
            s = s[self._point_dict_key]
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
                m['pkcb'] = _zeros
                m['tot_mass'] = _zeros
                m['cum_mass'] = _zeros
                m['albedo'] = 0.45
                m['swe'] = _zeros  # this should be initialized correctly using simulation results
                s['rew'] = minimum((2 + (s['tew'] / 3.)), 0.8 * s['tew'])
                if self._point_dict:
                    m['pdr'] = self._initial[point_dict_key]['dr']
                    m['pde'] = self._initial[point_dict_key]['de']
                    m['pdrew'] = self._initial[point_dict_key]['drew']
                else:
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

            # the soil ksat should be read each day from the static data, then set in the master #
            # otherwise the static is updated and diminishes each day #
            # [mm/day] #
            if start_monsoon.timetuple().tm_yday <= day.timetuple().tm_yday <= end_monsoon.timetuple().tm_yday:
                m['soil_ksat'] = s['soil_ksat'] * 2 / 24.
            else:
                m['soil_ksat'] = s['soil_ksat'] * 6 / 24.

            self._do_dual_crop_coefficient()

            self._do_snow()

            self._do_soil_water_balance()

            self._do_mass_balance()

            if day == start_date:
                self._tracker = initialize_tracker(self._master)

            if not point_dict:
                self._raster.update_save_raster(m, self._output_an, self._output_mo, self._last_yr,
                                                self._last_mo, self._outputs, day, out_pack, save_dates=None,
                                                save_outputs=None)

                self._do_accumulations()

                if self._raster_point:
                    self._update_point_tracker(day, self._raster_point)

            else:
                self._update_point_tracker(day)

            if point_dict and day == end_date:
                self._get_tracker_summary(self._tracker, point_dict_key)

                return self._tracker

    def _do_dual_crop_coefficient(self):
        """ Calculate dual crop coefficients, then transpiration, stage one and stage two evaporations.
        """

        m = self._master
        s = self._static
        if self._point_dict:
            s = s[self._point_dict_key]
        c = self._constants
        _ones = self._ones
        _zeros = self._zeros

        plant_exponent = s['plant_height'] * 0.5 + 1
        numerator_term = maximum(m['kcb'] - c['kc_min'], _ones * 0.001)
        denominator_term = maximum((c['kc_max'] - c['kc_min']), _ones * 0.001)
        cover_fraction_unbound = (numerator_term / denominator_term) ** plant_exponent
        cover_fraction_upper_bound = minimum(cover_fraction_unbound, _ones)
        m['fcov'] = maximum(cover_fraction_upper_bound, _ones * 0.001)  # covered fraction of ground
        m['few'] = maximum(1 - m['fcov'], _ones * 0.001)  # uncovered fraction of ground

        ####
        # transpiration
        m['ks'] = ((s['taw'] - m['pdr']) / ((1 - c['p']) * s['taw']))
        m['ks'] = minimum(m['ks'], _ones + 0.001)
        m['transp'] = m['ks'] * m['kcb'] * m['etrs']
        m['transp'] = maximum(_zeros, m['transp'])

        ####
        # stage 2 coefficient
        m['kr'] = minimum((s['tew'] - m['pde']) / (s['tew'] + s['rew']), _ones)

        ####
        # check for stage 1 evaporation, i.e. drew < rew
        # this evaporation rate is limited only by available energy, and water in the rew
        st_1_dur = (s['rew'] - m['pdrew']) / (c['ke_max'] * m['etrs'])
        st_1_dur = minimum(st_1_dur, _ones)
        m['st_1_dur'] = maximum(st_1_dur, _zeros)
        m['st_2_dur'] = (1 - m['st_1_dur'])

        m['ke_init'] = (m['st_1_dur'] + (m['st_2_dur'] * m['kr'])) * (c['kc_max'] - (m['ks'] * m['kcb']))
        if self._point_dict:
            if m['ke_init'] > m['few'] * c['kc_max']:
                m['adjust_ke'] = 'True'
                m['ke'] = m['few'] * c['kc_max']
                ke_adjustment = m['ke'] / m['ke_init']
            else:
                m['ke'] = m['ke_init']
                m['adjust_ke'] = 'False'
                ke_adjustment = 1.0
        else:
            pass  # distributed
        m['ke'] = minimum(m['ke'], _ones)

        # m['evap'] = m['ke'] * m['etrs']
        m['evap_1'] = m['st_1_dur'] * (c['kc_max'] - m['ks'] * m['kcb']) * m['etrs'] * ke_adjustment
        m['evap_2'] = m['st_2_dur'] * m['kr'] * (c['kc_max'] - (m['ks'] * m['kcb'])) * m['etrs'] * ke_adjustment
        m['evap'] = m['evap_1'] + m['evap_2']

        m['eta'] = m['transp'] + m['evap']

    def _do_snow(self):
        """ Calibrated snow model that runs using PRISM temperature and precipitation.

        The ETRM snow model takes a simple approach to modeling the snow cycle.  PRISM temperature and
        precipitation are used to account for snowfall.  The mean of the maximum and minimum daily temperature
        is found; any precipitation falling during a day when this mean temperature is less than 0 C is assumed
        to be sored as snow.  While other snow-modeling techniques assume that a transition zone exists over
        which the percent of precipitation falling as snow varies over a range of elevation or temperature,
        the ETRM assumes all precipitation on any given day falls either entirely as snow or as rain.
        The storage mechanism in the ETRM simply stores the snow as a snow water equivalent (SWE).
        No attempt is made to model the temporal and spatially-varying density and texture of snow
        during its duration in the snow pack, nor to model the effect the snow has on the underlying soil
        layers.  In the ETRM, ablation of snow by sublimation and the movement of snow by wind is ignored.
        In computing the melting rate of snowpack in above-freezing conditions, a balance has been sought between the
        use of available physical parameters in a simple and computationally efficient model and the representation
        of important physical parameters.  The ETRM uses incident shortwave radiation (Rsw), a modeled albedo with
        a temperature-dependent rate of decay, and air temperature (T air) to find snow melt. Flint and Flint (2008)
        used Landsat images to calibrate their soil water balance model, and found that a melting temperature of 0C
        had to be adjusted to 1.5C to accurately represent the time-varying snowpack in the Southwest United
        States; we have implemented this adjustment in the ETRM.

        melt = (1 - a) * R_sw * alpha + (T_air -  1.5) * beta

        where melt is snow melt (SWE, [mm]), ai is albedo [-], Rsw is incoming shortwave radiation [W m-2], alpha is the
        radiation-term calibration coefficient [-], T is temperature [deg C], and beta is the temperature correlation
        coefficient [-]
        Albedo is computed each time step, is reset following any new snowfall exceeding 3 mm SWE to 0.90, and decays
         according to an equation after Rohrer (1991):

         a(i) = a_min + (a(i-1) - a_min) * f(T_air)

        where a(i) and a(i - 1) are albedo on the current and previous day, respectively, a(min) is the minimum albedo of
        of 0.45 (Wiscombe and Warren: 1980), a(i - 1) is the previous day's albedo, and k is the decay constant. The
        decay  constant varies depending on temperature, after Rohrer (1991).


        :return: None
        """
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

    def _do_soil_water_balance(self):
        """ Calculate all soil water balance at each time step.

        This the most difficult part of the ETRM to maintain.  The function first defines 'water' as all liquid water
        incident on the surface, i.e. rain plus snow melt.  The quantities of vaporized water are then checked against
        the water in each soil layer. If vaporization exceeds available water (i.e. taw - dr < transp), that term
        is reduced and the value is updated.
        The function then performs a soil water balance from the 'top' (i.e., the rew/skin/ stage one evaporation layer)
        of the soil column downwards.  Runoff is calculated as water in excess of soil saturated hydraulic conductivity,
        which has both a summer and winter value at all sites (see etrm_processes.run). The depletion is updated
        according to withdrawls from stage one evaporation and input of water. Water is then
        recalculated before being applied to in the stage two (i.e., tew) layer.  This layer's depletion is then
        updated according only to stage two evaporation and applied water.
        Finally, any remaining water is passed to the root zone (i.e., taw) layer.  Depletion is updated according to
        losses via transpiration and inputs from water.  Water in excess of taw is then allowed to pass below as
        recharge.
        :return: None
        """
        m = self._master
        s = self._static
        _zeros = self._zeros

        water = m['rain'] + m['mlt']

        # it is difficult to ensure mass balance in the following code: do not touch/change w/o testing #
        ##
        if self._point_dict:  # point

            s = s[self._point_dict_key]

            # give days with melt a ksat value for entire day
            if m['rain'] < m['mlt']:
                m['soil_ksat'] = s['soil_ksat']

            # update variables
            m['pdr'] = m['dr']
            m['pde'] = m['de']
            m['pdrew'] = m['drew']

            # impose limits on vaporization according to present depletions #
            # this is a somewhat onerous way to see if evaporations exceed
            # the quantity of  water in that soil layer
            # additionally, if we do limit the evaporation from either the stage one
            # or stage two, we need to reduce the 'evap'
            if m['evap_1'] > s['rew'] - m['drew']:
                m['evap'] -= m['evap_1'] - (s['rew'] - m['drew'])
                m['evap_1'] = s['rew'] - m['drew']
                m['adjust_ev_1'] = 'True'
            else:
                m['adjust_ev_1'] = 'False'

            if m['evap_2'] > s['tew'] - m['de']:
                m['evap'] -= m['evap_2'] - (s['tew'] - m['de'])
                m['evap_2'] = s['tew'] - m['de']
                m['adjust_ev_2'] = 'True'
            else:
                m['adjust_ev_2'] = 'False'

            if m['transp'] > s['taw'] - m['dr']:
                m['transp'] = s['taw'] - m['dr']
                m['adjust_transp'] = 'True'
            else:
                m['adjust_transp'] = 'False'

            # this is where a new day starts in terms of depletions (i.e. pdr vs dr) #
            # water balance through skin layer #
            m['drew_water'] = water
            if water < m['drew'] + m['evap_1']:
                m['ro'] = 0.0
                m['drew'] = m['pdrew'] + m['evap_1'] - water
                if m['drew'] > s['rew']:
                    print 'why is drew greater than rew?'
                    m['drew'] = s['rew']
                water = 0.0
            elif water >= m['drew'] + m['evap_1']:
                m['drew'] = 0.0
                water -= m['pdrew'] + m['evap_1']
                if water > m['soil_ksat']:
                    m['ro'] = water - m['soil_ksat']
                    water = m['soil_ksat']
                    # print 'sending runoff = {}, water = {}, soil ksat = {}'.format(m['ro'], water, m['soil_ksat'])
                else:
                    m['ro'] = 0.0
            else:
                print 'warning: water in rew not calculated'

            # water balance through the stage 2 evaporation layer #
            m['de_water'] = water
            if water < m['de'] + m['evap_2']:
                m['de'] = m['pde'] + m['evap_2'] - water
                if m['de'] > s['tew']:
                    print 'why is de greater than tew?'
                    m['de'] = s['tew']
                water = 0.0
            elif water >= m['pde'] + m['evap_2']:
                m['de'] = 0.0
                water -= m['pde'] + m['evap_2']
                if water > m['soil_ksat']:
                    print 'warning: tew layer has water in excess of its ksat'
                    water = m['soil_ksat']
            else:
                print 'warning: water in tew not calculated'

            # water balance through the root zone #
            m['dr_water'] = water
            if water < m['dr'] + m['transp']:
                m['dp_r'] = 0.0
                m['dr'] = m['pdr'] + m['transp'] - water
                if m['dr'] > s['taw']:
                    print 'why is dr greater than taw?'
                    m['dr'] = s['taw']
            elif water >= m['dr'] + m['transp']:
                m['dr'] = 0.0
                water -= m['pdr'] + m['transp']
                if water > m['soil_ksat']:
                    print 'warning: taw layer has water in excess of its ksat'
                m['dp_r'] = water
            else:
                print 'error calculating deep percolation from root zone'

        else:  # distributed

            m['pdr'] = m['dr']
            m['pde'] = m['de']
            m['pdrew'] = m['drew']

            m['soil_ksat'] = where(m['rain'] < m['mlt'], s['soil_ksat'], m['soil_ksat'])

            # impose limits on vaporization according to present depletions #
            # we can't vaporize more than present difference between current available and limit (i.e. taw - dr) #
            m['evap_1'] = where(m['evap_1'] > s['rew'] - m['drew'], s['rew'] - m['drew'], m['evap_1'])
            m['evap_2'] = where(m['evap_2'] > s['tew'] - m['de'], s['tew'] - m['de'], m['evap_2'])
            m['transp'] = where(m['transp'] > s['taw'] - m['dr'], s['taw'] - m['dr'], m['transp'])

            # water balance through skin layer #
            water = where(water < m['drew'] + m['evap_1'], _zeros, water - m['drew'] - m['evap_1'])
            m['drew'] = where(water >= m['pdrew'] + m['evap_1'], _zeros, m['pdrew'] + m['evap_1'] - water)
            m['drew'] = where(water < m['pdrew'] + m['evap_1'], m['pdrew'] + m['evap'] - water, m['drew'])
            m['ro'] = where(water > m['soil_ksat'], water - m['soil_ksat'], _zeros)
            water = where(water > m['soil_ksat'], m['soil_ksat'], water)

            # water balance through the stage 2 evaporation layer #
            m['de'] = where(water >= m['pde'] + m['evap_2'], _zeros, m['pde'] + m['evap_2'] - water)
            m['de'] = where(water < m['pde'] + m['evap_2'], m['pde'] + m['evap_2'] - water, m['de'])
            water = where(water >= m['pde'] + m['evap_2'], water - m['pde'] - m['evap_2'], water)

            # water balance through the root zone layer #
            m['dp_r'] = where(water >= m['pdr'] + m['transp'], water - m['pdr'] - m['transp'], _zeros)
            m['dr'] = where(water >= m['pdr'] + m['transp'], _zeros, m['pdr'] + m['transp'] - water)
            m['dr'] = where(water < m['pdr'] + m['transp'], m['pdr'] + m['transp'] - water, m['dr'])

        return None

    def _do_accumulations(self):
        """ This function simply accumulates all terms.

        :return: None
        """
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
        m['cum_eta'] = maximum(m['cum_eta'], _ones * 0.001)

        m['cum_precip'] = m['precip'] + m['rain'] + m['snow_fall']
        m['cum_precip'] = maximum(m['precip'], _zeros)

        m['cum_ro'] += m['ro']
        m['cum_ro'] = maximum(m['cum_ro'], _zeros)

        m['cum_swe'] += m['swe']

        m['tot_snow'] += m['snow_fall']

    def _do_mass_balance(self):
        """ Checks mass balance.

        This function is important because mass balance errors indicate a problem in the soil water balance or
        in the dual crop coefficient functions.
        Think of the water balance as occurring at the very top of the soil column.  The only water that comes in
        is from rain and snow melt.  All other terms in the balance are subtractions from the input.  Runoff, recharge,
        transpiration, and stage one and stage two evaporation are subtracted.  Soil water storage change is another
        subtraction.  Remember that if the previous time step's depletion is greater than the current time step
        depletion, the storage change is positive.  Therefore the storage change is subtracted from the inputs of rain
        and snow melt.

        To do: This function is complete.  It will need to be updated with a lateral on and off-flow once that model
        is complete.

        :return:
        """
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
        # need to ensure nonnegative ppt
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
        m['ppt'] = max(m['ppt'], 0.0)
        m['etrs'] = ts['etrs_pm'][date]
        m['rg'] = ts['rg'][date]

    def _cells(self, raster):
        return raster[480:485, 940:945]

    def _get_tracker_summary(self, tracker, name):
        s = self._static[name]
        print 'summary stats for {}:\n{}'.format(name, tracker.describe())
        print 'a look at vaporization:'
        print 'stage one  = {}, stage two  = {}, together = {},  total evap: {}'.format(tracker['evap_1'].sum(),
                                                                                      tracker['evap_2'].sum(),
                                                                                      tracker['evap_1'].sum() +
                                                                                      tracker['evap_2'].sum(),
                                                                                      tracker['evap'].sum())
        print 'total transpiration = {}'.format(tracker['transp'].sum())
        depletions = ['drew', 'de', 'dr']
        capacities = [s['rew'], s['tew'], s['taw']]
        starting_water = sum([x - tracker[y][0] for x, y in zip(capacities, depletions)])
        ending_water = sum([x - tracker[y][-1] for x, y in zip(capacities, depletions)])
        delta_soil_water = ending_water - starting_water
        print 'soil water change = {}'.format(delta_soil_water)
        print 'input precip = {}, rain = {}, melt = {}'.format(tracker['ppt'].sum(), tracker['rain'].sum(),
                                                               tracker['mlt'].sum())
        print 'remaining snow on ground (swe) = {}'.format(tracker['swe'][-1])
        input_sum = sum([tracker['swe'][-1], tracker['mlt'].sum(), tracker['rain'].sum()])
        print 'swe + melt + rain ({}) should equal ppt ({})'.format(input_sum, tracker['ppt'].sum())
        print 'total inputs (swe, rain, melt): {}'.format(input_sum)
        print 'total runoff = {}, total recharge = {}'.format(tracker['ro'].sum(), tracker['dp_r'].sum())
        output_sum = sum([tracker['transp'].sum(), tracker['evap'].sum(), tracker['ro'].sum(), tracker['dp_r'].sum(),
                          delta_soil_water])
        print 'total outputs (transpiration, evaporation, runoff, recharge, delta soil water) = {}'.format(output_sum)
        mass_balance = input_sum - output_sum
        mass_percent = (mass_balance / input_sum) * 100
        print 'overall water balance for {} mm: {}, or {} percent'.format(name, mass_balance, mass_percent)
        print ''

    def _print_check(self, variable, category):
        print 'raster is {}'.format(category)
        print 'example values from data: {}'.format(self._cells(variable))
        print ''

# ============= EOF =============================================
