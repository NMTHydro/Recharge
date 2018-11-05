# ===============================================================================
# Copyright 2018 gabe-parrish
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
import os
import gdal
from subprocess import call

# ============= local library imports ===========================

def clip(poly, xres, yres, input_path, output_path):
    """"""

    # polygon, xres, yres, clipped_image_path, output_image_path
    cut_command = "gdalwarp -q -cutline {} -crop_to_cutline -tr {} {} -of GTiff {} {}".format(poly, xres, yres, input_path, output_path)

    call(cut_command, shell=True)

def run():
    """This program can run through PyRANA output and clip it to an area of interest defined by a shpefile polygon"""

    # ====== User Defined Section ========

    # TODO - RENAME the drive to
    # root_path = "/Volumes/Seagate_Backup_Plus_Drive/ETRM_results"
    root_path = "/Volumes/Seagate_Expansion_Drive/NewMexico_PyRANA_reps"

    # path to the polygon to clip by
    # poly_path = "/Volumes/Seagate_Expansion_Drive/sunshine_valley/" \
    #             "fwdsvareaofinterestforrechargedata/SV_major_draianges_bounding_polygon_merged.shp"
    poly_path = "/Volumes/Seagate_Expansion_Drive/sunshine_valley/svpolygon2/SV_major_draianges_bounding_polygon_2.shp"

    # output_path = "/Volumes/Seagate_Expansion_Drive/sunshine_valley/clipped_PyRANA_outputs"
    output_path = "/Volumes/Seagate_Expansion_Drive/sunshine_valley/clipped_outputs_10_15_18"

    # PyRANA resolution
    xres = 250
    yres = 250

    # ====================================

    print "Getting Files of interest"

    walk_obj = os.walk(root_path)

    working_paths_list = []

    for path, subdir, files in walk_obj:

        print "path", path
        print subdir
        print files
        terminal_pathname = path.split("/")[-1]

        if terminal_pathname.startswith('annual_rasters'):
            print 'files', files
            print "clipping"

            working_paths_list.append(path)


            for f in files:
                filepath = os.path.join(path, f)

                chunks = filepath.split("/")

                print 'chunks', chunks

                dirname = chunks[-2]

                print 'dirname', dirname

                filename = "{}{}".format(chunks[-1].split('.')[0], '.tif')

                print 'filename', filename

                output_dir = os.path.join(output_path, dirname)

                if not os.path.isdir(output_dir):
                    os.mkdir(output_dir)

                elif os.path.isdir(output_dir):
                    # print "clipping"
                    outfile = os.path.join(output_dir, filename)

                    clip(poly_path, xres, yres, filepath, outfile)

    # print 'walked dictionary', walk_dict

if __name__ == "__main__":

    run()