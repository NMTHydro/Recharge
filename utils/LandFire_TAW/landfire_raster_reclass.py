# ===============================================================================
# Copyright 2019 Jan Hendrickx and Gabriel Parrish
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
import gdal
# ============= standard library imports ========================
from recharge.raster_tools import convert_raster_to_array
from utils.depletions_modeling.cumulative_depletions import write_raster


def get_raster_geo(filepath):
    """
    Creates a dict of geographic attributes from a single raster file.

    :param filepath: Path to rasterfile.
    :return: dict of geographic attributes.
    """
    dataset = gdal.Open(filepath)

    print('dataset: ', dataset)

    band = dataset.GetRasterBand(1)
    raster_geo_dict = {'cols': dataset.RasterXSize, 'rows': dataset.RasterYSize, 'bands': dataset.RasterCount,
                       'data_type': band.DataType, 'projection': dataset.GetProjection(),
                       'geotransform': dataset.GetGeoTransform(), 'resolution': dataset.GetGeoTransform()[1]}
    return raster_geo_dict


def read_codes(path, first_col_string):
    """

    :param path: path to the reclass csv
    :param first_col_string: The string of the first column of the reclass .csv
    :return:
    """

    #instantiate the dictionary
    eco_dict = {}
    with open(path, 'r') as rfile:
        for line in rfile:
            # check to make sure the line is not the header.
            if not line.split(',')[0] == first_col_string:
                # a list of all the values in the line of the .csv
                vals = line.split(',')
                # if a cell is not empty and doesn't start with '\r' then keep it in the list
                vals = [i for i in vals if len(i) > 0 and not i.startswith('\r')]

                # store the ecosystem name as the key to the dictionary with a value of (newcode, oldcode)
                eco_dict['{}'.format(vals[4])] = (vals[0], vals[1])

    return eco_dict


def arr_modify(arr, dict):
    """

    :param arr: any 2d numpy array
    :param dict: has format key:(newval, oldval)
    :return: modified array
    """

    for key, val in dict.items():
        # print 'key', key
        # print 'val', val
        arr_overprint(arr, val[1], val[0])

    return arr


def arr_overprint(arr, val, newval):
    """
    Overprints a given raster value with a new value
    :param arr:
    :param val:
    :param newval:
    :return:
    """
    arr[arr == int(val)] = int(newval)


def main(eco_path, lf_path, outinfo, first_col_string):
    """"""

    # need a dictionary relating names to codes
    eco_dict = read_codes(eco_path, first_col_string)
    print 'eco dictionary-> \n', eco_dict

    # get the raster array
    landfire_arr = convert_raster_to_array(lf_path)

    # get the geo information for the raster
    landfire_geo = get_raster_geo(lf_path)
    print 'geo info \n', landfire_geo

    grouped_arr = arr_modify(landfire_arr, eco_dict)

    ## troubleshooting
    # print 'grouped array', grouped_arr
    # print landfire_geo['geotransform']
    # print outinfo[0], outinfo[1]
    # print (landfire_geo['rows'], landfire_geo['cols'])
    # print landfire_geo['projection']

    write_raster(grouped_arr, landfire_geo['geotransform'], outinfo[0], outinfo[1],
                 (landfire_geo['cols'], landfire_geo['rows']), landfire_geo['projection'])



if __name__ == "__main__":

    # path to the codes, counts and ecosystem names for the Landfire Dataset.
    # ...File produced by Landfire_Eco_Stringparse.py
    # eco_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/grouped_lf_rasters/landfire_reclassification/LandFire_Reclass_Combine_Sandvig.csv'
    eco_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/grouped_lf_rasters/landfire_reclassification/LandFire_Reclass_Combine_Sandvig_config_DGedit.csv'

    # path to new mexican landfire data.
    lf_path = '/Users/dcadol/Desktop/academic_docs_II/LandFire/CO_NM_Landfire_1_0_0_EVT/NM_Landfire_1.0.0_EVT_clip.tif'

    # ====== User-Defined Output path ======
    outpath = '/Users/dcadol/Desktop/academic_docs_II/LandFire/grouped_lf_rasters/grouped_landfire_rasters/'
    outname = 'gabe_reclass_july_24.tif'

    # outfile = os.path.join(outpath, outname)
    outinfo = [outpath, outname]

    # the exact string of the first column of the spreadsheet
    first_col_string = '\xef\xbb\xbfGroups(Gabe)'

    main(eco_path, lf_path, outinfo, first_col_string)