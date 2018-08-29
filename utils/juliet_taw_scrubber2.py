# ===============================================================================
# Copyright 2016 gabe-parrish
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
import pandas as pd
import numpy as np


# ============= local library imports ===========================

def changer(data, frame=False):
    """

    :param data: can be either a dataframe or a dictionary
    :param frame: True if you want to turn a df -> dict, False for dict -> df
    :return: dataframe or dictionary
    """

    if frame == False:
        # expect a dict and turn the dictionary into a dataframe.
        cols = []
        for key in data.iterkeys():
            cols.append(key)
        df = pd.DataFrame(data, columns = data["{}".format(cols)])

        return df

    else:
        # expect a frame and turn the frame into a dict

        dict = data.to_dict('list')

        return dict


def filter_func(df, taw):
    """
    takes the given dataframe and filters out all but a certain TAW value
    :param df: pandas dataframe
    :return:
    """

    # filter out rows of dataframe you don't want
    filtered = df[df['taw'] == taw]

    #df[df['taw'] < taw]

    # print "filtered df {}".format(df)

    #delete the taw column altogether
    filtered = filtered.drop('taw', 1)

    return filtered

def add_noise(df):
    """
    Adds normally distributed random noise to the dataframe rzsm
    :param df:
    :return:
    """


    # # Adding flat noise______________________________
    # noise = np.random.normal(0, 0.05, len(df['rzsm']))
    # df['rzsm'] = df['rzsm'] + noise
    #
    #
    # # # Adding proportional noise____________________
    # arr = np.random.normal(0, 0.1, len(df['rzsm']))
    # print "arr", arr
    # noise = df['rzsm'] * arr
    # std_def = np.std(noise)
    # print "std_def", std_def
    # df['rzsm'] = df['rzsm'] + noise


    # # Adding Progressive Noise_________________________
    arr1 = np.random.normal(0, 0.005, len(df['rzsm']))
    print "arr1", arr1
    sigma1 = 0.005

    arr2 = np.random.normal(0, 0.05, len(df['rzsm']))
    print "arr2", arr2
    sigma2 = 0.05

    noise1 = df['rzsm'] * arr1
    noise2 = df['rzsm'] * arr2

    sigma_list = []
    progressive_noise_list = []
    for i, j, k in zip(df['rzsm'], noise1, noise2):
        if i < 0.1:
            i = i + j
            progressive_noise_list.append(i)
            sigma_list.append(sigma1)
        else:
            i = i + k
            progressive_noise_list.append(i)
            sigma_list.append(sigma2)
    print "the progressive noise list", progressive_noise_list
    print "the sigma list", sigma_list
    noisy_arr = np.array(progressive_noise_list)
    sigma_arr = np.array(sigma_list)

    # add the noise added array back into the dataframe.
    df['rzsm'] = noisy_arr
    # add this to the array so Juliet can tell the chi_square
    df['noise_error'] = sigma_arr

    return df

def format_1(dict):
    """
    takes the dict of paths and reads in each csv as a dataframe, processes out the rows we dont want,
    turns the dataframe into a dictionary and appends it to a large dictionary
    :param dict:
    :return:
    """
    # remove nonessential rows by TAW
    removal_dict = {"p 2.csv": 70, "p 4.csv": 115, "p 7.csv": 205, "p 8.csv": 115, "p 10.csv": 160, "p 0.csv":250,
                    "p 1.csv": 295, "p 3.csv": 340, "p 5.csv": 295, "p 6.csv": 385, "p 9.csv": 250, "p 11.csv": 430,
                    "p 12.csv": 70, "p 13.csv": 205, "p 14.csv": 115, "p 15.csv": 385}
    essential_data = {}
    for key, value in dict.iteritems():

        df_value = pd.read_csv(value)
        #print "test df_value -> {}".format(df_value)
        value_filtered = filter_func(df_value, removal_dict["{}".format(key)])

        # print "value filtered", value_filtered

        essential_data["{}".format(key)] = value_filtered #changer(value_filtered, frame=True)

    #remove the taw layer


    # add noise
    noise_added = {}
    for key, value in essential_data.iteritems():

        noise_value = add_noise(value)

        noise_added["{}".format(key)] = noise_value

    print "noise added", noise_added



    # write all the dataframes out.
    for key, value in noise_added.iteritems():
        # fix in a sec

        output_list = dict["{}".format(key)].split("/")

        print output_list

        first_part = output_list[-1]

        print "first part", first_part

        path = output_list[0:-1]

        print "path", path

        path.append("done")

        path.append(first_part)

        outpath = "/".join(path)

        print "outpath", outpath



        value.to_csv("{}".format(outpath))



def run():
    """Calls all the functions in the script. Reads in a bunch of ETRM outputs organized by date and filters them by
    TAW and then deletes the TAW and adds noise to the RZSM column."""

    path = "/Volumes/SeagateExpansionDrive/juliet_inverse_problem/gabe_original_data_March_8_2018/progressive_error"

    path_dict = {}
    for directory_path, subdir, file in os.walk(path, topdown=False):

        for i in file:
            if i.endswith(".csv"):
                path_dict["{}".format(i)] = os.path.join(directory_path, i)


    #print "path dict", path_dict

    # pass the path dict off to a function that turns the path dict into a dict of dicts
    # create a special function to turn dicts into dataframes and vice versa:

    format_1(path_dict)



if __name__ == "__main__":


    run()