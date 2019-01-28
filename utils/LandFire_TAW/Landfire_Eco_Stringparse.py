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
import pandas as pd

# ============= local library imports ===========================

def parse_landfire_categories(category_textfile):
    """"""

    ecosystem_dictionary = {}
    with open(category_textfile, 'r') as rfile:

        for line in rfile:

            line_lst = line.split(' ')

            code = line_lst[0]
            desc = line_lst[1:]

            desc_string = '_'.join(desc)
            desc_string = desc_string[:-1]

            ecosystem_dictionary[code] = desc_string

    return ecosystem_dictionary


def parse_raster_report(grass_raster_report):
    """"""

    report_dictionary = {}
    code_list = []
    count_list = []

    with open(grass_raster_report, 'r') as rfile:

        for line in rfile:
            # print line

            if any(char.isdigit() for char in line):

                count_info = line.split('|')

                code = count_info[1].strip()
                code_list.append(code)

                count = count_info[-2]
                count = int(count)
                count_list.append(count)

                # put the code and counts related one to one in a dictionary
                report_dictionary[code] = count

    # # stick the codes into a two col dictionary and convert to pandas df
    # report_ledger = {'code': code_list, 'count': count_list}
    # report_df = pd.DataFrame(report_ledger, columns=['code', 'count'])

    # remove 'Total' from both lists
    code_list = code_list[:-1]
    count_list = count_list[:-1]

    report_lists = [code_list, count_list]

    return report_dictionary, report_lists #report_df


def lists_to_df(list_o_lists, list_o_column_names):
    """"""

    # make a dictionary first:
    d = {}
    for lst, col in zip(list_o_lists, list_o_column_names):
        d[col] = lst

    # convert to a dataframe
    df = pd.DataFrame(d, columns=list_o_column_names)

    return df


def main(root, eco_name, count_report, output_name):
    """"""
    eco_root = os.path.join(root, eco_name)
    count_root = os.path.join(root, count_report)

    # relate the codes to the ecosystems
    eco_dict = parse_landfire_categories(eco_root)

    # return a dictionary that contains the codes and the counts together, which may be useful. Return lists of codes
    # and counts in order to later make a dataframe
    report_dict, report_lsts = parse_raster_report(count_root)

    # make a list of ecosystem names to correspond to the code list
    code_lst = report_lsts[0]
    eco_lst = [eco_dict[code] for code in code_lst]
    print 'eco list', eco_lst

    # add the eco list to the code and count in report_lsts
    report_lsts.append(eco_lst)

    # the column headings
    cols = ['code', 'count', 'ecosystem']

    report_df = lists_to_df(report_lsts, cols)

    print 'the report dataframe \n', report_df

    # output to csv
    output_path = os.path.join(root, output_name)
    report_df.to_csv(output_path, index=False)


if __name__ == "__main__":

    root = "/Users/Gabe/Desktop/academic_docs/LandFire/raster_report"

    eco_name = 'landfire_econames.txt'

    count_report = 'nm_landfire_report.txt'

    output_csv = 'raster_report_processed.csv'

    main(root, eco_name, count_report, output_csv)