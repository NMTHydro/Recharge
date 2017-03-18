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

from numpy import maximum, minimum, where, isnan, exp, median

from app.paths import paths, PathsNotSetExecption
from recharge.dict_setup import initialize_master_dict, initialize_static_dict, initialize_initial_conditions_dict, \
    set_constants, initialize_master_tracker
from recharge.dynamic_raster_finder import get_penman, get_individ_kcb, get_kcb, get_prisms
from recharge.raster_manager import RasterManager
from recharge.tools import millimeter_to_acreft as mm_af, unique_path, add_extension, time_it, day_generator


class Processes(object):
    """
    The purpose of this class is update the etrm master dict daily.

    See function explanations.

    """

    def __init__(self, cfg):
        self.tracker = None
        self._initial_depletions = None

        self._date_range = cfg.date_range
        self._use_individual_kcb = cfg.use_individual_kcb

        if not paths.is_set():
            raise PathsNotSetExecption()

        mask = cfg.mask
        polygons = cfg.polygons

        paths.set_polygons_path(polygons)
        paths.set_mask_path(mask)

        if cfg.use_verify_paths:
            paths.verify()

        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered
        self._constants = time_it(set_constants)

        # Initialize point and raster dicts for static values (e.g. TAW) and initial conditions (e.g. de)
        # from spin up. Define shape of domain. Create a month and annual dict for output raster variables
        # as defined in self._outputs. Don't initialize point_tracker until a time step has passed

        # self._static = time_it(initialize_static_dict)
        # shape = self._static['taw'].shape
        # self._initial = time_it(initialize_initial_conditions_dict)
        # self._master = time_it(initialize_master_dict, shape)

        self._static = initialize_static_dict()
        self._initial = initialize_initial_conditions_dict()

        shape = self._static['taw'].shape
        self._master = initialize_master_dict(shape)

        self._raster_manager = RasterManager(cfg)

        self.initialize()

    def configure_run(self, runspec):
        """
        configure the model run with a RunSpec object

        :param runspec: RunSpec
        :return:
        """
        if runspec.save_dates:
            self.set_save_dates(runspec.save_dates)

        if runspec.taw_modification is not None:
            self.modify_taw(runspec.taw_modification)

    def run(self, ro_reinf_frac=0.0, swb_mode='vertical', allen_ceff=1.0):
        """

        :param ro_reinf_frac:
        :param swb_mode:
        :param allen_ceff:
        :return:
        """

        self._info('Run started. Simulation period: start={}, end={}'.format(*self._date_range))

        c = self._constants
        m = self._master
        s = self._static
        rm = self._raster_manager

        start_monsoon, end_monsoon = c['s_mon'].timetuple().tm_yday, c['e_mon'].timetuple().tm_yday
        self._info('Monsoon: {} to {}'.format(start_monsoon, end_monsoon))

        st = time.time()
        for day in day_generator(*self._date_range):
            tm_yday = day.timetuple().tm_yday
            self._info('DAY:     {}({})'.format(day, tm_yday))

            time_it(self._do_daily_raster_load, day)

            # Assume 2-hour storms in the monsoon season, and 6 hour storms otherwise
            # If melt is occurring (calculated in _do_snow), infiltration will be set to 24 hours
            # [mm/day] #
            if start_monsoon <= tm_yday <= end_monsoon:
                m['soil_ksat'] = s['soil_ksat'] * 2 / 24.
            else:
                m['soil_ksat'] = s['soil_ksat'] * 6 / 24.

            # if sensitivity_matrix_column:
            #     time_it(self._do_parameter_adjustment, m, s, sensitivity_matrix_column)

            time_it(self._do_snow, m, c)
            time_it(self._do_soil_ksat_adjustment, m, s)
            time_it(self._do_dual_crop_transpiration, tm_yday, m, s, c)
            time_it(self._do_fraction_covered, m, s, c)

            if swb_mode == 'fao':
                time_it(self._do_fao_soil_water_balance, m, s, c, ro_reinf_frac, allen_ceff)
            elif swb_mode == 'vertical':
                time_it(self._do_vert_soil_water_balance, m, s, c, ro_reinf_frac, allen_ceff)

            time_it(self._do_mass_balance, day, swb=swb_mode)

            time_it(self._do_accumulations)

            if self.tracker is None:
                self.tracker = initialize_master_tracker(m)

            time_it(rm.update_raster_obj, m, day)
            time_it(self._update_master_tracker, m, day)

        self._info('saving tabulated data')
        time_it(rm.save_csv)

        self.save_tracker()
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
        self._info('Initialize initial model state')
        m = self._master

        m['pdr'] = m['dr'] = self._initial['dr']
        m['pde'] = m['de'] = self._initial['de']
        m['pdrew'] = m['drew'] = self._initial['drew']

        s = self._static
        for key in ('rew', 'tew', 'taw', 'soil_ksat'):
            v = s[key]
            msg = '{} median: {}, mean: {}, max: {}, min: {}'.format(key, median(v), v.mean(), v.max(), v.min())
            self._debug(msg)

        self._initial_depletions = m['dr'] + m['de'] + m['drew']

        # copy the mask path file into results
        path = paths.mask
        name = os.path.basename(path)
        shutil.copyfile(paths.mask, os.path.join(paths.etrm_output_root, name))

    def save_tracker(self, path=None):
        """

        :param path:
        :return:
        """
        self._info('Saving tracker')

        base = 'etrm_master_tracker'
        if path is None:
            path = add_extension(os.path.join(paths.etrm_output_root, base), '.csv')

        if os.path.isfile(path):
            path = unique_path(paths.etrm_output_root, base, '.csv')

        path = add_extension(path, '.csv')
        print 'this should be your csv: {}'.format(path)
        self.tracker.to_csv(path, na_rep='nan', index_label='Date')

    def _do_snow(self, m, c):
        """ Calibrated snow model that runs using PRISM temperature and precipitation.

        :return: None
        """

        temp = m['temp']
        palb = m['albedo']

        precip = m['precip']

        a_min = c['a_min']
        a_max = c['a_max']

        sf = where(temp < 0.0, precip, 0)
        rain = where(temp >= 0.0, precip, 0)

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

        # o = ones(soil_ksat.shape)
        # soil_ksat = where((land_cover == 41) & (water < 50.0 * o),
        #                   soil_ksat * 2.0 * o, soil_ksat)
        # soil_ksat = where((land_cover == 41) & (water < 12.0 * ones(soil_ksat.shape)),
        #                   soil_ksat * 1.2 * o, soil_ksat)
        # soil_ksat = where((land_cover == 42) & (water < 50.0 * o),
        #                   soil_ksat * 2.0 * o, soil_ksat)
        # soil_ksat = where((land_cover == 42) & (water < 12.0 * o),
        #                   soil_ksat * 1.2 * o, soil_ksat)
        # soil_ksat = where((land_cover == 43) & (water < 50.0 * o),
        #                   soil_ksat * 2.0 * o, soil_ksat)
        # soil_ksat = where((land_cover == 43) & (water < 12.0 * o),
        #                   soil_ksat * 1.2 * o, soil_ksat)

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

        kcb = m['kcb']
        etrs = m['etrs']

        ####
        # transpiration:
        # ks- stress coeff- ASCE pg 226, Eq 10.6
        # TAW could be zero at lakes.
        taw = maximum(s['taw'], 0.001)
        ks = ((taw - m['pdr']) / ((1 - c['p']) * taw))
        ks = minimum(1 + 0.001, ks)  # this +0.001 may be unneeded
        ks = maximum(0, ks)
        m['ks'] = ks

        # Transpiration from dual crop coefficient
        transp = maximum(ks * kcb * etrs, 0.0)

        # enforce winter dormancy of vegetation
        m['transp_adj'] = False
        if 92 > tm_yday or tm_yday > 306:
            # super-important winter evap limiter. Jan suggested 0.03 (aka 3%) but that doesn't match ameriflux.
            # Using 30% DC 2/20/17
            transp *= 0.3
            m['transp_adj'] = True

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

    def _do_fao_soil_water_balance(self, m, s, c, ro_local_reinfilt_frac=0.0, ceff=1.0):
        """ Calculate evap and all soil water balance at each time step.

        :return: None
        """
        m['pdr'] = pdr = m['dr']
        m['pde'] = pde = m['de']
        m['pdrew'] = pdrew = m['drew']

        taw = maximum(s['taw'], 0.001)
        tew = maximum(s['tew'], 0.001)          # TEW is zero at lakes in our data set
        rew = s['rew']

        kcb = m['kcb']
        kc_max = maximum(c['kc_max'], kcb + 0.05)
        ks = m['ks']
        etrs = m['etrs']

        # Start Evaporation Energy Balancing
        st_1_dur = (s['rew'] - m['pdrew']) / (c['ke_max'] * etrs)  # ASCE 194 Eq 9.22; called Fstage1
        st_1_dur = minimum(st_1_dur, 0.99)
        m['st_1_dur'] = st_1_dur = maximum(st_1_dur, 0)
        m['st_2_dur'] = st_2_dur = (1 - st_1_dur)

        # kr- evaporation reduction coefficient Allen 2011 Eq
        # Slightly different from 7ASCE pg 193, eq 9.21, but the Fstage coefficients come into the ke calc.
        tew_rew_diff = maximum(tew - rew, 0.001)
        kr = maximum(minimum((tew - m['pde']) / (tew_rew_diff), 1), 0.001)
        # EXPERIMENTAL: stage two evap has been too high, force slowdown with decay
        # kr *= (1 / m['dry_days'] **2)

        m['kr'] = kr

        # Simple version for 3-bucket model
        ke_init = (kc_max - (ks * kcb))
        m['ke_init'] = ke_init

        # ke evaporation efficency; Allen 2011, Eq 13a
        few = m['few']
        ke = minimum((st_1_dur + st_2_dur * kr) * (kc_max - (ks * kcb)), few * kc_max, 1)
        ke = maximum(0.01, ke)
        m['ke'] = ke

        # Ketchum Thesis eq 36, 37
        m['evap_1'] = e1 = st_1_dur * ke_init * etrs
        m['evap_2'] = e2 = st_2_dur * kr * ke_init * etrs

        # Allen 2011
        evap = ke * etrs

        # limit evap so it doesn't exceed the amount of soil moisture available after transp occurs
        transp = m['transp']
        m['evap'] = evap = minimum(evap, (taw - pdr) - transp)

        m['eta'] = et_actual = evap + transp
        print 'evap 1 = {}, evap 2 = {}, evap = {}, transp = {}, ET = {}'.format(e1, e2, evap, transp, et_actual)

        # Start Water Balance
        water = m['rain'] + m['melt']

        # if snow is melting, set ksat to 24 hour value
        m['soil_ksat'] = soil_ksat = where(m['melt'] > 0.0, s['soil_ksat'], m['soil_ksat'])

        # Only used if Experimental stage 2 reduction is used
        dd = m['dry_days']
        dd[water < 0.1] = dd + 1
        dd[water >= 0.1] = 1
        m['dry_days'] = dd

        # Surface runoff (Hortonian- using storm duration modified ksat values)
        ro = where(water > soil_ksat, water - soil_ksat, 0)
        ro *= (1 - ro_local_reinfilt_frac)
        m['ro'] = ro

        # Calculate Deep Percolation (recharge or infiltration)
        m['infil'] = dp = maximum(water - ro - et_actual - pdr, 0)

        # Calculate depletion in TAW, full root zone
        m['dr'] = dr = minimum(maximum(pdr - (water - ro) + et_actual + dp, 0), taw)

        # Calculate depletion in TEW, full evaporative layer
        m['de'] = de = minimum(maximum(pde - (water - ro) + evap/few, 0), tew)

        # Calculate depletion in REW, skin layer
        m['drew'] = drew = minimum(maximum(pdrew - (water - ro) + evap/few, 0), rew)

        m['soil_storage'] = (pdr - dr)

    def _do_vert_soil_water_balance(self, m, s, c, ro_local_reinfilt_frac=0.0, ceff=1.0):
        """ Calculate all soil water balance at each time step.

        :return: None
        """
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
        # rew = s['rew']
        # tew_rew_diff = maximum(tew - rew, 0.001)
        kr = maximum(minimum((tew - m['pde']) / tew, 1), 0.001)
        # EXPERIMENTAL: stage two evap has been too high, force slowdown with decay
        # kr *= (1 / m['dry_days'] **2)

        m['kr'] = kr

        # Simple version for 3-bucket model
        ke_init = (kc_max - (ks * kcb))
        m['ke_init'] = ke_init

        # ke evaporation efficency; Allen 2011, Eq 13a
        ke = minimum((st_1_dur + st_2_dur * kr) * (kc_max - (ks * kcb)), tew * kc_max, 1)
        ke = maximum(0.01, ke)
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

        rew = s['rew']
        tew = s['tew']
        taw = s['taw']

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
        water_av_rew = water * ceff
        water_av_tew = water * (1.0 - ceff)  # May not be initializing as an array?

        # # fill depletion in REW if possible
        water_av_tew, drew = self._fill_depletions(water_av_rew, water_av_tew, rew, pdrew+evap_1)

        # # fill depletion in REW if possible
        # evap__ = pdrew + evap_1
        # drew = where(water_av_rew >= evap__, 0, evap__ - water_av_rew)
        # drew = minimum(drew, rew)
        #
        # # add excess water to the water available to TEW (Is this coding ok?)
        # water_av_tew = where(water_av_rew >= evap__,
        #                      water_av_tew + water_av_rew - evap__,
        #                      water_av_tew)

        # water balance through the stage 2 evaporation layer #
        # capture efficiency of soil- some water may bypass TEW even before it fills
        water_av_tew *= ceff
        water_av_taw += water_av_tew * (1.0 - ceff)

        # # fill depletion in TEW if possible
        water_av_taw, de = self._fill_depletions(water_av_tew, water_av_taw, tew, pde+evap_2)

        # # fill depletion in TEW if possible
        # evap2__ = pde + evap_2
        # de = where(water_av_tew >= evap2__, 0, evap2__ - water_av_tew)
        # de = minimum(de, tew)
        #
        # # add excess water to the water available to TAW (Help coding this more cleanly?)
        # water_av_taw = where(water_av_tew >= evap2__,
        #                      water_av_taw + water_av_tew - evap2__,
        #                      water_av_taw)

        # water balance through the root zone layer #
        m['dr_water'] = water_av_taw  # store value of water delivered to root zone

        # fill depletion in TAW if possible
        depletion = pdr + transp

        dd = water_av_taw - depletion
        m['infil'] = where(water_av_taw >= depletion, dd, 0)
        dr = where(water_av_taw >= depletion, 0, dd*-1)

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

        m['soil_storage_all'] = self._initial_depletions - (m['pdr'] + m['pde'] + m['pdrew'])

        ms = [mm_af(m[k]) for k in ('infil', 'etrs', 'eta', 'precip', 'ro', 'swe', 'soil_storage')]
        print 'today infil: {}, etrs: {}, eta: {}, precip: {}, ro: {}, swe: {}, stor {}'.format(*ms)

        ms = [mm_af(m[k]) for k in ('tot_infil', 'tot_etrs', 'tot_eta', 'tot_precip', 'tot_ro', 'tot_swe')]
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
        self._debug('total mass balance error: {}'.format(mm_af(tot_mass)))

    def _do_daily_raster_load(self, date):
        """ Find daily raster image for each ETRM input.

        param date: datetime.day object
        :return: None
        """
        m = self._master

        if self._use_individual_kcb:
            m['kcb'] = get_individ_kcb(date, m['pkcb'])  # paths.mask

        else:
            m['kcb'] = get_kcb(date, m['pkcb'])

        min_temp, max_temp, temp, precip = get_prisms(date)
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

        etrs = get_penman(date, variable='etrs')
        etrs = where(etrs < 0, 0, etrs)
        m['etrs'] = where(isnan(etrs), 0, etrs)

        m['rg'] = get_penman(date, variable='rg')

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

    def _update_master_tracker(self, m, date):
        def factory(k):
            v = m[k]

            if k in ('dry_days', 'kcb', 'kr', 'ks', 'ke', 'fcov', 'few', 'albedo',
                     'max_temp', 'min_temp', 'rg', 'st_1_dur', 'st_2_dur',):
                v = v.mean()
            elif k == 'transp_adj':
                v = median(v)
            else:
                v = mm_af(v)
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

        input_sum = rswe + ms + rs

        print 'total inputs (swe, rain, melt): {}'.format(input_sum)
        print 'swe + melt + rain ({}) should equal precip ({})'.format(input_sum, ps)
        print 'total runoff = {}, total recharge = {}'.format(ros, infils)

        output_sum = ts + et + ros + infils

        output_sum += delta_soil_water + rswe  # added swe to output_sum; Dan, 2/11/17

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
#     start_monsoon, end_monsoon = c['s_mon'], c['e_mon]
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
