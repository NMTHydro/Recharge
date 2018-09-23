import os, fnmatch
import gdal
from subprocess import call

input_folder = '/Volumes/SeagateExpansionDrive/ETRM_inputs/PM_RAD/PM2013' # C:\Recharge_GIS\land_use_land_cover /PM2000
output_folder = '/Volumes/SeagateExpansionDrive/ETRM_inputs/new_inputs/PM_RAD/PM2013' # C:\Recharge_GIS\OSG_Data
extent ='/Users/Gabe/Desktop/33_37_ETRM_aoi_project/created_layers/big_aoi_nad83_z13n.shp' #'/Users/Gabe/Desktop/33_37_ETRM_aoi_project/created_layers/p033r037_7dt20010613_z13_30_nad83z13_nn_crop_nad83.tif' # F:\\Reference_shape\\NM_poly500mbuf\\NM_poly500mbuf.shp

os.chdir(input_folder)

# metadata of Landsat file.
projection = 26913  # NAD83 UTM Zone 13 North
x_min = 279225  #114757
y_min = 3585165 # 3471163
x_max = 435225 # 682757
y_max = 3705165 #4102413
cols = 5200 # 2272
rows = 4000 # 2525
resample_method_one = 'cubic'
resample_method_two = 'mode'
cell_size = 30 #250


def find_rasters(path, filter_):
    for root, dirs, files in os.walk(path):
        for file_ in fnmatch.filter(files, filter_):
            print "here's your files -> ", file_
            yield file_
            print "file yielded"

for raster in find_rasters(input_folder, '*.tif'):
    FOLDER, raster_name = os.path.split(raster)

    print "folder", FOLDER

    print "raster name", raster_name


    in_raster = os.path.join(input_folder, raster_name)
    print "in raster", in_raster
    temp = os.path.join(output_folder, 'temp.tif')
    out_raster = os.path.join(output_folder, raster_name)
    print "out raster", out_raster

    #warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g} -r {h} -cutline {i} -crop_to_cutline -multi -srcnodata "-3.40282346639e+038" -dstnodata -999 {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows, h=resample_method_one, i=extent, j=in_raster, k=out_raster) # k = temp
    warp = 'gdalwarp -overwrite -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g} -r {h} -multi -srcnodata "-3.40282346639e+038" -dstnodata -999 {j} {k}'.format(a=projection, b=x_min, c=y_min, d=x_max, e=y_max, f=cols, g=rows, h=resample_method_one, j=in_raster, k=out_raster) # k = temp

    print "WARP ({})".format(warp)

    call(warp, shell=True)

    # warp2 = 'gdalwarp -overwrite  -s_srs EPSG:{a} -t_srs EPSG:{a} -te {b} {c} {d} {e} -tr {f} {f} \n' \
    #         ' -r {g} -multi -srcnodata -999 -dstnodata -999 {h} {i}'.format(a=projection, b=x_min, c=y_min, d=x_max,
    #                                                                         e=y_max, f=cell_size, g=cell_size,
    #                                                                         h=temp, i=out_raster)
    # call(warp2)

    print "Done processing {}".format(out_raster) # a = out_raster
