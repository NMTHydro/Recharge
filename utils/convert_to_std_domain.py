import os
import fnmatch
import gdal
from subprocess import call

INPUT_FOLDER = 'C:\Recharge_GIS\land_use_land_cover'
OUTPUT_FOLDER = 'C:\Recharge_GIS\OSG_Data'
extent = 'F:\\Reference_shape\\NM_poly500mbuf\\NM_poly500mbuf.shp'

os.chdir(INPUT_FOLDER)


def findRasters(path, filter_):
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, filter_):
            yield file


for raster in findRasters(INPUT_FOLDER, '*.tif'):
    (FOLDER, rastname) = os.path.split(raster)

    inRaster = INPUT_FOLDER + '\\' + rastname
    temp = OUTPUT_FOLDER + '\\' + 'temp.tif'
    outRaster = OUTPUT_FOLDER + '\\' + rastname

    outRaster = OUTPUT_FOLDER + '\\' + rastname
    warp = 'gdalwarp -overwrite -s_srs EPSG:26913 -t_srs EPSG:26913 -te 114757 3471163 682757 4102413 -ts 2272 2525 -r\n' \
           ' "near" -cutline %s -crop_to_cutline -multi -srcnodata "-3.40282346639e+038" -dstnodata -999 %s %s' % (
               extent, inRaster, temp)
    call(warp)

    warp2 = 'gdalwarp -overwrite  -s_srs EPSG:26913 -t_srs EPSG:26913 -te 114757 3471163 682757 4102413 -tr \n' \
            '250 250 -r "mode" -multi -srcnodata -999 -dstnodata -999 %s %s' % (
                temp, outRaster)
    call(warp2)
    print("Done processing {a}".format(a=outRaster))
