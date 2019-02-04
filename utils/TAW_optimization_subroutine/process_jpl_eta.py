import os
from subprocess import call
import gdal

def warp_jpl():
    """"""

    warp = 'gdalwarp -overwrite -t_srs EPSG:26913 -r near ' \
           '-te 114757.0000000000000000 3471163.0000000000000000 682757.0000000000000000 4102413.0000000000000000' \
           ' -ts 2272 2525 ' \
           '-of GTiff /Users/dcadol/Desktop/academic_docs_II/JPL_Data/PT/PT-JPL/ET_daily_kg/2002.01.22.PTJPL.ET_daily_kg.MODISsin1km.tif ' \
           '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach/JPL_warp_test/jpl_warp_test.tif'

    pass

def run():
    """"""

if __name__ == "__main__":

    # ETRM geographic inputs

    xmin = 114757.0000000000000000
    ymin = 3471163.0000000000000000
    xmax = 682757.0000000000000000
    ymax = 4102413.0000000000000000

    cols = 2272
    rows = 2525

    t_srs = 'EPSG:26913'

    resample_method = 'near'

    etrm_geo = (xmin, ymin, xmax, ymax, cols, rows, t_srs, resample_method)

    output_path = '/Users/dcadol/Desktop/academic_docs_II/JPL_Data/JPL_calibration_approach'




    jpl_rootpath = ''



    run()