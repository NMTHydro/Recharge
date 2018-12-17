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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import sys
from gdalconst import *
import gdal
# ============= local library imports ===========================

def write_raster(array, geotransform, output_path, output_filename, dimensions, projection, datatype):
    """

    :param array:
    :param geotransform:
    :param output_path:
    :param output_filename:
    :param dimensions:
    :param projection:
    :param datatype:
    :return:
    """

    filename = os.path.join(output_path, output_filename)

    driver = gdal.GetDriverByName('GTiff')
    # path, cols, rows, bandnumber, data type (if not specified, as below, the default is GDT_Byte)

    output_dataset = driver.Create(filename, dimensions[0], dimensions[1], 1, GDT_Float32)

    # we write TO the output band
    output_band = output_dataset.GetRasterBand(1)

    # we don't need to do an offset
    output_band.WriteArray(array, 0, 0)

    print 'done writing, Master.'

    # set the geotransform in order to georefference the image
    output_dataset.SetGeoTransform(geotransform)
    # set the projection
    output_dataset.SetProjection(projection)


def raster_extract(raster_path):
    """
    extracts array and geotransform information from the raster...

    :param raster_path: string - path to a raster, probably a GeoTIFF
    :return: raster array
    """
    print 'raster extract running'
    # don't forget to register
    gdal.AllRegister()

    datasource_obj = gdal.Open(raster_path, GA_ReadOnly)
    # open the raster datasource
    if datasource_obj is None:
        print "Can't open the datasource from {}".format(raster_path)
        sys.exit(1)

    # get the size of image (for reading)
    rows = datasource_obj.RasterYSize
    cols = datasource_obj.RasterXSize
    dimensions = (cols, rows)
    projection = datasource_obj.GetProjection()

    # # get georefference info
    transform = datasource_obj.GetGeoTransform()
    # xOrigin = transform[0]
    # yOrigin = transform[3]
    # width_of_pixel = transform[1]
    # height_of_pixel = transform[5]

    # read in a band (only one band)
    band = datasource_obj.GetRasterBand(1)
    # get the datatype
    dt = band.DataType
    print 'here is the data type of the original raster -> {}'.format(dt)
    # ReadAsArray(xoffset, yoffset, xcount, ycount)
    data = band.ReadAsArray(0, 0, cols, rows).astype(np.float32)

    arr_3d = np.zeros((rows, cols, datasource_obj.RasterCount))

    arr_3d[:, :, 0] = data
    # save memory
    # datasource_obj = None

    return data, transform, dimensions, projection, dt


def depletion_calc(f_out, f_in):

    # depletion is positive when f_out - f_in > 0
    depletion = f_out - f_in

    return depletion


def run_W_E():
    """

    :return:
    """
    # over 15 years we normalize every monthly map by the total precip. Do the same for SSEB ETa.

    # path to monthly ETa
    ssebop_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/SSEBop/SSEBOP_Geotiff_warped"

    # path to monthly Prism
    pris_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"

    # output path
    # output_folder = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_depletions"
    output_folder = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cum_depletions_neg"

    # seems like we need to start in Feb of 2000 (ETRM monthly precip outputs only start in Feb 2000...)

    # function to calculate the depletion at a monthly timestep
    #  within that function, output the running depletion raster that results from each month's F_in-F_out
    start_date = datetime.strptime("2000-2", "%Y-%m")
    end_date = datetime.strptime("2013-12", "%Y-%m")

    months_in_series = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)

    precip_name = "tot_precip_{}_{}.tif"
    ssebop_name = "ssebop_{}_{}_warped.tif"

    # at each timestep, keep track of how negative the depletion has gotten
    depletion_ledger = np.zeros((2525, 2272), dtype=float)
    # initialize depletion counter at zero.
    depletion_counter = np.zeros((2525, 2272), dtype=float)
    # keep track of the maximum depletion map
    max_depletion = np.zeros((2525, 2272), dtype=float)
    # depletion_list = []
    total_ssebop = np.zeros((2525, 2272), dtype=float)
    for i in range(months_in_series + 1):

        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(pris_path, precip_name.format(date.year, date.month))
        ssebop = os.path.join(ssebop_path, ssebop_name.format(date.year, date.month))

        print 'precip', precip
        print 'ssebop', ssebop

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        ssebop_arr, transform, dim, proj, dt = raster_extract(ssebop)

        total_ssebop += ssebop_arr

        # oldmax = max_depletion

        # depletion for the current monthly timestep
        depletion_delta = depletion_calc(ssebop_arr, precip_arr)

        # add to the running depletion tally
        print depletion_delta.shape
        print depletion_counter.shape
        depletion_counter += depletion_delta
        depletion_ledger += depletion_delta

        # for any values that become negative, make them zero. Assume runoff...Wang-Erlandsson (2016)
        # todo - comment out to ONLY allow positive depletions
        # depletion_counter[depletion_counter < 0.0] = 0.0

        # newmax_bool = [depletion_counter > max_depletion]
        # newmax = depletion_counter[newmax_bool == True]
        newmax = np.maximum(depletion_counter, max_depletion)

        max_depletion = newmax

        # print "is this messed up?", oldmax == newmax

        # for each monthly timestep, take the cumulative depletion condition and output it as a raster
        depletion_name = "cumulative_depletion_{}_{}.tif".format(date.year, date.month)
        write_raster(depletion_counter, transform, output_folder, depletion_name, dim, proj, dt)

    # output the maximum depletion
    max_depletion_name = 'max_depletion_{}_{}.tif'.format(start_date.year, end_date.year)
    write_raster(max_depletion, transform, output_folder, max_depletion_name, dim, proj, dt)

    # output total SSEBop (to test wheter it looks like the netcdf file)
    total_ssebop_name = "total_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(total_ssebop, transform, output_folder, total_ssebop_name, dim, proj, dt)

    # output the average SSEBop (to test whether it looks like the netcdf file)
    average_ssebop = total_ssebop/float(months_in_series)
    average_ssebop_name = "average_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(average_ssebop, transform, output_folder, average_ssebop_name, dim, proj, dt)


def run_rename():
    """
    renames the files from ETRM to be easier to code up.
    :return:
    """
    pris_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"

    for file in os.listdir(pris_path):
        print file

        filename = file.split(".")[0]
        fileparts = filename.split("_")

        year = fileparts[-1]

        month = fileparts[-2]

        new_filename = "tot_precip_{}_{}.tif".format(year, month)

        old_file = os.path.join(pris_path, file)
        new_file = os.path.join(pris_path, new_filename)

        os.rename(old_file, new_file)


if __name__ == "__main__":

    # wanted to rename tot_precip_mm_yyyy ->to-> tot_precip_yyyy_mm. ONLY NEED TO RUN ONCE.
    # run_rename()

    """
    At this time, I am running this script to output the depletions as wang-erlandsson did: simply neglecting runoff and
    subrtracting ETa from Precip. I'm doing this before taking into account Esther's runoff for simplicity's sake and to
    avoid having one more pre-processing step of subracting Runoff from Precip and averaging for 22 runs of Esther's
    model. I can simply have the monthly precip in a directory, and pre-processed SSEBop ETa in another and perform the
    monthly depletion calculation
    """
    run_W_E()

    """
    COMPLETE WHEN PYRANA OUTPUTS ARE PREPROCESSED
    """

    # run_PyRANA_infil()

