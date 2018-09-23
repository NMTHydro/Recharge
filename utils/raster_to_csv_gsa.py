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
import numpy as np

import pandas as pd


# ============= local library imports ===========================

def raster_to_csv(path, output_path):
    """"""

    gdal.AllRegister()

    # driver = gdal.GetDriverByName('HFA')
    #
    # driver.Register()

    datasource = gdal.Open(path)

    # size
    rows = datasource.RasterYSize
    cols = datasource.RasterXSize
    bands = datasource.RasterCount

    # georefference
    transform = datasource.GetGeoTransform()
    xorigin = transform[0]
    print('x oringin', xorigin)
    yorigin = transform[3]
    print('yorigin', yorigin)
    pixelwidth = transform[1]
    print('widht of pixel', pixelwidth)
    pixelheight = transform[5]
    # todo - is the pixelheight being 29.9999 a problem?
    print('pixelheight', pixelheight)

    # X and Y raster coordinates
    # build an array of all-zeros in the shape of the raster


    test_arr = np.zeros((rows, cols))
    x_arr = np.zeros((rows,cols))
    y_arr = np.zeros((rows, cols))
    print('test arr', test_arr)

    it = np.nditer(test_arr, flags=['multi_index'])
    while not it.finished:
        # print "%d <%s>" % (it[0], it.multi_index)
        # print 'it', it[0]
        # print "multiindex", it.multi_index


        x = it.multi_index[1]
        # print x
        y = it.multi_index[0]
        # print y

        xcoord = (x * pixelwidth) + xorigin
        ycoord = (y * pixelheight) + yorigin

        # print "x {}, y {}".format(xcoord, ycoord)
        # y is rows, x is cols
        x_arr[y, x] = xcoord
        y_arr[y, x] = ycoord

        it.iternext()


    print("the x, y coords of the test array", x_arr, '\n', y_arr)




    # something to hold the arrays from each band
    bandlist = []
    col_list = []

    # go through the bands and read in each raster
    for i in range(bands):
        band = datasource.GetRasterBand(i+1)
        data = band.ReadAsArray(0, 0, cols, rows).astype(np.float64)
        # flatten and turn into a list....
        data = list(data.ravel())
        bandlist.append(data)



    # now that all the arrays are stored let's build a dictionary and flatten them with .ravel() method


    band_dictionary = {}

    for i in range(len(bandlist)):

        band_dictionary['B{}'.format(i)] = bandlist[i]
        col_name = 'B{}'.format(i)
        col_list.append(col_name)

    # print 'band dictionary', band_dictionary

    band_dictionary['X'] = list(x_arr.ravel())
    band_dictionary['Y'] = list(y_arr.ravel())

    col_list.append('X')
    col_list.append('Y')

    df = pd.DataFrame(band_dictionary, columns=col_list)

    df.to_csv(os.path.join(output_path, 'hahaha.csv'))



def main():
    """"""

    layered_raster_path = '/Users/Gabe/Desktop/' \
                          'GSA_consulting/jan_coordinates/' \
                          'lc08_l1tp_040033_20150221__rnmc_x_y_alb_embb_ndvi_snowflag_ts_rb2_rb3_rb4_rb5_rb6_eb10_rb7_rsoflat_trbb_mask.img'

    output_path = '/Users/Gabe/Desktop/GSA_consulting/jan_coordinates/'

    # Steps
    # 1) open the image
    # 2) get the geotransform
    # 3) read the raster in for each pixel and determine the coordinates of each pixel
    # 4) store the info x, y, value in a datastructure


    raster_to_csv(layered_raster_path, output_path)


if __name__ == '__main__':

    main()