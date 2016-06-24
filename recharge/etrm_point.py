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

# ETRM - Evapotranspiration and Recharge Model, Point version, AMF Comparison
# For use with multiple Ameriflux stations
# David Ketchum, February 2016

# ============= standard library imports ========================
import logging
import os
# import pandas as pd
from datetime import datetime
from dateutil import rrule
from pandas import DataFrame
from numpy import array, column_stack, savetxt, exp

# ============= local library imports  ==========================
from recharge.model import BaseModel


# AMF = (('361716 3972654', 'Valles_conifer'),
#        ('355774 3969864', 'Valles_ponderosa'),
#        ('339552 3800667', 'Sev_shrub'),
#        ('343495 3803640', 'Sev_grass'),
#        ('386288 3811461', 'Heritage_pinyon_juniper'),
#        ('420840 3809672', 'Tablelands_juniper_savanna'))
#
# NAMES = [a[1] for a in AMF]


class ETRMPoint(BaseModel):
    _names = None
    _amf_data_root = None
    _amf_data_extracts_root = None
    _output_root = None

    _save_data_enabled = False
    _plot_data_enabled = False

    def run_model(self):
        amf = {}
        for name in self._names:
            logging.info('amf name={}'.format(name))
            data_path = os.path.join(self._amf_data_root, name)
            logging.info('amf path={}'.format(data_path))
            amf_data = self._get_amf_recs(data_path)
            logging.info('You have {} rows of --RAW-- data from {}'.format(len(amf_data), name))

            clean_amf_data, clean_amf_data2 = self._clean_amf_data(amf_data)
            logging.info('You have {} rows of FLUX  data from {}'.format(len(clean_amf_data), name))

            bal_data = self._get_bal_data(clean_amf_data)

            logging.info('The mean energy balance closure error is: {}'.format(bal_data[:, 11].mean()))
            bal_data = DataFrame(column_stack(bal_data).T,
                                 columns=['date', 'doy', 'year_doy_bal', 'rn', 'le', 'h', 'rg',
                                          'rgOut', 'rl', 'rlOut', 'aEt', 'err_rn_le_h',
                                          'err_rn_rg_grOut_rl_rlOut'])
            bal_data_lowErr = bal_data[bal_data.err_rn_le_h <= 0.20]
            logging.info('You have {} DAYS  of [0.0 < CLOSURE ERROR < 0.10] data from {}'.format(len(bal_data_lowErr),
                                                                                                 name))
            # amf_array.append(bal_data)
            amf[name] = bal_data

        self.process(amf)

    def _get_bal_data(self, name, clean_amf_data):
        # Find all complete days (48) records with no NULL values, makes lists, merge, stack, put in dataframe object
        rn = []
        le = []
        h = []
        bal = []
        rg = []
        rgOut = []
        rl = []
        rlOut = []
        err_rn_le_h = []
        err_rn_rg_grOut_rl_rlOut = []
        date_bal = []
        doy_bal = []
        year_doy_bal = []
        aEt = []
        x = -1
        y = -1
        rn_set = []
        le_set = []
        h_set = []
        rg_set = []
        rgOut_set = []
        rl_set = []
        rlOut_set = []
        sets = []
        sets_set = []

        for row in clean_amf_data.itertuples():
            if row[2] == row[3]:
                if x == y + 48:
                    if len(rn_set) == 48 and len(le_set) == 48:
                        # print (int(float(row[3])))
                        rn.append(sum(rn_set))
                        le.append(sum(le_set))
                        h.append(sum(h_set))
                        rg.append(sum(rg_set))
                        rgOut.append(sum(rgOut_set))
                        rl.append(sum(rl_set))
                        rlOut.append(sum(rlOut_set))
                        err_rn_rg_grOut_rl_rlOut.append(abs((sum(rn_set) - (sum(rg_set) - sum(rgOut_set) +
                                                                            sum(rl_set) - sum(rlOut_set))) / sum(rn_set)))
                        err_rn_le_h.append(abs((sum(rn_set) - (sum(le_set) + sum(h_set))) / sum(rn_set)))
                        date_bal.append(datetime.datetime(int(float(row[1])), 1, 1) + datetime.timedelta(
                            days=(int(float((row[3])) - 2))))
                        doy_bal.append(int(float(row[3])) - 1)
                        year_doy_bal.append((int(float(row[3])) - 1, row[1]))
                        # if int(float(row[3])) == 190:
                        # print row
                        bal.append(sum(rn_set) - (sum(le_set) + sum(h_set)))
                        aEt.append(sum(le_set) / 2.45)  # convert from MJ/(step * m**2) to mm water
                        sets.append(sets_set)
                    rn_set = []
                    le_set = []
                    h_set = []
                    rg_set = []
                    rgOut_set = []
                    rl_set = []
                    rlOut_set = []
                    sets_set = []
                y = x
            x += 1
            sets_set.append(row)
            # convert energies to MJ
            rn_set.append(float(row[7]) * (0.0864 / 48))
            le_set.append(float(row[5]) * (0.0864 / 48))
            h_set.append(float(row[4]) * (0.0864 / 48))
            rg_set.append(float(row[8]) * (0.0864 / 48))
            rgOut_set.append(float(row[9]) * (0.0864 / 48))
            rl_set.append(float(row[10]) * (0.0864 / 48))
            rlOut_set.append(float(row[11]) * (0.0864 / 48))

        logging.info('You have {} DAYS of CLEAN RN/LE/H/RAD data from {}'.format(len(bal), name))
        bal_data = zip(date_bal, doy_bal, year_doy_bal,
                       rn, le, h, rg, rgOut,
                       rl, rlOut, aEt, err_rn_le_h,
                       err_rn_rg_grOut_rl_rlOut)
        return array(bal_data)

    def process(self, amf):
        def factory(li):
            row = li.split(',')
            try:
                dt = datetime.strptime(row[0], '%m/%d/%Y')
            except ValueError:
                dt = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')

            rec = [dt, ]
            rec.extend(map(float, row[1:17]))
            return rec

        for name in self._names:
            logging.debug('Processing site. {}'.format(name))
            path = os.path.join(self._amf_data_extracts_root, 'AMF{}_extract.csv'.format(name))
            if not os.path.isfile(path):
                logging.warning('Could not locate {}'.format(path))

            with open(path, 'r') as rfile:
                data = array([factory(line) for line in rfile])

            df_amf = amf[name]
            extract_start, extract_end = data[0, 0], data[-1, 0]
            df_amf = df_amf[(df_amf.iloc[:, 0] >= extract_start) & (df_amf.iloc[:, 0] <= extract_end)]
            amf_start_obj, amf_end_obj = df_amf.iloc[0, 0], df_amf.iloc[-1, 0]

            #  Use the coincident data to only run the model during the period AMF data exists
            coin_data = data[data[:, 0] >= amf_start_obj]
            coin_data = coin_data[coin_data[:, 0] <= amf_end_obj]

            logging.info('Site {} at runs from {} to {}'.format(name, amf_start_obj, amf_end_obj))
            processed_data = self._process_site(name, data)
            if self._save_data_enabled:
                self._save_data(name, processed_data)
            if self._plot_data_enabled:
                self._plot_data(name, processed_data, df_amf)

    # private
    def _plot_data(self,  name, data, df_amf):
        import matplotlib.pyplot as plt

        amf_eta_mean = df_amf.iloc[:, 10].values.mean()
        etrm_eta_mean = array(data['Eta']).mean()
        cum_mass = data['cum_mass']

        plt.subplot(5, 1, 1)
        xs = data['Day']

        plt.plot(xs, data['Etrs'], 'orange', label='ETRS (mm)')
        plt.plot(xs, data['Eta'], 'r', label='Evapotranspiration (mm)')
        plt.plot(df_amf.iloc[:, 0].values, df_amf.iloc[:, 10].values, 'k+', label='Measured ET from Flux Tower')
        plt.legend()
        plt.title('ETRM vs AMF Data at {}... AMF ET mean: {}mm/day  ETRM ET mean:'
                  '  {}mm/day... Cumulative mass balance error: {}mm'.format(name, amf_eta_mean, etrm_eta_mean,
                                                                             cum_mass))
        plt.xlabel('Date')
        plt.ylabel('(mm)')
        plt.subplot(5, 1, 2)
        plt.plot(xs, data['Swe'], 'b', label='ETRM Snow Water Equivalent (mm)')
        plt.plot(xs, data['Rain'], 'red', label='Rain (mm)')
        plt.plot(xs, data['Snow_fall'], 'b', label='Snow Fall Water Equivalent (mm)')
        plt.legend()
        plt.subplot(5, 1, 3)
        plt.plot(xs, data['Dp_r'], 'g', label='Recharge (mm)')
        plt.plot(xs, data['Ro'], 'p', label='Runoff (mm)')
        plt.legend()
        plt.subplot(5, 1, 4)
        plt.plot(xs, data['Mass'], 'r')
        plt.legend()
        plt.subplot(5, 1, 5)
        plt.plot(xs, data['Ks'], 'r', label='Stress Coefficient (-)')
        plt.plot(xs, data['Fs1'], 'g', label='Stage 1 Evaporation Coefficient (-)')
        plt.plot(xs, data['Kr'], 'b', label='Evaporation Reduction Coefficient (-)')
        plt.legend()
        plt.show()

    def _save_data(self, name, data):
        path = os.path.join(self._output_root, '{}_calibrationdata.csv'.format(name))
        logging.info('Saving {} data to {}'.format(name, path))
        keys = ('Snow_fall', 'Rain', 'Mlt', 'Eta', 'Ro', 'Dp_r', 'Dr', 'De', 'Drew', 'Mass')
        fmt = ['%1.3f'] * len(keys)
        savetxt(path,
                column_stack(tuple((data[k] for k in keys))),
                fmt=fmt,
                delimiter=',')

    def _process_site(self, name, data):
        # Create indices to plot point time series, these are empty lists that will
        # be filled as the simulation progresses
        pltRain = []
        pltEta = []
        pltEvap = []
        pltSnow_fall = []
        pltRo = []
        pltDr = []
        pltPdr = []
        pltDe = []
        pltDrew = []
        pltTemp = []
        pltTempM = []
        pltDp_r = []
        pltKs = []
        pltEtrs = []
        pltKcb = []
        pltKe = []
        pltMlt = []
        pltSwe = []
        pltDay = []
        pltFs1 = []
        pltPpt = []
        pltKr = []
        pltMass = []
        pltPdrew = []

        # Define user-controlled constants, these are constants to start with day one, replace
        # with spin-up data when multiple years are covered
        ze = 40
        p = 0.4
        kc_min = 0.15
        infil = 0.0
        precip = 0.0
        et = 0.0
        runoff = 0.0
        ppt_tom = 0.0
        fb = 0.25
        swe = 0.0
        ke_max = 1.0
        cum_mass = 0.0
        tot_transp = 0.0
        tot_evap = 0.0
        a_min = 0.45
        a_max = 0.90
        pA = a_min

        logging.info('Starting {}.............'.format(name))
        end = self._end
        start = self.start
        for iday, dday in enumerate(rrule.rrule(rrule.DAILY, dtstart=start, until=end)):
            day_of_year = dday.timetuple().tm_yday

            if iday == 0:
                fc = data[0, 12] / 100.
                wp = data[0, 13] / 100.
                etrs = float(data[iday, 6])
                tew = (fc - 0.5 * wp) * ze  # don't use time-dependent etrs for long-term simulations
                taw = data[0, 14]
                aws = data[0, 15] * 100.
                logging.debug('TAW is {} and AWS is {}'.format(taw, aws))
                rew = min((2 + (tew / 3.)), 0.8 * tew)

                pDr = taw
                pDe = tew
                pDrew = rew
                dr = taw
                de = tew
                drew = rew

                ksat_init = data[0, 2] * 86.4 / 10.  # from micrometer/sec to mm/day
                old_ksat = data[0, 1] * 1000 / 3.281  # from ft/dat to mm/day
                logging.debug('SSURGO Ksat is {} and bedrock Ksat is {}'.format(ksat_init, old_ksat))
            if self._start_month < dday < self._end_month:
                ksat = ksat_init / 12.
            else:
                ksat = ksat_init / 4.
            #  Find et and evap

            kcb = data[iday, 3]

            etrs = data[iday, 6]

            kc_max_1 = kcb + 0.0001
            kc_max = max(0.0001, kc_max_1)

            # compute coverage/exposure of soil
            # plnt_hgt = data[day, 7]
            # plnt_term = plnt_hgt * 0.5 + 1
            # numr = max(kcb - kc_min, 0.01)
            # denom = max((kc_max - kc_min), 0.01)
            # fcov_ref = (numr / denom) ** plnt_term
            # fcov_min = min(fcov_ref, 1.00)
            # fcov = max(fcov_min, 0.1)   # vegetation-covered ground
            # few = max(1 - fcov, 0.01)   # exposed ground

            few = 1 - (kcb / 1.25)

            # root zone stress coefficient
            ks_ref = (taw - dr) / (0.6 * taw)
            ks_min = max(ks_ref, 0.001)
            ks = min(ks_min, 1.0)

            # total evaporation layer reduction coefficient (aka stage 2)
            kr = min((tew - de) / (tew - rew), 1.0)

            # check if stage 1 evaporation is occurring
            # and calculate STRESS
            # remember to apply a condition for bare ground
            # if NDVI < 0.05:
            #     ke = (fs1 + (1 - fs1) * kr) * ke_max

            fsa = (rew - drew) / (ke_max * etrs)
            fsb = min(fsa, 1.0)
            fs1 = max(fsb, 0.0)

            ke = min((fs1 + (1 - fs1) * kr) * (kc_max - (ks * kcb)), few * kc_max)

            eta = (ks * kcb + ke) * etrs
            eta = max(eta, 0.0)
            transp = (ks * kcb) * etrs
            evap_init = ke * etrs
            evap = max(evap_init, 0.0)

            if dday == end:
                temp = data[iday, 10]
                max_temp = data[iday, 9]
                min_temp = data[iday, 8]
                ppt_tot = data[iday, 11]
                ppt_tom = 0.0
            else:
                temp = data[iday, 10]
                max_temp = data[iday, 9]
                min_temp = data[iday, 8]
                ppt_tot = data[iday, 11]
                ppt_tom = data[iday + 1, 11]

            if temp < 0.0:
                snow_fall = ppt_tot

                if snow_fall > 3.0:
                    a = a_max
                else:
                    k = 0.12
                    a = a_min + (pA - a_min) * exp(-k)
                    a = min(a, a_max)
                    a = max(a, a_min)

                rain = 0.0
                rain_tom = 0.0
            else:
                snow_fall = 0.0
                rain = ppt_tot
                rain_tom = ppt_tom
                k = 0.05
                a = a_min + (pA - a_min) * exp(-k)
                a = min(a, a_max)
                a = max(a, a_min)

            pA = a
            swe = snow_fall + swe

            rg = data[iday, 5]
            mlt_init = max(((1 - a) * rg * 0.15) + (temp - 1.5) * 3.956, 0.0)
            mlt = min(swe, mlt_init)

            swe = swe - mlt

            # Find depletions

            pDr = dr
            pDe = de
            pDrew = drew

            watr = rain + mlt
            deps = dr + de + drew

            if watr <= deps:
                ro = 0.0
                dp_r = 0.0
            elif ksat + deps > watr > deps:
                ro = 0.0
                dp_r = watr - deps
            elif watr > ksat + deps:
                ro = watr - ksat - deps
                dp_r = ksat
            else:
                ro = 0.0
                dp_r = 0.0
                pass

            drew_1 = min((pDrew + ((ro + (few / evap)) - (rain + mlt))), rew)
            drew = max(drew_1, 0.0)
            diff = max(pDrew - drew, 0.0)

            de_1 = min(pDe + evap / few - (rain + mlt - diff), tew)
            de = max(de_1, 0.0)
            diff2 = max((diff + (pDe - de)), 0.0)

            dr_1 = min((pDr + ((transp + dp_r) - (rain + mlt - diff2))), taw)
            dr = max(dr_1, 0.0)

            infil += dp_r
            tot_transp += transp
            tot_evap += evap
            et += transp + evap
            precip += rain + snow_fall
            runoff += ro
            snow_ras = swe + snow_fall - mlt

            # Check MASS BALANCE for the love of WATER!!!
            mass = rain + mlt - (ro + transp + evap + dp_r + ((pDr - dr) + (pDe - de) + (pDrew - drew)))
            cum_mass += abs(mass)
            if dday == end:
                end_mass = precip - infil - runoff - snow_ras - et - ((taw - dr) + (tew - de) + (rew - drew))

            pltDay.append(dday)
            pltRain.append(rain)
            pltEta.append(eta)
            pltEvap.append(evap)
            pltSnow_fall.append(snow_fall)
            pltRo.append(ro)
            pltDr.append(dr)
            pltDe.append(de)
            pltDrew.append(drew)
            pltPdrew.append(pDrew)
            pltTemp.append(temp)
            pltDp_r.append(dp_r)
            pltKs.append(ks)
            pltPdr.append(pDr)
            pltEtrs.append(etrs)
            pltKcb.append(kcb)
            pltPpt.append(ppt_tot)
            pltKe.append(ke)
            pltKr.append(kr)
            pltMlt.append(mlt)
            pltSwe.append(swe)
            pltTempM.append(max_temp)
            pltFs1.append(fs1)
            pltMass.append(mass)

        processed_data = {'Rain': pltRain,
                          'Eta': pltEta,
                          'Evap': pltEvap,
                          'Snow_fall': pltSnow_fall,
                          'Ro': pltRo,
                          'Dr': pltDr,
                          'Pdr': pltPdr,
                          'De': pltDe,
                          'Drew': pltDrew,
                          'Temp': pltTemp,
                          'TempM': pltTempM,
                          'Dp_r': pltDp_r,
                          'Ks': pltKs,
                          'Etrs': pltEtrs,
                          'Kcb': pltKcb,
                          'Ke': pltKe,
                          'Mlt': pltMlt,
                          'Swe': pltSwe,
                          'Day': pltDay,
                          'Fs1': pltFs1,
                          'Ppt': pltPpt,
                          'Kr': pltKr,
                          'Mass': pltMass,
                          'Pdrew': pltPdrew,
                          'cumulative_mass': cum_mass}
        return processed_data

    def _clean_amf_data(self, data):
        # Find data where there is both RN and LE available, and thus all energy data, as RN is calculated
        # amf_data_RN = amf_data[data.RN != '-9999.0']
        # amf_data_RN_LE = amf_data_RN[amf_data_RN.LE != '-9999.0']

        pdata = data
        for attr in ('H', 'LE', 'RG', 'RGout', 'RGL', 'RGLout', 'RN'):
            pdata = pdata[getattr(pdata, attr) != '-9999.0']
        clean_amf_data = pdata
        # amf_data_H = amf_data[amf_data.H != '-9999.0']
        # amf_data_H_LE = amf_data_H[amf_data_H.LE != '-9999.0']
        # amf_data_H_LE_RG = amf_data_H_LE[amf_data_H_LE.RG != '-9999.0']
        # amf_data_H_LE_RG_RGout = amf_data_H_LE_RG[amf_data_H_LE_RG.RGout != '-9999.0']
        # amf_data_H_LE_RG_RGout_RGL = amf_data_H_LE_RG_RGout[amf_data_H_LE_RG_RGout.RGL != '-9999.0']
        # amf_data_H_LE_RG_RGout_RGL_RGLout = amf_data_H_LE_RG_RGout_RGL[amf_data_H_LE_RG_RGout_RGL.RGLout != '-9999.0']
        # amf_data_H_LE_RG_RGout_RGL_RGLout_RN = amf_data_H_LE_RG_RGout_RGL_RGLout[
        #     amf_data_H_LE_RG_RGout_RGL_RGLout.RN != '-9999.0']
        for attr in ('WS', 'WD', 'RH', 'TA', 'TA'):
            pdata = pdata[getattr(pdata, attr) != '-9999.0']
        clean_amf_data2 = pdata
        # amf_data_WS = amf_data_H_LE_RG_RGout_RGL_RGLout_RN[amf_data_H_LE_RG_RGout_RGL_RGLout_RN.WS != '-9999.0']
        # amf_data_WS_WD = amf_data_WS[amf_data_WS.WD != '-9999.0']
        # amf_data_WS_WD_RH = amf_data_WS_WD[amf_data_WS_WD.RH != '-9999.0']
        # amf_data_WS_WD_RH_TA = amf_data_WS_WD_RH[amf_data_WS_WD_RH.TA != '-9999.0']
        # amf_data_WS_WD_RH_TA_VPD = amf_data_WS_WD_RH_TA[amf_data_WS_WD_RH_TA.TA != '-9999.0']

        return clean_amf_data, clean_amf_data2

    def _get_amf_data(self, path):
        amf_data = []
        for item in os.listdir(path):
            with open(os.path.join(path, item), 'r') as rfile:
                rows = [line.split(',') for line in rfile.readlines()[3:]]
                for r in rows:
                    d = [r[0], ]
                    d.extend((float(r[i]) for i in (2, 3, 12, 14, 16, 28, 30, 33, 34, 35, 8, 7, 22, 6, 25)))
                    amf_data.append(d)
        amf_data = DataFrame(array(amf_data), columns=['year', 'dtime', 'doy', 'H', 'LE', 'FG', 'RN',
                                                       'RG', 'RGout', 'RGL', 'RGLout', 'WS', 'WD', 'RH', 'TA', 'VPD'])
        return amf_data

    def _default_config(self):
        cfg = {'names': ['Valles_conifer',
                         'Valles_ponderosa',
                         'Sev_shrub',
                         'Sev_grass',
                         'Heritage_pinyon_juniper',
                         'Tablelands_juniper_savanna'],
               'amf_data': '',
               'amf_data_extracts': '',
               'output': '',
               'plot': False,
               'save': False}
        return cfg

    def _load_config(self, cfg):
        self._names = cfg['names']
        self._amf_data_root = cfg['amf_data']
        self._amf_data_extracts_root = cfg['amf_data_extracts']
        self._output_root = cfg['output']
        self._save_data_enabled = cfg['save']
        self._plot_data_enabled = cfg['plot']
        self._load_start_end(cfg)


# ============= EOF =============================================

# # Set start datetime object
# start, end = datetime.datetime(2007, 1, 1), datetime.datetime(2013, 12, 31)
# # Define winter and summer for SNOW algorithm
# # sWin, eWin = datetime.datetime(start.year, 11, 1), datetime.datetime(end.year, 3, 30)
# # Define monsoon for Ksat, presumed storm intensity
# sMon, eMon = datetime.datetime(start.year, 6, 1), datetime.datetime(start.year, 10, 1)
#
# amfdict = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_conifer'},
#            '2': {'Coords': '355774 3969864', 'Name': 'Valles_ponderosa'},
#            '3': {'Coords': '339552 3800667', 'Name': 'Sev_shrub'},
#            '4': {'Coords': '343495 3803640', 'Name': 'Sev_grass'},
#            '5': {'Coords': '386288 3811461', 'Name': 'Heritage_pinyon_juniper'},
#            '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_juniper_savanna'}}
#
# info = amfdict.items()
# codes = [int(x[0]) for x in info]
# info = [str(x[1]) for x in info]
# coords = [str(x[12:26]) for x in info]
# names = [str(x[38:-2]) for x in info]
#
# years = [x for x in range(start.year, end.year + 1)]
#
# # Load amf  data, all dates, be sure the points are at the same place!
# # In this version, use AMF  precipitation, temperature, and energy fluxes
# #
# # Actual ET
# amf_names = []
# amf_length = []
# amf_array = []
# select_codes = []
# for code in codes:
#     print code
#     amf_name = amfdict['{a}'.format(a=code)]['Name']
#     print amf_name
#     folder = "C:\\Users\\David\Documents\\Recharge\\aET\\AMF_Data\\" + '{a}'.format(a=amf_name)
#     os.chdir(folder)
#     csvList = os.listdir(folder)
#     for item in csvList:
#
#         if item == csvList[0]:
#             # if item == "C:\\Users\\David\Documents\\Recharge\\aET\\AMF_Data\\" + '{a}_extract.csv'.format(a=amf_name):
#             #     break
#             amf_recs = []
#         fid = open(item)
#         # print "opening file: " + '{a}'.format(a=fid)
#         lines = fid.readlines()[3:]
#         fid.close()
#         rows = [line.split(',') for line in lines]
#         for line in rows:
#             amf_recs.append([line[0], float(line[2]), float(line[3]),
#                              float(line[12]), float(line[14]), float(line[16]),
#                              float(line[28]), float(line[30]), float(line[33]), float(line[34]), float(line[35]),
#                              float(line[8]), float(line[7]), float(line[22]), float(line[6]), float(line[25])])
#
#     amf_data = np.array(amf_recs)
#
#     amf_data = pd.DataFrame(amf_data, columns=['year', 'dtime', 'doy', 'H', 'LE', 'FG', 'RN',
#                                                'RG', 'RGout', 'RGL', 'RGLout', 'WS', 'WD', 'RH', 'TA', 'VPD'])
#     norm = [x for x in range(1, 366)]
#     leap = [x for x in range(1, 367)]
#     leaps = ['2004', '2008', '2012']
#     print 'You have {a} rows of --RAW-- data from {b}'.format(a=len(amf_data), b=amf_name)
#
#     #  (year, dtime, H, LE, FG, RN, RG, RGin, RGout)
#     # H  = sensible heat flux
#     # LE = latent heat flux
#     # FG = soil heat flux
#     # RN = net radiation
#     # RG = incoming shortwave
#     # RGout = outgoing shortwave
#     # RGL  = incoming longwave
#     # RGLout = outgoing longwave
#
#     # Find data where there is both RN and LE available, and thus all energy data, as RN is calculated
#     amf_data_RN = amf_data[amf_data.RN != '-9999.0']
#     amf_data_RN_LE = amf_data_RN[amf_data_RN.LE != '-9999.0']
#
#     amf_data_H = amf_data[amf_data.H != '-9999.0']
#     amf_data_H_LE = amf_data_H[amf_data_H.LE != '-9999.0']
#     amf_data_H_LE_RG = amf_data_H_LE[amf_data_H_LE.RG != '-9999.0']
#     amf_data_H_LE_RG_RGout = amf_data_H_LE_RG[amf_data_H_LE_RG.RGout != '-9999.0']
#     amf_data_H_LE_RG_RGout_RGL = amf_data_H_LE_RG_RGout[amf_data_H_LE_RG_RGout.RGL != '-9999.0']
#     amf_data_H_LE_RG_RGout_RGL_RGLout = amf_data_H_LE_RG_RGout_RGL[amf_data_H_LE_RG_RGout_RGL.RGLout != '-9999.0']
#     amf_data_H_LE_RG_RGout_RGL_RGLout_RN = amf_data_H_LE_RG_RGout_RGL_RGLout[
#         amf_data_H_LE_RG_RGout_RGL_RGLout.RN != '-9999.0']
#     del amf_data_H, amf_data_H_LE, amf_data_H_LE_RG, amf_data_H_LE_RG_RGout, amf_data_H_LE_RG_RGout_RGL, amf_data_H_LE_RG_RGout_RGL_RGLout
#     amf_data_WS = amf_data_H_LE_RG_RGout_RGL_RGLout_RN[amf_data_H_LE_RG_RGout_RGL_RGLout_RN.WS != '-9999.0']
#     amf_data_WS_WD = amf_data_WS[amf_data_WS.WD != '-9999.0']
#     amf_data_WS_WD_RH = amf_data_WS_WD[amf_data_WS_WD.RH != '-9999.0']
#     amf_data_WS_WD_RH_TA = amf_data_WS_WD_RH[amf_data_WS_WD_RH.TA != '-9999.0']
#     amf_data_WS_WD_RH_TA_VPD = amf_data_WS_WD_RH_TA[amf_data_WS_WD_RH_TA.TA != '-9999.0']
#     del amf_data_WS, amf_data_WS_WD, amf_data_WS_WD_RH, amf_data_WS_WD_RH_TA
#     print 'You have {a} rows of FLUX  data from {b}'.format(a=len(amf_data_H_LE_RG_RGout_RGL_RGLout_RN), b=amf_name)
#
#     # Find all complete days (48) records with no NULL values, makes lists, merge, stack, put in dataframe object
#     rn = []
#     le = []
#     h = []
#     bal = []
#     rg = []
#     rgOut = []
#     rl = []
#     rlOut = []
#     err_rn_le_h = []
#     err_rn_rg_grOut_rl_rlOut = []
#     date_bal = []
#     doy_bal = []
#     year_doy_bal = []
#     aEt = []
#     x = -1
#     y = -1
#     rn_set = []
#     le_set = []
#     h_set = []
#     rg_set = []
#     rgOut_set = []
#     rl_set = []
#     rlOut_set = []
#     sets = []
#     sets = []
#     sets_set = []
#     amf_test = amf_data_H_LE_RG_RGout_RGL_RGLout_RN.iloc[6900:7300, :]
#     for row in amf_data_H_LE_RG_RGout_RGL_RGLout_RN.itertuples():
#         if row[2] == row[3]:
#             if x == y + 48:
#                 if len(rn_set) == 48 and len(le_set) == 48:
#                     # print (int(float(row[3])))
#                     rn.append(sum(rn_set))
#                     le.append(sum(le_set))
#                     h.append(sum(h_set))
#                     rg.append(sum(rg_set))
#                     rgOut.append(sum(rgOut_set))
#                     rl.append(sum(rl_set))
#                     rlOut.append(sum(rlOut_set))
#                     err_rn_rg_grOut_rl_rlOut.append(abs((sum(rn_set) - (sum(rg_set) - sum(rgOut_set) +
#                                                                         sum(rl_set) - sum(rlOut_set))) / sum(rn_set)))
#                     err_rn_le_h.append(abs((sum(rn_set) - (sum(le_set) + sum(h_set))) / sum(rn_set)))
#                     date_bal.append(datetime.datetime(int(float(row[1])), 1, 1) + datetime.timedelta(
#                         days=(int(float((row[3])) - 2))))
#                     doy_bal.append(int(float(row[3])) - 1)
#                     year_doy_bal.append((int(float(row[3])) - 1, row[1]))
#                     # if int(float(row[3])) == 190:
#                     # print row
#                     bal.append(sum(rn_set) - (sum(le_set) + sum(h_set)))
#                     aEt.append(sum(le_set) / 2.45)  # convert from MJ/(step * m**2) to mm water
#                     sets.append(sets_set)
#                 rn_set = []
#                 le_set = []
#                 h_set = []
#                 rg_set = []
#                 rgOut_set = []
#                 rl_set = []
#                 rlOut_set = []
#                 sets_set = []
#             y = x
#         x += 1
#         sets_set.append(row)
#         # convert energies to MJ
#         rn_set.append(float(row[7]) * (0.0864 / 48))
#         le_set.append(float(row[5]) * (0.0864 / 48))
#         h_set.append(float(row[4]) * (0.0864 / 48))
#         rg_set.append(float(row[8]) * (0.0864 / 48))
#         rgOut_set.append(float(row[9]) * (0.0864 / 48))
#         rl_set.append(float(row[10]) * (0.0864 / 48))
#         rlOut_set.append(float(row[11]) * (0.0864 / 48))
#
#     print 'You have {a} DAYS of CLEAN RN/LE/H/RAD data from {b}'.format(a=len(bal), b=amf_name)
#     bal_data = zip(date_bal, doy_bal, year_doy_bal, rn, le, h, rg, rgOut, rl, rlOut, aEt, err_rn_le_h,
#                    err_rn_rg_grOut_rl_rlOut)
#     bal_data = np.array(bal_data)
#     print 'The mean energy balance closure error is: {a}'.format(a=np.mean(bal_data[:, 11]))
#     bal_data = np.column_stack(bal_data)
#     bal_data = np.transpose(bal_data)
#     bal_data = pd.DataFrame(bal_data, columns=['date', 'doy', 'year_doy_bal', 'rn', 'le', 'h', 'rg',
#                                                'rgOut', 'rl', 'rlOut', 'aEt', 'err_rn_le_h',
#                                                'err_rn_rg_grOut_rl_rlOut'])
#     bal_data_lowErr = bal_data[bal_data.err_rn_le_h <= 0.20]
#     print 'You have {a} DAYS  of [0.0 < CLOSURE ERROR < 0.10] data from {b}'.format(a=len(bal_data_lowErr), b=amf_name)
#     amf_array.append(bal_data)
#     amf_length.append(len(bal_data))
#     filepath = 'C:\\Users\\David\\Documents\\Recharge\\aET\\AMF_Cleaned_Data'
#     # bal_data.to_csv('{a}\\{b}_cleaned_all.csv'.format(a=filepath, b=amf_name))
#     # bal_data_lowErr.to_csv('{a}\\{b}_cleaned_lowErr.csv'.format(a=filepath, b=amf_name))
#     amf_names.append(amf_name)
#     select_codes.append(code)
#     # del bal_data, bal_data_lowErr
#
# # Find all complete records with no NULL values, makes lists, merge,
# # stack, put in dataframe object, regardless of having full days
# #     rn = []
# #     le = []
# #     h = []
# #     bal = []
# #     rg = []
# #     rgOut = []
# #     rl = []
# #     rlOut = []
# #     err_rn_le_h = []
# #     date_bal = []
# #     dtime_bal = []
# #     aEt = []
# #     wd = []
# #     ws = []
# #     rh = []
# #     ta = []
# #     vpd = []
# #     # amf_test = amf_data_WS_WD_RH_TA_VPD.iloc[-500:, :]
# #     for row in amf_data_WS_WD_RH_TA_VPD.itertuples():
# #         rn.append(float(row[7]))
# #         le.append(float(row[5]))
# #         h.append(float(row[4]))
# #         rg.append(float(row[8]))
# #         rgOut.append(float(row[9]))
# #         rl.append(float(row[10]))
# #         rlOut.append(float(row[11]))
# #         err_rn_le_h.append(abs((float(row[7]) - (float(row[5]) + float(row[4]))) / float(row[7])))
# #         date_bal.append(datetime.datetime(int(float(row[1])), 1, 1) + datetime.timedelta(days=(int(float((row[3])) - 2))))
# #         dtime_bal.append(float(row[2]))
# #         aEt.append(float(row[5]) * 0.03525)
# #         ws.append(float(row[12]))
# #         wd.append(float(row[13]))
# #         rh.append(float(row[14]))
# #         ta.append(float(row[15]))
# #         vpd.append(float(row[16]))
# #
# #     print 'You have {a} RECORDS of CLEAN RN/LE/H/RAD/METEOROLOGY data from {b}'.format(a=len(rn), b=amf_name)
# #     bal_data = zip(date_bal, dtime_bal, rn, le, h, rg, rgOut, rl, rlOut, aEt, err_rn_le_h,  ws, wd, rh, ta, vpd)
# #     bal_data = np.array(bal_data)
# #     print 'The mean energy balance closure error is: {a}'.format(a=np.mean(bal_data[:, 10]))
# #     bal_data = np.column_stack(bal_data)
# #     bal_data = np.transpose(bal_data)
# #     bal_data = pd.DataFrame(bal_data, columns=['date', 'doy', 'rn', 'le', 'h', 'rg', 'rgOut', 'rl', 'rlOut',
# #                                                'aEt', 'err_rn_le_h', 'WS', 'WD', 'RH', 'TA', 'VPD'])
# #     bal_data_lowErr = bal_data[bal_data.err_rn_le_h <= 0.10]
# #     print 'You have {a} RECORDS  of [0.0 < CLOSURE ERROR < 0.10] data from {b}'.format(a=len(bal_data_lowErr),
# #                                                                                        b=amf_name)
# #     amf_array.append(bal_data)
# #     amf_length.append(len(bal_data))
# #     filepath = 'C:\\Users\\David\\Documents\\Recharge\\aET\\AMF_Cleaned_Data'
# #     # bal_data.to_csv('{a}\\{b}_cleaned_all.csv'.format(a=filepath, b=amf_name))
# #     # bal_data_lowErr.to_csv('{a}\\{b}_cleaned_lowErr.csv'.format(a=filepath, b=amf_name))
# #     amf_names.append(amf_name)
#
# meta_amf = zip(select_codes, amf_names, amf_array, amf_length)
# print codes
# print amf_names
#
# print ''
# print ''
# print ''
# print 'Moving on to EXTRACT PARAMETERS.................................................................'
# print ''
# print ''
# print ''
#
# # Load up all data needed for ETRM from extract .csv
# # EXTRACT PARAMETERS
#
# for site in select_codes:
#     extract_name = amf_names[select_codes.index(site)]
#     name = 'C:\\Users\\David\\Documents\\Recharge\\aET\\AMF_extracts\\AMF{a}_extract.csv'.format(a=site)
#     print 'Processing site {} code AMF{}'.format(extract_name, site)
#     # Get a numpy object of all raster-extracted data out of the csv it is held in
#     recs = []
#     try:
#         fid = open(name)
#         # print "file: " + str(fid)
#         lines = fid.readlines()[:]
#         fid.close()
#     except IOError:
#         print "couldn't find " + '{a}'.format(a=fid)
#         # break
#     rows = [line.split(',') for line in lines]
#     for line in rows:
#         try:
#             recs.append([datetime.datetime.strptime(line[0], '%m/%d/%Y'),  # date
#                          float(line[1]), float(line[2]), float(line[3]), float(line[4]),
#                          float(line[5]), float(line[6]), float(line[7]), float(line[8]),
#                          float(line[9]), float(line[10]), float(line[11]), float(line[12]),
#                          float(line[13]), float(line[14]), float(line[15]), float(line[16])])
#         except ValueError:
#             recs.append([datetime.datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S'),  # date
#                          float(line[1]), float(line[2]), float(line[3]), float(line[4]),
#                          float(line[5]), float(line[6]), float(line[7]), float(line[8]),
#                          float(line[9]), float(line[10]), float(line[11]), float(line[12]),
#                          float(line[13]), float(line[14]), float(line[15]), float(line[16])])
#
#             # ['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
#             # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z']
#
#     data = np.array(recs)
#     # print len(data)
#
#     # Data format now in [date, ksat, soil_ksat, kcb, rlin, rg, etrs_Pm, plant height, min temp,
#     # max temp, temp, prcip, fc, wp, taw, aws, root_z]
#
#     # Loop daily time step over chosen interval, computing all madel variables each day
#     # fit select start and end dates for each panel (site)
#     panel = select_codes.index(site)
#     df_amf = amf_array[panel]
#     extract_start, extract_end = data[0, 0], data[-1, 0]
#     df_amf = df_amf[(df_amf.iloc[:, 0] >= extract_start) & (df_amf.iloc[:, 0] <= extract_end)]
#     amf_start_obj, amf_end_obj = df_amf.iloc[0, 0], df_amf.iloc[-1, 0]
#
#     #  Use the coincident data to only run the model during the period AMF data exists
#     coin_data = data[data[:, 0] >= amf_start_obj]
#     coin_data = coin_data[coin_data[:, 0] <= amf_end_obj]
#
#     print 'Site {a} at {d} runs from {b} to {c}'.format(a=amf_names[panel],
#                                                         b=amf_start_obj, c=amf_end_obj, d=select_codes[panel])
#
#     # Create indices to plot point time series, these are empty lists that will
#     # be filled as the simulation progresses
#     pltRain = []
#     pltEta = []
#     pltEvap = []
#     pltSnow_fall = []
#     pltRo = []
#     pltDr = []
#     pltPdr = []
#     pltDe = []
#     pltDrew = []
#     pltTemp = []
#     pltTempM = []
#     pltDp_r = []
#     pltKs = []
#     pltEtrs = []
#     pltKcb = []
#     pltKe = []
#     pltMlt = []
#     pltSwe = []
#     pltDay = []
#     pltFs1 = []
#     pltPpt = []
#     pltKr = []
#     pltMass = []
#     pltPdrew = []
#
#     # Define user-controlled constants, these are constants to start with day one, replace
#     # with spin-up data when multiple years are covered
#     ze = 40
#     p = 0.4
#     kc_min = 0.15
#     infil = 0.0
#     precip = 0.0
#     et = 0.0
#     runoff = 0.0
#     ppt_tom = 0.0
#     fb = 0.25
#     swe = 0.0
#     ke_max = 1.0
#     cum_mass = 0.0
#     tot_transp = 0.0
#     tot_evap = 0.0
#     a_min = 0.45
#     a_max = 0.90
#     pA = a_min
#     print 'Starting {a}...........'.format(a=amf_names[panel])
#
#     for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
#         if dday == start:
#             day = 0
#             print '......................at day zero'
#         else:
#             day += 1
#         day_of_year = dday.timetuple().tm_yday
#         loopTime = datetime.datetime.now()
#
#         # 'date', 'ksat', 'kcb', 'rlin', 'etrs_Pm', 'plant height', 'min temp',
#         # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws'
#         if dday == start:
#             fc = data[0, 12] / 100.
#             wp = data[0, 13] / 100.
#             etrs = float(data[day, 6])
#             tew = (fc - 0.5 * wp) * ze  # don't use time-dependent etrs for long-term simulations
#             taw = data[0, 14]
#             aws = data[0, 15] * 100.
#             print 'TAW is {a} and AWS is {b}'.format(a=taw, b=aws)
#             rew = min((2 + (tew / 3.)), 0.8 * tew)
#
#             pDr = taw
#             pDe = tew
#             pDrew = rew
#             dr = taw
#             de = tew
#             drew = rew
#
#             ksat_init = data[0, 2] * 86.4 / 10.  # from micrometer/sec to mm/day
#             old_ksat = data[0, 1] * 1000 / 3.281  # from ft/dat to mm/day
#             print 'SSURGO Ksat is {a} and bedrock Ksat is {b}'.format(a=ksat_init, b=old_ksat)
#
#         if sMon < dday < eMon:
#             ksat = ksat_init / 12.
#         else:
#             ksat = ksat_init / 4.
#         # print 'Ksat for this day is {a} mm/day'.format(a=ksat)
#
#         #  Find et and evap
#
#         kcb = data[day, 3]
#
#         etrs = data[day, 6]
#
#         kc_max_1 = kcb + 0.0001
#         kc_max = max(0.0001, kc_max_1)
#
#         # compute coverage/exposure of soil
#         # plnt_hgt = data[day, 7]
#         # plnt_term = plnt_hgt * 0.5 + 1
#         # numr = max(kcb - kc_min, 0.01)
#         # denom = max((kc_max - kc_min), 0.01)
#         # fcov_ref = (numr / denom) ** plnt_term
#         # fcov_min = min(fcov_ref, 1.00)
#         # fcov = max(fcov_min, 0.1)   # vegetation-covered ground
#         # few = max(1 - fcov, 0.01)   # exposed ground
#
#         few = 1 - (kcb / 1.25)
#
#         # root zone stress coefficient
#         ks_ref = (taw - dr) / (0.6 * taw)
#         ks_min = max(ks_ref, 0.001)
#         ks = min(ks_min, 1.0)
#
#         # total evaporation layer reduction coefficient (aka stage 2)
#         kr = min((tew - de) / (tew - rew), 1.0)
#
#         # check if stage 1 evaporation is occurring
#         # and calculate STRESS
#         # remember to apply a condition for bare ground
#         # if NDVI < 0.05:
#         #     ke = (fs1 + (1 - fs1) * kr) * ke_max
#
#         fsa = (rew - drew) / (ke_max * etrs)
#         fsb = min(fsa, 1.0)
#         fs1 = max(fsb, 0.0)
#
#         ke = min((fs1 + (1 - fs1) * kr) * (kc_max - (ks * kcb)), few * kc_max)
#
#         eta = (ks * kcb + ke) * etrs
#         eta = max(eta, 0.0)
#         transp = (ks * kcb) * etrs
#         evap_init = ke * etrs
#         evap = max(evap_init, 0.0)
#
#         if dday == end:
#             temp = data[day, 10]
#             max_temp = data[day, 9]
#             min_temp = data[day, 8]
#             ppt_tot = data[day, 11]
#             ppt_tom = 0.0
#         else:
#             temp = data[day, 10]
#             max_temp = data[day, 9]
#             min_temp = data[day, 8]
#             ppt_tot = data[day, 11]
#             ppt_tom = data[day + 1, 11]
#
#         if temp < 0.0:
#             snow_fall = ppt_tot
#
#             if snow_fall > 3.0:
#                 a = a_max
#             else:
#                 k = 0.12
#                 a = a_min + (pA - a_min) * np.exp(-k)
#                 a = min(a, a_max)
#                 a = max(a, a_min)
#
#             rain = 0.0
#             rain_tom = 0.0
#         else:
#             snow_fall = 0.0
#             rain = ppt_tot
#             rain_tom = ppt_tom
#             k = 0.05
#             a = a_min + (pA - a_min) * np.exp(-k)
#             a = min(a, a_max)
#             a = max(a, a_min)
#
#         pA = a
#         swe = snow_fall + swe
#
#         rg = data[day, 5]
#         mlt_init = max(((1 - a) * rg * 0.15) + (temp - 1.5) * 3.956, 0.0)
#         mlt = min(swe, mlt_init)
#
#         swe = swe - mlt
#
#         # Find depletions
#
#         pDr = dr
#         pDe = de
#         pDrew = drew
#
#         watr = rain + mlt
#         deps = dr + de + drew
#
#         if watr <= deps:
#             ro = 0.0
#             dp_r = 0.0
#         elif ksat + deps > watr > deps:
#             ro = 0.0
#             dp_r = watr - deps
#         elif watr > ksat + deps:
#             ro = watr - ksat - deps
#             dp_r = ksat
#         else:
#             ro = 0.0
#             dp_r = 0.0
#             pass
#
#         drew_1 = min((pDrew + ((ro + (few / evap)) - (rain + mlt))), rew)
#         drew = max(drew_1, 0.0)
#         diff = max(pDrew - drew, 0.0)
#
#         de_1 = min(pDe + evap / few - (rain + mlt - diff), tew)
#         de = max(de_1, 0.0)
#         diff2 = max((diff + (pDe - de)), 0.0)
#
#         dr_1 = min((pDr + ((transp + dp_r) - (rain + mlt - diff2))), taw)
#         dr = max(dr_1, 0.0)
#
#         infil += dp_r
#         tot_transp += transp
#         tot_evap += evap
#         et += transp + evap
#         precip += rain + snow_fall
#         runoff += ro
#         snow_ras = swe + snow_fall - mlt
#
#         # Check MASS BALANCE for the love of WATER!!!
#         mass = rain + mlt - (ro + transp + evap + dp_r + ((pDr - dr) + (pDe - de) + (pDrew - drew)))
#         cum_mass += abs(mass)
#         if dday == end:
#             end_mass = precip - infil - runoff - snow_ras - et - ((taw - dr) + (tew - de) + (rew - drew))
#
#         # Append everything to its index plotting object (list) daily
#         pltDay.append(dday)
#         pltRain.append(rain)
#         pltEta.append(eta)
#         pltEvap.append(evap)
#         pltSnow_fall.append(snow_fall)
#         pltRo.append(ro)
#         pltDr.append(dr)
#         pltDe.append(de)
#         pltDrew.append(drew)
#         pltPdrew.append(pDrew)
#         pltTemp.append(temp)
#         pltDp_r.append(dp_r)
#         pltKs.append(ks)
#         pltPdr.append(pDr)
#         pltEtrs.append(etrs)
#         pltKcb.append(kcb)
#         pltPpt.append(ppt_tot)
#         pltKe.append(ke)
#         pltKr.append(kr)
#         pltMlt.append(mlt)
#         pltSwe.append(swe)
#         pltTempM.append(max_temp)
#         pltFs1.append(fs1)
#         pltMass.append(mass)
#
#     amf_eta_mean = np.mean(df_amf.iloc[:, 10].values)
#     etrm_eta_mean = np.mean(np.array(pltEta))
#     print ''
#     print 'AMF ET mean: {}mm/day  ETRM ET mean:  {}mm/day'.format(amf_eta_mean, etrm_eta_mean)
#     print 'Cumulative mass balance error: {}'.format(cum_mass)
#     print ''
#     if dday == end:
#         fdata = np.column_stack((pltSnow_fall, pltRain, pltMlt, pltEta, pltRo, pltDp_r, pltDr, pltDe, pltDrew, pltMass))
#         np.savetxt('C:\\Users\\David\\Documents\\Recharge\\aET\extra_data\\calibration_1APR.csv',
#                    fdata,
#                    fmt=['%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f'],
#                    delimiter=',')
#
#     # plt.plot(pltDay, pltEtrs, 'orange', label='ETRS (mm)')
#     # plt.plot(pltDay, pltEta, 'r', label='Evapotranspiration (mm)')
#     # plt.plot(df_amf.iloc[:, 0].values, df_amf.iloc[:, 10].values, 'k+', label='Measured ET from Flux Tower')
#     # plt.legend()
#     # plt.title('ETRM vs AMF Data at {}... AMF ET mean: {}mm/day  ETRM ET mean:  {}mm/day... Cumulative mass balance error: {}mm'.format(extract_name, amf_eta_mean, etrm_eta_mean, cum_mass))
#     # plt.xlabel('Date')
#     # plt.ylabel('(mm)')
#     # plt.show()
#
#     plt.subplot(5, 1, 1)
#     plt.plot(pltDay, pltEtrs, 'orange', label='ETRS (mm)')
#     plt.plot(pltDay, pltEta, 'r', label='Evapotranspiration (mm)')
#     plt.plot(df_amf.iloc[:, 0].values, df_amf.iloc[:, 10].values, 'k+', label='Measured ET from Flux Tower')
#     plt.legend()
#     plt.title('ETRM vs AMF Data at {}... AMF ET mean: {}mm/day  ETRM ET mean:'
#               '  {}mm/day... Cumulative mass balance error: {}mm'.format(extract_name,
#                                                                          amf_eta_mean, etrm_eta_mean, cum_mass))
#     plt.xlabel('Date')
#     plt.ylabel('(mm)')
#     plt.subplot(5, 1, 2)
#     plt.plot(pltDay, pltSwe, 'b', label='ETRM Snow Water Equivalent (mm)')
#     plt.plot(pltDay, pltRain, 'red', label='Rain (mm)')
#     plt.plot(pltDay, pltSnow_fall, 'b', label='Snow Fall Water Equivalent (mm)')
#     plt.legend()
#     plt.subplot(5, 1, 3)
#     plt.plot(pltDay, pltDp_r, 'g', label='Recharge (mm)')
#     plt.plot(pltDay, pltRo, 'p', label='Runoff (mm)')
#     plt.legend()
#     plt.subplot(5, 1, 4)
#     plt.plot(pltDay, pltMass, 'r')
#     plt.legend()
#     plt.subplot(5, 1, 5)
#     plt.plot(pltDay, pltKs, 'r', label='Stress Coefficient (-)')
#     plt.plot(pltDay, pltFs1, 'g', label='Stage 1 Evaporation Coefficient (-)')
#     plt.plot(pltDay, pltKr, 'b', label='Evaporation Reduction Coefficient (-)')
#     plt.legend()
#
#     # plt.subplot(5, 1, 1)
#     # plt.plot(pltDay, pltKs, 'r', label='Stress Coefficient (-)')
#     # plt.plot(pltDay, pltFs1, 'g', label='Stage 1 Evaporation Coefficient (-)')
#     # plt.plot(pltDay, pltKr, 'b', label='Evaporation Reduction Coefficient (-)')
#     # plt.legend()
#     # plt.subplot(5, 1, 2)
#     # plt.plot(pltDay, pltSwe, 'b', label='ETRM Snow Water Equivalent (mm)')
#     # plt.plot(pltDay, pltRain, 'purple', label='Rain (mm)')
#     # plt.plot(pltDay, pltSnow_fall, 'b', label='Snow Fall Water Equivalent (mm)')
#     # plt.legend()
#     # plt.subplot(5, 1, 3)
#     # plt.plot(pltDay, pltDr, 'p', label='Root Zone Depletion (mm)')
#     # plt.xlabel('Days')
#     # plt.legend()
#     # plt.subplot(5, 1, 4)
#     # plt.plot(pltDay, pltDrew, 'p', label='Skin Layer Depletion (mm)')
#     # plt.xlabel('Days')
#     # plt.subplot(5, 1, 5)
#     # plt.plot(pltDay, pltDe, 'p', label='Evaporation Layer Depletion (mm)')
#     # plt.xlabel('Days')
#     # plt.legend()
#     # plt.show()
