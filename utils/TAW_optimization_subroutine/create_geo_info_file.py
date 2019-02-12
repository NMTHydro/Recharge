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
import gdal
import sys
import yaml
# ============= local library imports ===========================

def extract_geo_info(geotiff_path):
    """"""

    gdal.AllRegister()

    # open the raster datasource
    datasource_obj = gdal.Open(geotiff_path)
    if datasource_obj is None:
        print "Can't open the datasource from {}".format(geotiff_path)
        sys.exit(1)

    # get the size of image (for reading)
    rows = datasource_obj.RasterYSize
    cols = datasource_obj.RasterXSize
    # x - cols, y - rows
    dimensions = (cols, rows)

    # get the projection
    proj = datasource_obj.GetProjection()

    # get georefference info to eventually calculate the offset:
    transform = datasource_obj.GetGeoTransform()

    geo_dict = {'geotransform': transform, 'dimensions': dimensions, 'projection': proj}

    return geo_dict

def main(sample_file, output_path, filename):
    """
    Taking a ETRM domain and saving the pertinent geo information to a text or yml file
    :param sample_file: filepath to geotiff representing the ETRM model domain for the TAW optimiation
    :return:
    """

    geo_dict = extract_geo_info(sample_file)

    # write_raster(array, geotransform, output_path, output_filename, dimensions, projection)

    yml_file = os.path.join(output_path, filename)

    with open(yml_file, 'w') as w_file:
        yaml.dump(geo_dict, w_file)


if __name__ == "__main__":

    sample_geotiff_file_path = '/Volumes/Seagate_Expansion_Drive/ETRM_espanola_aoi_inputs/statics/taw_reduced.tif'
    output_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder'


    main(sample_file=sample_geotiff_file_path, output_path=output_path, filename='geo_info_espanola.yml')