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

import os
import time
from numpy import ones, zeros, maximum, minimum, where, isnan, exp, median
from dateutil import rrule
from recharge.dict_setup import initialize_master_dict, initialize_static_dict, initialize_initial_conditions_dict, \
    set_constants, initialize_master_tracker

from recharge.raster_manager import RasterManager
from recharge.dynamic_raster_finder import get_penman, get_prism, get_kcb
from tools import millimeter_to_acreft as mm_af


def add_extension(p, ext='.txt'):
    if not p.endswith(ext):
        p = '{}{}'.format(p, ext)
    return p


def time_it(func, *args, **kw):
    st = time.time()
    ret = func(*args, **kw)
    print '######### {:<30s} execution time={:0.3f}'.format(func.func_name, time.time() - st)
    return ret


class Processes(object):
    """
    The purpose of this class is update the etrm master dict daily.  It should work for both point and
    distributed model runs.
    See function explanations.

    Returns dict with all rasters under keys of etrm variable names.

    dgketchum 24 JUL 2016
    """

    tracker = None
    _initial_depletions = None

    def __init__(self,
                 date_range,
                 input_root,
                 output_root,
                 mask='Mask',
                 polygons='Blank_Geo',
                 write_freq=None):

        self._mask_path = os.path.join(input_root, mask)
        self._output_root = output_root

        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered
        self._constants = time_it(set_constants)

        # Initialize point and raster dicts for static values (e.g. TAW) and initial conditions (e.g. de)
        # from spin up. Define shape of domain. Create a month and annual dict for output raster variables
        # as defined in self._outputs. Don't initialize point_tracker until a time step has passed

        static_inputs = os.path.join(input_root, 'statics'),
        initial_inputs = os.path.join(input_root, 'initialize')

        self._static = time_it(initialize_static_dict, static_inputs, self._mask_path)
        self._shape = self._static['taw'].shape
        self._initial = time_it(initialize_initial_conditions_dict, initial_inputs, self._mask_path)
        self._master = time_it(initialize_master_dict, self._shape)

        self._ones, self._zeros = ones(self._shape), zeros(self._shape)
        self._raster_manager = RasterManager(static_inputs, polygons, date_range, output_root,
                                             write_freq)  # self._outputs

        self._ndvi = os.path.join(input_root, 'NDVI', 'NDVI_std_all')
        self._prism = os.path.join(input_root, 'PRISM')
        self._penman = os.path.join(input_root, 'PM_RAD')
        self._start_date, self._end_date = date_range

        time_it(self.initialize)

    def run(self, sensitivity_matrix_column=None, apply_rofrac=0.0, swb_mode='vertical', allen_ceff=1.0):

        start, end = self._start_date, self._end_date
        self._info('Simulation period: start={}, end={}'.format(start, end))

        c = self._constants
        m = self._master
        s = self._static
        rm = self._raster_manager

        start_monsoon, end_monsoon = c['s_mon'].timetuple().tm_yday, c['e_mon'].timetuple().tm_yday

        st = time.time()
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            tm_yday = day.timetuple().tm_yday
            self._info('DAY:     {}({})'.format(day, tm_yday))

            time_it(self._do_daily_raster_load, day)

            # the soil ksat should be read each day from the static data, then set in the master #
            # otherwise the static is updated and diminishes each day #
            # [mm/day] #
            if start_monsoon <= tm_yday <= end_monsoon:
                m['soil_ksat'] = s['soil_ksat'] * 2 / 24.
            else:
                m['soil_ksat'] = s['soil_ksat'] * 6 / 24.

            if sensitivity_matrix_column:
                time_it(self._do_parameter_adjustment, sensitivity_matrix_column)

            # self._do_dual_crop_coefficient(tm_yday, m, s, c)
            # self._do_snow()
            # self._do_soil_ksat_adjustment(m, s)

            time_it(self._do_dual_crop_coefficient, tm_yday, m, s, c)
            time_it(self._do_snow)
            time_it(self._do_soil_ksat_adjustment, m, s)

            if swb_mode == 'fao':
                time_it(self._do_fao_soil_water_balance, m, s, apply_rofrac)
            elif swb_mode == 'vertical':
                time_it(self._do_vert_soil_water_balance, apply_rofrac, allen_ceff)

            time_it(self._do_mass_balance, day, swb=swb_mode)

            time_it(self._do_accumulations)

            if self.tracker is None:
                self.tracker = initialize_master_tracker(m)

            time_it(rm.update_raster_obj, m, self._mask_path, day)
            time_it(self._update_master_tracker, day)

            m['first_day'] = False

        time_it(rm.save_csv)

        self._info('saving tabulated data')
        self.save_tracker()
        self._info('Execution time: {}'.format(time.time() - st))

    def initialize(self):
        m = self._master

        m['first_day'] = True
        m['albedo'] = self._ones * 0.45
        m['swe'] = self._zeros  # this should be initialized correctly using simulation results
        # s['rew'] = minimum((2 + (s['tew'] / 3.)), 0.8 * s['tew'])  # this has been replaced
        # by method of Ritchie et al (1989), rew derived from percent sand/clay
        m['dry_days'] = self._ones

        m['pdr'], m['dr'] = self._initial['dr'], self._initial['dr']
        m['pde'], m['de'] = self._initial['de'], self._initial['de']
        m['pdrew'], m['drew'] = self._initial['drew'], self._initial['drew']

        s = self._static
        for key in ('rew', 'tew', 'taw', 'soil_ksay'):
            v = s[key]
            msg = '{} median: {}, mean: {}, max: {}, min: {}'.format(key, median(v), v.mean(), v.max(), v.min())
            self._debug(msg)

        # self._debug('rew median: {}, mean {}, max {}, min {}'.format(median(s['rew']), s['rew'].mean(),
        #                                                        s['rew'].max(),
        #                                                        s['rew'].min()))
        # self._debug('tew median: {}, mean {}, max {}, min {}'.format(median(s['tew']), s['tew'].mean(),
        #                                                        s['tew'].max(),
        #                                                        s['tew'].min()))
        # self._debug('taw median: {}, mean {}, max {}, min {}'.format(median(s['taw']), s['taw'].mean(),
        #                                                        s['taw'].max(),
        #                                                        s['taw'].min()))
        # self._debug('soil_ksat median: {}, mean {}, max {}, min {}'.format(median(s['soil_ksat']),
        #                                                              s['soil_ksat'].mean(),
        #                                                              s['soil_ksat'].max(),
        #                                                              s['soil_ksat'].min()))

        self._initial_depletions = m['dr'] + m['de'] + m['drew']

    def save_tracker(self, path=None):
        base = 'etrm_master_tracker'
        if path is None:
            path = add_extension(os.path.join(self._output_root, base), '.csv')

        if os.path.isfile(path):
            cnt = 0
            while 1:
                path = os.path.join(self._output_root, '{}-{:04n}.csv'.format(base, cnt))
                if not os.path.isfile(path):
                    break
                cnt += 1

        path = add_extension(path, '.csv')
        print 'this should be your csv: {}'.format(path)
        self.tracker.to_csv(path, na_rep='nan', index_label='Date')

    # private
    def _do_dual_crop_coefficient(self, tm_yday, m, s, c):
        """ Calculate dual crop coefficients, then transpiration, stage one and stage two evaporations.

        """

        kcb = m['kcb']
        etrs = m['etrs']
        kc_max = c['kc_max']
        kc_min = c['kc_min']

        # ASCE pg 199, Eq 9.27
        plant_exponent = s['plant_height'] * 0.5 + 1  # h varaible, derived from ??
        numerator_term = maximum(kcb - kc_min, self._ones * 0.001)
        denominator_term = maximum((kc_max - kc_min), self._ones * 0.001)
        cover_fraction_unbound = (numerator_term / denominator_term) ** plant_exponent
        cover_fraction_upper_bound = minimum(cover_fraction_unbound, self._ones)
        # ASCE pg 198, Eq 9.26
        m['fcov'] = fcov = maximum(cover_fraction_upper_bound, self._ones * 0.001)  # covered fraction of ground

        # m['few'] = maximum(1 - m['fcov'], self._ones * 0.001)  # uncovered fraction of ground
        m['few'] = few = maximum(1 - fcov, self._ones * 0.001)  # uncovered fraction of ground

        ####
        # transpiration:
        # ks- stress coeff- ASCE pg 226, Eq 10.6

        # m['ks'] = ((s['taw'] - m['pdr']) / ((1 - c['p']) * s['taw']))
        taw = s['taw']
        ks = ((taw - m['pdr']) / ((1 - c['p']) * taw))

        # m['ks'] = minimum(m['ks'], self._ones + 0.001) #this 0.001 may be unneeded
        ks = minimum(ks, self._ones + 0.001)  # this 0.001 may be unneeded

        # m['ks'] = maximum(self._zeros, m['ks'])
        ks = maximum(self._zeros, ks)
        m['ks'] = ks

        # m['transp'] = m['ks'] * m['kcb'] * m['etrs']
        transp = ks * kcb * etrs

        m['transp_adj'] = False
        # enforce winter dormancy of vegetation
        if 92 > tm_yday or tm_yday > 306:
            # super-important winter evap limiter. Jan suggested 0.03 (aka 3%) but that doesn't match ameriflux.
            # m['transp'] *= 0.3
            transp *= 0.3

            # m['transp'] = maximum(self._zeros, self._ones * 0.03)
            m['transp_adj'] = True

        # m['transp'] = maximum(self._zeros, m['transp'])
        transp = maximum(self._zeros, transp)
        m['transp'] = transp
        # kr- evaporation reduction coefficient ASCE pg 193, eq 9.21; only non time dependent portion of Eq 9.21
        # m['kr'] = minimum((s['tew'] - m['pde']) / s['tew'], self._ones) #changed denominator

        tew = s['tew']
        kr = minimum((tew - m['pde']) / tew, self._ones)  # changed denominator

        # EXPERIMENTAL: stage two evap has been too high, force slowdown with decay
        # m['kr'] *= (1 / m['dry_days'] **2)

        # this seems like a round about way to limit the min value. SWA 1/25/17
        # if self._point_dict:
        #    if m['kr'] < 0.01:
        #        m['kr'] = 0.01
        # else:
        #    m['kr'] = where(m['kr'] < zeros(m['kr'].shape), ones(m['kr'].shape) * 0.01, m['kr'])
        # this is a simpler way
        # m['kr'] = maximum(m['kr'], self._ones * 0.01)
        kr = maximum(kr, self._ones * 0.01)
        m['kr'] = kr

        ####
        # check for stage 1 evaporation, i.e. drew < rew
        # this evaporation rate is limited only by available energy, and water in the rew

        st_1_dur = (s['rew'] - m['pdrew']) / (c['ke_max'] * etrs)  # ASCE 194 Eq 9.22; called Fstage1
        # st_1_dur = (s['rew'] - m['pdrew']) / ((c['kc_max'] - (m['ks'] * m['kcb'])) * m['etrs'])
        st_1_dur = minimum(st_1_dur, self._ones * 0.99)
        m['st_1_dur'] = st_1_dur = maximum(st_1_dur, self._zeros)
        m['st_2_dur'] = st_2_dur = (1 - st_1_dur)

        # ke evaporation efficency; Allen 2011, Eq 13a
        ke_init = (st_1_dur + (st_2_dur * kr)) * (kc_max - (ks * kcb))

        ke = where(ke_init > few * kc_max, few * kc_max, ke_init)
        ke = where(ke_init < zeros(ke.shape), zeros(ke.shape) + 0.01, ke)
        ke_adjustment = where(ke_init > few * kc_max, ke / ke_init, self._ones)

        m['ke'] = minimum(ke, self._ones)
        m['ke_init'] = ke_init
        # print 'etrs: {}'.format(mm_af(m['etrs']))

        # m['evap'] = m['ke'] * m['etrs']
        # Ketchum Thesis eq 36, 37
        m['evap_1'] = e1 = st_1_dur * (kc_max - (ks * kcb)) * etrs * ke_adjustment
        m['evap_2'] = e2 = st_2_dur * kr * (kc_max - (ks * kcb)) * etrs * ke_adjustment
        m['evap'] = e1 + e2

    def _do_snow(self):
        """ Calibrated snow model that runs using PRISM temperature and precipitation.

        :return: None
        """
        m = self._master
        c = self._constants

        temp = m['temp']
        palb = m['albedo']

        precip = m['precip']

        a_min = c['a_min']
        a_max = c['a_max']

        sf = where(temp < 0.0, precip, self._zeros)
        rain = where(temp >= 0.0, precip, self._zeros)
        # alb = where(m['snow_fall'] > 3.0, self._ones * c['a_max'], palb)
        # alb = where(m['snow_fall'] <= 3.0, c['a_min'] + (palb - c['a_min']) * exp(-0.12), alb)
        # alb = where(m['snow_fall'] == 0.0, c['a_min'] + (palb - c['a_min']) * exp(-0.05), alb)
        # alb = where(alb < c['a_min'], c['a_min'], alb)
        alb = where(sf > 3.0, self._ones * a_max, palb)
        alb = where(sf <= 3.0, a_min + (palb - a_min) * exp(-0.12), alb)
        alb = where(sf == 0.0, a_min + (palb - a_min) * exp(-0.05), alb)
        palb = where(alb < a_min, a_min, alb)
        # m['albedo'] = alb

        # m['swe'] += m['snow_fall']
        m['swe'] += sf

        melt_init = maximum(((1 - palb) * m['rg'] * c['snow_alpha']) + (temp - 1.8) * c['snow_beta'],
                            zeros(m['rg'].shape))

        m['melt'] = melt = minimum(m['swe'], melt_init)
        m['swe'] -= melt

        m['rain'] = rain
        m['snow_fall'] = sf
        m['albedo'] = palb

    def _do_soil_ksat_adjustment(self, m, s):
        """ Adjust soil hydraulic conductivity according to land surface cover type.

        :return: None
        """

        water = m['rain'] + m['melt']
        land_cover = s['land_cover']
        soil_ksat = m['soil_ksat']

        o = ones(soil_ksat.shape)
        soil_ksat = where((land_cover == 41) & (water < 50.0 * o),
                          soil_ksat * 2.0 * o, soil_ksat)
        soil_ksat = where((land_cover == 41) & (water < 12.0 * ones(soil_ksat.shape)),
                          soil_ksat * 1.2 * o, soil_ksat)
        soil_ksat = where((land_cover == 42) & (water < 50.0 * o),
                          soil_ksat * 2.0 * o, soil_ksat)
        soil_ksat = where((land_cover == 42) & (water < 12.0 * o),
                          soil_ksat * 1.2 * o, soil_ksat)
        soil_ksat = where((land_cover == 43) & (water < 50.0 * o),
                          soil_ksat * 2.0 * o, soil_ksat)
        soil_ksat = where((land_cover == 43) & (water < 12.0 * o),
                          soil_ksat * 1.2 * o, soil_ksat)

        m['soil_ksat'] = soil_ksat

    # def _do_fao_soil_water_balance(self, ro_local_reinfilt_frac=0.0, ceff=1.0):
    def _do_fao_soil_water_balance(self, m, s, ro_local_reinfilt_frac=0.0):
        """ Calculate all soil water balance at each time step.

        :return: None
        """
        # m = self._master
        # s = self._static

        melt = m['melt']
        # find liquid water incident on the soil surface
        water = m['rain'] + melt

        # update number of days of dry weather
        m['dry_days'] = where(water < 0.1, m['dry_days'] + self._ones, self._ones)

        # print 'shapes: rain is {}, melt is {}, water is {}'.format(m['rain'].shape, m['melt'].shape, water.shape)
        # it is difficult to ensure mass balance in the following code: do not touch/change w/o testing #
        ##

        # update variables
        m['pdr'] = pdr = dr = m['dr']
        m['pde'] = pde = de = m['de']
        m['pdrew'] = pdrew = drew = m['drew']
        srew = s['rew']
        stew = s['tew']
        staw = s['taw']
        transp = m['transp']
        evap_1 = m['evap_1']
        evap_2 = m['evap_2']
        soil_ksat = m['soil_ksat']

        # print 'rain: {}, melt: {}, water: {}'.format(mm_af(m['rain']),
        #                                              mm_af(m['melt']), mm_af(water))

        soil_ksat = where(melt > 0.0, s['soil_ksat'], soil_ksat)

        # impose limits on vaporization according to present depletions #
        # we can't vaporize more than present difference between current available and limit (i.e. taw - dr) #
        evap_1 = where(evap_1 > srew - pdrew, srew - drew, evap_1)
        evap_1 = where(evap_1 < 0.0, zeros(evap_1.shape), evap_1)
        evap_2 = where(evap_2 > stew - pde, stew - pde, evap_2)
        evap_2 = where(evap_2 < 0.0, zeros(evap_2.shape), evap_2)
        transp = where(transp > staw - pdr, staw - dr, transp)

        m['evap'] = evap_1 + evap_2
        m['eta'] = transp + evap_1 + evap_2

        # print 'evap 1: {}, evap_2: {}, transpiration: {}'.format(mm_af(m['evap_1']), mm_af(m['evap_2']),
        #                                                          mm_af(m['transp']))

        # water balance through skin layer #
        drew = where(water >= pdrew + evap_1, self._zeros, pdrew + evap_1 - water)
        water = where(water < pdrew + evap_1, self._zeros, water - pdrew - evap_1)
        # print 'water through skin layer: {}'.format(mm_af(water))
        m['ro'] = where(water > soil_ksat, water - soil_ksat, self._zeros)
        water = where(water > soil_ksat, soil_ksat, water)

        # water balance through the stage 2 evaporation layer #
        de = where(water >= pde + evap_2, self._zeros, pde + evap_2 - water)

        water = where(water < pde + evap_2, self._zeros, water - (pde + evap_2))
        # print 'water through  de  layer: {}'.format(mm_af(water))

        # water balance through the root zone layer #
        # print 'deep percolation total: {}'.format(mm_af(m['infil']))
        dr = where(water >= pdr + transp, self._zeros, pdr + transp - water)

        m['infil'] = where(water >= pdr + transp, water - pdr - transp, self._zeros)
        m['soil_storage'] = ((pdr - dr) + (pde - de) + (pdrew - drew))
        m['dr'] = dr
        m['de'] = de
        m['drew'] = drew
        m['evap_1'] = evap_1
        m['evap_2'] = evap_2
        m['soil_ksat'] = soil_ksat

    def _do_vert_soil_water_balance(self, ro_local_reinfilt_frac=0.0, ceff=1.0):
        """ Calculate all soil water balance at each time step.

        :return: None
        """
        m = self._master
        s = self._static

        water = m['rain'] + m['melt']

        # m['dry_days'] = where(water < 0.1, m['dry_days'] + self._ones, self._ones)
        dd = m['dry_days']
        dd[water < 0.1] = dd + 1
        dd[water >= 0.1] = 1
        m['dry_days'] = dd

        # print 'shapes: rain is {}, melt is {}, water is {}'.format(m['rain'].shape, m['melt'].shape, water.shape)
        # it is difficult to ensure mass balance in the following code: do not touch/change w/o testing #
        ##

        m['pdr'] = pdr = m['dr']
        m['pde'] = pde = m['de']
        m['pdrew'] = pdrew = m['drew']

        # print 'rain: {}, melt: {}, water: {}'.format(mm_af(m['rain']),
        #                                              mm_af(m['melt']), mm_af(water))

        m['soil_ksat'] = soil_ksat = where(m['melt'] > 0.0, s['soil_ksat'], m['soil_ksat'])

        # impose limits on vaporization according to present depletions #
        # we can't vaporize more than present difference between current available and limit (i.e. taw - dr) #
        evap_1 = m['evap_1']

        dv = s['rew'] - pdrew
        evap_1 = where(evap_1 > dv, dv, evap_1)
        evap_1[evap_1 < 0] = 0

        evap_2 = m['evap_2']
        dv = s['tew'] - pde

        evap_2 = where(evap_2 > dv, dv, evap_2)
        evap_2[evap_2 < 0] = 0

        transp = m['transp']
        dv = s['taw'] - m['pdr']
        # transp[transp > dv] = dv
        # m['transp'] = where(m['transp'] > s['taw'] - m['pdr'], s['taw'] - m['dr'], m['transp'])
        transp = where(transp > dv, dv, transp)

        m['evap'] = evap_1 + evap_2
        m['eta'] = transp + evap_1 + evap_2

        # print 'evap 1: {}, evap_2: {}, transpiration: {}'.format(mm_af(m['evap_1']), mm_af(m['evap_2']),
        #                                                          mm_af(m['transp']))

        # water balance through skin layer #
        drew = where(water >= pdrew + evap_1, self._zeros, pdrew + evap_1 - water)
        water = where(water < pdrew + evap_1, self._zeros, water - pdrew - evap_1)
        # print 'water through skin layer: {}'.format(mm_af(water))

        # m['ro'] = where(water > soil_ksat, water - soil_ksat, self._zeros)
        ro = m['ro']
        ro[water > soil_ksat] = water - soil_ksat
        ro[water <= soil_ksat] = 0
        m['ro'] = ro

        # water = where(water > m['soil_ksat'], m['soil_ksat'], water)
        water[water > soil_ksat] = soil_ksat

        # water balance through the stage 2 evaporation layer #
        v = pde + evap_2
        de = where(water >= v, self._zeros, v - water)

        water = where(water < v, self._zeros, water - v)
        # print 'water through  de  layer: {}'.format(mm_af(water))

        # water balance through the root zone layer #
        v = pdr + transp
        m['infil'] = where(water >= v, water - pdr - transp, self._zeros)

        # print 'deep percolation total: {}'.format(mm_af(m['infil']))
        dr = where(water >= v, self._zeros, v - water)

        m['soil_storage'] = ((pdr - dr) + (pde - de) + (pdrew - drew))

        m['drew'] = drew
        m['de'] = de
        m['dr'] = dr
        m['evap_1'] = evap_1
        m['evap_2'] = evap_2
        m['transp'] = transp

    def _do_accumulations(self):
        """ This function simply accumulates all terms.

        :return: None
        """
        m = self._master

        # strangely, these keys wouldn't update with augmented assignment
        # i.e. m['tot_infil] += m['infil'] wasn't working
        # m['tot_infil'] = m['infil'] + m['tot_infil']
        # m['tot_etrs'] = m['etrs'] + m['tot_etrs']
        # m['tot_eta'] = m['eta'] + m['tot_eta']
        # m['tot_precip'] = m['precip'] + m['tot_precip']
        # m['tot_rain'] = m['rain'] + m['tot_rain']
        # m['tot_melt'] = m['melt'] + m['tot_melt']
        # m['tot_ro'] = m['ro'] + m['tot_ro']
        # m['tot_snow'] = m['snow_fall'] + m['tot_snow']

        for k in ('infil', 'etrs', 'eta', 'precip', 'rain', 'melt', 'ro', 'swe'):
            kk = 'tot_{}'.format(k)
            m[kk] = m[k] + m[kk]

        m['soil_storage_all'] = self._initial_depletions - (m['pdr'] + m['pde'] + m['pdrew'])

        print 'today infil: {}, etrs: {}, eta: {}, ' \
              'precip: {}, ro: {}, swe: {}, stor {}'.format(mm_af(m['infil']),
                                                            mm_af(m['etrs']),
                                                            mm_af(m['eta']),
                                                            mm_af(m['precip']),
                                                            mm_af(m['ro']),
                                                            mm_af(m['swe']),
                                                            mm_af(m['soil_storage']))

        print 'total infil: {}, etrs: {}, eta: {}, ' \
              'precip: {}, ro: {}, swe: {}'.format(mm_af(m['tot_infil']),
                                                   mm_af(m['tot_etrs']),
                                                   mm_af(m['tot_eta']),
                                                   mm_af(m['tot_precip']),
                                                   mm_af(m['tot_ro']),
                                                   mm_af(m['tot_swe']))

    def _do_mass_balance(self, date, swb):
        """ Checks mass balance.
        :return:
        """

        m = self._master

        melt = m['melt']
        rain = m['rain']
        # ro = m['ro']
        # transp = m['transp']
        # evap = m['evap']
        # infil = m['infil']

        ddr = m['pdr'] - m['dr']
        dde = m['pde'] - m['de']
        ddrew = m['pdrew'] - m['drew']

        b = 0
        if swb == 'vertical':
            b = dde + ddrew

        a = m['ro'] + m['transp'] + m['evap'] + m['infil'] + ddr + b
        mass = rain + melt - a
        # mass = rain + melt - ro + transp + evap + infil - ddr

        # if swb == 'fao':
        #     m['mass'] = m['rain'] + m['melt'] - (m['ro'] + m['transp'] + m['evap'] + m['infil'] +
        #                              (m['pdr'] - m['dr']))
        # elif swb == 'vertical':
        #     m['mass'] = m['rain'] + m['melt'] - (m['ro'] + m['transp'] + m['evap'] + m['infil'] +
        #                                      ((m['pdr'] - m['dr']) + (m['pde'] - m['de']) +
        #                                       (m['pdrew'] - m['drew'])))
        # if swb == 'vertical':
        # mass -= (m['pde'] - m['de']) + (m['pdrew'] - m['drew'])

        m['mass'] = mass
        # print 'mass from _do_mass_balance: {}'.format(mm_af(m['mass']))
        # if date == self._date_range[0]:
        #     # print 'zero mass balance first day'
        #     m['mass'] = zeros(m['mass'].shape)
        m['tot_mass'] = tot_mass = abs(mass) + m['tot_mass']
        self._debug('total mass balance error: {}'.format(mm_af(tot_mass)))

    def _do_daily_raster_load(self, date):
        """ Find daily raster image for each ETRM input.

        param date: datetime.day object
        :return: None
        """
        ndvi, prism, penman = self._ndvi_path, self._prism_path, self._penman_path
        m = self._master

        m['kcb'] = get_kcb(self._mask_path, ndvi, date, m['pkcb'])
        # print 'kcb nan values = {}'.format(count_nonzero(isnan(m['kcb'])))

        m['min_temp'] = min_temp = get_prism(self._mask_path, prism, date, variable='min_temp')
        m['max_temp'] = max_temp = get_prism(self._mask_path, prism, date, variable='max_temp')

        m['temp'] = (min_temp + max_temp) / 2
        # print 'raw temp nan values = {}'.format(count_nonzero(isnan(m['temp'])))

        precip = get_prism(self._mask_path, prism, date, variable='precip')
        m['precip'] = where(precip < self._zeros, self._zeros, precip)
        # print 'raw precip nan values = {}'.format(count_nonzero(isnan(m['precip'])))
        # print 'precip min {} precip max on day {} is {}'.format(m['precip'].min(), date, m['precip'].max())
        # print 'total precip et on {}: {:.2e} AF'.format(date, (m['precip'].sum() / 1000) * (250 ** 2) / 1233.48)

        etrs = get_penman(self._mask_path, penman, date, variable='etrs')
        # print 'raw etrs nan values = {}'.format(count_nonzero(isnan(m['etrs'])))
        etrs = where(etrs < self._zeros, self._zeros, etrs)
        m['etrs'] = where(isnan(etrs), self._zeros, etrs)
        # print 'bounded etrs nan values = {}'.format(count_nonzero(isnan(m['etrs'])))
        # print 'total ref et on {}: {:.2e} AF'.format(date, (m['etrs'].sum() / 1000) * (250 ** 2) / 1233.48)

        m['rg'] = get_penman(self._mask_path, penman, date, variable='rg')

        m['pkcb'] = m['kcb']

    def _do_parameter_adjustment(self, adjustment_array):

        m = self._master
        s = self._static

        alpha, beta, gamma, delta, zeta, theta = adjustment_array
        if m['first_day']:
            print 'a: {}, b: {}, gam: {}, del: {}, z: {}, theta: {}'.format(*adjustment_array)
            # taw is found once, and should be modified once
            s['taw'] *= delta
        # these are found daily, so can be modified daily
        m['temp'] += alpha
        m['precip'] *= beta
        m['etrs'] *= gamma
        m['kcb'] *= zeta
        m['soil_ksat'] *= theta

    def _update_master_tracker(self, date):
        m = self._master

        def factory(k):
            v = m[k]
            try:
                v = mm_af(v)
            except AttributeError:
                # this is to handle the non-float (e.g. boolean) parameters which can't be converted to AF
                pass

            return v

        tracker_from_master = [factory(key) for key in sorted(m)]
        # print 'tracker from master, list : {}, length {}'.format(tracker_from_master, len(tracker_from_master))
        # remember to use loc. iloc is to index by integer, loc can use a datetime obj.
        self.tracker.loc[date] = tracker_from_master

    def _get_tracker_summary(self, tracker, name):
        s = self._static[name]

        s1 = tracker['evap_1'].sum()
        s2 = tracker['evap_2'].sum()
        et = tracker['evap'].sum()
        ts = tracker['transp'].sum()

        ps = tracker['precip'].sum()
        rs = tracker['rain'].sum()
        ms = tracker['melt'].sum()
        ros = tracker['ro'].sum()
        infils = tracker['infil'].sum()

        # print 'summary stats for {}:\n{}'.format(name, tracker.describe())
        print '---------------------------------Tracker Summary--------------------------------'
        print 'a look at vaporization:'
        print 'stage one  = {}, stage two  = {}, together = {},  total evap: {}'.format(s1, s2, s1 + s2, et)
        print 'total transpiration = {}'.format(ts)

        depletions = ('drew', 'de', 'dr')
        capacities = (s['rew'], s['tew'], s['taw'])

        starting_water = sum((x - tracker[y][0] for x, y in zip(capacities, depletions)))
        ending_water = sum((x - tracker[y][-1] for x, y in zip(capacities, depletions)))

        delta_soil_water = ending_water - starting_water
        print 'soil water change = {}'.format(delta_soil_water)

        print 'input precip = {}, rain = {}, melt = {}'.format(ps, rs, ms)

        rswe = tracker['swe'][-1]
        print 'remaining snow on ground (swe) = {}'.format(rswe)

        # input_sum = tracker['swe'][-1] + tracker['melt'].sum() + tracker['rain'].sum()
        input_sum = rswe + ms + rs

        print 'total inputs (swe, rain, melt): {}'.format(input_sum)
        print 'swe + melt + rain ({}) should equal precip ({})'.format(input_sum, ps)
        print 'total runoff = {}, total recharge = {}'.format(ros, infils)

        # output_sum = reduce(lambda a, b: a + b, map(sum, (tracker[k] for k in ('transp', 'evap', 'ro', 'infil'))))
        # output_sum = reduce(lambda a, b: a + b, (sum(tracker[k]) for k in ('transp', 'evap', 'ro', 'infil')))
        # output_sum = sum(sum(tracker[k]) for k in ('transp', 'evap', 'ro', 'infil'))
        output_sum = ts + et + ros + infils

        # output_sum = sum((tracker[k] for k in ('transp', 'evap', 'ro', 'infil')))
        output_sum += delta_soil_water + tracker['swe'][-1]  # added swe to output_sum; Dan, 2/11/17

        # output_sum = tracker['transp'].sum() + tracker['evap'].sum() + tracker['ro'].sum() + tracker[
        #     'infil'].sum() + delta_soil_water

        print 'total outputs (transpiration, evaporation, runoff, recharge, delta soil water) = {}'.format(output_sum)
        mass_balance = input_sum - output_sum
        mass_percent = (mass_balance / input_sum) * 100
        print 'overall water balance for {}: {} mm, or {} percent'.format(name, mass_balance, mass_percent)
        print '--------------------------------------------------------------------------------'

    def _info(self, msg):
        print '-------------------------------------------------------'
        print msg
        print '-------------------------------------------------------'

    def _debug(self, msg):
        print '%%%%%%%%%%%%%%%% {}'.format(msg)

# ============= EOF =============================================
# def run(self, ndvi_path=None, prism_path=None, penman_path=None,
#         point_dict=None, point_dict_key=None, sensitivity_matrix_column=None, sensitivity=False,
#         modify_soils=False, apply_rofrac=0.0, swb_mode='vertical', allen_ceff=1.0):
#     """
#     Perform all ETRM functions for each time step, updating master dict and saving data as specified.
#
#     :param swb_mode:
#     :param apply_rofrac:
#     :param allen_ceff
#     :param modify_soils:
#     :param sensitivity: True if running a sensitivity analysis.  Will trigger call of _do_parameter_adjustment().
#     :param sensitivity_matrix_column: Column of varied parameters (see sensitivity_analysis.py docs)
#     :param ndvi_path: NDVI input data path.
#     :param prism_path: PRISM input data path.
#     :param penman_path: Reference ET and shortwave radiation data.
#     :param point_dict: Dict of point metadata for the point model.
#     :param point_dict_key: Passed from point model main, will be iterated through each point.
#     :return: Point: point tracker dataframe object.  Distributed: master tracker dataframe object.
#     """
#
#     self._point_dict_key = point_dict_key
#     m = self._master
#     s = self._static
#     if point_dict:
#         s = s[self._point_dict_key]
#
#     if modify_soils:
#         s['rew'] *= 0.1
#         s['tew'] *= 1.0
#
#     c = self._constants
#
#     start_date, end_date = self._date_range
#     print 'simulation period: {}'.format((start_date, end_date))
#     start_monsoon, end_monsoon = c['s_mon'], c['e_mon']
#     start_time = datetime.now()
#     print 'start time :{}'.format(start_time)
#     for day in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
#
#         if not point_dict:
#             print ''
#             print "Time : {a} day {b}_{c}".format(a=str(datetime.now() - start_time),
#                                                   b=day.timetuple().tm_yday, c=day.year)
#             self._zeros = zeros(self._shape)
#             self._ones = ones(self._shape)
#
#         if day == start_date:
#
#             m['first_day'] = True
#             m['albedo'] = self._ones * 0.45
#             m['swe'] = self._zeros  # this should be initialized correctly using simulation results
#             # s['rew'] = minimum((2 + (s['tew'] / 3.)), 0.8 * s['tew'])  # this has been replaced
#             # by method of Ritchie et al (1989), rew derived from percent sand/clay
#             m['dry_days'] = self._ones
#
#             if self._point_dict:
#                 m['pdr'], m['dr'] = self._initial[point_dict_key]['dr'], self._initial[point_dict_key]['dr']
#                 m['pde'], m['de'] = self._initial[point_dict_key]['de'], self._initial[point_dict_key]['de']
#                 m['pdrew'], m['drew'] = self._initial[point_dict_key]['drew'], self._initial[point_dict_key]['drew']
#                 print 'rew: {}, tew: {}, taw: {}'.format(s['rew'], s['tew'], s['taw'])
#
#             else:
#                 m['pdr'], m['dr'] = self._initial['dr'], self._initial['dr']
#                 m['pde'], m['de'] = self._initial['de'], self._initial['de']
#                 m['pdrew'], m['drew'] = self._initial['drew'], self._initial['drew']
#                 print 'rew median: {}, mean {}, max {}, min {}'.format(median(s['rew']), s['rew'].mean(),
#                                                                        s['rew'].max(),
#                                                                        s['rew'].min())
#                 print 'tew median: {}, mean {}, max {}, min {}'.format(median(s['tew']), s['tew'].mean(),
#                                                                        s['tew'].max(),
#                                                                        s['tew'].min())
#                 print 'taw median: {}, mean {}, max {}, min {}'.format(median(s['taw']), s['taw'].mean(),
#                                                                        s['taw'].max(),
#                                                                        s['taw'].min())
#                 print 'soil_ksat median: {}, mean {}, max {}, min {}'.format(median(s['soil_ksat']),
#                                                                              s['soil_ksat'].mean(),
#                                                                              s['soil_ksat'].max(),
#                                                                              s['soil_ksat'].min())
#
#             self._initial_depletions = m['dr'] + m['de'] + m['drew']
#         else:
#             m['first_day'] = False
#
#         if self._point_dict:
#             self._do_daily_point_load(point_dict, day)
#         else:
#             self._do_daily_raster_load(ndvi_path, prism_path, penman_path, day)
#
#         # the soil ksat should be read each day from the static data, then set in the master #
#         # otherwise the static is updated and diminishes each day #
#         # [mm/day] #
#         if start_monsoon.timetuple().tm_yday <= day.timetuple().tm_yday <= end_monsoon.timetuple().tm_yday:
#             m['soil_ksat'] = s['soil_ksat'] * 2 / 24.
#         else:
#             m['soil_ksat'] = s['soil_ksat'] * 6 / 24.
#
#         if sensitivity:
#             self._do_parameter_adjustment(sensitivity_matrix_column)
#
#         self._do_dual_crop_coefficient(day)
#
#         self._do_snow()
#
#         self._do_soil_ksat_adjustment()
#         if swb_mode == 'fao':
#             self._do_fao_soil_water_balance(apply_rofrac, allen_ceff)
#         elif swb_mode == 'vertical':
#             self._do_vert_soil_water_balance(apply_rofrac, allen_ceff)
#
#         self._do_mass_balance(day, swb=swb_mode)
#
#         self._do_accumulations()
#
#         if day == start_date:
#             if self._point_dict:
#                 self.tracker = initialize_point_tracker(self._master)
#             else:
#                 self.tracker = initialize_master_tracker(self._master)
#
#         if point_dict:
#             self._update_point_tracker(day)
#         else:
#             self._raster_manager.update_raster_obj(m, day)
#             self._update_master_tracker(day)
#
#         if point_dict and day == end_date:
#             self._get_tracker_summary(self.tracker, point_dict_key)
#             # print 'returning tracker: {}'.format(self.tracker)
#             return self.tracker
#
#         elif day == end_date:
#             print 'last day: saving tabulated data'
#             self.save_tracker(self.tracker)
#
#             # if point_dict:
#             #     self._get_tracker_summary(self.tracker, point_dict_key)
