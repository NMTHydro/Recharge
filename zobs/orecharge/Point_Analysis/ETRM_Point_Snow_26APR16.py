# ETRM - Evapotranspiration and Recharge Model, Point version, SNOW CALIBRATION
# For use with multiple SNOTEL stations
# David Ketchum, December 2015
import pandas as pd
from  matplotlib import pyplot as plt
from datetime import datetime
from dateutil import rrule
import os
import numpy as np
startTime = datetime.now()
print(startTime)


# Define user-controlled constants, these are constants to start with day one, replace
# with spin-up data when multiple years are covered
ze = 10
p = 0.4
kc_min = 0.015

# Set start datetime object
start, end = datetime(2000, 1, 1), datetime(2013, 12, 31)
# Define winter and summer for SNOW algorithm
sWin, eWin = datetime(start.year, 11, 1), datetime(end.year, 3, 30)
# Define monsoon for Ksat, presumed storm intensity
sMon, eMon = datetime(start.year, 6, 1), datetime(start.year, 10, 1)

# Create snow dict, with SNOTEL locations, station code, etc.
# I'm just using the data with complete sets
snowdict = { # '1034': {'Coords': '427072 3696447', 'Name': 'Sierra_Blanca'},
# '316': {'Coords': '382254 4041874', 'Name': 'Bateman'},
# '394': {'Coords': '352748 4092121', 'Name': 'Chamita'},
# '921': {'Coords': '427111 3951608', 'Name': 'Elk_Cabin'},
# '491': {'Coords': '450102 4005710', 'Name': 'Gallegos_Pk'},
# '532': {'Coords': '387931 4065100', 'Name': 'Hopewell'},
# '665': {'Coords': '477309 4094348', 'Name': 'North_Costilla'},
# '1170': {'Coords': '470862 4030028', 'Name': 'Palo'},
# '708': {'Coords': '375051 3976516', 'Name': 'Quemazon'},
# '715': {'Coords': '470078 4062200', 'Name': 'Red_River'},
# '922': {'Coords': '429952 3959270', 'Name': 'Santa_Fe'},
# '1168': {'Coords': '459296 4048933', 'Name': 'Taos'},
# '934': {'Coords': '483426 4062200', 'Name': 'Tolby'},
# '1083': {'Coords': '452763 3999049', 'Name': 'Tres_Ritos'},
# '1017': {'Coords': '337383 3989335', 'Name': 'Vacas_Locas'},
# '854': {'Coords': '451650 3960234', 'Name': 'Wesner_Sprgs'}}
# '744': {'Coords': '335518 3986043', 'Name': 'Senorita_Div'},
# '1048': {'Coords': '232363 3656597', 'Name': 'Mcknight_cabin'},
# '1138': {'Coords': '684790 4006424', 'Name': 'Navajo_Whisky_Crk'},
# '755': {'Coords': '766973 3646589', 'Name': 'Signal_pk'},
# '933': {'Coords': '748889 3902532', 'Name': 'Rice_Pk'},
'486': {'Coords': '690355 3735779', 'Name': 'Frisco_Div'}}
# '757': {'Coords': '713500 3695213', 'Name': 'Silver_Crk_Div'}}

info = snowdict.items()
codes = [int(x[0]) for x in info]
info = [str(x[1]) for x in info]
coords = [str(x[12:26]) for x in info]
names = [str(x[38:-2]) for x in info]

years = [x for x in range(start.year, end.year + 1)]

# Load amf  data, all dates, be sure the points are at the same place!
# In this version, use SNOTEL precipitation, temperature, and SWE
# SNOW
name_fill = '_STAND_YEAR='
snow_length = []
snow_array = []
select_codes = []
select_names = []
for code in codes:
    print(code)
    snow_name = snowdict['{a}'.format(a=code)]['Name']
    folder = "C:\\Users\\David\\Documents\\Recharge\\Snow\\Data\\{a}".format(a=snow_name)
    os.chdir(folder)
    csvList = os.listdir(folder)
    snow_files = []
    if code in csvList[:3] or csvList[:4]:
        for element in csvList:
            try:
                short_code = int(element[-8:-4])
                if short_code in years:
                    yr = element[-8:-4]
                    sn_name = '{a}\\{b}{c}{d}.csv'.format(a=folder, b=code, c=name_fill, d=yr)
                    snow_files.append(sn_name)
            except ValueError:
                pass
                # print "ValueError"
        for item in snow_files:
            if item == snow_files[0]:
                sn_recs = []
            fid = open(item)
            # print "opening file: " + '{a}'.format(a=fid)
            lines = fid.readlines()[3:]
            fid.close()
            rows = [line.split(',') for line in lines]
            for line in rows:
                try:
                    if line[0] is '\n':
                        print("Found newline glitch value:  skipping")
                        print(rows.index(line))
                        del line
                    elif line[1] == 'Date':
                        del line
                        # print 'Deleted line with strings'
                    elif line[3] == '-99.9':
                        # print "Found September glitch value:  skipping"
                        # print rows.index(line)
                        del line
                    # incoming csv format :
                    # [Site Id,Date,Time,WTEQ.I-1 (in) ,PREC.I-1 (in) ,TOBS.I-1 (degC) ,TMAX.D-1 (degC) ,
                    # TMIN.D-1 (degC) ,TAVG.D-1 (degC) ,SNWD.I-1 (in)

                    # sn_data append format  :
                    # [date, swe, precip, Tobs, Tmax, Tmin, Tavg,SNWD]

                    else:
                        try:
                            sn_recs.append([(datetime.strptime(line[1], '%Y-%m-%d')), (float(line[3]) * 25.4),
                                            (float(line[4])), (float(line[5])), (float(line[6])),
                                            (float(line[7])), (float(line[8])), (float(line[9]))])
                        except ValueError:
                            sn_recs.append([(datetime.strptime(line[1], '%Y-%m-%d')), (float(line[3]) * 25.4),
                                            (float(line[4])), (float(line[5])), (float(line[6])),
                                            (float(line[7])), (float(line[8])), (str(line[9]))])
                    # This is to correct values if we ever use SNWD.H-1, another will go in the first except:
                    # if datetime.strptime(line[1], '%Y-%m-%d') in year_end:
                    #     print "Found New Year's problem"
                    #     print datetime.strptime(line[1], '%Y-%m-%d')
                except ValueError:
                    if line[3] == '-99.9':
                        # print "Found September glitch value:  skipping"
                        # print rows.index(line)
                        del line
                    else:
                        try:
                            sn_recs.append([(datetime.strptime(line[1], '%m/%d/%Y')), (float(line[3]) * 25.4),
                                        (float(line[4])), (float(line[5])), (float(line[6])),
                                        (float(line[7])), (float(line[8])), (float(line[9]))])
                        except ValueError:
                            sn_recs.append([(datetime.strptime(line[1], '%Y-%m-%d')), (float(line[3]) * 25.4),
                                        (float(line[4])), (float(line[5])), (float(line[6])),
                                        (float(line[7])), (float(line[8])), (float(line[9]))])
                except IndexError:
                    pass
                        # print "Index error " + '{a}'.format(a=line)
            # print "records in " + '{a} is {b}'.format(a=item, b=len(sn_recs))
    sn_data = np.array(sn_recs)
    print("array length for site " '{c} code {a} is {b}'.format(a=code, b=len(sn_recs), c=snow_name))
    # Convert accumulated precipitation to daily precipitation
    current_precip = []
    xx = -1
    for record in sn_data:
        xx += 1
        if xx == 0:
            p = sn_data[xx + 1, 2] - record[2]
        elif record[2] == 0.0:
            p = 0.0
        else:
            p = record[2] - sn_data[xx - 1, 2]
        current_precip.append(p * 25.4)
    replace_precip = np.array(current_precip)
    first_part = sn_data[:, 0:2]
    last_part = sn_data[:, 3:8]
    sn_data = np.column_stack((first_part, replace_precip, last_part))
    # Find null values (i.e. -99.9) in sn_data, don't worry about SNWD values (i.e. sn_data[:, 6, :]), which have null
    # values but we won't be using it
    print(sn_data.shape)
    for x in range(0, len(sn_data[0, :])):
        for y in range(0, len(sn_data[:, 0])):
            z = sn_data[y, x]
            if z == -99.9:
                sn_data[y, x] = sn_data[y - 1, x]
                # print "Found null value : " + '{a}'.format(a=(y, x))
    sn_data = pd.DataFrame(sn_data)
    snow_array.append(sn_data)
    snow_length.append(len(sn_data))
    select_codes.append(code)
    select_names.append(snow_name)

# (stel_date, stel_snow, stel_precip, stel_tobs, stel_tmax, stel_tmin, stel_tavg, stel_snwd)
meta_snow = zip(select_codes, select_names, snow_array, snow_length)

print('')
print('')
print('')
print('Moving on to EXTRACT PARAMETERS.................................................................')
print('')
print('')
print('')

#
#
# Load up all data needed for ETRM from extract .csv
# EXTRACT PARAMETERS
site_count = 0
for site in select_codes:
    site_count += 1
    extract_name = select_names[select_codes.index(site)]
    folder = 'C:\\Users\\David\\Documents\\Recharge\\Snow\\Data' + '\\{a}'.format(a=extract_name)
    extract_fill = '_extract2'
    name = '{a}\\{b}{c}.csv'.format(a=folder, b=extract_name, c=extract_fill)
    # Get a numpy object of all raster-extracted data out of the csv it is held in
    os.chdir(folder)
    recs = []
    try:
        fid = open(name)
        # print "file: " + str(fid)
        lines = fid.readlines()[:]
        fid.close()
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

    # Loop daily time step over chosen interval, computing all madel variables each day
    # fit select start and end dates for each panel (site)
    panel = select_codes.index(site)
    df_snow = snow_array[panel]
    extract_start, extract_end = data[0, 0], data[-1, 0]
    df_snow = df_snow[(df_snow.iloc[:, 0] >= extract_start) & (df_snow.iloc[:, 0] <= extract_end)]

    snotel_start_obj, snotel_end_obj = df_snow.iloc[0, 0], df_snow.iloc[-1, 0]

    #  Use the coincident data to only run the model during the period snotel data exists
    coin_data = data[data[:, 0] >= snotel_start_obj]
    data = coin_data[coin_data[:, 0] <= snotel_end_obj]

    print('Site {a} at {d} runs from {b} to {c}'.format(a=select_names[panel], b=snotel_start_obj,
                                                        c=snotel_end_obj, d=select_codes[panel]))

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
    infil = 0.0
    precip = 0.0
    et = 0.0
    runoff = 0.0
    ppt_tom = 0.0
    fb = 0.25
    a_min = 0.45
    a_max = 0.90
    pA = a_min
    ke_max = 1.2
    tot_transp = 0.0
    tot_evap = 0.0
    cum_mass = 0.0
    print('Starting {a}...........'.format(a=select_names[panel]))
    # for dday in rrule.rrule(rrule.DAILY, dtstart=snotel_start_obj, until=snotel_end_obj):
    for dday in rrule.rrule(rrule.DAILY, dtstart=snotel_start_obj, until=snotel_end_obj):
        if dday == snotel_start_obj:
            day = 0
            # print '..................at day zero'
        else:
            day += 1

        day_of_year = dday.timetuple().tm_yday
        loopTime = datetime.now()
        if dday == snotel_end_obj:
            ppt_tot = data[day - 1, 11]
        else:
            ppt_tot = data[day, 11]
        # print str(dday) + " PRECIP  " + str(ppt_tot)

        # ['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
        # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z'

        if dday == snotel_start_obj:
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

            ksat_init = data[0, 1] * 86.4 / 10.  # from micrometer/sec to mm/day
            old_ksat = data[1, 1] * 1000 / 3.281  # from ft/dat to mm/day
            # print 'SSURGO Ksat is {a} and bedrock Ksat is {b}'.format(a=ksat_init, b=old_ksat)
            swe = df_snow.iloc[0, 1]
        else:
            pEtrs = etrs

        if sMon < dday < eMon:
            ksat = ksat_init / 12.
        else:
            ksat = ksat_init / 4.
        # print 'Ksat for this day is {a} mm/day'.format(a=ksat)

        kcb = data[day, 3]

        etrs = data[day, 6]
        if etrs < 0.01:
            etrs = pEtrs

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

        # Load temp, find swe, melt, and precipitation, load Ksat
        # Use SNOTEL data for precip and temps:
        # df_snow : (stel_date, stel_snow, stel_precip, stel_tobs,
        # stel_tmax, stel_tmin, stel_tavg, stel_snwd)
        if dday == snotel_end_obj:
            temp = df_snow.iloc[day - 1, 3]
            max_temp = df_snow.iloc[day - 1, 4]
            min_temp = df_snow.iloc[day - 1, 5]
            ppt_tot = df_snow.iloc[day - 1, 2]
            ppt_tom = 0.0
        else:
            temp = df_snow.iloc[day, 3]
            max_temp = df_snow.iloc[day, 4]
            min_temp = df_snow.iloc[day, 5]
            ppt_tot = df_snow.iloc[day, 2]
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
        mlt_init = max(((1 - a) * rg * 0.07) + (temp - 1.5) * 1.0, 0.0)
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

    # [day, rain, eta, snow_fall, ro, dr, de, drew, temp, dp_r, ks pDr, etrs, kcb, kr, mlt, swe, max_temp]

    # df_snow : (stel_date, stel_snow, stel_precip, stel_tobs, stel_tmax, stel_tmin, stel_tavg, stel_snwd)

    # Plot six parameters at one site
    fig_path = 'C:\Users\David\Documents\Recharge\Snow\snow_figs\\5may\used_for_report'
    fig = plt.figure(xx, figsize=(20, 10))
    ax1 = fig.add_subplot(111)
    ax1.plot(pltDay, pltSwe, 'b', label='ETRM Snow Water Equivalent (mm)')
    ax1.plot(df_snow.iloc[:, 0].values, df_snow.iloc[:, 1].values, 'red', label='SNOTEL Observed Snow \n'
                                                                                   'Water Equivalent (mm)')
    plt.ylabel('Snow Water Equivalent (mm)')
    plt.xlabel('Date')
    # plt.plot(pltDay, pltRain, 'green', label='Rain (mm)')
    # plt.plot(pltDay, pltSnow_fall, 'b', label='Snow Fall Water Equivalent (mm)')
    plt.title('Modeled and Observed Snowfall at {}'.format(select_names[panel].replace('_', ' ')))
    plt.legend()
    plt.savefig('{}\\{}_9MAY'.format(fig_path, select_names[panel].replace('_', ' ')), ext='jpg', dpi=600, figsize=(10, 20))
    plt.close()

    # plt.figure(site_count)
    # plt.subplot(5, 1, 1)
    # plt.plot(pltDay, pltEtrs, 'k', label='ETRS (mm)')
    # plt.plot(pltDay, pltEta, 'r*', label='Evapotranspiration (mm)')
    # plt.legend()
    # plt.title('ETRM vs SNOTEL Data at {a}'.format(a=snow_name))
    # plt.xlabel('Date')
    # plt.ylabel('(mm)')
    # plt.subplot(5, 1, 2)
    # plt.plot(pltDay, pltSwe, 'b', label='ETRM Snow Water Equivalent (mm)')
    # plt.plot(df_snow.iloc[:, 0].values, df_snow.iloc[:, 1].values, 'purple', label='SNOTEL Observed', alpha=0.5)
    # plt.plot(pltDay, pltRain, 'purple', label='Rain (mm)')
    # plt.plot(pltDay, pltSnow_fall, 'b', label='Snow Fall Water Equivalent (mm)')
    # plt.legend()
    # plt.subplot(5, 1, 3)
    # plt.plot(pltDay, pltDp_r, 'g', label='Recharge (mm)')
    # plt.plot(pltDay, pltRo, 'p', label='Runoff (mm)')
    # plt.legend()
    # plt.subplot(5, 1, 4)
    # plt.plot(pltDay, pltTemp, 'r', label='Temperature (deg. C)')
    # plt.plot(pltDay, pltMlt, 'purple', label='Snow Melt (mm)')
    # plt.legend()
    # plt.subplot(5, 1, 5)
    # plt.plot(pltDay, pltKs, 'r', label='Stress Coefficient (-)')
    # plt.plot(pltDay, pltFs1, 'g', label='Stage 1 Evaporation Coefficient (-)')
    # plt.plot(pltDay, pltKe, 'b', label='Evaporation Coefficient (-)')
    # plt.legend()
    # plt.show()



# plt.subplot(5, 1, 1)
# plt.plot(pltDay, pltDp_r, 'g', label='Recharge (mm)')
# plt.plot(pltDay, pltRo, 'p', label='Runoff (mm)')
# plt.legend()
# plt.subplot(5, 1, 2)
# plt.plot(pltDay, pltSwe, 'b', label='ETRM Snow Water Equivalent (mm)')
# plt.plot(df_snow.iloc[:, 0].values, df_snow.iloc[:, 1].values, 'purple', label='SNOTEL Observed', alpha=0.5)
# plt.plot(pltDay, pltRain, 'purple', label='Rain (mm)')
# plt.plot(pltDay, pltSnow_fall, 'b', label='Snow Fall Water Equivalent (mm)')
# plt.legend()
# plt.subplot(5, 1, 3)
# plt.plot(pltDay, pltDr, 'p', label='Root Zone Depletion (mm)')
# plt.title('{a}'.format(a=snow_name))
# plt.xlabel('Days')
# plt.legend()
# plt.subplot(5, 1, 4)
# plt.plot(pltDay, pltDrew, 'p', label='Skin Layer Depletion (mm)')
# plt.title('{a}'.format(a=snow_name))
# plt.xlabel('Days')
# plt.subplot(5, 1, 5)
# plt.plot(pltDay, pltDe, 'p', label='Evaporation Layer Depletion (mm)')
# plt.title('{a}'.format(a=snow_name))
# plt.xlabel('Days')
# plt.legend()
# plt.show()
# raw_input("Press enter....")
# plt.show()
# plt.close()

# fig, ax1 = plt.subplots(1, figsize=(15,5))
# ax1.plot(pltDay, pltSwe, 'b', label='ETRM (mm)')
# ax1.plot(df_snow.iloc[:, 0].values, df_snow.iloc[:, 1].values, 'Purple', label='SNOTEL (mm)', alpha=0.5)
# ax1.plot(pltDay, pltRain, 'purple', label='Precipitation (mm)')
# ax1.plot(pltDay, pltEta, 'k', label='ETRS (mm)')
# ax1.set_ylabel('Snow Water Equivalent (mm)', color='k')
# ax1.set_xlabel('Date')
# ax1.legend()
# # plt.ylim(0.0, 140.0)
# for tl in ax1.get_yticklabels():
#     tl.set_color('b')
# ax2 = ax1.twinx()
# ax2.plot(pltDay, pltDp_r, 'g', label='Recharge')
# ax2.plot(pltDay, pltRo, color='brown', label='Runoff', alpha=0.3)
# ax2.set_ylabel('Temperature (C)', color='k')
# # plt.ylim(-5.0, 15.0)
# for tl in ax2.get_yticklabels():
#     tl.set_color('g')
# for tl in ax2.get_xticklabels():
#     tl.set_color('k')
# plt.title('Snow Water Equivalent at Sierra Blanca')
# ax2.legend()
# plt.show()
#
# print "Show me the RECHARGE!"

