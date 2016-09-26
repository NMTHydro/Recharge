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


from numpy import ones, zeros, maximum, minimum, where, isnan, exp, median
from datetime import datetime
from dateutil import rrule

from recharge.dict_setup import initialize_master_dict, initialize_static_dict, initialize_initial_conditions_dict, \
    initialize_point_tracker, set_constants, initialize_master_tracker
from recharge.raster_manager import Rasters
from recharge.dynamic_raster_finder import get_penman, get_prism, get_ndvi
from tools import millimeter_to_acreft as mm_af
from tools import save_master_tracker


class Processes(object):
    """
    The purpose of this class is update the etrm master dict daily.  It should work for both point and
    distributed model runs
    See functions for explanations.

    Returns dict with all rasters under keys of etrm variable names.

    dgketchum 24 JUL 2016
    """
    _point_tracker = None
    _point_dict_key = None
    _master_tracker = None
    _initial_depletions = None

    def __init__(self, date_range, output_root, polygons=None, static_inputs=None, initial_inputs=None,
                 point_dict=None, write_freq=None):

        self._output_root = output_root
        self._date_range = date_range
        self._point_dict = point_dict
        self._outputs = ['tot_infil']  # , 'tot_ref_et', 'tot_eta', 'tot_precip', 'tot_ro', 'tot_snow', 'soil_storage']

        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered
        self._constants = set_constants()

        # Initialize point and raster dicts for static values (e.g. TAW) and initial conditions (e.g. de)
        # from spin up. Define shape of domain. Create a month and annual dict for output raster variables
        # as defined in self._outputs. Don't initialize point_tracker until a time step has passed
        if point_dict:
            self._static = initialize_static_dict(static_inputs, point_dict)
            self._initial = initialize_initial_conditions_dict(initial_inputs, point_dict)
            self._zeros, self._ones = 0.0, 1.0
            self._master = initialize_master_dict()

        else:
            self._polygons = polygons
            self._static = initialize_static_dict(static_inputs)
            self._initial = initialize_initial_conditions_dict(initial_inputs)
            self._shape = self._static['taw'].shape
            self._ones, self._zeros = ones(self._shape), zeros(self._shape)
            self._raster = Rasters(static_inputs, polygons, self._outputs, date_range, output_root, write_freq)
            self._master = initialize_master_dict(self._shape)

    def run(self, ndvi_path=None, prism_path=None, penman_path=None,
            point_dict=None, point_dict_key=None):
        """
        Perform all ETRM functions for each time step, updating master dict and saving data as specified.

        :param date_range: The beginning and end of the simulation.
        :param results_path: Send saved raster to this path. File structure is created automatically.
        :param ndvi_path: NDVI input data path.
        :param prism_path: PRISM input data path.
        :param penman_path: Reference ET and shortwave radiation data.
        :param point_dict: Dict of point metadata for the point model.
        :param point_dict_key: Passed from point model main, will be iterated through each point.
        :param polygons: Shapes to clip and tabulate results.
        :return: Point: point tracker dataframe object.  Distributed: master tracker dataframe object.
        """

        self._point_dict_key = point_dict_key
        m = self._master
        s = self._static
        if point_dict:
            s = s[self._point_dict_key]
        c = self._constants

        start_date, end_date = self._date_range
        print 'simulation period: {}'.format((start_date, end_date))
        start_monsoon, end_monsoon = c['s_mon'], c['e_mon']
        start_time = datetime.now()
        print 'start time :{}'.format(start_time)
        for day in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):

            if not point_dict:
                print ''
                print "Time : {a} day {b}_{c}".format(a=str(datetime.now() - start_time),
                                                      b=day.timetuple().tm_yday, c=day.year)
                self._zeros = zeros(self._shape)
                self._ones = ones(self._shape)

            if day == start_date:

                m['first_day'] = True
                m['albedo'] = self._ones * 0.45
                m['swe'] = self._zeros  # this should be initialized correctly using simulation results
                # s['rew'] = minimum((2 + (s['tew'] / 3.)), 0.8 * s['tew'])  # this has been replaced
                # by method of Ritchie et al (1989), rew derived from percent sand/clay
                m['dry_days'] = self._ones

                if self._point_dict:
                    m['pdr'], m['dr'] = self._initial[point_dict_key]['dr'], self._initial[point_dict_key]['dr']
                    m['pde'], m['de'] = self._initial[point_dict_key]['de'], self._initial[point_dict_key]['de']
                    m['pdrew'], m['drew'] = self._initial[point_dict_key]['drew'], self._initial[point_dict_key]['drew']
                    print 'rew: {}, tew: {}, taw: {}'.format(s['rew'], s['tew'], s['taw'])

                else:
                    m['pdr'], m['dr'] = self._initial['dr'], self._initial['dr']
                    m['pde'], m['de'] = self._initial['de'], self._initial['de']
                    m['pdrew'], m['drew'] = self._initial['drew'], self._initial['drew']
                    print 'rew median: {}, mean {}, max {}, min {}'.format(median(s['rew']), s['rew'].mean(),
                                                                           s['rew'].max(),
                                                                           s['rew'].min())
                    print 'tew median: {}, mean {}, max {}, min {}'.format(median(s['tew']), s['tew'].mean(),
                                                                           s['tew'].max(),
                                                                           s['tew'].min())
                    print 'taw median: {}, mean {}, max {}, min {}'.format(median(s['taw']), s['taw'].mean(),
                                                                           s['taw'].max(),
                                                                           s['taw'].min())

                self._initial_depletions = m['dr'] + m['de'] + m['drew']
            else:
                m['first_day'] = False

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

            self._do_accumulations()

            if day == start_date:
                if self._point_dict:
                    self._point_tracker = initialize_point_tracker(self._master)
                else:
                    self._master_tracker = initialize_master_tracker(self._master)

            if not point_dict:
                self._raster.update_raster_obj(m, day)

                self._update_master_tracker(day)

            else:
                self._update_point_tracker(day)

            if point_dict and day == end_date:
                self._get_tracker_summary(self._point_tracker, point_dict_key)
                return self._point_tracker

            elif day == end_date:
                print 'last day: saving tabulated data'
                save_master_tracker(self._master_tracker, self._output_root)

    def _do_dual_crop_coefficient(self):
        """ Calculate dual crop coefficients, then transpiration, stage one and stage two evaporations.
        """

        m = self._master
        s = self._static
        if self._point_dict:
            s = s[self._point_dict_key]
        c = self._constants

        plant_exponent = s['plant_height'] * 0.5 + 1
        numerator_term = maximum(m['kcb'] - c['kc_min'], self._ones * 0.001)
        denominator_term = maximum((c['kc_max'] - c['kc_min']), self._ones * 0.001)
        cover_fraction_unbound = (numerator_term / denominator_term) ** plant_exponent
        cover_fraction_upper_bound = minimum(cover_fraction_unbound, self._ones)
        m['fcov'] = maximum(cover_fraction_upper_bound, self._ones * 0.001)  # covered fraction of ground
        m['few'] = maximum(1 - m['fcov'], self._ones * 0.001)  # uncovered fraction of ground

        ####
        # transpiration
        m['ks'] = ((s['taw'] - m['pdr']) / ((1 - c['p']) * s['taw']))
        m['ks'] = minimum(m['ks'], self._ones + 0.001)
        m['ks'] = maximum(self._zeros, m['ks'])
        m['transp'] = m['ks'] * m['kcb'] * m['etrs']
        m['transp'] = maximum(self._zeros, m['transp'])

        ####
        # stage 2 coefficient
        # print '{} of tew, {} of pde, and {} of rew are nan'.format(count_nonzero(isnan(s['tew'])),
        #                                                            count_nonzero(isnan(m['pde'])),
        #                                                            count_nonzero(isnan(s['rew'])))
        #
        # print '{} of tew, {} of pde, and {} of rew are zero or less'.format(count_nonzero(where(s['tew'] <= self._zeros,
        #                                                                                         self._ones, self._zeros)),
        #                                                                     count_nonzero(where(m['pde'] <= self._zeros,
        #                                                                                         self._ones, self._zeros)),
        #                                                                     count_nonzero(where(s['rew'] <= self._zeros,
        #                                                                                         self._ones, self._zeros)))

        m['kr'] = minimum((s['tew'] - m['pde']) / (s['tew'] + s['rew']), self._ones)

        # EXPERIMENTAL: stage two evap has been way too high, force slowdown with decay
        m['kr'] *= (1 / m['dry_days'] ** 2)

        if self._point_dict:
            if m['kr'] < 0.01:
                m['kr'] = 0.01
        else:
            m['kr'] = where(m['kr'] < zeros(m['kr'].shape), ones(m['kr'].shape) * 0.01, m['kr'])

        ####
        # check for stage 1 evaporation, i.e. drew < rew
        # this evaporation rate is limited only by available energy, and water in the rew
        st_1_dur = (s['rew'] - m['pdrew']) / (c['ke_max'] * m['etrs'])
        st_1_dur = minimum(st_1_dur, self._ones * 0.99)
        m['st_1_dur'] = maximum(st_1_dur, self._zeros)
        m['st_2_dur'] = (1 - m['st_1_dur'])

        m['ke_init'] = (m['st_1_dur'] + (m['st_2_dur'] * m['kr'])) * (c['kc_max'] - (m['ks'] * m['kcb']))

        if self._point_dict:
            if m['ke_init'] < 0.0:
                m['adjust_ke'] = 'True'
                m['ke'] = 0.01
            if m['ke_init'] > m['few'] * c['kc_max']:
                m['adjust_ke'] = 'True'
                m['ke'] = m['few'] * c['kc_max']
                ke_adjustment = m['ke'] / m['ke_init']
            else:
                m['ke'] = m['ke_init']
                m['adjust_ke'] = 'False'
                ke_adjustment = 1.0
        else:
            m['ke'] = where(m['ke_init'] > m['few'] * c['kc_max'], m['few'] * c['kc_max'], m['ke_init'])
            m['ke'] = where(m['ke_init'] < zeros(m['ke'].shape), zeros(m['ke'].shape) + 0.01, m['ke'])
            ke_adjustment = where(m['ke_init'] > m['few'] * c['kc_max'], m['ke'] / m['ke_init'], self._ones)

        m['ke'] = minimum(m['ke'], self._ones)

        # print 'etrs: {}'.format(mm_af(m['etrs']))

        # m['evap'] = m['ke'] * m['etrs']
        m['evap_1'] = m['st_1_dur'] * (c['kc_max'] - m['ks'] * m['kcb']) * m['etrs'] * ke_adjustment
        m['evap_2'] = m['st_2_dur'] * m['kr'] * (c['kc_max'] - (m['ks'] * m['kcb'])) * m['etrs'] * ke_adjustment

        # for key, val in m.iteritems():
        #     nan_ct = count_nonzero(isnan(val))
        #     if nan_ct > 0:
        #         print '{} has {} nan values'.format(key, nan_ct)
        #     try:
        #         neg_ct = count_nonzero(where(val < 0.0, ones(val.shape), zeros(val.shape)))
        #         if neg_ct > 0:
        #             print '{} has {} negative values'.format(key, neg_ct)
        #     except AttributeError:
        #         pass

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

        temp = m['temp']
        palb = m['albedo']

        if self._point_dict:
            if temp < 0.0 < m['precip']:
                # print 'producing snow fall'
                m['snow_fall'] = m['precip']
                m['rain'] = 0.0
            else:
                m['rain'] = m['precip']
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
            m['snow_fall'] = where(temp < 0.0, m['precip'], self._zeros)
            m['rain'] = where(temp >= 0.0, m['precip'], self._zeros)
            alb = where(m['snow_fall'] > 3.0, self._ones * c['a_max'], palb)
            alb = where(m['snow_fall'] <= 3.0, c['a_min'] + (palb - c['a_min']) * exp(-0.12), alb)
            alb = where(m['snow_fall'] == 0.0, c['a_min'] + (palb - c['a_min']) * exp(-0.05), alb)
            alb = where(alb < c['a_min'], c['a_min'], alb)
            m['albedo'] = alb

        m['swe'] += m['snow_fall']

        melt_init = maximum(((1 - m['albedo']) * m['rg'] * c['snow_alpha']) + (temp - 1.8) * c['snow_beta'],
                            self._zeros)
        m['melt'] = minimum(m['swe'], melt_init)

        m['swe'] -= m['melt']

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

        water = m['rain'] + m['melt']

        m['dry_days'] = where(water < 0.1, m['dry_days'] + self._ones, self._ones)

        # print 'shapes: rain is {}, melt is {}, water is {}'.format(m['rain'].shape, m['melt'].shape, water.shape)
        # it is difficult to ensure mass balance in the following code: do not touch/change w/o testing #
        ##
        if self._point_dict:  # point

            s = s[self._point_dict_key]

            # give days with melt a ksat value for entire day
            if m['melt'] > 0.0:
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

            m['evap'] = m['evap_1'] + m['evap_2']
            m['eta'] = m['transp'] + m['evap_1'] + m['evap_2']

            # this is where a new day starts in terms of depletions (i.e. pdr vs dr) #
            # water balance through skin layer #
            m['drew_water'] = water
            if water < m['pdrew'] + m['evap_1']:
                m['ro'] = 0.0
                m['drew'] = m['pdrew'] + m['evap_1'] - water
                if m['drew'] > s['rew']:
                    print 'why is drew greater than rew?'
                    m['drew'] = s['rew']
                water = 0.0
            elif water >= m['pdrew'] + m['evap_1']:
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
            if water < m['pde'] + m['evap_2']:
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
            if water < m['pdr'] + m['transp']:
                m['infil'] = 0.0
                m['dr'] = m['pdr'] + m['transp'] - water
                if m['dr'] > s['taw']:
                    print 'why is dr greater than taw?'
                    m['dr'] = s['taw']
            elif water >= m['pdr'] + m['transp']:
                m['dr'] = 0.0
                water -= m['pdr'] + m['transp']
                if water > m['soil_ksat']:
                    print 'warning: taw layer has water in excess of its ksat'
                m['infil'] = water
            else:
                print 'error calculating deep percolation from root zone'

        else:  # distributed

            m['pdr'] = m['dr']
            m['pde'] = m['de']
            m['pdrew'] = m['drew']

            # print 'rain: {}, melt: {}, water: {}'.format(mm_af(m['rain']),
            #                                              mm_af(m['melt']), mm_af(water))

            m['soil_ksat'] = where(m['melt'] > 0.0, s['soil_ksat'], m['soil_ksat'])

            # impose limits on vaporization according to present depletions #
            # we can't vaporize more than present difference between current available and limit (i.e. taw - dr) #
            m['evap_1'] = where(m['evap_1'] > s['rew'] - m['pdrew'], s['rew'] - m['drew'], m['evap_1'])
            m['evap_1'] = where(m['evap_1'] < 0.0, zeros(m['evap_1'].shape), m['evap_1'])
            m['evap_2'] = where(m['evap_2'] > s['tew'] - m['pde'], s['tew'] - m['pde'], m['evap_2'])
            m['evap_2'] = where(m['evap_2'] < 0.0, zeros(m['evap_2'].shape), m['evap_2'])
            m['transp'] = where(m['transp'] > s['taw'] - m['pdr'], s['taw'] - m['dr'], m['transp'])

            m['evap'] = m['evap_1'] + m['evap_2']
            m['eta'] = m['transp'] + m['evap_1'] + m['evap_2']

            # print 'evap 1: {}, evap_2: {}, transpiration: {}'.format(mm_af(m['evap_1']), mm_af(m['evap_2']),
            #                                                          mm_af(m['transp']))

            # water balance through skin layer #
            m['drew'] = where(water >= m['pdrew'] + m['evap_1'], self._zeros, m['pdrew'] + m['evap_1'] - water)
            water = where(water < m['pdrew'] + m['evap_1'], self._zeros, water - m['pdrew'] - m['evap_1'])
            # print 'water through skin layer: {}'.format(mm_af(water))
            m['ro'] = where(water > m['soil_ksat'], water - m['soil_ksat'], self._zeros)
            water = where(water > m['soil_ksat'], m['soil_ksat'], water)

            # water balance through the stage 2 evaporation layer #
            m['de'] = where(water >= m['pde'] + m['evap_2'], self._zeros, m['pde'] + m['evap_2'] - water)

            water = where(water < m['pde'] + m['evap_2'], self._zeros, water - (m['pde'] + m['evap_2']))
            # print 'water through  de  layer: {}'.format(mm_af(water))

            # water balance through the root zone layer #
            m['infil'] = where(water >= m['pdr'] + m['transp'], water - m['pdr'] - m['transp'], self._zeros)
            # print 'deep percolation total: {}'.format(mm_af(m['infil']))
            m['dr'] = where(water >= m['pdr'] + m['transp'], self._zeros, m['pdr'] + m['transp'] - water)

            m['soil_storage'] = ((m['pdr'] - m['dr']) + (m['pde'] - m['de']) + (m['pdrew'] - m['drew']))

            # print 'water: {}, out: {}, storage: {}'.format(mm_af(water_tracker),
            #                                                mm_af(m['ro'] + m['eta'] + m['infil']),
            #                                                mm_af(m['soil_storage']))

        return None

    def _do_accumulations(self):
        """ This function simply accumulates all terms.

        :return: None
        """
        m = self._master

        # strangely, these keys wouldn't update with augmented assignment
        # i.e. m['tot_infil] += m['infil'] wasn't working
        m['tot_infil'] = m['infil'] + m['tot_infil']
        m['tot_etrs'] = m['etrs'] + m['tot_etrs']
        m['tot_eta'] = m['eta'] + m['tot_eta']
        m['tot_precip'] = m['precip'] + m['tot_precip']
        m['tot_rain'] = m['rain'] + m['tot_rain']
        m['tot_melt'] = m['melt'] + m['tot_melt']
        m['tot_ro'] = m['ro'] + m['tot_ro']
        m['tot_snow'] = m['snow_fall'] + m['tot_snow']

        m['soil_storage_all'] = self._initial_depletions - (m['pdr'] + m['pde'] + m['pdrew'])

        if not self._point_dict:
            print 'today infil: {}, etrs: {}, eta: {}, precip: {}, ro: {}, swe: {}, stor {}'.format(mm_af(m['infil']),
                                                                                                    mm_af(m['etrs']),
                                                                                                    mm_af(m['eta']),
                                                                                                    mm_af(m['precip']),
                                                                                                    mm_af(m['ro']),
                                                                                                    mm_af(m['swe']),
                                                                                                    mm_af(
                                                                                                        m[
                                                                                                            'soil_storage']))

            print 'total infil: {}, etrs: {}, eta: {}, precip: {}, ro: {}, swe: {}'.format(mm_af(m['tot_infil']),
                                                                                           mm_af(m['tot_etrs']),
                                                                                           mm_af(m['tot_eta']),
                                                                                           mm_af(m['tot_precip']),
                                                                                           mm_af(m['tot_ro']),
                                                                                           mm_af(m['tot_swe']))

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
        m['mass'] = m['rain'] + m['melt'] - (m['ro'] + m['transp'] + m['evap'] + m['infil'] +
                                             ((m['pdr'] - m['dr']) + (m['pde'] - m['de']) +
                                              (m['pdrew'] - m['drew'])))
        # print 'mass from _do_mass_balance: {}'.format(mm_af(m['mass']))
        m['tot_mass'] = abs(m['mass']) + m['tot_mass']
        if not self._point_dict:
            print 'total mass balance error: {}'.format(mm_af(m['tot_mass']))

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
            self._point_tracker.loc[date] = list_

        else:
            # print 'master: {}'.format(m)
            self._point_tracker.loc[date] = tracker_from_master

    def _do_daily_raster_load(self, ndvi, prism, penman, date):

        m = self._master

        m['pkcb'] = m['kcb']
        m['kcb'] = get_ndvi(ndvi, m['pkcb'], date)
        # print 'kcb nan values = {}'.format(count_nonzero(isnan(m['kcb'])))

        m['min_temp'] = get_prism(prism, date, variable='min_temp')
        m['max_temp'] = get_prism(prism, date, variable='max_temp')

        m['temp'] = (m['min_temp'] + m['max_temp']) / 2
        # print 'raw temp nan values = {}'.format(count_nonzero(isnan(m['temp'])))

        m['precip'] = get_prism(prism, date, variable='precip')
        m['precip'] = where(m['precip'] < self._zeros, self._zeros, m['precip'])
        # print 'raw precip nan values = {}'.format(count_nonzero(isnan(m['precip'])))
        # print 'precip min {} precip max on day {} is {}'.format(m['precip'].min(), date, m['precip'].max())
        # print 'total precip et on {}: {:.2e} AF'.format(date, (m['precip'].sum() / 1000) * (250 ** 2) / 1233.48)

        m['etrs'] = get_penman(penman, date, variable='etrs')
        # print 'raw etrs nan values = {}'.format(count_nonzero(isnan(m['etrs'])))
        m['etrs'] = where(m['etrs'] < self._zeros, self._zeros, m['etrs'])
        m['etrs'] = where(isnan(m['etrs']), self._zeros, m['etrs'])
        # print 'bounded etrs nan values = {}'.format(count_nonzero(isnan(m['etrs'])))
        # print 'total ref et on {}: {:.2e} AF'.format(date, (m['etrs'].sum() / 1000) * (250 ** 2) / 1233.48)

        m['rg'] = get_penman(penman, date, variable='rg')

        return None

    def _do_daily_point_load(self, point_dict, date):
        m = self._master
        ts = point_dict['etrm']
        m['kcb'] = ts['kcb'][date]
        m['min_temp'] = ts['min temp'][date]
        m['max_temp'] = ts['max temp'][date]
        m['temp'] = (m['min_temp'] + m['max_temp']) / 2
        m['precip'] = ts['precip'][date]
        m['precip'] = max(m['precip'], 0.0)
        m['etrs'] = ts['etrs_pm'][date]
        m['rg'] = ts['rg'][date]

    def _update_master_tracker(self, date):

        m = self._master

        master_keys_sorted = m.keys()
        master_keys_sorted.sort()
        # print 'master keys sorted: {}, length {}'.format(master_keys_sorted, len(master_keys_sorted))
        tracker_from_master = []
        for key in master_keys_sorted:
            try:
                tracker_from_master.append(mm_af(m[key]))
            except AttributeError:
                # this is to handle the non-float (e.g. boolean) parameters which can't be converted to AF
                tracker_from_master.append(m[key])

        # print 'tracker from master, list : {}, length {}'.format(tracker_from_master, len(tracker_from_master))
        # remember to use loc. iloc is to index by integer, loc can use a datetime obj.
        self._master_tracker.loc[date] = tracker_from_master

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
        print 'input precip = {}, rain = {}, melt = {}'.format(tracker['precip'].sum(), tracker['rain'].sum(),
                                                               tracker['melt'].sum())
        print 'remaining snow on ground (swe) = {}'.format(tracker['swe'][-1])
        input_sum = sum([tracker['swe'][-1], tracker['melt'].sum(), tracker['rain'].sum()])
        print 'swe + melt + rain ({}) should equal precip ({})'.format(input_sum, tracker['precip'].sum())
        print 'total inputs (swe, rain, melt): {}'.format(input_sum)
        print 'total runoff = {}, total recharge = {}'.format(tracker['ro'].sum(), tracker['infil'].sum())
        output_sum = sum([tracker['transp'].sum(), tracker['evap'].sum(), tracker['ro'].sum(), tracker['infil'].sum(),
                          delta_soil_water])
        print 'total outputs (transpiration, evaporation, runoff, recharge, delta soil water) = {}'.format(output_sum)
        mass_balance = input_sum - output_sum
        mass_percent = (mass_balance / input_sum) * 100
        print 'overall water balance for {} mm: {}, or {} percent'.format(name, mass_balance, mass_percent)
        print ''

# ============= EOF =============================================
