import sys
import gdal
from gdalconst import *
import os
import numpy as np

from subprocess import call


def reproject_rasters(path, ras, outpath, env_path, output_ras_proj=None, input_ras_proj=None, resample=None, pixel_size=None):
    """
    Reprojects the rasters based on coord system given.
    :param path:
    :param ras: path to rasterfile
    :param outpath:
    :param output_ras_proj:
    :param input_ras_proj:
    :param resample:
    :param pixel_size:
    :return:
    """

    print "The projection", ras.GetProjection()

    # get the geotransform from the input raster (ras)
    # ras.GetGeo

    print "reprojecting the raster"

    # === Format the file name for output ====
    filename = path.split("\\")[-1]
    filename_lst = filename.split(".")
    filename = "_".join(filename_lst[0:3])
    appendage = "warp_{}_resample.tiff".format(output_ras_proj.split(":")[-1])
    filepath = os.path.join(outpath, "{}_{}".format(filename, appendage))

    print "Filepath of output file -> {}".format(filepath)

    # format gdal warpcommand to be called by subprocess.call()
    warpcommand = "gdalwarp --config GDAL_DATA {} -overwrite -s_srs {} -t_srs {} -r {} -tr {} -of GTiff {} {}".format(env_path, input_ras_proj,
                                                                                               output_ras_proj,
                                                                                               resample, pixel_size,
                                                                                             path, filepath)

    print "#========== \n Calling the following warp command: \n {} \n #==========".format(warpcommand)

    call(warpcommand)


def process_rasters(tsrs, ssrs, ts, r, input_dir, process_output, env_path):
    """processes rasters based on settings defined below."""

    # print "registering gdal driver (for reading)"
    # register driver for geotiff anyway
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()

    print "Running process rasters"

    # === run a loop ===

    for path, dirs, files in os.walk(input_dir, topdown=False):

        print "path", path
        print "dirs", dirs
        print "files", files

        for file in files:
            print "file processing -> {}".format(file)
            if file.endswith("tif"):

                f_path = os.path.join(path, file)

                # open the raster and read in
                razter = gdal.Open(f_path, GA_ReadOnly)  # other option GA_Update
                if razter is None:
                    print "can't open {}".format(f_path)
                    sys.exit(1)

                # now reproject using the function
                reproject_rasters(f_path, razter, process_output, env_path, output_ras_proj=tsrs, input_ras_proj=ssrs, resample=r, pixel_size=ts)

def zero_out(zeroout_input, zeroout_output_dir):
    """
    Here we read in the rasters from the previous output directory, set the minimum value to zero to correct for edge
    effects and re-write the files
    :return:
    """

    # try:
    #     if zeroout_output_dir is None:
    #         print "making directory"
    #         os.mkdir(zeroout_output_dir)
    # except:
    #     print 'cant make the output directory'
    #     Exception
    #     pass

    # register the geotiff driver
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()

    for path, dirs, files in os.walk(zeroout_input, topdown=False):
        print "path", path
        print "dirs", dirs
        print "files", files

        for file in files:

            if file.endswith("tiff"):

                f_path = os.path.join(path, file)

                # open the raster and read in
                razter_dataset = gdal.Open(f_path, GA_ReadOnly)  # other option GA_Update
                if razter_dataset is None:
                    print "can't open {}".format(f_path)
                    sys.exit(1)

                # set the minimum value to an appropriate one for ETa

                outrazter_band = razter_dataset.GetRasterBand(1)

                outrazter = outrazter_band.ReadAsArray().astype(np.float32)
                negatives = outrazter[outrazter < 0]
                print "old negatives", negatives
                #maybe works
                outrazter[np.where(outrazter < 0)] = 0
                print 'zeroed out', outrazter
                print "new negatives", outrazter[outrazter < 0]

                # a name and a path for this raster file
                o_path = os.path.join(zeroout_output_dir, file)

                # get rows and cols
                print "x", razter_dataset.RasterXSize
                print 'y', razter_dataset.RasterYSize
                rows = razter_dataset.RasterYSize
                cols = razter_dataset.RasterXSize


                # write the raster to the output file

                out_data = driver.Create(o_path, cols, rows, 1, GDT_Float32)
                if out_data is None:
                    print "can't create {}".format(o_path)
                    sys.exit(1)

                out_band = out_data.GetRasterBand(1)

                out_band.WriteArray(outrazter, 0, 0)

                out_data.SetProjection(razter_dataset.GetProjection())
                out_data.SetGeoTransform(razter_dataset.GetGeoTransform())

            razter_dataset = None
            out_data = None


def fix_names():
    """
    Only run if you need to get the filenames fixed for example if you are using model builder and there are some
    non-ideal characters in the path like '-' or '.'
    :return:
    """

    print "RUNNING FIX NAMES FUNCTION"

    # start with the output path from the zero_out() function
    root = 'E:\SSEB\monthly_NM'
    output_dir = os.path.join(root, 'SSEB_ETA_warp_resampled_2000_2015_min_vals_set')

    os.chdir(output_dir)

    for filename in os.listdir(output_dir):

        if "-" in filename:

            print "filename", filename

            namelist = filename.split("-")
            new_filename = "_".join(namelist)

            # rename the thing
            os.rename(filename, new_filename)

    print "ALL DONE"


def main():

    # Which coord system do you want to reproject to? (-t_srs)
    # EPSG:26913 == NAD 83 UTM zone 13N
    tsrs = 'EPSG:26913'

    # what is the projection of the input rasters?
    # EPSG:4326 is WGS 84 Lat Lon
    ssrs = 'EPSG:26913' # 'EPSG:4326'

    # how big to you want the raster pixels to be? (-ts)
    ts = "30 30"  # width and height of pixel

    # what algorithm do you want to use to resample? (-r)
    r = "cubic"

    # ==== PATHS ====

    # path to set the gdal environment.
    env_path = "C:\Users\gparrish-admin\AppData\Local\conda\conda\envs\ETRM\Library\share\gdal"

    # === Reprojecting with process_rasters ===

    input_root = 'C:\Users\gparrish-admin\Desktop\monthly_rasters_backup' #'E:\SSEB\monthly_NM'
    output_root = 'E:\ETRM_Results\monthly_results_5_2018'
    # the original input files
    input_dir = os.path.join(input_root, 'ETa')#'Raw_SSEB_ETA_2000_2015\sseb_nm_extent'
    # the directory where you want to output your processed files
    process_output = os.path.join(output_root, 'Resampled_monthly_etrm')

    # # ^^^^^^^^ RUN process rasters ^^^^^^^^
    #
    # process_rasters(tsrs, ssrs, ts, r, input_dir, process_output, env_path)

    # === Dealing with negative raster values ===

    # directory where you want to get your zero_out input from
    zeroout_input = process_output
    # and to output form the zero out function...
    zeroout_output_dir = os.path.join(output_root, 'Resampled_monthly_etrm_min_vals_set')

    # ^^^^^^^^ RUN zero_out ^^^^^^^^

    zero_out(zeroout_input, zeroout_output_dir)

    # === Dealing with weird filenames (SSEB) ===

    # # only use if you need to change the naming conventions of the file outputs from the other two functions.
    # fix_names()


if __name__ == "__main__":

    main()

    # EOF
