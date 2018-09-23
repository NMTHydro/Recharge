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
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
import numpy as np
import gdal
import seaborn
from jdcal import gcal2jd, jd2gcal

# ============= local library imports ===========================


def calculate_julian_date(year, julian_doy):
    """"""

    first_of_the_year = int(sum(gcal2jd(year, 1, 1)))
    # print "first day jd", first_of_the_year

    julian_date = first_of_the_year + int(julian_doy)
    # print "full julian date", julian_date

    return julian_date

def format_date(date, year):
    """"""

    year_jd = int(sum(gcal2jd(year, 1, 1)))
    # print "year 2000", year_2000

    date = date - year_jd
    d = jd2gcal(year_jd, date)
    print("datedate", d)

    # test
    for i in (1, 10, 100):
        print("{num:02d}".format(num=i))

    date_string = "{}_{a:02d}_{b:02d}".format(d[0], a=d[1], b=d[2])

    return date_string

def read_files(file_list):
    """"""
    # erdas imagine driver..
    driver = gdal.GetDriverByName('HFA')
    # must register the driver before you can use it.
    driver.Register()

    # now we can open files
    img_file_list = []
    for img_file in file_list:
        img_obj = gdal.Open(img_file)
        if img_obj is None:
            print('Couldnt open' + img_file)

            gdal.sys.exit(1)
        img_file_list.append(img_obj)

    return img_file_list

def format_list(lst):

    length = len(lst)

    print("length of list", length)
    print("heres the list", lst)

    print("range {}".format(range(length)))

    tuple_list = []
    for i in range(length):
        if i < length-1:
            tupper = (lst[i],lst[i+1])
            tuple_list.append(tupper)

        elif i == range(length):
            tupper = (lst[i - 1], lst[i])
            tuple_list.append(tupper)

    print("tuple list {}".format(tuple_list))

    return tuple_list

def findRasterIntersect(raster1, raster2):
    # load data
    band1 = raster1.GetRasterBand(1)
    band2 = raster2.GetRasterBand(1)
    gt1 = raster1.GetGeoTransform()
    # print "here is geotransform 1 {}".format(gt1)
    gt2 = raster2.GetGeoTransform()
    # print "here is geotransform 1 {}".format(gt2)

    # print "raster1.RasterXSize = {}".format(raster1.RasterXSize)
    # print "raster1.RasterYSize = {}".format(raster1.RasterYSize)
    # print "raster2.RasterXSize = {}".format(raster2.RasterXSize)
    # print "raster2.RasterYSize = {}".format(raster2.RasterYSize)



    # find each image's bounding box
    # r1 has left, top, right, bottom of dataset's bounds in geospatial coordinates.
    r1 = [gt1[0], gt1[3], gt1[0] + (gt1[1] * raster1.RasterXSize), gt1[3] + (gt1[5] * raster1.RasterYSize)]
    r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * raster2.RasterXSize), gt2[3] + (gt2[5] * raster2.RasterYSize)]
    print('\t1 bounding box: %s' % str(r1))
    print('\t2 bounding box: %s' % str(r2))

    test_list = [r1[0], r2[0]]

    # find intersection between bounding boxes
    intersection = [max(test_list), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
    if r1 != r2:
        print('\t** different bounding boxes **')
        # check for any overlap at all...
        if (intersection[2] < intersection[0]) or (intersection[1] < intersection[3]):
            intersection = None
            print('\t*** no overlap ***')
            return
        else:
            print('\tintersection:', intersection)
            left1 = int(round((intersection[0] - r1[0]) / gt1[1]))  # difference divided by pixel dimension
            top1 = int(round((intersection[1] - r1[1]) / gt1[5]))
            col1 = int(round((intersection[2] - r1[0]) / gt1[1])) - left1  # difference minus offset left
            row1 = int(round((intersection[3] - r1[1]) / gt1[5])) - top1

            print("left 1: {}, top1: {}, col1: {}, row1: {}".format(left1, top1, col1, row1))

            left2 = int(round((intersection[0] - r2[0]) / gt2[1]))  # difference divided by pixel dimension
            top2 = int(round((intersection[1] - r2[1]) / gt2[5]))
            col2 = int(round((intersection[2] - r2[0]) / gt2[1])) - left2  # difference minus new left offset
            row2 = int(round((intersection[3] - r2[1]) / gt2[5])) - top2

            # print '\tcol1:',col1,'row1:',row1,'col2:',col2,'row2:',row2
            if col1 != col2 or row1 != row2:
                print("*** MEGA ERROR *** COLS and ROWS DO NOT MATCH ***")
            # these arrays should now have the same spatial geometry though NaNs may differ
            array1 = band1.ReadAsArray(left1, top1, col1, row1)
            array2 = band2.ReadAsArray(left2, top2, col2, row2)

    else:  # same dimensions from the get go
        print("same dimensions from the get go...")
        col1 = raster1.RasterXSize  # = col2
        row1 = raster1.RasterYSize  # = row2
        array1 = band1.ReadAsArray()
        array2 = band2.ReadAsArray()

    return array1, array2, col1, row1, intersection

def pull_files(path_to_files):
    """"""
    # TODO - somehow go back and make all the lists returned here be filled w tuples of current and next interpolation
    # TODO - so then, we can iterate through each list in run_interpolation() and feed the function two rasters at a time.
    jd_list = []
    path_list = []
    year_list = []
    for p, dir, files in os.walk(path_to_files):
        for i in files:
            if i.endswith(".img"):
                print("i", i)

                date = i[9:16]
                year = date[:-3]
                julian_doy = date[4:]

                # print "date", date
                # print "year", year
                # print "Julian DOY", julian_doy

                year_list.append(year)

                julian_date = calculate_julian_date(year, julian_doy)
                jd_list.append(julian_date)

                file_path = os.path.join(p, i)
                path_list.append(file_path)

    # print "jd list", jd_list
    # print "file path list", path_list

    # diff = jd_list[1] - jd_list[0] # just checking that the difference between days of the year is correct...
    # print "difference", diff

    # return a list of arrays from gdal, or a list of tuples containing arrays,
    raster_obj_list = read_files(path_list)

    # print "obj list", raster_obj_list

    jd_list = format_list(jd_list)
    path_list = format_list(path_list)
    raster_obj_list = format_list(raster_obj_list)

    return jd_list, path_list, raster_obj_list, year_list

def get_arr(gdal_obj):
    """"""
    # get the imagine driver and register it

    driver = gdal.GetDriverByName('HFA')
    driver.Register()

    # print "here is the gdal_obj", gdal_obj

    band = gdal_obj.GetRasterBand(1)

    data = band.ReadAsArray(0, 0)

    # print "data", data

    return data

def write_file(current_obj, arr, col, row, filename):
    """"""

    driver = current_obj.GetDriver()
    driver.Register()

    # TODO - Change for new output folder...
    ds = driver.Create("/Volumes/Seagate Backup Plus Drive/all_dates_test/{}.img".format(filename), col, row, 1, gdal.GDT_Float32) #"" /Users/Gabe/Desktop/hard_drive_overflow/rapid_testfile_output/{}.img
    ds.SetGeoTransform(current_obj.GetGeoTransform())
    ds.SetProjection(current_obj.GetProjection())
    ds_band = ds.GetRasterBand(1)
    ds_band.WriteArray(arr)

def output_rasters(current_arr, next_arr, slope, start_date, end_date, date_count, current_obj, next_obj, year):
    """"""
    # get the driver from one of the objects
    driver = current_obj.GetDriver()
    driver.Register()

    # geotransform = current_obj.GetGeoTransform()
    col = current_obj.RasterXSize
    row = current_obj.RasterYSize

    # output the current arr to a file


    print("START -> ndvi{}".format(start_date))
    # reformat the date stirng
    date_string = format_date(start_date, year)
    write_file(current_obj, current_arr, col, row, "NDVI{}".format(date_string))

    # output all the in-between rasters to files
    cnt = 1 # TODO - Check here again if problem
    print("here's the range \n", range(start_date + 1, end_date))
    for i in range(start_date + 1, end_date): # -1
        interp_arr = np.add(current_arr, (slope * cnt))
        print("Bout to write ndvi_{}".format(i))
        # reformat the date String
        date_string = format_date(i, year)
        write_file(current_obj, interp_arr, col, row, "NDVI{}".format(date_string))
        print("wrote a file. Count: {}".format(cnt))
        cnt += 1


    # # output the next arr to a file

    # todo fix the filename thing...
    print("END -> ndvi_{}".format(end_date))

    date_string = format_date(end_date, year)

    write_file(current_obj, next_arr, col, row, "NDVI{}".format(date_string))

def interpolator(jd_list, path_list, raster_obj_list, year):
    """

    :param jd_list:
    :param path_list:
    :param raster_obj_list:
    :return:
    """

    start_date = jd_list[0]
    end_date = jd_list[-1]
    # we need a total count of the number of days between our images.
    date_count = end_date - start_date # + 1
    print("date count", date_count)
    # this creates a range of every date between start and end.
    date_range = range(start_date, end_date + 1)
    # print "date range", date_range

    current_obj = raster_obj_list[0]
    next_obj = raster_obj_list[1]

    current_arr = get_arr(current_obj)
    # print "shape current arr", current_arr.shape
    next_arr = get_arr(next_obj)
    # print "shape next arr", next_arr.shape

    diff = np.subtract(next_arr, current_arr)
    slope = np.divide(diff, float(date_count))

    # print "we got a slope, people!", slope

    # Get the paths as well
    current_path = path_list[0]
    next_path = path_list[1]

    output_rasters(current_arr, next_arr, slope, start_date, end_date, date_count, current_obj, next_obj, year)


def run_interpolator():
    """
    This function is the master function that orchestrates reading of raster files into arrays, then passes them into an
     interpolation function that interpolates the ndvi on a daily basis with a linear interpolation
    :return:
    """

    path_to_files = "/Users/Gabe/Desktop/hard_drive_overflow/METRIC_ETRM_Jornada_NDVI_P33R37" #METRIC_ETRM_Jornada_NDVI_P33R37"

    jd_list, path_list, raster_obj_list, year_list = pull_files(path_to_files)

    # # todo - have the array use findRasterIntersect here for each pair of rasters in the raster_obj_list
    # # not sure if it's necessary yet to use it so...
    # for i in raster_obj_list:
    #     findRasterIntersect(i[0], i[1])

    print('jd list \n', jd_list)

    # use the lists to run the interpolation.
    for i, k, j, year in zip(jd_list, path_list, raster_obj_list, year_list):
        interpolator(i, k, j, year)

if __name__ == "__main__":

    run_interpolator()
