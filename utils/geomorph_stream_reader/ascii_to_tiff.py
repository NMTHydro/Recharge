
# ============= standard library imports ========================
import os
import numpy as np
import gdal
from gdalconst import *
from matplotlib import pyplot as plt
import pandas as pd


# ============= local library imports ===========================

def write_raster(array, geotransform, output_path, output_filename, dimensions, projection):
    """

    :param array: numpy array
    :param geotransform:
    :param output_path: user specified output path
    :param output_filename: user specified output filename. String
    :param dimensions: raster rows, cols
    :param projection: ESPG projection code. In meters for this script
    :return:
    """

    filename = os.path.join(output_path, output_filename)

    driver = gdal.GetDriverByName('GTiff')
    # path, cols, rows, bandnumber, data type (if not specified, as below, the default is GDT_Byte)

    output_dataset = driver.Create(filename, dimensions[0], dimensions[1], 1, GDT_Float32)

    # output_dataset = driver.Create(filename, dimensions[1], dimensions[0], 1, GDT_Float32)

    # we write TO the output band
    output_band = output_dataset.GetRasterBand(1)

    # we don't need to do an offset
    output_band.WriteArray(array, 0, 0)

    'There you go, Michael!'

    # set the geotransform in order to georefference the image
    output_dataset.SetGeoTransform(geotransform)
    # # set the projection
    # output_dataset.SetProjection(projection)


def read_ascii(ascii_file, shp):
    """"""

    data = pd.read_csv(ascii_file, header=None)
    data1d = np.asarray(data[2][:])
    new = np.reshape(data1d, (301, 201))

    plt.imshow(new)
    plt.show()

    return new


def main(ascii_path, geo_dict, output_path):
    """"""

    geo = geo_dict['geo']
    proj = geo_dict['proj']
    dim = geo_dict['dim']

    for f in os.listdir(ascii_path):
        # print 'this is the file:', f
        if 'sr4' in f:
            print 'reading for sure'
            fname_lst = f.split('.')
            print 'fnamelist', fname_lst
            fname = "{}_{}.tif".format(fname_lst[0], fname_lst[1])
            f = os.path.join(ascii_path, f)
            # print 'new f \n {}'.format(f)

            # todo - WHAAAT??
            tiff_arr = read_ascii(f, geo_dict['dim'])



            # ==========



            print 'vals \n', tiff_arr
            print 'shape', tiff_arr.shape
            write_raster(tiff_arr, geo, output_path, fname, dim, proj)

            # onesies = np.ones(tiff_arr.shape)

            # write_raster(onesies, geo, output_path, fname, dim, proj)

if __name__ == "__main__":

    ascii_path = '/Users/Gabe/Desktop/berry_data'

    proj = 'ESPG:32613'

    shape_of_raster = (201, 301)
    # shape_of_raster = (301, 201)

    topleftx = 0
    toplefty = 60200
    wepixelres = 200
    nspixelres = 200
    rotation = 0

    geotransform = [topleftx, wepixelres, rotation, toplefty, rotation, nspixelres]

    geo_dict = {'geo': geotransform, 'dim': shape_of_raster, 'proj': proj}

    output_path = '/Users/Gabe/Desktop/berry_data/berry_tifs'

    main(ascii_path, geo_dict, output_path)
