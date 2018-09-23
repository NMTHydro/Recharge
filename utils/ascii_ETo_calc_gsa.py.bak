# ===============================================================================
# Copyright 2018 gabe-parrish
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

# ============= standard library imports ========================
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ============= local library imports ===========================

def get_percentile(close_values, percentile_value):
    """"""

    diff_list = []
    for temp in close_values:
        x = abs(temp - percentile_value)
        diff_list.append(x)

    ts_dry_diff = min(diff_list)

    for temp, diff in zip(close_values, diff_list):

        if diff == ts_dry_diff:
            print 'here is the one {}'.format(temp)

            closest_value = temp

    return closest_value


def parse_file(path, first_col, num_cols):
    """

    :param path:
    :return:
    """

    print 'path -> {}, first col -> {}, num_cols -> {}'.format(path, first_col, num_cols)

    ascii_unformatted_dict = {}
    ascii_unformatted_dict["good_lines"] = []

    with open(path, 'r') as readfile:
        for line in readfile:
            # print "line ->{}".format(line)

            # kill the spaces, make a list, check by the length of the list.
            line_lst = line.split(" ")
            # print "line list -> {}".format(line_lst)

            #kill spaces
            space_free = list(filter(lambda a: a != '', line_lst))

            # print "space free! -> {}".format(space_free)

            # print 'space free !!1 {}'.format(space_free[0])

            if space_free[0] == first_col and len(space_free) == num_cols:
                bands = space_free

                bands[-1] = bands[-1][:-1]

                # print "bands {}".format(bands)

                ascii_unformatted_dict["bands"] = bands

            # elif space_free[0].startswith("B"):
            #     print 'this happens'
            #     files = space_free
            #     files[-1] = files[-1][:-1]
            #     ascii_unformatted_dict['files'] = files

            elif len(space_free) == num_cols and space_free[0] != first_col:

                goodln = space_free
                # Turn the lines into floats...
                bestln = [float(i) for i in goodln]
                ascii_unformatted_dict["good_lines"].append(bestln)

    # print "the full unformatted dict \n", ascii_unformatted_dict

    #format the headers list
    headers_list = []
    print 'ascii unformatted', ascii_unformatted_dict
    for i in ascii_unformatted_dict['bands']:
        headers_list.append(i)

    # print "headers list", headers_list

    # add the headers list to the ascii_unformatted_dict
    ascii_unformatted_dict['headers'] = headers_list

    # print "this should work", ascii_unformatted_dict['headers']

    ascii_dict = {}
    for i in ascii_unformatted_dict['headers']:
        ascii_dict[i] = []

    # zip through each good_lines list and the headers and append the correct value to the list in ascii dict
    for lst in ascii_unformatted_dict['good_lines']:
        for h, val in zip(ascii_unformatted_dict['headers'], lst):
            # print "header", h
            # print "value", val

            ascii_dict[h].append(val)

    # print "ascii dict", ascii_dict

    return ascii_dict, headers_list


def plotter(x, y, image, dep_var, ind_var):
    """

    :param x: your dependent variable
    :param y: your independent variable
    :return:
    """
    # todo - make little gridlines

    # turn your x and y into numpy arrays
    x = np.array(x)
    y = np.array(y)

    ETrF_vs_NDVI = plt.figure()
    aa = ETrF_vs_NDVI.add_subplot(111)
    aa.set_title('Bare soils/Tailings Pond - {}'.format(image), fontweight='bold')
    aa.set_xlabel('{}'.format(dep_var), style='italic')
    aa.set_ylabel('{}'.format(ind_var), style='italic')
    aa.scatter(x, y, facecolors='none', edgecolors='blue')
    plt.minorticks_on()
    # aa.grid(b=True, which='major', color='k')
    aa.grid(b=True, which='minor', color='white')
    plt.tight_layout()
    # TODO - UNCOMMENT AND CHANGE THE PATH TO SAVE THE FIGURE AS A PDF TO A GIVEN LOCATION.
    # plt.savefig(
    #      "/Volumes/SeagateExpansionDrive/jan_metric_PHX_GR/green_river_stack/stack_output/20150728_ETrF_NDVI_gr.pdf")

    plt.show()


def simple_plot(x,y):
    """"""

    # turn your x and y into numpy arrays
    x = np.array(x)
    y = np.array(y)

    plt.scatter(x, y)
    plt.show()


def run_ascii():
    """
    Reads in an ascii file from erdas, parses the information and stores it as a numpy array for plotting.
    :return:
    """

    # TODO - CHANGE FOR EVERY NEW ASCII
    # Here's the path to a particular ascii file to start out.
    path = "/Users/Gabe/Desktop/GSA_consulting/jan/ascii_and_metdata/lc08_l1tp_040033_20150715__rnmc_x_y_alb_embb_ndvi_snowflag_ts_rb2_rb3_rb4_rb5_rb6_eb10_rb7_rsoflat_trbb_mask.asc"

    # Give the parser the string of the first column header so that the parsing can be done corectly
    first_col = "X"

    # TODO- CHANGE ONLY IF YOU CHANGE THE NUMBER OF VARIABLES IN THE ASCII
    # Give the parser the number of cols
    num_cols = 17

    # TODO - MODIFY THE OUTPUT PATH FOR THE CONVERTED CSV OF THE ASCII FILE.
    output_path = '/Users/Gabe/Desktop/GSA_consulting/jan/ascii_and_metdata/lc08_l1tp_040033_20150715__rnmc_x_y_alb_embb_ndvi_snowflag_ts_rb2_rb3_rb4_rb5_rb6_eb10_rb7_rsoflat_trbb_mask.csv'

    parsed_dict, headers = parse_file(path, first_col, num_cols)

    # print 'parsed dict \n {}'.format(parsed_dict)


    # convert the parsed dictionary as a dataframe. Output the dataframe to a csv. as we go, we may determine that
    #  outputting the ascii to a csv is unecessary and that calculations can continue just using the dataframe.
    df = pd.DataFrame(parsed_dict, columns=headers)
    df.to_csv('{}'.format(output_path))

    return df

    # # ======== disregard for now ============
    # # TODO - CHANGE IF YOU WANT TO PLOT SOMETHING DIFFERENT
    # # what two variables do you want to plot?
    # # in this case since its x = ndvi and y = etrf and based on the ascii file that translates to:
    # x = parsed_dict['B2']
    # y = parsed_dict['B1']
    #
    # # TODO - LEAVE THIS UNCOMMENTED FOR PLOTS OF NDVI AND ETRF
    # # this plotter function is customized for NDVI vs ETRF plotting
    # plotter(x, y)
    #
    # # TODO - UNCOMMENT THESE LINES IF YOU ARENT PLOTTING ETRF AND NDVI AGAINST EACH OTHER
    # # # for a simple x, y plot use
    # # simple_plot(x, y)
    # # ======== disregard for now ============


def get_metdata():

    # TODO - Update the metadata path (Just once)
    metpath = '/Users/Gabe/Desktop/GSA_consulting/jan/ascii_and_metdata/Cattle_Camp_NV_hourly_meteorological_data_at_satellite_overpass.csv'

    met_df = pd.read_csv(metpath, skiprows=[0, 1])

    print 'met_DF \n', met_df

    return met_df


def calculations(ascii_df, met_df, image):
    """"""

    # get the index of the row of the metdata file that contains the proper image
    met_df = met_df[met_df['Image'] == image]
    print "do we have the right row? \n", met_df

    # get the index of the image
    met_indx = met_df[met_df['Image'] == image].index
    print 'the met index', met_indx

    # get the ETo
    print 'marker', met_df['Eto']
    eto = met_df.loc[met_indx, 'Eto']
    print 'eto', eto

    # get tair in Celcius
    tair = met_df.loc[met_indx, 'Air T']

    # Calculate air temperature in Kelvin
    tairk = tair + 273.15
    print 'tairk', tairk

    # change all Ts values to NaN if surface_temp <= 0; Ts = B5 in ascii_df
    ascii_df['B5'] = ascii_df['B5'].mask(ascii_df['B5'] <= 0.0, np.nan)

    # Calculate NDWI
    rb3 = ascii_df['B7']
    rb4 = ascii_df['B8']
    rb5 = ascii_df['B9']
    rb6 = ascii_df['B10']

    ascii_df['ndwi'] = (rb6 - rb3)/(rb6 + rb3)
    print 'ascii w ndvi', ascii_df.head(5)

    ascii_full = ascii_df

    # Delete all pixels outside of the mask so if mask = 0.0 then delete the entire row. Mask is B16
    ascii_df = ascii_df.drop(ascii_df[ascii_df['B15'] == 0].index)

    # Delete all pixels with snow. Snowflag is B4
    ascii_df = ascii_df.drop(ascii_df[ascii_df['B4'] == 1].index)

    # Delete pixels with water and mixed pixels with water NDVI and NDWI < 0.02, B3 and ndwi respectively
    ascii_df = ascii_df.drop(ascii_df[(ascii_df['B3'] < 0.02) & (ascii_df['ndwi'] < 0.02)].index)

    # Delete pixels with vegetation NDVI > 0.12 aka B3 > 0.12
    ascii_df = ascii_df.drop(ascii_df[ascii_df['B3'] > 0.12].index)

    # make plots TS*ALB
    ts = ascii_df['B5']
    alb = ascii_df['B1']
    ndvi = ascii_df['B3']

    dep_var = 'ts'
    ind_var = 'alb'
    # plotter(ts, alb, image, dep_var, ind_var)

    # make plots TS*NDVI
    ind_var = 'ndvi'
    # plotter(ts, ndvi, image, dep_var, ind_var)

    # surface temperature statistics
    ts = np.array(ts)
    mean = np.mean(ts)
    maximum = np.max(ts)
    minimum = np.min(ts)
    p1 = np.percentile(ts, 1)
    p5 = np.percentile(ts, 5)
    p10 = np.percentile(ts, 10)
    p90 = np.percentile(ts, 90)
    p95 = np.percentile(ts, 95)
    p99 =np.percentile(ts, 99)

    n = len(ts)

    # find the pixel value of ts closest to the 95th and 5th percentile
    print "all the stats {}".format([mean, minimum, maximum, p1, p5, p10, p90, p95, p99, n])

    close_to_fith = ascii_full[(ascii_full['B5'] > p1) & (ascii_full['B5'] < p10)].index

    print 'temps close to fifth', ascii_full.loc[close_to_fith, 'B5']

    close_to_90fith = ascii_full[(ascii_full['B5'] > p90) & (ascii_full['B5'] < p99)].index

    print 'temps close to ninetyfifth', ascii_full.loc[close_to_90fith, 'B5']

    temps_cold_close = ascii_full.loc[close_to_fith, 'B5']
    temps_dry_close = ascii_full.loc[close_to_90fith, 'B5']

    ts_p5 = p5
    ts_p95 = p95

    ts_cold = get_percentile(temps_cold_close, ts_p5)
    ts_dry = get_percentile(temps_dry_close, ts_p95)

    print 'ts dry', ts_dry

    print 'the dry index', ascii_full[ascii_full['B5'] == ts_dry].index
    print 'the cold index', ascii_full[ascii_full['B5'] == ts_cold].index


    return ascii_full, ts_cold, ts_dry, eto

    # # === CALCULATION OF NET RADIATION RN AND SOIL HEAT FLUX G ===
    # ascii_df = ascii_df.drop(ascii_df[ascii_df['B5'] == np.nan].index)
    #
    # ts = ascii_df['B5']
    #
    # # CALCULATE THE NET INCOMING SHORT WAVE RADIATION RSN
    # rso_flat = ascii_df['B14']
    # ascii_df['rsn'] = (1 - alb) * rso_flat
    #
    # # CALCULATE THE OUTGOING LONG WAVE RADIATION RLOUT; RLOUT=EMBB*5.67*10**(-8)*TS**4;
    # embb = ascii_df['B2']
    # ascii_df['rlout'] = embb * 5.67 * 10 ** (-8) * ts ** 4
    #
    # print 'so far so good \n', ascii_df
    # # CALCULATE THE INCOMING LONG WAVE RADIATION RLIN; RLIN=0.85*(-LOG(TRBB))**(0.09)*5.67*10**(-8)*TSCOLD**4;
    # trbb = np.array(ascii_df['B15'])
    # ascii_df['rlin'] = 0.85 * (-np.log(trbb)) ** (0.09) * 5.67 * 10 ** (-8) * ts_cold ** 4
    #
    # # CALCULATE THE NET RADIATION RN; RN=RSN+RLIN-RLOUT
    # rsn = ascii_df['rsn']
    # rlout = ascii_df['rlout']
    # rlin = ascii_df['rlin']
    # rn = ascii_df['rn'] = rsn + rlin - rlout
    #
    #
    # print 'ascii df \n', ascii_df
    #
    # # === CALCULATION OF SOIL HEAT FLUX USING WRIGHT METHOD GWRI; ===
    #
    # # CALCULATION OF WATER HEAT FLUX GWRI AS GWRI=RN*0.5;
    # # if ndwi >= 0, gwri =  rn * 1.80 * (TS-273.16)/RN+0.084)
    #
    # print 'this is the indexes\n', ascii_df[ascii_df['ndwi'] >= 0.0].index
    # ndwi_greater = ascii_df[ascii_df['ndwi'] >= 0.0].index
    # print 'greater', ndwi_greater
    # rn_values_great = ascii_df.loc[ndwi_greater, 'rn']
    # ts_values_great = ascii_df.loc[ndwi_greater, 'B5']
    # gwri1 = rn_values_great * 1.80 * (ts_values_great - 273.16) / rn_values_great + 0.084
    #
    # # ELSE GWRI=RN*0.5;
    # ndwi_lesser = ascii_df[ascii_df['ndwi'] < 0.0].index
    # print 'lesser', ndwi_lesser
    # rn_values_less = ascii_df.loc[ndwi_lesser, 'rn']
    # ts_values_less = ascii_df.loc[ndwi_greater, 'B5']
    # gwri2 = rn_values_less * 0.5
    #
    # print ' the two vals \n 1) {} \n 2) {}'.format(gwri1, gwri2)
    # gwri = pd.concat([gwri1, gwri2])
    # print 'gwri', gwri
    # ascii_df['gwri'] = gwri
    #
    # print 'ascii df before multiplying by 1.5 \n', ascii_df['gwri']
    #
    # #FROZEN OR THAWING SOILS USE PART OF THE INCOMING RADIATION TO HEAT UP THE SOIL AND G IS 1.5*G_REGULAR;
    # # if Ts < 279, then gwri = 1.5 * gwri
    # gwri_greater = ascii_df[ascii_df['B5'] < 279].index
    # ascii_df.loc[gwri_greater, 'gwri'] *= 1.5
    #
    # # GBAS
    # # if NDWI >= 0; GBAS=RN*((TS-273.15)*(0.0038+0.0074*ALB)*(1-0.98*NDVI**4))
    # gbas1 = rn_values_great * ((ts_values_great - 273.15) * (0.0038 + 0.0074 * alb) * (1 - 0.98 * ndvi ** 4))
    # # if NDWI < 0; GBAS = RN * 0.5
    # gbas2 = rn_values_less * 0.5
    # gbas = pd.concat([gbas1, gbas2])
    # ascii_df['gbas'] = gbas
    #
    # # === CALCULATE THE RATIO OF SOIL HEAT FLUX OVER NET RADIATION GRN ===
    # #GRNWRI=GWRI/RN;
    # grnwri = ascii_df['gwri'] / ascii_df['rn']
    # #GRNBAS=GBAS/RN
    # grnbas = ascii_df['gbas'] / ascii_df['rn']
    #
    # ascii_df['grnwri'] = grnwri
    # ascii_df['grnbas'] = grnbas
    #
    # return ts_dry

    # # === CALCULATION OF STATISTICS FOR DETERMINATION OF TSHOT ===
    # # some of these calcs seem to be redundant from earlier. TODO - ask Jan
    # tslow = ts_dry - 0.5
    # tshigh = ts_dry + 0.5
    #
    # # TODO - this drymask thing, it seems like it should come earlier in the calculations, as-is it doesn't find any zeros.
    # # find the indexes where drymask will be 1
    # indexes_drymask = ascii_df[(ascii_df['B5'] > tslow) & (ascii_df['B5'] < tshigh)].index
    #
    # # make the drymask of zeros
    # print 'ze length', len(ascii_df['rn'])
    # drymask_zeros = np.zeros((len(ascii_df['rn']), 1))
    # print 'zero array for drymask', drymask_zeros
    # ascii_df['drymask'] = drymask_zeros
    # print 'asky drymask', ascii_df['drymask']
    #
    # # fill in the ones in the correct locations
    # ascii_df.loc[indexes_drymask, 'drymask'] == 1
    #
    # print 'asky df drymaks', ascii_df['drymask']
    #
    # # Delete low albedo values
    # # IF ALB<0.20 THEN DELETE;
    # ascii_df = ascii_df.drop(ascii_df[ascii_df['B1'] < 0.2].index)
    #
    # print 'no lower albedoes', ascii_df


def calculations2(ascii_df, ascii_ndwi, ts_cold, ts_dry):
    """"""


    # === CALCULATION OF NET RADIATION RN AND SOIL HEAT FLUX G ===

    ascii_ndwi = ascii_ndwi.drop(ascii_ndwi[ascii_ndwi['B5'].isnull()].index)

    ts = ascii_ndwi['B5']

    # CALCULATE THE NET INCOMING SHORT WAVE RADIATION RSN
    rso_flat = ascii_ndwi['B14']
    alb = ascii_ndwi['B1']
    ascii_ndwi['rsn'] = (1 - alb) * rso_flat

    # CALCULATE THE OUTGOING LONG WAVE RADIATION RLOUT; RLOUT=EMBB*5.67*10**(-8)*TS**4;
    embb = ascii_ndwi['B2']
    ascii_ndwi['rlout'] = embb * 5.67 * 10 ** (-8) * ts ** 4

    # CALCULATE THE INCOMING LONG WAVE RADIATION RLIN; RLIN=0.85*(-LOG(TRBB))**(0.09)*5.67*10**(-8)*TSCOLD**4;
    trbb = np.array(ascii_ndwi['B14'])
    ascii_ndwi['rlin'] = 0.85 * (-np.log(trbb)) ** (0.09) * 5.67 * 10 ** (-8) * ts_cold ** 4

    # CALCULATE THE NET RADIATION RN; RN=RSN+RLIN-RLOUT
    rsn = ascii_ndwi['rsn']
    rlout = ascii_ndwi['rlout']
    rlin = ascii_ndwi['rlin']
    rn = ascii_ndwi['rn'] = rsn + rlin - rlout

    # === CALCULATION OF SOIL HEAT FLUX USING WRIGHT METHOD GWRI; ===

    # CALCULATION OF WATER HEAT FLUX GWRI AS GWRI=RN*0.5;
    # if ndwi >= 0, gwri =  rn * 1.80 * (TS-273.16)/RN+0.084)
    ndwi_greater = ascii_ndwi[ascii_ndwi['ndwi'] >= 0.0].index
    rn_values_great = ascii_ndwi.loc[ndwi_greater, 'rn']
    ts_values_great = ascii_ndwi.loc[ndwi_greater, 'B5']
    gwri1 = rn_values_great * 1.80 * (ts_values_great - 273.16) / rn_values_great + 0.084

    # ELSE GWRI=RN*0.5;
    ndwi_lesser = ascii_ndwi[ascii_ndwi['ndwi'] < 0.0].index
    rn_values_less = ascii_ndwi.loc[ndwi_lesser, 'rn']
    ts_values_less = ascii_ndwi.loc[ndwi_greater, 'B5']
    gwri2 = rn_values_less * 0.5

    # print ' the two vals \n 1) {} \n 2) {}'.format(gwri1, gwri2)
    gwri = pd.concat([gwri1, gwri2])
    ascii_ndwi['gwri'] = gwri

    # print 'ascii df before multiplying by 1.5 \n', ascii_ndwi['gwri']

    # FROZEN OR THAWING SOILS USE PART OF THE INCOMING RADIATION TO HEAT UP THE SOIL AND G IS 1.5*G_REGULAR;
    # if Ts < 279, then gwri = 1.5 * gwri
    gwri_greater = ascii_ndwi[ascii_ndwi['B5'] < 279].index
    ascii_ndwi.loc[gwri_greater, 'gwri'] *= 1.5

    # GBAS
    # if NDWI >= 0; GBAS=RN*((TS-273.15)*(0.0038+0.0074*ALB)*(1-0.98*NDVI**4))
    # we only want to use the albedoes and ndvi values that correspond to the correct gbas
    ndvi_great = ascii_ndwi.loc[ndwi_greater, 'B3']
    alb_great = ascii_ndwi.loc[ndwi_greater, 'B1']
    gbas1 = rn_values_great * ((ts_values_great - 273.15) * (0.0038 + 0.0074 * alb_great) * (1 - 0.98 * ndvi_great ** 4))
    # if NDWI < 0; GBAS = RN * 0.5
    gbas2 = rn_values_less * 0.5
    gbas = pd.concat([gbas1, gbas2])
    ascii_ndwi['gbas'] = gbas

    # === CALCULATE THE RATIO OF SOIL HEAT FLUX OVER NET RADIATION GRN ===
    # GRNWRI=GWRI/RN;
    grnwri = ascii_ndwi['gwri'] / ascii_ndwi['rn']
    # GRNBAS=GBAS/RN
    grnbas = ascii_ndwi['gbas'] / ascii_ndwi['rn']

    ascii_ndwi['grnwri'] = grnwri
    ascii_ndwi['grnbas'] = grnbas

    return ascii_ndwi


def calculations3(ascii_rn_g, ts_cold, ts_dry):
    """"""
    # preserve the original dataframe for later use
    oringinal_df = ascii_rn_g

    # === CALCULATION OF STATISTICS FOR DETERMINATION OF TSHOT ===

    # Delete all pixels outside of the mask so if mask = 0.0 then delete the entire row. Mask is B16
    ascii_rn_g = ascii_rn_g.drop(ascii_rn_g[ascii_rn_g['B15'] == 0].index)

    tslow = ts_dry - 0.5
    tshigh = ts_dry + 0.5

    # === Calculation of TSHOT ====
    # TODO - this drymask thing, it seems like it should come earlier in the calculations, as-is it doesn't find any zeros.
    # find the indexes where drymask will be 1
    indexes_drymask = ascii_rn_g[(ascii_rn_g['B5'] > tslow) & (ascii_rn_g['B5'] < tshigh)].index


    # print 'these are the drymask indexes', indexes_drymask

    # make the drymask of zeros
    print 'ze length', len(ascii_rn_g['rn'])
    drymask_zeros = np.zeros((len(ascii_rn_g['rn']), 1))
    # print 'zero array for drymask', drymask_zeros
    ascii_rn_g['drymask'] = drymask_zeros
    # print 'asky drymask', ascii_rn_g['drymask']

    # fill in the ones in the correct locations
    ascii_rn_g.loc[indexes_drymask, 'drymask'] = 1
    print 'ascii rn g after drymask is added', ascii_rn_g['drymask']

    ascii_rn_g_full = ascii_rn_g

    # === Cull the dataframe of unwanted values ===

    # IF DRYMASK=0.0 THEN DELETE;
    ascii_rn_g = ascii_rn_g.drop(ascii_rn_g[ascii_rn_g['drymask'] == 0].index)
    # IF NDWI<=0.0 THEN DELETE;
    ascii_rn_g = ascii_rn_g.drop(ascii_rn_g[ascii_rn_g['ndwi'] <= 0.0].index)
    # IF NDVI<0.02 THEN DELETE;
    ascii_rn_g = ascii_rn_g.drop(ascii_rn_g[ascii_rn_g['B3'] < 0.02].index)
    # IF NDVI>0.12 THEN DELETE;
    ascii_rn_g = ascii_rn_g.drop(ascii_rn_g[ascii_rn_g['B3'] > 0.12].index)
    # IF ALB<0.20 THEN DELETE;
    ascii_rn_g = ascii_rn_g.drop(ascii_rn_g[ascii_rn_g['B1'] < 0.2].index)

    print 'after culling', ascii_rn_g

    # find the median and the mean of the culled Ts
    print 'ts of dry dataframe', ascii_rn_g['B5']

    # todo - is it possible that the dataframe comes up empty?

    if ascii_rn_g['B5'].empty:
        tshot = ts_dry

        # find the albedo albedo and G of the hotpixel
        hotpixel_indxs = oringinal_df[oringinal_df['B5'] == tshot].index
        print 'them hotpixel indxs', hotpixel_indxs

        rndry = oringinal_df.loc[hotpixel_indxs, 'rn']
        albdry = oringinal_df.loc[hotpixel_indxs, 'B1']
        gdry = oringinal_df.loc[hotpixel_indxs, 'gwri']
        print 'the dry rn alb and gdry, respectively \n', rndry, albdry, gdry

        # TODO - Is this necessary now?
        # IF TS=. THEN DELETE;
        # IF RNDRY=. THEN DELETE;

        print 'ascii calc', ascii_rn_g_full
        print 'tshot', tshot
        print 'rndry', rndry
        print 'albdry', albdry
        print 'gdry', gdry
        return ascii_rn_g_full, tshot, rndry, albdry, gdry

    else:
        print 'the culled dataframe was not empty'
        print 'test', ascii_rn_g['B5']
        dry_temps = np.array(ascii_rn_g['B5'])
        print 'dry temps', dry_temps
        mean = np.mean(dry_temps)
        median = np.median(dry_temps)

        print 'xx11'

        if median == None:
            tshot = ts_dry

            # find the albedo albedo and G of the hotpixel

            hotpixel_indxs = oringinal_df[oringinal_df['B5'] == tshot].index

            print 'xx13'

            print 'them hotpixel indxs', hotpixel_indxs

            rndry = oringinal_df.loc[hotpixel_indxs, 'rn']
            albdry = oringinal_df.loc[hotpixel_indxs, 'B1']
            gdry = oringinal_df.loc[hotpixel_indxs, 'gwri']

            print 'the dry rn alb and gdry, respectively \n', rndry, albdry, gdry

            # TODO - Is this necessary now?
            # IF TS=. THEN DELETE;
            # IF RNDRY=. THEN DELETE;

            return ascii_rn_g_full, tshot, rndry, albdry, gdry

        else:
            tshot = median

            print 'xx12'

            # find the albedo albedo and G of the hotpixel

            hotpixel_indxs = oringinal_df[oringinal_df['B5'] == tshot].index

            print 'them hotpixel indxs', hotpixel_indxs

            rndry = oringinal_df.loc[hotpixel_indxs, 'rn']
            albdry = oringinal_df.loc[hotpixel_indxs, 'B1']
            gdry = oringinal_df.loc[hotpixel_indxs, 'gwri']

            print 'the dry rn alb and gdry, respectively \n', rndry, albdry, gdry

            # TODO - Is this necessary now?
            # IF TS=. THEN DELETE;
            # IF RNDRY=. THEN DELETE;

            return ascii_rn_g_full, tshot, rndry, albdry, gdry


def calculations4(ascii_rn_g, tshot, ts_cold, rndry, albdry, gdry, eto, output_path):
    """"""
    # Normalized Difference Temperature Index (NDTI)
    denom = tshot - ts_cold
    num = ascii_rn_g['B5'] - ts_cold

    ndti = (ascii_rn_g['B5'] - ts_cold) / (tshot - ts_cold)
    ascii_rn_g['ndti'] = ndti

    # IF TS>TSHOT THEN NDTI=1.0;
    hotter_indx = ascii_rn_g[ascii_rn_g['B5'] > tshot].index
    ascii_rn_g.loc[hotter_indx, 'ndti'] = 1.0

    # IF TS<TSCOLD THEN NDTI=0.0;
    colder_indx = ascii_rn_g[ascii_rn_g['B5'] < ts_cold].index
    ascii_rn_g.loc[colder_indx, 'ndti'] = 0.0
    # print 'test that ish ndti', ascii_rn_g['ndti']

    # CALCULATE THE EVAPORATION E AND REFERENCE ETO FRACTION ETOF;
    # RN AND GWRI ARE IN W/m^2 OR Joule/m^2. MULTIPLY BY 3600 SECONDS TO GO TO HOUR.
    # DIVIDE BY 1,000,000 TO GO TO MJoule. DIVIDE BY 2.45 MJ/kg TO FIND kg OR mm WATER EVAPORATED PER m^2;
    rn = np.array(ascii_rn_g['rn'])
    gwri = np.array(ascii_rn_g['gwri'])
    ndti = np.array(ascii_rn_g['ndti'])
    b = float(rndry - gdry)
    e = (rn - gwri - b * ndti) * 3600/1000000/2.45

    print 'this is e', e

    # ETOF=E/ETO;
    print 'eto test', eto
    etof = e / float(eto)

    # add these to the ascii
    ascii_rn_g['e'] = e
    ascii_rn_g['etof'] = etof

    print 'ascii etof', ascii_rn_g['etof']
    print 'ascii ts', ascii_rn_g['B5']

    # === ALL WATER PIXELS HAVE ETOF=1.05; ===
    # IF NDVI<0.00 AND TS<TSCOLD+(TSHOT-TSCOLD)/2.0 AND ALB<0.15 THEN ETOF=1.05
    water_indx = ascii_rn_g[(ascii_rn_g['B3'] <= 0.0) & (ascii_rn_g['B5'] < (ts_cold + (tshot-ts_cold)/2.0))
                      & (ascii_rn_g['B1'] < 0.15)].index
    ascii_rn_g.loc[water_indx, 'etof'] = 1.05
    # IF NDWI<=0.00 AND TS<TSCOLD+(TSHOT-TSCOLD)/2.0 AND ALB<0.15 THEN ETOF=1.05 # TODo - This seems reduntant
    # IF TS>TSHOT-1 AND ETOF=1.05 THEN ETOF=E/ETO;
    tshot_indx =  ascii_rn_g[(ascii_rn_g['B5'] > (tshot - 1)) & (ascii_rn_g['etof'] == 1.05)].index
    ascii_rn_g.loc[tshot_indx, 'etof'] = (ascii_rn_g['e'] / eto)

    # === SNOW PIXELS HAVE ETOF=0.5; ===
    # IF SNOWFLAG=1.0 THEN ETOF=0.5;
    snowflag_indx = ascii_rn_g[ascii_rn_g['B4'] == 1].index
    ascii_rn_g.loc[snowflag_indx, 'etof'] = 0.5
    # IF ETOF<0.0 THEN ETOF=0.00;
    neg_indx = ascii_rn_g[ascii_rn_g['etof'] < 0.0].index
    ascii_rn_g.loc[neg_indx, 'etof'] = 0.00

    # === COLD PIXELS WITH ICE (FROZEN WATER) MAY THAW LATER IN THE DAY AND EVAPORATE WATER; ===
    # IF TS<273.15 AND NDVI>0.00 AND ETOF>1.05 THEN ETOF=0.3;
    frozen_water_indx = ascii_rn_g[(ascii_rn_g['B5'] < 273.15) & (ascii_rn_g['B3'] > 0.00)
                                   & (ascii_rn_g['etof'] > 1.05)].index
    ascii_rn_g.loc[frozen_water_indx, 'etof'] = 0.3
    # IF TS<273.15 AND ETOF>=1.05 THEN ETOF=0.3;
    frozen_water_indx2 = ascii_rn_g[(ascii_rn_g['B5'] < 273.15) & (ascii_rn_g['etof'] >= 1.05)].index
    ascii_rn_g.loc[frozen_water_indx2, 'etof'] = 0.3
    # IF ETOF>1.12 THEN ETOF=1.12;
    etof_1_12_indx = ascii_rn_g[(ascii_rn_g['etof'] > 1.12)].index
    ascii_rn_g.loc[etof_1_12_indx, 'etof'] = 1.12

    # === CALCULATE ACTUAL EVAPORATION EACT FROM CORRECT ETOF; ===
    # EACT=ETO*ETOF;

    eact = eto * ascii_rn_g['etof']
    ascii_rn_g['eact'] = eact

    # IF TS=. THEN ETOF=.;
    nan_indx = ascii_rn_g[ascii_rn_g['B5'].isnull()].index
    ascii_rn_g.loc[nan_indx, 'etof'] = np.nan
    # IF TS=. THEN EACT=.;
    ascii_rn_g.loc[nan_indx, 'eact'] = np.nan
    # IF TS=. THEN NDTI=.;
    ascii_rn_g.loc[nan_indx, 'ndti'] = np.nan


    # === PLOT ETOF*TS ETOF*GWRI NDTI*TS ;TITLE 'EVAPORATION'; ===
    # tODO - uncomment 'plotter' lines to generate plots.
    etof = ascii_rn_g['etof']
    ts = ascii_rn_g['B5']
    # plotter(etof, ts)

    gwri = ascii_rn_g['gwri']
    # plotter(etof, gwri)

    ndti = ascii_rn_g['ndti']
    # plotter(ndti, ts)


    # IF TS=. THEN DELETE; # TODO - we want to keep the NaN values still no?

    # === MERGE ALL EVAPORATION;BY X Y; ===
    # KEEP X Y TS NDTI ETOF;
    xy_df = ascii_rn_g.loc[:, ['X', 'Y', 'B5', 'ndti', 'etof']]
    # IF TS=. THEN TS=0;
    nan_temps_indx = xy_df[xy_df['B5'].isnull()].index
    print 'here are the indices ! ', nan_temps_indx
    xy_df.loc[nan_temps_indx, 'B5'] = 0.00
    # IF TS=. THEN NDTI=0;
    xy_df.loc[nan_temps_indx, 'ndti'] = 0.00
    # IF TS=. THEN ETOF=0;
    xy_df.loc[nan_temps_indx, 'etof'] = 0.00
    # IF NDTI=. THEN NDTI=0;
    nan_ndti_indx = xy_df[xy_df['ndti'].isnull()].index
    xy_df.loc[nan_ndti_indx, 'ndti'] = 0.00
    # IF ETOF=. THEN ETOF=0;
    nan_etof_indx = xy_df[xy_df['etof'].isnull()].index
    xy_df.loc[nan_etof_indx, 'etof'] = 0.00

    print 'the final resultant dataframe {}'.format(xy_df)

    xy_df.to_csv(output_path)


def run():
    """
    This is the main function. It collects the data and performs the calculations and outputs the results.
    :return:
    """

    # TODO - !!! JAN START HERE !!!

    # TODO - Indicate the image your are using e.g. 'LC08_L1TP_040033_20150221_20170227_01_T1_MTL.txt'
    # as it apears in metdata csv
    image = 'LC08_L1TP_040033_20150715_20170226_01_T1_MTL.txt'

    # todo - output path for the final dataframe with the X, Y, TS, NDTI and ETOF
    output_path = '/Users/Gabe/Desktop/GSA_consulting/jan/ascii_and_metdata/results.csv'

    # TODO - DO NOT FORGET TO CHANGE THE PATHS IN THE RUN_ASCII() AND GET_METDATA() FUNCTIONS...
    # get a dataframe with all the values from the ascii stackfile
    ascii_df = run_ascii() # TODO - come up with procedure to parse ascii filename into column headings for dataframe

    # get a dataframe from the metadata
    met_df = get_metdata()

    # do the first batch of calculations that were formerly done in SAS
    ascii_ndwi, ts_cold, ts_dry, eto = calculations(ascii_df, met_df, image)

    # do the second batch of calculations from the SAS program
    ascii_rn_g = calculations2(ascii_df, ascii_ndwi, ts_cold, ts_dry)

    print 'ascii rn g', ascii_rn_g

    # the third batch of calculations that were done
    ascii_rn_g_full, tshot, rndry, albdry, gdry = calculations3(ascii_rn_g, ts_cold, ts_dry)

    # Don't use ascii_rn_g_full for the third calculations. Calculations3 is
    # just to get the tshot and the dry rn, alb and g
    # This function outputs everything to a single .csv file in the output path.
    calculations4(ascii_rn_g, tshot, ts_cold, rndry, albdry, gdry, eto, output_path)


if __name__ == "__main__":

    run()