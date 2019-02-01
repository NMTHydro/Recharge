import os
import gdal
from subprocess import call
import yaml


def warpfunc(files, path, geo_info, proc_out):

    with open(geo_info, mode='r') as geofile:
        geo_dict = yaml.load(geofile)

    dim = geo_dict['dimensions']
    geotrans = geo_dict['geotransform']
    print 'dim', dim

    print 'geo', geotrans

    # get the tiff file from the files list, i don't think we need the world file
    f_name = files[1]
    in_raster = os.path.join(path, f_name)

    out_raster = os.path.join(proc_out, f_name)

    # todo - dont hardcode
    orig_projection = '32613'
    projection = '26913'

    # projection = geo_dict['projection']

    cols = dim[0]
    rows = dim[1]

    rastsize = geotrans[1]

    x_min = geotrans[0]
    x_max = x_min + (cols * rastsize)
    y_max = geotrans[3]
    y_min = y_max - (rows * rastsize)

    resample_method = 'near'

    # print x_min, x_max, y_min, y_max

    warp = 'gdalwarp -overwrite -s_srs EPSG:{aa} -t_srs EPSG:{a} -te {b} {c} {d} {e} -ts {f} {g} -r {h} -multi' \
           ' -srcnodata "-3.40282346639e+038" -dstnodata -999 {j} {k}'.format(aa=orig_projection, a=projection, b=x_min, c=y_min, d=x_max,
                                                                              e=y_max, f=cols, g=rows,
                                                                              h=resample_method, j=in_raster,
                                                                              k=out_raster)
    warp = 'gdalwarp -overwrite -s_srs EPSG:32613 -t_srs EPSG:26913 -r near ' \
           '-te 568257.0000000000000000 3942663.0000000000000000 573507.0000000000000000 3945913.0000000000000000 ' \
           '-ts 21 13 -of GTiff {} {}'.format(in_raster, out_raster)
    print "WARP {}".format(warp)
    call(warp, shell=True)

def geowarp_to_aoi(eeflux_root, cal_var, geo_info, proc_out):
    """"""
    if cal_var == 'rzsm':
        cal_var = 'ETrF'

    for p, dirs, files in os.walk(eeflux_root, topdown=True):

        # print 'paths \n', p
        # print 'dirs \n', dirs
        # print 'files', files

        if p.endswith(cal_var):
            print 'files', files

            warpfunc(files, p, geo_info, proc_out)

def main(eeflux_root, cal_var, geo_info, proc_out):
    """"""

    # todo - warp and clip images to geo_info mask extent

    geowarp_to_aoi(eeflux_root, cal_var, geo_info, proc_out)


if __name__ == "__main__":

    eeflux_root = '/Volumes/Seagate_Expansion_Drive/METRIC_observations/NE_NM'

    # Which value do you want to do the calibration on? OPTIONS 'ETrF', 'ETa' or 'rzsm'
    cal_variable = 'ETa'

    # we're going to get all of the available dates of either ETrF, ETa or (rzsm processed separately from ETrF) and
    # warp them to the domain of the study area

    # === Study Area Specs ===
    # File is created by the create_geo_info.py script referencing the mask used for the AOI in the ETRM grid search.
    geo_info = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/geo_info.yml'

    # processing output
    proc_out = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/metric_obs_processed'

    main(eeflux_root, cal_variable, geo_info, proc_out)