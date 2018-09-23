# ETRM - Evapotranspiration and Recharge Model, Point version, SNOW CALIBRATION
# For use with multiple SNOTEL stations
# David Ketchum, December 2015
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
from dateutil import rrule
import os
from osgeo import ogr
import numpy as np
startTime = datetime.now()
print(startTime)


# Define user-controlled constants, these are constants to start with day one, replace
# with spin-up data when multiple years are covered
ze = 100
p = 0.4
kc_min = 0.015

# Set start datetime object
start, end = datetime(2000, 1, 1), datetime(2013, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime(start.year, 11, 1), datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime(start.year, 6, 1), datetime(start.year, 10, 1)

shp_filename = 'C:\\Recharge_GIS\\qgis_layers\\sensitivity_points\\SA_pnts29APR16_UTM.shp'

ds = ogr.Open(shp_filename)
lyr = ds.GetLayer()
defs = lyr.GetLayerDefn()
x = 0
recs = []
already_done = ['Bateman']
for feat in lyr:
    name = feat.GetField("Name")
    if name not in already_done:
        pass
    else:
        x += 1
        point_id_obj = x
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()
        etrm_rech_ind = []
        file_name = 'C:\Users\David\Documents\Recharge\Sensitivity_analysis\SA_extracts\{a}_extract.csv'.format(a=name)
        try:
            fid = open(file_name)
            lines = fid.readlines()[:]
            fid.close()
            print(name)
        except IOError:
            print("couldn't find " + '{a}'.format(a=fid))
            # break
        rows = [line.split(',') for line in lines]

        for line in rows:
            try:
                recs.append([datetime.strptime(line[0], '%m/%d/%Y'),  # date
                             float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                             float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                             float(line[9]), float(line[10]), float(line[11]), float(line[12]), float(line[13]),
                             float(line[14]), float(line[15]), float(line[16])])

            except ValueError:
                try:
                    recs.append([datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S'),  # date
                                 float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                                 float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                                 float(line[9]), float(line[10]), float(line[11]), float(line[12]), float(line[13]),
                                 float(line[14]), float(line[15]), float(line[16])])
                except ValueError:
                    recs.append([datetime.strptime(line[0], '%Y/%m/%d'),  # date
                                 float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                                 float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                                 float(line[9]), float(line[10]), float(line[11]), float(line[12]), float(line[13]),
                                 float(line[14]), float(line[15]), float(line[16])])

                # ['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
                # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z'

        data = np.array(recs)

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
        pltA = []
        pltPdrew = []
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
        ke_max = 1.2
        tot_transp = 0.0
        tot_evap = 0.0
        cum_mass = 0.0
        print('Starting {a}...........'.format(a=name))
        # for dday in rrule.rrule(rrule.DAILY, dtstart=snotel_start_obj, until=snotel_end_obj):
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
                fc = data[0, 12]
                wp = data[0, 13]
                etrs = float(data[day, 6])
                tew = (fc - 0.5 * wp) * ze  # don't use time-dependent etrs for long-term simulations
                taw = data[0, 14]
                aws = data[0, 15] * 100.
                # print 'TAW is {a} and AWS is {b}'.format(a=taw, b=aws)
                rew = min((2+(tew/3.)), 0.8 * tew)

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

            kcb = data[day, 3]

            etrs = data[day, 6]

            kc_max_1 = kcb + 0.0001
            kc_max = max(0.0001, kc_max_1)

            # compute coverage/exposure of soil
            plnt_hgt = data[day, 7]
            plnt_term = plnt_hgt * 0.5 + 1
            numr = max(kcb - kc_min, 0.01)
            denom = max((kc_max - kc_min), 0.01)
            fcov_ref = (numr / denom) ** plnt_term
            fcov_min = min(fcov_ref, 1.00)
            fcov = max(fcov_min, 0.1)   # vegetation-covered ground
            few = max(1 - fcov, 0.01)   # exposed ground

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
                temp = data[day, 10]
                max_temp = data[day, 9]
                min_temp = data[day, 8]
                ppt_tot = data[day, 11]
                ppt_tom = 0.0
            else:
                temp = data[day, 10]
                max_temp = data[day, 9]
                min_temp = data[day, 8]
                ppt_tot = data[day, 11]
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

            # Append everything to its index plotting object (list) daily
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

        site_etrm_rech_ind = sum(pltDp_r) / sum(pltPpt)
        etrm_rech_ind.append(site_etrm_rech_ind)

    # xx = np.linspace(0, 0.25, 2)
    # yy = xx
    # plt.scatter(cmb_rech_ind, etrm_rech_ind, c='blue', marker=u'o', edgecolor='none')
    # plt.plot(xx, yy, c='red', marker=u' ')
    # plt.title('Modeled Recharge vs. Chloride Mass Balance Recharge')
    # plt.xlabel('CMB Recharge (Percent of Precipitation)')
    # plt.ylabel('ETRM Recharge (Perceent of Precipitation)')
    # plt.show()

