import os
import fnmatch
import gdal
from subprocess import call


paths = ['F:\PRISM\Temp\Minimum']
path2s = ['F:\PRISM\Temp\Minimum_standard']
for path, path2 in zip(paths, path2s):
    print path, path2
# folders = [d for d in os.listdir('F:\PRISM\Precip\800m_revised') if os.path.isdir(os.path.join('F:\PRISM\Precip\800m_revised', d))]
    folders = [str(x) for x in range(2000, 2014)]
    for yr in folders:
        print yr
        input_folder = '{a}\\{b}'.format(a=path, b=yr)
        print input_folder
        if not os.path.exists('{a}\\{b}_std'.format(a=path2, b=yr)):
            os.makedirs('{a}\\{b}_std'.format(a=path2, b=yr))
            print 'Making new folder'
        output_folder = '{a}\\{b}_std'.format(a=path2, b=yr)
        extent = 'E:\\Reference_shape\\NM_poly500mbuf\\NM_poly500mbuf.shp'

        os.chdir(input_folder)

        def findRasters(path, filter):
            for root, dirs, files in os.walk(path):
                for file in fnmatch.filter(files, filter):
                    yield file

        for raster in findRasters(input_folder, '*.tif'):
            print raster
            (FOLDER, rastname)= os.path.split(raster)

            inRaster = input_folder + '\\' + rastname

            outRaster = output_folder + '\\' + rastname
            warp = 'gdalwarp -overwrite -s_srs EPSG:26913 -t_srs  EPSG:26913 -r "cubic" -cutline %s -crop_to_cutline -multi  -tr 250 250 -srcnodata "-3.40282346639e+038" -dstnodata -999 %s %s' % (extent, inRaster, outRaster)
            call(warp)
