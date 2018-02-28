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
import os

# ============= local library imports ===========================

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
import os
# import gdal
import ogr
from osgeo.ogr import *
# ============= local library imports ===========================

# # some methods in modules don't rely on a pre-existing object - just on the module itself
# """
# gp = arcgisscripting.create()
# driver  = ogr.GetDriverByName('ESRI Shapefile')
# """
# # some methods rely on pre-existing objects...
# """
# dsc = gp.Describe('landcover')
# ds = driver.Open('path')
# """
#
#
#

def notes_part_1():

    # A driver is an object that knows how to interact with a cetain data type...
    # you might as well grab the driver for reading so its ready to go for writing
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # open metnod Open(<filename>, <update>) retruns a DataSource object.
    # <update> = 1 for writeable, 0 for read only.

    path = "/Users/Gabe/Desktop/gdal_slides/hw_1/ospy_data1"

    # change the path to the working directory
    os.chdir(path)

    datasource = driver.Open('sites.shp', 0) # read only
    if datasource is None:
        print "could not open" + path
        sys.exit(1) #what is sys btw? <- exits w/ error code

    # ==== Opening a layer (shapefile) ====

    # the <index> is always zero and optional for shapefiles
    # the <index> is useful for GML, TIGER and other data types...What are those???

    layer = datasource.GetLayer()
    #or
    layer = datasource.GetLayer(0)

    # ===== Get info about the Layer =====

    # number of features in the layer:
    num_features = layer.GetFeatureCount()
    print "Feature count {}".format(num_features)

    # get the extent as a tuple
    extent = layer.GetExtent()
    print "Extent {}".format(extent)
    print "uppper left {}".format(extent[0], extent[3])
    print "upper right {}".format(extent[1], extent[2]) # kida werd its 0,3 and 1,2 but whatever

    # ==== Getting Features ====

    # if you know FID (offset) you can use GetFeature(<index>) on the layer
    feature = layer.GetFeature(0)

    # you can loop through all the features with GetNextFeature()

    feature = layer.GetNextFeature()
    while feature:
        feature = layer.GetNextFeature()
    layer.ResetReading() # you need this to loop again...

    # ==== Getting feature attributes ====

    # feature object has GetField(<name>) method that returns the value of the attribute field

    # e.g.
    # a few variations exist - GetFieldAsString(<name>) and - GetFieldAsInterger(<name>)
    id = feature.GetField('id')
    id = feature.GetFieldAsString('id')

    # ===== Getting a Feature's Geometry =====

    # Geature objects have a method called GetGeometryRef() which returns a Geometry object
    # geomotry objects can be point, polygon, line etc
    # point objects have GetX() GetY() methods

    geometry = feature.GetGeometryRef()
    x = geometry.GetX()
    y = geometry.GetY()

    print "geometry {}"
    print " geometry x {}"
    print " geometry y {}"

    # ===== DESTRUCTION (Destroying Objects) ======

    # for memory management we must destroy the features and the DataSource Objects when we're done with them.

    feature.Destroy()
    datasource.Destroy()


def feature_count():
    """

    :return:
    """

    driver = ogr.GetDriverByName('ESRI Shapefile')

    filepath = "/Users/Gabe/Desktop/gdal_slides/hw_1/ospy_data1"

    os.chdir(filepath)

    # use driver to get a datasource object
    # use 0 for read only.
    datasource = driver.Open("sites.shp", 0)

    layer = datasource.GetLayer()

    print "Here's the layer {}".format(layer)

    print "Now we're going to print out the id, x and y coords for each point"

    # How many features are there anyway?

    num = layer.GetFeatureCount()

    print "There are {} features in the layer".format(num)

    feature = layer.GetFeature(0)
    # feature = layer.GetNextFeature()
    count = 0
    while feature:
        feature = layer.GetNextFeature()

        if feature is None:
            print "blank feature"

        else:

            count += 1

            print "count", count

            print "Heres the feature {}".format(feature)

        # for each feature print id, x and y coords


            id = feature.GetField('id')

            print "id -> {}".format(id)

            # geometry obj

            geometry = feature.GetGeometryRef()

            x = geometry.GetX()
            y = geometry.GetY()

            print "Here is x -> {}, here is y -> {}".format(x, y)

            cover = feature.GetFieldAsString('cover')

            print "Cover -> {}".format(cover)

if __name__ == "__main__":
    feature_count()