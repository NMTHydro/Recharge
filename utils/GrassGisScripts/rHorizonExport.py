import grass.script as grass
import grass.script.setup as gsetup
import datetime
import os, fnmatch
from dateutil import rrule

# ~~~~~~~~~~ USER DEFINED SECTION ~~~~~~~~~~
# path to your rsun generated radiation files within your GRASS GIS working folder
search = '/Users/dcadol/Desktop/academic_docs_II/pyMETRIC_GRASS/sky_angles/PERMANENT/cell'
# path where you want to output the extracted radiation .tiff files
path2 = '/Users/dcadol/Desktop/academic_docs_II/pyMETRIC_GRASS/horizon_angles_extract'
dest = path2

prefix = 'espanola_horizon_'

start_degree = 0.0
end_degree = 360.0
degree_step = 15.0

# ====== The remainder of the Script is automatic ======

steps = (int(end_degree) - int(start_degree)) / int(degree_step)

print 'steps', steps

for i in range(steps):
    angle = int(i * degree_step)

    grass_file = "{}_{:03}.tif".format(prefix, angle)
    print 'grass file: ', grass_file

    out = dest + '/' + grass_file
    inRaster = grass_file
    print 'out ', out
    grass.run_command('r.out.gdal', overwrite=True, flags="c", input=inRaster, output=out, nodata="-999",
                      format='GTiff', type='Float32')


# # ====== Peter's old export script here =====
# for day in rrule.rrule(rrule.DAILY, dtstart=startday, until=endday):
#     strdoy = int(day.strftime('%j'))
#     day3 = '%03d' % strdoy
#
#     grass_file = 'Rbflat_' + day3
#     dates = 'Rbflat' + '_' + day.strftime('%j') + '.tif'
#
#     inRaster = grass_file
#     # convert file to str to add destination, file extension
#     out = dest + '/' + dates
#     grass.run_command('r.out.gdal', overwrite=True, flags="c", input=inRaster, output=out, nodata="-999",
#                       format='GTiff', type='Float32')