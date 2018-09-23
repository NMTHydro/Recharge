# ETRM - Evapotranspiration and Recharge Model, Point version, CMB Comparison
# For use with multiple chloride mass balance sites
# David Ketchum, April 2016

import matplotlib.pyplot as plt
import datetime
from dateutil import rrule
import os
import numpy as np

# Define user-controlled constants, these are constants to start with day one, replace
# with spin-up data when multiple years are covered
ze = 100
p = 0.4
kc_min = 0.015

# Set start datetime object
start, end = datetime.datetime(2009, 1, 1), datetime.datetime(2013, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime.datetime(start.year, 11, 1), datetime.datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime.datetime(start.year, 6, 1), datetime.datetime(start.year, 10, 1)

# beware coordinates that reside in another UTM zone!
cmbDict = {'SR0003': {'Coords': '518279 3544204', 'Name': 'Davils_Den', 'Recharge_Index': '0.0411'},
           'SR0005': {'Coords': '521144 3546779', 'Name': 'Hatchet', 'Recharge_Index': '0.0615'},
           'SR0006': {'Coords': '520059 3546560', 'Name': 'Upper_Soldier', 'Recharge_Index': '0.0491'},
           'SR0008': {'Coords': '269973 3752417', 'Name': 'N_Withington', 'Recharge_Index': '0.0386'},
           'SR0009': {'Coords': '269853 3750017', 'Name': 'Chimney_Rock', 'Recharge_Index': '0.0584'},
           'SR0013': {'Coords': '132085 3724098', 'Name': 'Pueblo_CG', 'Recharge_Index': '0.0590'},       # UTM Z12
           'SR0014': {'Coords': '136997 3728614', 'Name': 'Quarter_Corner', 'Recharge_Index': '0.0689'},  # UTM Z12
           'SR0015': {'Coords': '138987 3735586', 'Name': 'Wet_Legget', 'Recharge_Index': '0.0583'},      # UTM Z12
           'SR0018': {'Coords': '169658 3714919', 'Name': 'Old_Cabin', 'Recharge_Index': '0.0288'},       # UTM Z12
           'SR0019': {'Coords': '159431 3704014', 'Name': 'Bear_Wallow', 'Recharge_Index': '0.0272'},     # UTM Z12
           'SR0020': {'Coords': '168414 3731949', 'Name': 'Eagle_Peak', 'Recharge_Index': '0.1076'},      # UTM Z12
           'SR0021': {'Coords': '298352 3762484', 'Name': 'S_Baldy', 'Recharge_Index': '0.1278'},
           'SR0022': {'Coords': '300584 3762423', 'Name': 'Timber_Peak_1', 'Recharge_Index': '0.1201'},
           'SR0023': {'Coords': '301097 3761532', 'Name': 'Timber_Peak_2', 'Recharge_Index': '0.1195'},
           'SR0025': {'Coords': '301541 3761632', 'Name': 'Six_Mile', 'Recharge_Index': '0.0935'},
           'SR0026': {'Coords': '381910 4030350', 'Name': 'Rock', 'Recharge_Index': '0.0546'},
           'SR0027': {'Coords': '381936 4032236', 'Name': 'Rancherilla', 'Recharge_Index': '0.0594'},
           'SR0029': {'Coords': '344319 3991508', 'Name': 'Cerro', 'Recharge_Index': '0.0797'},
           'SR0030': {'Coords': '343470 3989456', 'Name': 'Lutiero', 'Recharge_Index': '0.0608'},
           'SR0031': {'Coords': '442271 3954494', 'Name': 'Rosilla', 'Recharge_Index': '0.0807'},
           'SR0032': {'Coords': '442098 3954470', 'Name': 'Rosilla_300', 'Recharge_Index': '0.0785'},
           'SR0033': {'Coords': '438861 3945210', 'Name': 'Alamosa', 'Recharge_Index': '0.0210'},
           'SR0034': {'Coords': '528056 3566678', 'Name': 'Sitting_Bull', 'Recharge_Index': '0.0330'},
           # Single-sample sites
           'SR0001': {'Coords': '519625 3543303', 'Name': 'Heliport_Tank', 'Recharge_Index': '0.0457'},
           'SR0002': {'Coords': '519504 3543327', 'Name': 'E_Heliport_Tank', 'Recharge_Index': '0.0830'},
           'SR0007': {'Coords': '520075 3546588', 'Name': 'Lower_Soldier', 'Recharge_Index': '0.0474'},
           'SR0010': {'Coords': '373611 3973635', 'Name': 'N_Ski_Area_Draw', 'Recharge_Index': '0.0556'},
           'SR0011': {'Coords': '374748 3974465', 'Name': 'XC_Draw', 'Recharge_Index': '0.0571'},
           'SR0012': {'Coords': '372303 3969057', 'Name': 'Cerro_Grande', 'Recharge_Index': '0.0587'},
           'SR0016': {'Coords': '298839 3763615', 'Name': 'Trail_11_1', 'Recharge_Index': '0.1229'},
           # 'SR0017': {'Coords': '299439 3763490', 'Name': 'Trail_11_2', 'Recharge_Index': 'x.xxx'},
           'SR0024': {'Coords': '301906 3761086', 'Name': 'Timber_Peak_3', 'Recharge_Index': '0.1025'},
           'SR0028': {'Coords': '427223 3960482', 'Name': 'Vista_Grande', 'Recharge_Index': '0.0838'}}

info = cmbDict.items()
codes = [(x[0]) for x in info]
info = [str(x[1]) for x in info]
coords = [str(x[40:52]) for x in info]
names = [str(x[66:-2]) for x in info]
cmb_rech_ind = [float(x[20:26]) for x in info]

years = [x for x in range(start.year, end.year + 1)]

# Load up all data needed for ETRM from extract .csv
# EXTRACT PARAMETERS
etrm_rech_ind = []

site_count = 0
for site in codes:
    site_count += 1
    extract_name = names[codes.index(site)]
    rech_ind = float(cmb_rech_ind[codes.index(site)])
    name = 'C:\\Users\\David\\Documents\\Recharge\\CMB\\CMB_extracts\\{a}_extract.csv'.format(a=site)
    print('Processing site {} code {}'.format(extract_name, site))
    # Get a numpy object of all raster-extracted data out of the csv it is held in
    recs = []
    try:
        fid = open(name)
        # print "file: " + str(fid)
        lines = fid.readlines()[:]
        fid.close()
    except IOError:
        print("couldn't find ")  # + '{a}'.format(a=fid)
        break
    rows = [line.split(',') for line in lines]
    for line in rows:
        try:
            recs.append([datetime.datetime.strptime(line[0], '%m/%d/%Y'),  # date
                         float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                         float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                         float(line[9]), float(line[10]), float(line[11]), float(line[12]),
                         float(line[13]), float(line[14]), float(line[15]), float(line[16])])
        except ValueError:
            recs.append([datetime.datetime.strptime(line[0], '%Y/%m/%d'),  # date
                         float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                         float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                         float(line[9]), float(line[10]), float(line[11]), float(line[12]),
                         float(line[13]), float(line[14]), float(line[15]), float(line[16])])

        # ['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
        # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z']

    data = np.array(recs)

    # Data format now in [date, ksat, soil_ksat, kcb, rlin, rg, etrs_Pm, plant height, min temp,
    # max temp, temp, prcip, fc, wp, taw, aws, root_z]

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
    ze = 100
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
    # print 'Starting {a}...........'.format(a=names[panel])
    # for dday in rrule.rrule(rrule.DAILY, dtstart=snotel_start_obj, until=snotel_end_obj):
    for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        if dday == start:
            day = 0
            # print '..................at day zero'
        else:
            day += 1

        day_of_year = dday.timetuple().tm_yday
        loopTime = datetime.datetime.now()

        # 'date', 'ksat', 'kcb', 'rlin', 'etrs_Pm', 'plant height', 'min temp',
        # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws'
        if dday == start:
            fc = data[0, 12] / 100
            wp = data[0, 13] / 100
            etrs = float(data[day, 6])
            tew = (fc - 0.5 * wp) * ze  # don't use time-dependent etrs for long-term simulations
            taw = data[0, 14]
            # aws = data[0, 15] * 100.
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

    #  Find et and evap

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

xx = np.linspace(0, 0.15, 2)
yy = xx
plt.scatter(cmb_rech_ind, etrm_rech_ind, c='blue', marker=u'o', edgecolor='none')
plt.plot(xx, yy, c='red', marker=u' ')
plt.title('Modeled Recharge vs. Chloride Mass Balance Recharge')
plt.xlabel('CMB Recharge (Percent of Precipitation)')
plt.ylabel('ETRM Recharge (Perceent of Precipitation)')
plt.show()

