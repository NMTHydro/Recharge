import os
from subprocess import call
import gdal

def warp_jpl(jpl_filepath, etrm_geo, output_path):
    """"""
    # change

    jpl_filename = jpl_filepath.split('/')[-1]
    jpl_name = jpl_filename[:-4]
    # print 'jpl name', jpl_name
    jpl_outname = '{}_etrm.tif'.format(jpl_name)

    out_loc = os.path.join(output_path, jpl_outname)
    print 'out loc', out_loc

    (xmin, ymin, xmax, ymax, cols, rows, t_srs, resample_method) = etrm_geo


    warp = '/Users/dcadol/.conda/envs/Recharge/bin/gdalwarp -overwrite -t_srs {tsrs} -r {resample} -te {xmin} {ymin} {xmax} {ymax} -ts {cols} {rows} -of GTiff {current_file} {output_file}'.format(tsrs=t_srs, resample=resample_method, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, cols=cols, rows=rows, current_file=jpl_filepath, output_file=out_loc)

    call(warp, shell=True)


def run(jpl_rootpath, etrm_geo, output_path):
    """"""

    for path, dirs, files in os.walk(jpl_rootpath, topdown=False):
        # print 'paths', paths
        # print 'dirs', dirs
        # print 'files', files
        for file in files:
            jpl_fp = os.path.join(path, file)
            if jpl_fp.endswith('.tif'):
                print 'jpl fp', jpl_fp
                warp_jpl(jpl_fp, etrm_geo, output_path)

if __name__ == "__main__":

    # === ETRM geographic inputs ===

    xmin = 114757.0000000000000000
    ymin = 3471163.0000000000000000
    xmax = 682757.0000000000000000
    ymax = 4102413.0000000000000000

    cols = 2272
    rows = 2525

    t_srs = 'EPSG:26913'

    resample_method = 'near'

    etrm_geo = (xmin, ymin, xmax, ymax, cols, rows, t_srs, resample_method)

    # === PATHS ====

    output_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/jpl_etrm_warp_PT'

    jpl_rootpath = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/PT'



    run(jpl_rootpath, etrm_geo, output_path)