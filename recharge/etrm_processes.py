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
import shutil
import time
import numpy
import psutil
import csv
import pandas
import gdal
import ogr
import osgeo
from subprocess import call
from numpy import maximum, minimum, where, isnan, exp, median, full

from numpy import maximum, minimum, where, isnan, exp, median, nonzero, random, log, zeros_like

from app.paths import paths, PathsNotSetExecption
from recharge import MM
from recharge.dict_setup import initialize_master_dict, initialize_static_dict, initialize_initial_conditions_dict, \
    set_constants, initialize_master_tracker
from recharge.dynamic_raster_finder import get_penman, get_individ_kcb, get_kcb, get_prisms
from recharge.raster_manager import RasterManager
from recharge.tools import millimeter_to_acreft, unique_path, add_extension, time_it, day_generator
from scipy.stats import norm
from recharge.raster_tools import convert_raster_to_array

from recharge.dict_setup import initialize_point_tracker
from recharge.raster_tools import apply_mask, apply_mask_pixel_tracker
from utils.tracker_plot import run_tracker_plot


class NotConfiguredError(BaseException):
    def __str__(self):
        return 'The model has not been configured. Processes.configure_run must be called before Processes.run'


class Processes(object):
    """
    The purpose of this class is update the etrm master dict daily.

    See function explanations.

    """

    # Config values. Default values should be specified in RunSpec not here.
    _date_range = None
    _use_individual_kcb = None
    _ro_reinf_frac = None
    _swb_mode = None
    _rew_ceff = None
    _evap_ceff = None
    _winter_evap_limiter = None
    _winter_end_day = None
    _winter_start_day = None

    _is_configured = False

    def __init__(self, cfg, taw=None):
        # JIR
        # self.tracker = None
        self.taw = taw
        self.point_tracker = None
        self._initial_depletions = None

        if not paths.is_set():
            raise PathsNotSetExecption()

        self._cfg = cfg

        # set global mask and polygons paths
        paths.set_polygons_path(cfg.polygons)
        if cfg.mask:
            paths.set_mask_path(cfg.mask)
        if cfg.binary_shapefile:
            paths.set_point_shape_path(cfg.binary_shapefile)
        if cfg.use_verify_paths:
            paths.verify()

        print '##############################', paths.mask, cfg.mask
        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered

        self._info('Constructing/Initializing Processes')

        self._constants = set_constants()

        # Initialize point and raster dicts for static values (e.g. TAW) and initial conditions (e.g. de)
        # from spin up. Define shape of domain. Create a month and annual dict for output raster variables
        # as defined in self._outputs. Don't initialize point_tracker until a time step has passed #TODO - point_tracker?
        self._static = initialize_static_dict(cfg.static_pairs)

        # JIR
        # not necessary
        # self._initial = initialize_initial_conditions_dict(cfg.initial_pairs)

        self.xplot = self._cfg.xplot
        self.yplot = self._cfg.yplot
        self.plot_output = self._cfg.plot_output

        shape = self._static['taw'].shape  # Here's where the shape of the grid is determined GELP
        self._master = initialize_master_dict(shape)

        self._raster_manager = RasterManager(cfg, self.taw)

        self.initialize()

    def configure_run(self, runspec):
        """
        configure the model run with a RunSpec object

        :param runspec: RunSpec
        :return:
        """

        self._info('Configuring Processes')

        if runspec.save_dates:
            self.set_save_dates(runspec.save_dates)

        if runspec.taw_modification is not None:
            self.modify_taw(runspec.taw_modification)

        if runspec.uniform_taw is not None:
            self.uniform_taw(runspec.uniform_taw)

        self._date_range = runspec.date_range
        self._use_individual_kcb = runspec.use_individual_kcb
        self._ro_reinf_frac = runspec.ro_reinf_frac
        self._swb_mode = runspec.swb_mode
        self._rew_ceff = runspec.rew_ceff
        self._evap_ceff = runspec.evap_ceff
        self._winter_evap_limiter = runspec.winter_evap_limiter
        self._winter_end_day = runspec.winter_end_day
        self._winter_start_day = runspec.winter_start_day
        print '---------- CONFIGURATION ---------------'
        for attr in ('date_range', 'use_individual_kcb',
                     'winter_evap_limiter', 'winter_end_day', 'winter_start_day',
                     'ro_reinf_frac', 'swb_mode', 'rew_ceff', 'evap_ceff'):
            print '{:<20s}{}'.format(attr, getattr(self, '_{}'.format(attr)))
        print '----------------------------------------'
        self._is_configured = True

    def run(self):
        """
        run the ETRM model
        :return:
        """
        if not self._is_configured:
            raise NotConfiguredError()

        self._info('Run started. Simulation period: start={}, end={}'.format(*self._date_range))

        c = self._constants
        m = self._master
        s = self._static
        rm = self._raster_manager

        start_monsoon, end_monsoon = c['s_mon'].timetuple().tm_yday, c['e_mon'].timetuple().tm_yday
        self._info('Monsoon: {} to {}'.format(start_monsoon, end_monsoon))
        # big_counter = 0
        st = time.time()

        if self.point_tracker is None:
            # to avoid a memory leak, at this stage we write to a file.
            # initialize_point_tracker(m, point_arr)
            # self.point_tracker = True
            if paths.point_shape and os.path.isfile(paths.point_shape):
                point_arr = self._pixels_of_interest_to_array(paths.point_shape)
                self.point_tracker = initialize_point_tracker(m, point_arr)

        for counter, day in enumerate(day_generator(*self._date_range)):
            tm_yday = day.timetuple().tm_yday
            self._info('DAY:     {}({})'.format(day, tm_yday))

            time_it(self._do_daily_raster_load, day)
            # modify the PRISM precipitation
            if start_monsoon <= tm_yday <= end_monsoon:
                m['precip'] = maximum((m['precip'] - 1.612722) / 0.676904, 0)
            else:
                m['precip'] = maximum((m['precip'] - 0.488870) / 0.993831, 0)

            m['inten'] = m['precip'] * 0

            # generate random number
            random_number = random.randn()
            percentile = norm.cdf(random_number)

            log_precip = log(m['precip'][m['precip'] > 0])
            log_inten = zeros_like(log_precip)
            if start_monsoon <= tm_yday <= end_monsoon:
                log_inten[log_precip < 0] = norm.ppf(percentile, -2.43, 1.21)
                log_inten[(log_precip >= 0) & (log_precip < 0.5)] = norm.ppf(percentile, -2.89, 1.06)
                log_inten[(log_precip >= 0.5) & (log_precip < 1)] = norm.ppf(percentile, -2.83, 0.96)
                log_inten[(log_precip >= 1) & (log_precip < 1.5)] = norm.ppf(percentile, -2.57, 0.95)
                log_inten[(log_precip >= 1.5) & (log_precip < 2)] = norm.ppf(percentile, -2.44, 0.90)
                log_inten[(log_precip >= 2) & (log_precip < 2.5)] = norm.ppf(percentile, -2.31, 0.89)
                log_inten[(log_precip >= 2.5) & (log_precip < 3)] = norm.ppf(percentile, -2.18, 0.84)
                log_inten[(log_precip >= 3) & (log_precip < 3.5)] = norm.ppf(percentile, -1.85, 0.77)
                log_inten[log_precip >= 3.5] = norm.ppf(percentile, -1.86, 0.73)
            else:
                log_inten[log_precip < 0] = norm.ppf(percentile, -2.77, 1.33)
                log_inten[(log_precip >= 0) & (log_precip < 0.5)] = norm.ppf(percentile, -3.48, 0.91)
                log_inten[(log_precip >= 0.5) & (log_precip < 1)] = norm.ppf(percentile, -3.47, 0.77)
                log_inten[(log_precip >= 1) & (log_precip < 1.5)] = norm.ppf(percentile, -3.37, 0.70)
                log_inten[(log_precip >= 1.5) & (log_precip < 2)] = norm.ppf(percentile, -3.38, 0.61)
                log_inten[(log_precip >= 2) & (log_precip < 2.5)] = norm.ppf(percentile, -3.28, 0.65)
                log_inten[(log_precip >= 2.5) & (log_precip < 3)] = norm.ppf(percentile, -3.08, 0.56)
                log_inten[(log_precip >= 3) & (log_precip < 3.5)] = norm.ppf(percentile, -3.12, 0.45)
                log_inten[log_precip >= 3.5] = norm.ppf(percentile, -3.13, 0.66)

            m['inten'][m['precip'] > 0] = exp(log_inten)  # mm/min

            # Assume 2-hour storms in the monsoon season, and 6 hour storms otherwise
            # If melt is occurring (calculated in _do_snow), infiltration will be set to 24 hours
            # [mm/day] #
            m['soil_ksat'] = s['soil_ksat']
            # ksat-runoff version
            # if start_monsoon <= tm_yday <= end_monsoon:
            #     m['soil_ksat'] = s['soil_ksat'] * 2 / 24.
            # else:
            #     m['soil_ksat'] = s['soil_ksat'] * 6 / 24.

            time_it(self._do_snow, m, c)
            # time_it(self._do_soil_ksat_adjustment, m, s) # forest litter adjustment is hard to justify
            time_it(self._do_dual_crop_transpiration, tm_yday, m, s, c)
            time_it(self._do_fraction_covered, m, s, c)

            # if self._swb_mode == 'fao':
            #     time_it(self._do_fao_soil_water_balance, m, s, c)
            # elif self._swb_mode == 'vertical':
            #     time_it(self._do_vert_soil_water_balance, m, s, c)

            func = self._do_fao_soil_water_balance if self._swb_mode == 'fao' else self._do_vert_soil_water_balance
            time_it(func, m, s, c, tm_yday)

            time_it(self._do_mass_balance, day, swb=self._swb_mode)

            time_it(self._do_accumulations)

            time_it(rm.update_raster_obj, m, day)

            is_first = counter == 0
            time_it(self._update_master_tracker, m, day, is_first)
            self._update_point_tracker(m, day, is_first)

        self._info('saving tabulated data')
        time_it(rm.save_csv)

        if paths.mask is not None:
            self.save_mask()

        # self.save_tracker() #TODO check gabe merge
        self._info('Execution time: {}'.format(time.time() - st))

    def set_save_dates(self, dates):
        """
        set the individual days to write

        :param dates: list of datetimes
        :return:
        """
        self._raster_manager.set_save_dates(dates)

    def modify_master(self, alpha=1, beta=1, gamma=1, zeta=1, theta=1):
        """
        modify the master dictionary

        :param alpha: temp scalar
        :param beta: precip scalar
        :param gamma: etrs scalar
        :param zeta: kcb scalar
        :param theta: soil_ksat scalar
        :return:
        """
        m = self._master
        m['temp'] += alpha
        m['precip'] *= beta
        m['etrs'] *= gamma
        m['kcb'] *= zeta
        m['soil_ksat'] *= theta

    def modify_taw(self, taw_modification):
        """
        Gets the taw array, modifies it by a constant scalar value
        (taw_modification) and returns the resulting array

        :param taw_modification: object
        :return: taw array

        """

        s = self._static
        taw = s['taw']
        taw = taw * taw_modification
        s['taw'] = taw

        return taw

    def uniform_taw(self, taw_value):
        """Replaces the taw array with a single value

        :param taw_value: object
        :return taw_uniform array

        """
        print '===========================\nrunning uniform_taw\n==========================='
        m = self._master  # testing 6/2/17
        s = self._static
        taw = s['taw']
        taw_shape = taw.shape
        s['taw'] = numpy.full(taw_shape, taw_value)
        taw = s['taw']
        m['pdr'] = m['dr'] = taw

        return taw

    def get_taw(self):
        """
        Gets the TAW array and returns it

        :return: TAW array
        """

        s = self._static
        taw = s['taw']

        return taw

    def initialize(self):
        """
        initialize the models initial state

        :return:
        """
        # JIR
        initial = initialize_initial_conditions_dict(self._cfg.initial_pairs)

        self._info('Initialize initial model state')
        m = self._master

        # option to force dry TAW start conditions
        initial_state = 'wet'  # 'dry'
        if initial_state is 'wet':
            m['pdr'] = m['dr'] = initial['dr']
        elif initial_state is 'dry':
            m['pdr'] = m['dr'] = self._static['taw']  # This makes the whole state start totally dry
        print 'initial dr {}'.format(initial['dr'])

        # JIR
        m['pde'] = m['de'] = initial['de']
        m['pdrew'] = m['drew'] = initial['drew']

        s = self._static
        for key in ('rew', 'tew', 'taw', 'soil_ksat'):
            v = s[key]
            msg = '{} median: {}, mean: {}, max: {}, min: {}'.format(key, median(v), v.mean(), v.max(), v.min())
            self._debug(msg)

        self._initial_depletions = m['dr']  # + m['de'] + m['drew']

    def save_mask(self):
        path = paths.mask
        if path is not None:
            self._info('saving mask to results')

            # copy the mask path file into results
            name = os.path.basename(path)
            shutil.copyfile(path, os.path.join(paths.results_root, name))

    # def save_point_tracker(self, path=None):
    #
    #     output_loc = paths.etrm_output_root
    #     count = 0
    #
    #     csv_pathlist = []
    #     for tuple in self.point_tracker:
    #
    #         base = 'etrm_tracker_{:03n}'.format(count)
    #
    #         if path is None:
    #             path = add_extension(os.path.join(output_loc, base), '.csv')
    #
    #         if os.path.isfile(path):
    #             path = unique_path(output_loc, base, '.csv')
    #
    #         path = add_extension(path, '.csv')
    #         print 'this should be your csv: {}'.format(path)
    #         print tuple, 'self. point tracker'
    #         tuple[1].to_csv(path, na_rep='nan', index_label='Date')
    #         count += 1
    #
    #         csv_pathlist.append(path)
    #     return csv_pathlist

    # JIR # TODO check gabe merge
    # def save_tracker(self, path=None):
    #     """
    #
    #     :param path:
    #     :return:
    #     """
    #     self._info('Saving tracker')
    #
    #     root = paths.results_root
    #     base = 'etrm_master_tracker'
    #     if path is None:
    #         path = add_extension(os.path.join(root, base), '.csv')
    #
    #     if os.path.isfile(path):
    #         path = unique_path(root, base, '.csv')
    #
    #     path = add_extension(path, '.csv')
    #     print 'this should be your csv: {}'.format(path)
    #     print self.tracker, 'self. tracker'
    #     self.tracker.to_csv(path, na_rep='nan', index_label='Date')

    # JIR
    def _get_tracker_path(self, path=None):
        root = paths.results_root
        base = 'etrm_master_tracker'
        if path is None:
            path = add_extension(os.path.join(root, base), '.csv')

        # if os.path.isfile(path):
        #     path = unique_path(root, base, '.csv')

        path = add_extension(path, '.csv')
        return path

    def _do_snow(self, m, c):
        """ Calibrated snow model that runs using PRISM temperature and precipitation.

        :return: None
        """

        temp = m['temp']
        palb = m['albedo']

        precip = m['precip']

        a_min = c['a_min']
        a_max = c['a_max']

        # The threshold values here were 0.0 and were changed to 4.0 in revision 84238ff
        # If the threshold values are going to be manipulated then the should change to Config values
        # and be set in the configuration file
        sf = where(temp < 4.0, precip, 0)
        rain = where(temp >= 4.0, precip, 0)

        alb = where(sf > 3.0, a_max, palb)
        alb = where(sf <= 3.0, a_min + (palb - a_min) * exp(-0.12), alb)
        alb = where(sf == 0.0, a_min + (palb - a_min) * exp(-0.05), alb)
        alb = where(alb < a_min, a_min, alb)

        m['swe'] += sf

        melt = maximum(((1 - alb) * m['rg'] * c['snow_alpha']) + (temp - 1.8) * c['snow_beta'], 0)

        m['melt'] = melt = minimum(m['swe'], melt)
        m['swe'] -= melt

        m['rain'] = rain
        m['snow_fall'] = sf
        m['albedo'] = alb

    def _do_soil_ksat_adjustment(self, m, s):
        """ Adjust soil hydraulic conductivity according to land surface cover type.

        :return: None
        """

        water = m['rain'] + m['melt']
        land_cover = s['land_cover']
        soil_ksat = m['soil_ksat']

        # TO DO: Fix limits to match mm/day units
        for lc, wthres, ksat_scalar in ((41, 50.0, 2.0),
                                        (41, 12.0, 1.2),

                                        (42, 50.0, 2.0),
                                        (42, 12.0, 1.2),

                                        (43, 50.0, 2.0),
                                        (43, 12.0, 1.2)):
            soil_ksat = where((land_cover == lc) & (water < wthres), soil_ksat * ksat_scalar, soil_ksat)

        m['soil_ksat'] = soil_ksat

    def _do_dual_crop_transpiration(self, tm_yday, m, s, c):
        """ Calculate dual crop coefficients for transpiration only.

        """

        # basal crop coefficient - GELP
        kcb = m['kcb']
        # Ref ET -GELP
        etrs = m['etrs']
        # Root zone depletion -GELP
        pdr = m['dr']

        ####
        # transpiration:
        # ks- stress coeff- ASCE pg 226, Eq 10.6
        # TAW could be zero at lakes.
        taw = maximum(s['taw'], 0.001)
        ks = ((taw - pdr) / ((1 - c['p']) * taw))
        ks = minimum(1 + 0.001, ks)  # this +0.001 may be unneeded
        ks = maximum(0, ks)
        m['ks'] = ks

        # Transpiration from dual crop coefficient
        transp = maximum(ks * kcb * etrs, 0.0)

        # enforce winter dormancy of vegetation
        m['transp_adj'] = False
        if self._winter_end_day > tm_yday or tm_yday > self._winter_start_day:
            # super-important winter evap limiter. Jan suggested 0.03 (aka 3%) but that doesn't match ameriflux.
            # Using 30% DDC 2/20/17
            transp *= self._winter_evap_limiter
            m['transp_adj'] = True

        # limit transpiration so it doesn't exceed the amount of water available in the root zone
        transp = minimum(transp, (taw - pdr))
        m['transp'] = transp

    def _do_fraction_covered(self, m, s, c):
        """ Calculate covered fraction and fraction evaporating-wetted.

        """
        kcb = m['kcb']
        kc_max = maximum(c['kc_max'], kcb + 0.05)
        kc_min = c['kc_min']

        # Cover Fraction- ASCE pg 199, Eq 9.27
        plant_exponent = s['plant_height'] * 0.5 + 1  # h varaible, derived from ??
        numerator_term = maximum(kcb - kc_min, 0.01)
        denominator_term = maximum(kc_max - kc_min, 0.01)

        cover_fraction_unbound = (numerator_term / denominator_term) ** plant_exponent

        # ASCE pg 198, Eq 9.26
        m['fcov'] = fcov = maximum(minimum(cover_fraction_unbound, 1), 0.001)  # covered fraction of ground
        m['few'] = maximum(1 - fcov, 0.001)  # uncovered fraction of ground

    def _do_fao_soil_water_balance(self, m, s, c, tm_yday, ro_local_reinfilt_frac=None, rew_ceff=None, evap_ceff=None):
        """ Calculate evap and all soil water balance at each time step.

        """
        if ro_local_reinfilt_frac is None:
            ro_local_reinfilt_frac = self._ro_reinf_frac

        if rew_ceff is None:
            rew_ceff = self._rew_ceff

        if evap_ceff is None:
            evap_ceff = self._evap_ceff

        m['pdr'] = pdr = m['dr']
        m['pde'] = pde = m['de']
        m['pdrew'] = pdrew = m['drew']

        taw = maximum(s['taw'], 0.001)
        m['taw'] = taw  # add taw to master dict - Jul 9 2017, GELP
        tew = maximum(s['tew'], 0.001)  # TEW is zero at lakes in our data set
        rew = s['rew']

        kcb = m['kcb']
        kc_max = maximum(c['kc_max'], kcb + 0.05)
        ks = m['ks']
        etrs = m['etrs']  # comes from get_penman function

        # Start Evaporation Energy Balancing
        st_1_dur = (s['rew'] - m['pdrew']) / (c['ke_max'] * etrs)  # ASCE 194 Eq 9.22; called Fstage1
        st_1_dur = minimum(st_1_dur, 1.0)
        m['st_1_dur'] = st_1_dur = maximum(st_1_dur, 0)
        m['st_2_dur'] = st_2_dur = (1.0 - st_1_dur)

        # kr- evaporation reduction coefficient Allen 2011 Eq
        # Slightly different from 7ASCE pg 193, eq 9.21, but the Fstage coefficients come into the ke calc.
        tew_rew_diff = maximum(tew - rew, 0.001)
        kr = maximum(minimum((tew - m['pde']) / (tew_rew_diff), 1), 0)
        # EXPERIMENTAL: stage two evap has been too high, force slowdown with decay
        # kr *= (1 / m['dry_days'] **2)

        m['kr'] = kr

        # Simple version for 3-bucket model
        ke_init = (kc_max - (ks * kcb))
        m['ke_init'] = ke_init

        # ke evaporation efficency; Allen 2011, Eq 13a
        few = m['few']
        ke = minimum((st_1_dur + st_2_dur * kr) * (kc_max - (ks * kcb)), few * kc_max)
        ke = maximum(0.0, minimum(ke, 1))
        m['ke'] = ke

        # Ketchum Thesis eq 36, 37
        e1 = st_1_dur * ke_init * etrs
        m['evap_1'] = minimum(e1, rew - pdrew)
        e2 = st_2_dur * kr * ke_init * etrs
        m['evap_2'] = minimum(e2, (tew - pde) - e1)

        # Allen 2011
        evap = ke * etrs

        # limit evap so it doesn't exceed the amount of soil moisture available in the TEW
        evap = minimum(evap, (tew - pde))

        # limit evap so it doesn't exceed the amount of soil moisture available after transp occurs
        transp = m['transp']
        m['evap'] = evap = minimum(evap, (taw - pdr) - transp)

        m['eta'] = et_actual = evap + transp

        # Start Water Balance
        water = m['rain'] + m['melt']

        # if snow is melting, set ksat to 24 hour value
        m['soil_ksat'] = soil_ksat = where(m['melt'] > 0.0, s['soil_ksat'], m['soil_ksat'])

        # Dry days are only used if Experimental stage 2 reduction is used
        dd = m['dry_days']
        dd = where(water < 0.1, dd + 1, 1)
        m['dry_days'] = dd

        # Surface runoff (Hortonian- using storm duration modified ksat values)
        # ro = where(water > soil_ksat, water - soil_ksat, 0)
        # ro *= (1 - ro_local_reinfilt_frac)
        '''Esther's Stats'''
        num = random.uniform(0, 1)
        start_monsoon, end_monsoon = c['s_mon'].timetuple().tm_yday, c['e_mon'].timetuple().tm_yday
        if start_monsoon <= tm_yday <= end_monsoon:
            ro = 0.001160957 * (m['rain'] ** 2) + 0.199019984 * m['rain'] * m['inten']
            if num > 0.01392405:
                ro = where(m['rain'] <= 2, 0, ro)
            if num > 0.05977011:
                ro = where((m['rain'] <= 5) & (m['rain'] > 2), 0, ro)
            if num > 0.06521739:
                ro = where((m['rain'] <= 8) & (m['rain'] > 5), 0, ro)
            if num > 0.2393617:
                ro = where((m['rain'] <= 12) & (m['rain'] > 8), 0, ro)
            if num > 0.4554455:
                ro = where((m['rain'] <= 22) & (m['rain'] > 12), 0, ro)
            if num > 0.8:
                ro = where((m['rain'] <= 40) & (m['rain'] > 22), 0, ro)
            if num > 0.9:
                ro = where(m['rain'] > 40, 0, ro)
        else:
            ro = 0.0003765849 * (m['rain'] ** 2) + 0.0964337598 * m['rain'] * m['inten']
            if num > 0.001658375:
                ro = where(m['rain'] <= 10, 0, ro)
            if num > 0.05504587:
                ro = where((m['rain'] <= 20) & (m['rain'] > 10), 0, ro)
            if num > 0.1111111:
                ro = where((m['rain'] <= 30) & (m['rain'] > 20), 0, ro)
            if num > 0.5454545:
                ro = where(m['rain'] > 30, 0, ro)
        m['ro'] = ro

        # Calculate Deep Percolation (recharge or infiltration)
        m['infil'] = dp = maximum(water - ro - et_actual - pdr, 0)

        # Calculate depletion in TAW, full root zone
        m['dr'] = dr = minimum(maximum(pdr - (water - ro) + et_actual + dp, 0), taw)

        # Calculate depletion in TEW, full evaporative layer
        # ceff, capture efficiency, reduces depletion recovery as representation of bypass flow through macropores
        m['de'] = de = minimum(maximum(pde - ((water - ro) * evap_ceff) + evap / few, 0), tew)

        # Calculate depletion in REW, skin layer; ceff, capture efficiency, reduces depletion recovery
        m['drew'] = minimum(maximum(pdrew - ((water - ro) * rew_ceff) + evap / few, 0), rew)

        m['soil_storage'] = (pdr - dr)

        m['rzsm'] = 1 - (dr / taw)  # add root zone soil moisture (RZSM) to master dict - Jul 9, 2017 GELP

    def _do_vert_soil_water_balance(self, m, s, c, tm_yday, ro_local_reinfilt_frac=None, rew_ceff=None):
        """ Calculate all soil water balance at each time step.

        :return: None
        """

        if ro_local_reinfilt_frac is None:
            ro_local_reinfilt_frac = self._ro_reinf_frac

        if rew_ceff is None:
            rew_ceff = self._rew_ceff

        kcb = m['kcb']
        etrs = m['etrs']
        kc_max = maximum(c['kc_max'], kcb + 0.05)
        ks = m['ks']

        st_1_dur = (s['rew'] - m['pdrew']) / (c['ke_max'] * etrs)  # ASCE 194 Eq 9.22; called Fstage1
        # st_1_dur = (s['rew'] - m['pdrew']) / ((c['kc_max'] - (m['ks'] * m['kcb'])) * m['etrs'])
        st_1_dur = minimum(st_1_dur, 0.99)
        m['st_1_dur'] = st_1_dur = maximum(st_1_dur, 0)
        m['st_2_dur'] = st_2_dur = (1 - st_1_dur)

        # kr- evaporation reduction coefficient Allen 2011 Eq
        # Slightly different from 7ASCE pg 193, eq 9.21, but the Fstage coefficients come into the ke calc.
        # TEW is zero at lakes.
        tew = maximum(s['tew'], 0.001)
        kr = maximum(minimum((tew - m['pde']) / tew, 1), 0.001)
        # EXPERIMENTAL: stage two evap has been too high, force slowdown with decay
        # kr *= (1 / m['dry_days'] **2)

        m['kr'] = kr

        # Simple version for 3-bucket model
        ke_init = (kc_max - (ks * kcb))
        m['ke_init'] = ke_init

        # ke evaporation efficency; Allen 2011, Eq 13a
        few = m['few']
        ke = minimum((st_1_dur + st_2_dur * kr) * (kc_max - (ks * kcb)), few * kc_max)
        ke = maximum(0.0, minimum(ke, 1))
        m['ke'] = ke

        # Ketchum Thesis eq 36, 37
        m['evap_1'] = e1 = st_1_dur * ke_init * etrs
        m['evap_2'] = e2 = st_2_dur * kr * ke_init * etrs

        # Allen 2011
        # problem: what if evap exceedes water avialable in TEW (i.e. evap > tew-pde
        m['evap'] = e1 + e2

        # if snow is melting, set ksat to 24 hour value
        m['soil_ksat'] = soil_ksat = where(m['melt'] > 0.0, s['soil_ksat'], m['soil_ksat'])

        m['pdr'] = pdr = m['dr']
        m['pde'] = pde = m['de']
        m['pdrew'] = pdrew = m['drew']

        rew = m['rew'] = s['rew']
        tew = m['tew'] = s['tew']
        taw = m['taw'] = s['taw']

        # impose limits on vaporization according to present depletions #
        # we can't vaporize more than present difference between current available and limit (i.e. taw - dr) #
        evap_1 = m['evap_1']
        wrew = rew - pdrew
        evap_1 = where(evap_1 > wrew, wrew, evap_1)
        evap_1[evap_1 < 0] = 0

        evap_2 = m['evap_2']
        wtew = tew - pde
        evap_2 = where(evap_2 > wtew, wtew, evap_2)
        evap_2[evap_2 < 0] = 0

        transp = m['transp']
        wr = taw - m['pdr']
        transp = where(transp > wr, wr, transp)

        m['eta'] = transp + evap_1 + evap_2
        m['evap_1'] = evap_1
        m['evap_2'] = evap_2
        m['evap'] = evap_1 + evap_2
        m['transp'] = transp

        # apply water to the surface
        water = m['rain'] + m['melt']
        # m['dry_days'] = where(water < 0.1, m['dry_days'] + self._ones, self._ones)
        dd = m['dry_days']
        dd = where(water < 0.1, dd + 1, 1)
        m['dry_days'] = dd

        # it is difficult to ensure mass balance in the following code: do not touch/change w/o testing #
        ##

        # Surface runoff (Hortonian- using storm duration modified ksat values)
        ro = where(water > soil_ksat, water - soil_ksat, 0)
        water = where(water > soil_ksat, soil_ksat, water)
        water_av_taw = ro * ro_local_reinfilt_frac
        ro *= (1 - ro_local_reinfilt_frac)
        m['ro'] = ro
        # water balance through the stage 1 evaporation layer #
        # capture efficiency of soil- some water may bypass REW even before it fills
        water_av_rew = water * rew_ceff
        m['drew_water'] = water_av_rew  # store value of water delivered to evap layer
        water_av_tew = water * (1.0 - rew_ceff)

        # fill depletion in REW if possible
        # water_av_tew, drew = self._fill_depletions(water_av_rew, water_av_tew, rew, pdrew + evap_1)

        # fill depletion in REW if possible
        depletion = pdrew + evap_1
        drew = where(water_av_rew >= depletion, 0, depletion - water_av_rew)
        # drew = minimum(drew, rew) # redundant check

        # add excess water to the water available to TEW (Is this coding ok?)
        water_av_tew = where(water_av_rew >= depletion, water_av_tew + water_av_rew - depletion, water_av_tew)

        # water balance through the stage 2 evaporation layer #
        # capture efficiency of soil- some water may bypass TEW even before it fills
        water_av_taw = water_av_taw + (water_av_tew * (1.0 - rew_ceff))
        water_av_tew = water_av_tew * rew_ceff
        m['de_water'] = water_av_tew  # store value of water delivered to evap layer

        # fill depletion in TEW if possible
        # water_av_taw, de = self._fill_depletions(water_av_tew, water_av_taw, tew, pde + evap_2)

        # fill depletion in TEW if possible
        depletion = pde + evap_2
        de = where(water_av_tew >= depletion, 0, depletion - water_av_tew)
        # de = minimum(de, tew) # redundant check

        # add excess water to the water available to TAW (Help coding this more cleanly?)
        water_av_taw = where(water_av_tew >= depletion,
                             water_av_taw + water_av_tew - depletion,
                             water_av_taw)

        # water balance through the root zone layer #
        m['dr_water'] = water_av_taw  # store value of water delivered to root zone

        # fill depletion in TAW if possible
        depletion = pdr + transp

        m['infil'] = where(water_av_taw >= depletion, water_av_taw - depletion, 0)
        dr = where(water_av_taw >= depletion, 0, depletion - water_av_taw)

        m['soil_storage'] = (pdr + pde + pdrew - dr - de - drew)

        m['drew'] = drew
        m['de'] = de
        m['dr'] = dr

    def _fill_depletions(self, arr_1, arr_2, t, evap):

        # fill depletion in REW if possible
        drew = where(arr_1 >= evap, 0, evap - arr_1)
        drew = minimum(drew, t)

        # add excess water to the water available to TEW (Is this coding ok?)
        arr_2 = where(arr_1 >= evap, arr_2 + arr_1 - evap, arr_2)

        return arr_2, drew

    def _do_accumulations(self):
        """ This function simply accumulates all terms.

        :return: None
        """
        m = self._master

        for k in ('infil', 'etrs', 'eta', 'precip', 'rain', 'melt', 'ro', 'swe'):
            kk = 'tot_{}'.format(k)
            m[kk] = m[k] + m[kk]

        m['soil_storage_all'] = self._initial_depletions - (m['pdr'])  # removed m['pde'] + m['pdrew'] 6/2/17

        func = self._output_function
        ms = [func(m[k]) for k in ('infil', 'etrs', 'eta', 'precip', 'ro', 'swe', 'soil_storage')]
        print 'today infil: {}, etrs: {}, eta: {}, precip: {}, ro: {}, swe: {}, stor {}'.format(*ms)

        ms = [func(m[k]) for k in ('tot_infil', 'tot_etrs', 'tot_eta', 'tot_precip', 'tot_ro', 'tot_swe')]
        print 'total infil: {}, etrs: {}, eta: {}, precip: {}, ro: {}, swe: {}'.format(*ms)

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
        self._debug('total mass balance error: {}'.format(self._output_function(tot_mass)))

    def _do_daily_raster_load(self, date):
        """ Find daily raster image for each ETRM input.

        param date: datetime.day object
        :return: None
        """
        m = self._master

        if self._use_individual_kcb:
            func = get_individ_kcb
        else:
            func = get_kcb

        kcb = time_it(func, date, m['pkcb'])

        m['kcb'] = kcb
        min_temp, max_temp, temp, precip = time_it(get_prisms, date, self._cfg.is_reduced)
        m['min_temp'] = min_temp
        m['max_temp'] = max_temp
        m['temp'] = temp
        m['precip'] = precip

        # m['min_temp'] = min_temp = get_prism(date, variable='min_temp')
        # m['max_temp'] = max_temp = get_prism(date, variable='max_temp')
        #
        # m['temp'] = (min_temp + max_temp) / 2
        #
        # precip = get_prism(date, variable='precip')
        # m['precip'] = where(precip < 0, 0, precip)

        etrs = time_it(get_penman, date, variable='etrs')
        etrs = where(etrs < 0, 0, etrs)
        m['etrs'] = where(isnan(etrs), 0, etrs)

        m['rg'] = time_it(get_penman, date, variable='rg')

        m['pkcb'] = m['kcb']

    # def _do_parameter_adjustment(self, m, s, adjustment_array):
    #
    #     alpha, beta, gamma, delta, zeta, theta = adjustment_array
    #     if m['first_day']:
    #         print 'a: {}, b: {}, gam: {}, del: {}, z: {}, theta: {}'.format(*adjustment_array)
    #         # taw is found once, and should be modified once
    #         s['taw'] *= delta
    #     # these are found daily, so can be modified daily
    #     m['temp'] += alpha
    #     m['precip'] *= beta
    #     m['etrs'] *= gamma
    #     m['kcb'] *= zeta
    #     m['soil_ksat'] *= theta

    # TODO - eventually make point_tracker work from a shapefile. Code is below -vvv-
    # def _shapefile_to_array(self, point_shape):
    #     """
    #     takes a point shapefile that has any number of points of attribute value 1.
    #     :param point_shape:
    #     :return:
    #     This function converts the shapefile into a .tif of the entire model domain with pixel values of 1
    #     corresponding to the points in the shapefile and zeros everywhere else.
    #     Then, the .tif is converted into an array with the convert_raster_to_array function and that output array is
    #     returned.
    #     """
    #     print 'shapefile path', point_shape
    #     point_data = ogr.Open(point_shape)
    #
    #     print 'point_data', point_data
    #
    #     print 'cfg.new_mexico_extent', self._cfg.new_mexico_extent
    #     #convert_raster_to_array()
    #     if self._cfg.new_mexico_extent == True:
    #         rasterize = 'gdal_rasterize -a id -ts 2272 2525 -tr 250 250 -te 114757 3471163 682757 4102413 -l pixel_shapefile_for_mask {} /Users/Gabe/Desktop/exp/pixel_mask_for_array.tif'.format(point_shape)
    #         print rasterize
    #         call(rasterize)
    #
    #     else:
    #         print '_shapefile_to_array only formatted to work with a new_mexico extent of \n \
    #               -te 114757 3471163 682757 4102413 -ts 2272 2525 -tr 250 250. If different extent needed,\n \
    #           edit _shapefile_to_array function '
    #         pass
    #
    #     # rasterize = 'gdal_rasterize -a id -ts 2272 -tr 250 250 -te 114757 3471163 682757 4102413 \
    #     #              -l pixel_shapefile_for_mask /Users/Gabe/Desktop/RZSM_analysis/pixel_shapefile_for_mask.shp \
    #     #               /Users/Gabe/Desktop/experimental_rasterize/pixel_mask_for_array.tif'
    #     # gdal_rasterize - a
    #     # id - l
    #     # pixel_shapefile_for_mask / Users / Gabe / Desktop / RZSM_analysis / pixel_shapefile_for_mask.shp

    def _pixels_of_interest_to_array(self, point_tif):

        # =========== Jul 8, 2017
        # print 'point tif', point_tif

        point_arr = convert_raster_to_array(point_tif)

        try:
            if os.path.isfile(paths.mask):
                point_arr = apply_mask(paths.mask, point_arr)
        except TypeError:
            pass

        point_arr = apply_mask_pixel_tracker(paths.point_shape, point_arr)

        # print 'new point arr', point_arr
        # print 'new point arr shape', point_arr.shape

        return point_arr
        # ============

    def _update_point_tracker(self, m, date, is_first):
        """

        :param m: Master dict of the processes class.
        :param date: The date of the current timestep to be recorded
        :return: Writes to a csv file the important things to track for a given pixel. Each pixel has its own csv.
        """

        # print "UPDATING POINT TRACKER"
        # print "==\nTHIS is the POINT TRACKER\n=={}".format(self.point_tracker)
        # # print self.point_tracker
        # total_mem = 0
        # for index, dataframe in self.point_tracker:
        #     mem = dataframe.memory_usage(index=False)
        #     # print "mem {}".format(mem)
        #     total_mem += mem
        #
        # print "Total memory used by {} is {}".format(date, total_mem)
        # # Todo - write memory values and date to text file
        # the item tracker has been initialized and written to csv in _initialize_point_tracker
        # Here we just append the "item_tracker" to the correct csv...
        # get the file directory and loop through
        tracker_files_path = paths.tracker_csv_path

        for root, dirs, files in os.walk(tracker_files_path, topdown=False):
            # print "paaaath", root
            # print "dirs", dirs
            # print "files leeeest", files
            for f in files:
                # print "FFFF", f
                file_indx = f.split("_")[-1]
                # print "AAA", file_indx
                file_indx = file_indx.split('.')[0]
                # print "BBB", file_indx

                # print "FILE index ", file_indx
                for index, cols in self.point_tracker:
                    # print "this is the index", index
                    if "{}".format(index[0]) == file_indx:
                        # print "MAAATCH"
                        # TODO - Now we are going to append this to the correct .csv from initialize.
                        # append this to a file.
                        keys = sorted(m.keys())
                        values = [m[key][index[1]] for key in keys if key not in ('transp_adj',)]

                        self._write_csv('Point Tracker', os.path.join(root, f), date, keys, values, is_first)
                        # for key in sorted(m):
                        #     if key not in ('transp_adj',):
                        #         print "update Keys!!!", key
                        # item_tracker = [date] + item_tracker
                        # # print "about to write"
                        # with open(os.root.join(root, f), 'a') as append_file:
                        #     writer = csv.writer(append_file)
                        #     writer.writerow(item_tracker)

    def _update_master_tracker(self, m, date, is_first):  # TODO check gabe merge
        def factory(k):

            v = m[k]

            if k in ('dry_days', 'kcb', 'kr', 'ks', 'ke', 'fcov', 'few', 'albedo',
                     'max_temp', 'min_temp', 'rg', 'st_1_dur', 'st_2_dur',):
                v = v.mean()
            elif k == 'transp_adj':
                v = median(v)
            else:
                v = self._output_function(v)
            return v

        keys = sorted(m.keys())
        values = [factory(key) for key in keys]
        path = self._get_tracker_path()
        self._write_csv('Master tracker', path, date, keys, values, is_first)
        
    def _write_csv(self, msg, path, date, keys, values, is_first):
        values = [str(v) for v in values]
        lines = ['{},{}'.format(date, ','.join(values))]
        if is_first:
            header = 'date,{}'.format(','.join(keys))
            print 'writinsad heasder', msg, header
            lines.insert(0, header)

        print '{} - path {}'.format(msg, path)
        with open(path, 'a') as wfile:
            for line in lines:
                wfile.write('{}\n'.format(line))
                
    def _output_function(self, param):
        '''determine if units are acre-feet (volume, summed over area of interest) or mm (average depth)'''
        if self._cfg.output_units == MM:
            param = param.mean()
        if not self._cfg.output_units == MM:
            param = millimeter_to_acreft(param)
        return param

    # JIR
    # def _get_tracker_summary(self, tracker, name):
    #     s = self._static[name]
    #
    #     s1 = tracker['evap_1'].sum()
    #     s2 = tracker['evap_2'].sum()
    #     et = tracker['evap'].sum()
    #     ts = tracker['transp'].sum()
    #
    #     ps = tracker['precip'].sum()
    #     rs = tracker['rain'].sum()
    #     ms = tracker['melt'].sum()
    #     ros = tracker['ro'].sum()
    #     infils = tracker['infil'].sum()
    #
    #     # print 'summary stats for {}:\n{}'.format(name, tracker.describe())
    #     print '---------------------------------Tracker Summary--------------------------------'
    #     print 'a look at vaporization:'
    #     print 'stage one  = {}, stage two  = {}, together = {},  total evap: {}'.format(s1, s2, s1 + s2, et)
    #     print 'total transpiration = {}'.format(ts)
    #
    #     depletions = ('drew', 'de', 'dr')
    #     capacities = (s['rew'], s['tew'], s['taw'])
    #
    #     starting_water = sum((x - tracker[y][0] for x, y in zip(capacities, depletions)))
    #     ending_water = sum((x - tracker[y][-1] for x, y in zip(capacities, depletions)))
    #
    #     delta_soil_water = ending_water - starting_water
    #     print 'soil water change = {}'.format(delta_soil_water)
    #
    #     print 'input precip = {}, rain = {}, melt = {}'.format(ps, rs, ms)
    #
    #     rswe = tracker['swe'][-1]
    #     print 'remaining snow on ground (swe) = {}'.format(rswe)
    #
    #     input_sum = rswe + ms + rs
    #
    #     print 'total inputs (swe, rain, melt): {}'.format(input_sum)
    #     print 'swe + melt + rain ({}) should equal precip ({})'.format(input_sum, ps)
    #     print 'total runoff = {}, total recharge = {}'.format(ros, infils)
    #
    #     output_sum = ts + et + ros + infils
    #
    #     output_sum += delta_soil_water + rswe  # added swe to output_sum; Dan, 2/11/17
    #
    #     print 'total outputs (transpiration, evaporation, runoff, recharge, delta soil water) = {}'.format(output_sum)
    #     mass_balance = input_sum - output_sum
    #     mass_percent = (mass_balance / input_sum) * 100
    #     print 'overall water balance for {}: {} mm, or {} percent'.format(name, mass_balance, mass_percent)
    #     print '--------------------------------------------------------------------------------'

    def _info(self, msg):
        print '-------------------------------------------------------'
        print msg
        print '-------------------------------------------------------'

    def _debug(self, msg):
        print '%%%%%%%%%%%%%%%% {}'.format(msg)

# ============= EOF =============================================
