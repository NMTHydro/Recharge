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
# import os
# import fiona
# import rasterio
# import rasterio.tools.mask as maskit
# from rasterio import features

#from recharge.raster_tools import convert_raster_to_array
import operator
from osgeo import gdal, gdalnumeric, ogr, osr
from PIL import Image, ImageDraw
from numpy import array, asarray
import os, sys
gdal.UseExceptions()
# ============= local library imports ===========================

"""
This script will be used to:

1) separate out pixels of an image by land use by multiplying pixels by a mask array.



"""

def convert_raster_to_array(input_raster_path, raster=None, band=1):
    """
    Convert .tif raster into a numpy numerical array.

    :param input_raster_path: Path to raster.
    :param raster: Raster name with \*.tif
    :param band: Band of raster sought.

    :return: Numpy array.
    """
    # print "input raster path", input_raster_path
    # print "raster", raster
    p = input_raster_path
    if raster is not None:
        p = os.path.join(p, raster)

    # print "filepath", os.path.isfile(p)
    # print p
    if not os.path.isfile(p):
        print 'Not a valid file: {}'.format(p)

    raster_open = gdal.Open(p)
    ras = array(raster_open.GetRasterBand(band).ReadAsArray(), dtype=float)
    return ras

def convert_array_to_raster(output_path, arr, geo, output_band=1):
    driver = gdal.GetDriverByName('GTiff')
    out_data_set = driver.Create(output_path, geo['cols'], geo['rows'],
                                 geo['bands'], geo['data_type'])
    print 'out dataset', out_data_set
    out_data_set.SetGeoTransform(geo['geotransform'])
    out_data_set.SetProjection(geo['projection'])

    output_band = out_data_set.GetRasterBand(output_band)
    print 'heres the array to save convere_array_to_raster ', arr
    output_band.WriteArray(arr, 0, 0)
    del out_data_set, output_band

    if not os.path.isfile(output_path):
        print "Not a valid file: '{}' - Raster could not be written!".format(output_path)
        return


def get_raster_geo_attributes(root):
    """
    Creates a dict of geographic attributes from any of the pre-processed standardized rasters.

    :param root: Path to a folder with pre-processed standardized rasters.
    :return: dict of geographic attributes.
    """
    # statics = [filename for filename in os.listdir(statics_path) if filename.endswith('.tif')]
    # file_name = statics[0]
    file_name = next((fn for fn in os.listdir(root) if fn.endswith('.tif')), None)
    print 'filename', file_name
    dataset = gdal.Open(os.path.join(root, file_name))

    band = dataset.GetRasterBand(1)
    raster_geo_dict = {'cols': dataset.RasterXSize, 'rows': dataset.RasterYSize, 'bands': dataset.RasterCount,
                       'data_type': band.DataType, 'projection': dataset.GetProjection(),
                       'geotransform': dataset.GetGeoTransform(), 'resolution': dataset.GetGeoTransform()[1]}
    return raster_geo_dict



# TODO - CHANGES HERE EACH TIME
def format_raster_conv(geo_attributes, root, output_path, master_dict):

    for k, v in master_dict.iteritems():

        opath = "/{}/filtered_images/{}_ag.tif".format(output_path, k)

        convert_array_to_raster(opath, v, geo_attributes)

    # for k, v in master_dict.iteritems():
    #
    #     if k.startswith("et"):
    #
    #         opath = "/{}/ETa_warped_ag_filtered/{}_ag.tif".format(output_path, k)
    #
    #         print "output path", opath
    #
    #         convert_array_to_raster(opath, v, geo_attributes)
    #
    #     elif k.startswith("ndvi"):
    #
    #         # output_path = os.path.join(output_path, "ndvi_warped_ag_filtered", "{}.tif".format(k))
    #
    #         opath = "/{}/ndvi_warped_ag_filtered/{}_ag.tif".format(output_path, k)
    #
    #         print "output path", opath
    #
    #         convert_array_to_raster(opath, v, geo_attributes)
    #
    #     elif k.startswith("ETrF"):
    #
    #         opath = "/{}/sh_ETrF_ag_filtered/{}_ag.tif".format(output_path, k)
    #
    #         print "output path", opath
    #
    #         convert_array_to_raster(opath, v, geo_attributes)



def run():

    #root = "/Volumes/SeagateExpansionDrive/SEBAL_Data_Sung-ho/SH_warp"
    # TODO Change Root Each time
    root = "/Volumes/SeagateExpansionDrive/ee_images_corrto_sungho/unfiltered_ee_images"

    mask_path = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/nlcd_ag_vectormask_1_test.tif"

    #TODO - Change output path each time.
    #output_path = "/Volumes/SeagateExpansionDrive/SEBAL_Data_Sung-ho/SH_warp"

    output_path = "/Volumes/SeagateExpansionDrive/ee_images_corrto_sungho/unfiltered_ee_images/filtered_images"

    master_dict = {}
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):

        for file in filenames:
            print file

            if file.endswith(".tif"):
                name = file.split(".")[0]
                master_dict["{}".format(name)] = os.path.join(dirpath, file)

    # print master_dict

    # The geo attributes will be the same for both. I don't know why it wants a whole directory and not a file. I could
    # redesign it but forget it for now.
    #Todo - Change geo_att path each time.
    geo_att = get_raster_geo_attributes(os.path.join(root, "2004_06_13_ee_unfil")) # "ETa_warped"
    #geo_att2 = get_raster_geo_attributes(os.path.join(root, "ndvi_warped"))

    # Get the mask array
    mask_arr = convert_raster_to_array(mask_path)


    # for each path in the master_dict, turn the raster into an array and store in master_dict

    for k, v in master_dict.iteritems():
        rast_arr = convert_raster_to_array(v)
        master_dict[k] = rast_arr


    # print master_dict

    #use the mask array to mask/filter the arrays now in master dict. Store arrs in master dict.
    for k, v in master_dict.iteritems():
        filtered_array = mask_arr * v
        master_dict[k] = filtered_array


    # format the output path create new arrays and save them to file:

    format_raster_conv(geo_att, root, output_path, master_dict)

    print "DONE"







if __name__ == "__main__":

    run()




# ============ RASTER TOOLS =================================

#def convert_raster_to_array(input_raster_path, raster=None, band=1):
#     """
#     Convert .tif raster into a numpy numerical array.
#
#     :param input_raster_path: Path to raster.
#     :param raster: Raster name with \*.tif
#     :param band: Band of raster sought.
#
#     :return: Numpy array.
#     """
#     # print "input raster path", input_raster_path
#     # print "raster", raster
#     p = input_raster_path
#     if raster is not None:
#         p = os.path.join(p, raster)
#
#     # print "filepath", os.path.isfile(p)
#     # print p
#     if not os.path.isfile(p):
#         print 'Not a valid file: {}'.format(p)
#
#     raster_open = gdal.Open(p)
#     ras = array(raster_open.GetRasterBand(band).ReadAsArray(), dtype=float)
#     return ras
#
#
# def convert_array_to_raster(output_path, arr, geo, output_band=1):
#     driver = gdal.GetDriverByName('GTiff')
#     out_data_set = driver.Create(output_path, geo['cols'], geo['rows'],
#                                  geo['bands'], geo['data_type'])
#     print 'out dataset', out_data_set
#     out_data_set.SetGeoTransform(geo['geotransform'])
#     out_data_set.SetProjection(geo['projection'])
#
#     output_band = out_data_set.GetRasterBand(output_band)
#     print 'heres the array to save convere_array_to_raster ', arr
#     output_band.WriteArray(arr, 0, 0)
#     del out_data_set, output_band
#
#     if not os.path.isfile(output_path):
#         print "Not a valid file: '{}' - Raster could not be written!".format(output_path)
#         return
#
# def get_raster_geo_attributes(root):
#     """
#     Creates a dict of geographic attributes from any of the pre-processed standardized rasters.
#
#     :param root: Path to a folder with pre-processed standardized rasters.
#     :return: dict of geographic attributes.
#     """
#     # statics = [filename for filename in os.listdir(statics_path) if filename.endswith('.tif')]
#     # file_name = statics[0]
#     file_name = next((fn for fn in os.listdir(root) if fn.endswith('.tif')), None)
#     dataset = gdal.Open(os.path.join(root, file_name))
#
#     band = dataset.GetRasterBand(1)
#     raster_geo_dict = {'cols': dataset.RasterXSize, 'rows': dataset.RasterYSize, 'bands': dataset.RasterCount,
#                        'data_type': band.DataType, 'projection': dataset.GetProjection(),
#                        'geotransform': dataset.GetGeoTransform(), 'resolution': dataset.GetGeoTransform()[1]}
#     return raster_geo_dict

#============================================== RASTERIO -----------------------------
# with rasterio.open("/Volumes/SeagateExpansionDrive/NLCD_2011_2006/LT50330362004133PAC02_NDVI.NDVI.tif") as src:
#     blue = src.read(1)
#
# mask = blue != 255
#
# with fiona.open("/Volumes/SeagateExpansionDrive/NLCD_2011_2006/aligned_nlcd_vector/aligned_nlcd_vector.shp",
#                 "r") as shapefile:
#     for i in shapefile:
#         print i
#
#     features = [feature["geometry"] for feature in shapefile]
#
#     print features
#
#     for feature in shapefile:
#         print feature
#         print 'geom', feature["geometry"]
#
# with rasterio.open("/Volumes/SeagateExpansionDrive/NLCD_2011_2006/LT50330362004133PAC02_NDVI.NDVI.tif") as src:
#     print(src)
#     # maskit.mask(src, features, crop=True)
#     print features
#     out_image, out_transform = maskit.mask(src, features, crop=True)
#     out_meta = src.meta.copy()
#
# out_meta.update({"driver": "GTiff",
#                  "height": out_image.shape[1],
#                  "width": out_image.shape[2],
#                  "transform": out_transform})
#
# with rasterio.open("Volumes/SeagateExpansionDrive/NLCD_2011_2006/"
#                    "ag_ndvi_pixels_masked.tif", "w", **out_meta) as dest:
#     dest.write(out_image)

############-==========================================================================
    ############-==========================================================================
    ############-==========================================================================
    ############-==========================================================================
    ############-==========================================================================

#
#  # This function will convert the rasterized clipper shapefile
# # to a mask for use within GDAL.
# def imageToArray(i):
#     """
#     Converts a Python Imaging Library array to a
#     gdalnumeric image.
#     """
#     a=gdalnumeric.fromstring(i.tostring(),'b')
#     a.shape=i.im.size[1], i.im.size[0]
#     return a
#
# def arrayToImage(a):
#     """
#     Converts a gdalnumeric array to a
#     Python Imaging Library Image.
#     """
#     i=Image.fromstring('L',(a.shape[1],a.shape[0]),
#             (a.astype('b')).tostring())
#     return i
#
# def world2Pixel(geoMatrix, x, y):
#   """
#   Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
#   the pixel location of a geospatial coordinate
#   """
#   ulX = geoMatrix[0]
#   ulY = geoMatrix[3]
#   xDist = geoMatrix[1]
#   yDist = geoMatrix[5]
#   rtnX = geoMatrix[2]
#   rtnY = geoMatrix[4]
#   pixel = int((x - ulX) / xDist)
#   line = int((ulY - y) / xDist)
#   return (pixel, line)
#
# #
# #  EDIT: this is basically an overloaded
# #  version of the gdal_array.OpenArray passing in xoff, yoff explicitly
# #  so we can pass these params off to CopyDatasetInfo
# #
# def OpenArray( array, prototype_ds = None, xoff=0, yoff=0 ):
#     ds = gdal.Open( gdalnumeric.GetArrayFilename(array) )
#
#     if ds is not None and prototype_ds is not None:
#         if type(prototype_ds).__name__ == 'str':
#             prototype_ds = gdal.Open( prototype_ds )
#         if prototype_ds is not None:
#             gdalnumeric.CopyDatasetInfo( prototype_ds, ds, xoff=xoff, yoff=yoff )
#     return ds
#
# def histogram(a, bins=range(0,256)):
#   """
#   Histogram function for multi-dimensional array.
#   a = array
#   bins = range of numbers to match
#   """
#   fa = a.flat
#   n = gdalnumeric.searchsorted(gdalnumeric.sort(fa), bins)
#   n = gdalnumeric.concatenate([n, [len(fa)]])
#   hist = n[1:]-n[:-1]
#   return hist
#
# def stretch(a):
#   """
#   Performs a histogram stretch on a gdalnumeric array image.
#   """
#   hist = histogram(a)
#   im = arrayToImage(a)
#   lut = []
#   for b in range(0, len(hist), 256):
#     # step size
#     step = reduce(operator.add, hist[b:b+256]) / 255
#     # create equalization lookup table
#     n = 0
#     for i in range(256):
#       lut.append(n / step)
#       n = n + hist[i+b]
#   im = im.point(lut)
#   return imageToArray(im)
#
# def main( shapefile_path, raster_path ):
#     # Load the source data as a gdalnumeric array
#     srcArray = gdalnumeric.LoadFile(raster_path)
#
#     # Also load as a gdal image to get geotransform
#     # (world file) info
#     srcImage = gdal.Open(raster_path)
#     geoTrans = srcImage.GetGeoTransform()
#
#     # Create an OGR layer from a boundary shapefile
#     shapef = ogr.Open(shapefile_path)
#     lyr = shapef.GetLayer( os.path.split( os.path.splitext( shapefile_path )[0] )[1] )
#     poly = lyr.GetNextFeature()
#
#     # Convert the layer extent to image pixel coordinates
#     minX, maxX, minY, maxY = lyr.GetExtent()
#     ulX, ulY = world2Pixel(geoTrans, minX, maxY)
#     lrX, lrY = world2Pixel(geoTrans, maxX, minY)
#
#     # Calculate the pixel size of the new image
#     pxWidth = int(lrX - ulX)
#     pxHeight = int(lrY - ulY)
#
#     clip = srcArray[:, ulY:lrY, ulX:lrX]
#
#     #
#     # EDIT: create pixel offset to pass to new image Projection info
#     #
#     xoffset =  ulX
#     yoffset =  ulY
#     print "Xoffset, Yoffset = ( %f, %f )" % ( xoffset, yoffset )
#
#     # Create a new geomatrix for the image
#     geoTrans = list(geoTrans)
#     geoTrans[0] = minX
#     geoTrans[3] = maxY
#
#     # Map points to pixels for drawing the
#     # boundary on a blank 8-bit,
#     # black and white, mask image.
#     points = []
#     pixels = []
#     geom = poly.GetGeometryRef()
#     pts = geom.GetGeometryRef(0)
#     for p in range(pts.GetPointCount()):
#       points.append((pts.GetX(p), pts.GetY(p)))
#     for p in points:
#       pixels.append(world2Pixel(geoTrans, p[0], p[1]))
#     rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
#     rasterize = ImageDraw.Draw(rasterPoly)
#     rasterize.polygon(pixels, 0)
#     mask = imageToArray(rasterPoly)
#
#     # Clip the image using the mask
#     clip = gdalnumeric.choose(mask, \
#         (clip, 0)).astype(gdalnumeric.uint8)
#
#     # This image has 3 bands so we stretch each one to make them
#     # visually brighter
#     for i in range(3):
#       clip[i,:,:] = stretch(clip[i,:,:])
#
#     # Save new tiff
#     #
#     #  EDIT: instead of SaveArray, let's break all the
#     #  SaveArray steps out more explicity so
#     #  we can overwrite the offset of the destination
#     #  raster
#     #
#     ### the old way using SaveArray
#     #
#     # gdalnumeric.SaveArray(clip, "OUTPUT.tif", format="GTiff", prototype=raster_path)
#     #
#     ###
#     #
#     gtiffDriver = gdal.GetDriverByName( 'GTiff' )
#     if gtiffDriver is None:
#         raise ValueError("Can't find GeoTiff Driver")
#     gtiffDriver.CreateCopy( "OUTPUT.tif",
#         OpenArray( clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset )
#     )
#
#     # Save as an 8-bit jpeg for an easy, quick preview
#     clip = clip.astype(gdalnumeric.uint8)
#     gdalnumeric.SaveArray(clip, "OUTPUT.jpg", format="JPEG")
#
#     gdal.ErrorReset()
#
#
# if __name__ == '__main__':
#
#     #
#     # example run : $ python clip.py /<full-path>/<shapefile-name>.shp /<full-path>/<raster-name>.tif
#     #
#     if len( sys.argv ) < 2:
#         print "[ ERROR ] you must two args. 1) the full shapefile path and 2) the full raster path"
#         sys.exit( 1 )
#
#     main( sys.argv[1], sys.argv[2] )



# ===== WORK IN PROGRESS =====

# # This function will convert the rasterized clipper shapefile to a mask for use within GDAL.
#
# def imageToArray(i):
#      """"
#
#      Converts a python imaging Library array to a gdalnumeric image. cool.
#
#      """
#      a = gdalnumeric.fromstring(i.tostring(), 'b')
#      a.shape = i.im.size[1], i.im.size[0]
#      return a
#
#
#
#
# def run():
#     # Raster image to clip:
#     raster = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/LT50330362004133PAC02_NDVI.NDVI.tif"
#
#     # Polygon Shapefile used to clip
#     shp = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/aligned_nlcd_vector/aligned_nlcd_vector.shp"
#
#     # name of clip raster files:
#
#     output = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/aligned_nlcd_vector/aligned_nlcd_vector_clip"
#
#     # load the source data as a gdalunumeric array
#     srcArray = gdalnumeric.LoadFile(raster)
#
#     # Also load as a gdal image to get the geotransform
#     # file info
#
#     srcImage = gdal.Open(raster)
#     geoTrans = srcImage.getGeoTransform()
#
#     # Create an OGR layer from a  boundary shapefile
#     shapef = ogr.Open("%s.shp" % shp)
#
#
## def run():
#
#     mask_path = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/nlcd_ag_vectormask_1_test.tif"
#
#     exe_filepath = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/good_raster/LT50330362004133PAC02_NDVI_NDVI.tif"
#
#     ex_filepath = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/good_raster"
#
#     output_path = "/Volumes/SeagateExpansionDrive/NLCD_2011_2006/ag_ndvi_test1.tif"
#
#     mask_arr = convert_raster_to_array(mask_path)
#
#     ndvi_arr = convert_raster_to_array(exe_filepath)
#
#     print mask_arr
#
#     print ndvi_arr
#
#     new_arr = mask_arr * ndvi_arr
#
#     print 'new_arr', new_arr
#
#     print 'filepath', os.listdir(ex_filepath)
#
#     new_arr_geo = get_raster_geo_attributes(ex_filepath)
#
#     print 'geo dict', new_arr_geo

    # convert_array_to_raster(output_path, new_arr, new_arr_geo)
#
#
# if __name__ == "__main__":
#
#     run()