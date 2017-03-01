from datetime import datetime
from dateutil import rrule
import numpy as np


def run_daily_etrm(start, end, data, sMon, eMon, col):
    alpha = col[0]
    beta = col[1]
    gamma = col[2]
    delta = col[3]
    zeta = col[4]
    theta = col[5]

    # Define user-controlled constants, these are constants to start with day one, replace
    # with spin-up data when multiple years are covered
    ze = 100 * theta
    p = 0.4
    kc_min = 0.15
    infil = 0.0
    precip = 0.0
    et = 0.0
    runoff = 0.0
    ppt_tom = 0.0
    fb = 0.25
    swe = 0.0
    cum_mass = 0.0
    tot_transp = 0.0
    tot_evap = 0.0
    a_min = 0.45
    a_max = 0.90
    pA = a_min
    ke_max = 1.0
    tot_transp = 0.0
    tot_evap = 0.0
    cum_mass = 0.0
    infil = 0.0
    tot_transp = 0.0
    tot_evap = 0.0
    et = 0.0
    precip = 0.0
    runoff = 0.0
    cum_mass = 0.0

    # Create indices to plot point time series, these are empty lists that will
    # be filled as the simulation progresses
    pltRain = []
    pltEta = []
    pltEvap = []
    pltTransp = []
    pltSnow_fall = []
    pltRo = []
    pltDr = []
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
    pltA = []
    pltKr = []
    pltMass = []
    pltPdr = []
    pltPde = []
    pltPdrew = []

    for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        if dday == start:
            day = 0
            # print '..................at day zero'
        else:
            day += 1

        day_of_year = dday.timetuple().tm_yday
        loopTime = datetime.now()
        if dday == start:
            ppt_tot = data[day - 1, 11]
        else:
            ppt_tot = data[day, 11]
        # print str(dday) + " PRECIP  " + str(ppt_tot)

        # ['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
        # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z'

        if dday == start:
            fc = data[0, 12] / 100.
            wp = data[0, 13] / 100.
            etrs = float(data[day, 6])
            tew = (fc - 0.5 * wp) * ze  # don't use time-dependent etrs for long-term simulations
            taw = data[0, 14] * delta
            aws = data[0, 15] * 10.
            # print 'TAW is {a} and AWS is {b}'.format(a=taw, b=aws)
            rew = min((2 + (tew / 3.)), 0.8 * tew)

            pDr = taw
            pDe = tew
            pDrew = rew
            dr = taw
            de = tew
            drew = rew

            ksat_init = data[0, 2] * 86.4  # from micrometer/sec to mm/day
            old_ksat = data[0, 1] * 1000 / 3.281  # from ft/dat to mm/day
            # print 'SSURGO Ksat is {a} and bedrock Ksat is {b}'.format(a=ksat_init, b=old_ksat)

        if sMon < dday < eMon:
            ksat = ksat_init / 12.
        else:
            ksat = ksat_init / 4.
        # print 'Ksat for this day is {a} mm/day'.format(a=ksat)

        kcb = (data[day, 3] / 1.25) * zeta

        etrs = data[day, 6] * gamma

        kc_max_1 = kcb + 0.0001
        kc_max = max(0.0001, kc_max_1)

        # compute coverage/exposure of soil
        plnt_hgt = data[day, 7]
        plnt_term = plnt_hgt * 0.5 + 1
        numr = max(kcb - kc_min, 0.01)
        denom = max((kc_max - kc_min), 0.01)
        fcov_ref = (numr / denom) ** plnt_term
        fcov_min = min(fcov_ref, 1.00)
        fcov = max(fcov_min, 0.1)  # vegetation-covered ground
        few = max(1 - fcov, 0.01)  # exposed ground

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
            temp = data[day, 10] + alpha
            max_temp = data[day, 9]
            min_temp = data[day, 8]
            ppt_tot = data[day, 11] * beta
            ppt_tom = 0.0
        else:
            temp = data[day, 10] + alpha
            max_temp = data[day, 9]
            min_temp = data[day, 8]
            ppt_tot = data[day, 11] * beta
            ppt_tom = data[day + 1, 11]

        if temp < 0.0:
            snow_fall = ppt_tot

            if snow_fall > 3.0:
                a = a_max
            else:
                k = 0.12
                a = a_min + (pA - a_min) * np.exp(-k)
                a = min(a, a_max)
                a = max(a, a_min)

            rain = 0.0
            rain_tom = 0.0
        else:
            snow_fall = 0.0
            rain = ppt_tot
            rain_tom = ppt_tom
            k = 0.05
            a = a_min + (pA - a_min) * np.exp(-k)
            a = min(a, a_max)
            a = max(a, a_min)

        pA = a
        swe = snow_fall + swe

        rg = data[day, 5]
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

        drew_1 = min((pDrew + ((ro + (fs1 * evap)) - (rain + mlt))), rew)
        drew = max(drew_1, 0.0)
        diff = max(pDrew - drew, 0.0)

        de_1 = min(pDe + ((1 - fs1) * evap) - (rain + mlt - diff), tew)
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
        pltTransp.append(transp)
        pltSnow_fall.append(snow_fall)
        pltRo.append(ro)
        pltDr.append(dr)
        pltDe.append(de)
        pltDrew.append(drew)
        pltPdr.append(pDr)
        pltPde.append(pDe)
        pltPdrew.append(pDrew)
        pltTemp.append(temp)
        pltDp_r.append(dp_r)
        pltKs.append(ks)
        pltEtrs.append(etrs)
        pltKcb.append(kcb)
        pltPpt.append(ppt_tot)
        pltKe.append(ke)
        pltKr.append(kr)
        pltMlt.append(mlt)
        pltSwe.append(swe)
        pltTempM.append(max_temp)
        pltA.append(a)
        pltFs1.append(fs1)
        pltMass.append(mass)

    tot_data = [precip, et, tot_transp, tot_evap, infil, runoff, snow_fall, cum_mass, end_mass]

    pltDay = np.array(pltDay, dtype=object)
    pltRain = np.array(pltRain, dtype=float)
    pltEta = np.array(pltEta, dtype=float)
    pltEvap = np.array(pltEvap, dtype=float)
    pltTransp = np.array(pltTransp, dtype=float)
    pltSnow_fall = np.array(pltSnow_fall, dtype=float)
    pltRo = np.array(pltRo, dtype=float)
    pltDr = np.array(pltDr, dtype=float)
    pltDe = np.array(pltDe, dtype=float)
    pltDrew = np.array(pltDrew, dtype=float)
    pltTemp = np.array(pltTemp, dtype=float)
    pltDp_r = np.array(pltDp_r, dtype=float)
    pltKs = np.array(pltKs, dtype=float)
    pltEtrs = np.array(pltEtrs, dtype=float)
    pltKcb = np.array(pltKcb, dtype=float)
    pltPpt = np.array(pltPpt, dtype=float)
    pltKe = np.array(pltKe, dtype=float)
    pltKr = np.array(pltKr, dtype=float)
    pltMlt = np.array(pltMlt, dtype=float)
    pltSwe = np.array(pltSwe, dtype=float)
    pltTempM = np.array(pltTempM, dtype=float)
    pltFs1 = np.array(pltFs1, dtype=float)
    pltMass = np.array(pltMass, dtype=float)
    pltA = np.array(pltA, dtype=float)

    pt_data = np.column_stack((pltDay, pltRain, pltSnow_fall, pltSwe, pltMlt, pltEtrs, pltEta, pltEvap, pltTransp,
                               pltDp_r, pltRo, pltDr, pltDe, pltDrew, pltTemp, pltKs, pltKe, pltKr, pltFs1, pltMass,
                               pltA))

    mass_data = np.column_stack((pltRain, pltMlt, pltRo, pltTransp, pltEvap, pltDp_r, pltPdr, pltPde, pltPdrew,
                                 pltDr, pltDe, pltDrew, pltMass))

    return pt_data, tot_data, mass_data
