import os, fnmatch
import gdal
from subprocess import call

input_folder = 'C:\Recharge_GIS\land_use_land_cover'
output_folder = 'C:\Recharge_GIS\OSG_Data'
extent = 'F:\\Reference_shape\\NM_poly500mbuf\\NM_poly500mbuf.shp'

os.chdir(input_folder)

projection = 26913  # NAD83 UTM Zone 13 North
x_min = 114757
y_min = 3471163
x_max = 682757
y_max = 4102413
cols = 2272
rows = 2525
resample_method_one = 'near'
resample_method_two = 'mode'
cell_size = 250


def find_rasters(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            yield file_


for raster in find_rasters(input_folder, '*.tif'):
    FOLDER, raster_name = os.path.split(raster)

    in_raster = os.path.join(input_folder, raster_name)
    temp = os.path.join(output_folder, 'temp.tif')
    out_raster = os.path.join(output_folder, raster_name)

    warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g}\n' \
           ' -r {h} -cutline {i} -crop_to_cutline -multi -srcnodata "-3.40282346639e+038" \n' \
           '-dstnodata -999 {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows,
                                            h=resample_method_one, i=extent, j=in_raster, k=temp)
    call(warp)

    warp2 = 'gdalwarp -overwrite  -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -tr {f} {f} \n' \
            ' -r {g} -multi -srcnodata -999 -dstnodata -999 {h} {i}'.format(a=projection, b=x_min, c=y_min, d=x_max,
                                                                            e=y_max, f=cell_size, g=cell_size,
                                                                            h=temp, i=out_raster)
    call(warp2)

    print "Done processing {a}".format(a=out_raster)
