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
    print 'raster extract running on {}, {}'.format(os.path.isfile(raster_path), raster_path)
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


def run_W_E(cfg, eta_path=None, pris_path=None, output_folder=None, is_ssebop=True, shape=None):
    """

    :return:
    """
    # over 15 years we normalize every monthly map by the total precip. Do the same for SSEB ETa.

    # path to monthly ETa
    if eta_path is None:
        eta_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/SSEBop/SSEBOP_Geotiff_warped"

    # path to monthly Prism
    if pris_path is None:
        pris_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"

    # output path
    if output_folder is None:
        output_folder = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/cum_depletions_neg"

    # seems like we need to start in Feb of 2000 (ETRM monthly precip outputs only start in Feb 2000...)

    # function to calculate the depletion at a monthly timestep
    #  within that function, output the running depletion raster that results from each month's F_in-F_out
    # start_date = datetime.strptime("2000-2", "%Y-%m")
    # end_date = datetime.strptime("2013-12", "%Y-%m")
    start_date, end_date = cfg.date_range
    months_in_series = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)
    print 'start and end dates: {}, {}'.format(start_date, end_date)
    precip_name = "tot_precip_{}_{}.tif"
    if is_ssebop:
        eta_name = "ssebop_{}_{}_warped.tif"
    else:
        eta_name = "tot_eta_{}_{}.tif"

# at each timestep, keep track of how negative the depletion has gotten; initialize at zero
    if shape is None:
        shape = 2525, 2272
    depletion_ledger = np.zeros(shape, dtype=float)
    # keep track of the maximum depletion map
    max_depletion = np.zeros(shape, dtype=float)
    # depletion_list = []
    total_eta = np.zeros(shape, dtype=float)
    for i in range(months_in_series + 1):
        print 'run we iteration {}'.format(i)
        # count up from the start date by months...
        date = start_date + relativedelta(months=+i)

        precip = os.path.join(pris_path, precip_name.format(date.year, date.month))
        eta = os.path.join(eta_path, eta_name.format(date.year, date.month))
        if not os.path.isfile(precip):
            break

        # print 'precip', precip
        # print 'ETa (ssebop)', eta

        # array, transform, dimensions, projection, data type
        precip_arr, transform, dim, proj, dt = raster_extract(precip)
        eta_arr, transform, dim, proj, dt = raster_extract(eta)

        total_eta += eta_arr

        # depletion for the current monthly timestep
        depletion_delta = depletion_calc(eta_arr, precip_arr)

        # add to the running depletion tally
        depletion_ledger += depletion_delta

        # for any values that become negative, make them zero. Assume runoff...Wang-Erlandsson (2016)
        # todo - comment out to allow negative depletions (i.e., accumulation of water beyond storage)
        depletion_ledger[depletion_ledger < 0.0] = 0.0

        # newmax_bool = [depletion_ledger > max_depletion]
        # newmax = depletion_ledger[newmax_bool == True]
        max_depletion = np.maximum(depletion_ledger, max_depletion)

        # print "is this messed up?", oldmax == newmax

        # for each monthly timestep, take the cumulative depletion condition and output it as a raster
        depletion_name = "cumulative_depletion_{}_{}.tif".format(date.year, date.month)
        print 'trying to write cumulative dep'
        write_raster(depletion_ledger, transform, output_folder, depletion_name, dim, proj, dt)

    print 'iterations finished'
    # output the maximum depletion
    max_depletion_name = 'max_depletion_{}_{}.tif'.format(start_date.year, end_date.year)
    write_raster(max_depletion, transform, output_folder, max_depletion_name, dim, proj, dt)

    # output total ETa (i.e., SSEBop) to test wheter it looks like the netcdf file
    total_eta_name = "total_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(total_eta, transform, output_folder, total_eta_name, dim, proj, dt)

    # output the average ETa (i.e., SSEBop) to test whether it looks like the netcdf file
    average_eta = total_eta/float(months_in_series)
    average_eta_name = "average_ssebop_{}_{}.tif".format(start_date.year, end_date.year)
    write_raster(average_eta, transform, output_folder, average_eta_name, dim, proj, dt)


def run_rename(param_path=None, param='precip'):
    """
    renames the files from ETRM to be easier to code up.
    :return:
    """
    if param_path is None:
        param_path = "/Volumes/Seagate_Expansion_Drive/SSEBop_research/monthly_prism"

    for rfile in os.listdir(param_path):
        if os.path.basename(rfile).startswith('tot_{}'.format(param)):

            filename = rfile.split(".")[0]
            fileparts = filename.split("_")

            year = fileparts[-1]

            month = fileparts[-2]
            if param is 'precip':
                new_filename = "tot_precip_{}_{}.tif".format(year, month)
            elif param is 'eta':
                new_filename = "tot_eta_{}_{}.tif".format(year, month)
            old_file = os.path.join(param_path, rfile)
            new_file = os.path.join(param_path, new_filename)

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

