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


def millimeter_to_acreft(param):
    return '{:.2e}'.format((param.sum() / 1000) * (250**2) / 1233.48)


def save_tabulated_results_to_csv(tabulated_results, results_directories, polygons):

    print 'results directories: {}'.format(results_directories)

    folders = os.listdir(polygons)
    for in_fold in folders:
        print 'saving tab data for input folder: {}'.format(in_fold)
        region_type = os.path.basename(in_fold).replace('_Polygons', '')
        files = os.listdir(os.path.join(polygons, os.path.basename(in_fold)))
        print 'tab data from shapes: {}'.format([infile for infile in files if infile.endswith('.shp')])
        for element in files:
            if element.endswith('.shp'):
                sub_region = element.strip('.shp')

                df_month = tabulated_results[region_type][sub_region]
                # print 'df for {} {}'.format(region_type, sub_region)
                # print df_month.describe()

                df_annual = df_month.resample('A').sum()

                save_loc_annu = os.path.join(results_directories['annual_tabulated'][region_type],
                                             '{}.csv'.format(sub_region))

                save_loc_month = os.path.join(results_directories['root'],
                                              results_directories['monthly_tabulated'][region_type],
                                              '{}.csv'.format(sub_region))

                dfs = [df_month, df_annual]
                locations = [save_loc_month, save_loc_annu]
                for df, location in zip(dfs, locations):
                    print 'this should be your csv: {}'.format(location)
                    df.to_csv(location, na_rep='nan', index_label='Date')
    return None

if __name__ == '__main__':
    pass

# =================================== EOF =========================
