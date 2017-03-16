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
from osgeo import gdal
from numpy import array, asarray
from numpy.ma import masked_where, nomask, filled
from datetime import datetime

# ============= local library imports ===========================

import rasterio
import numpy as np
from numpy import meshgrid, arange
from affine import Affine
from pyproj import Proj, transform

fname = '/path/to/your/raster.tif'

def coord_getter(tiff_path):

    # Read raster
    with rasterio.open(tiff_path) as r:
        T0 = r.affine  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        A = r.read(1)  # pixel values

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[1]), np.arange(A.shape[0]))

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    #print "T1",T1
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * T1

    # All eastings and northings (there is probably a faster way to do this)
    northings, eastings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

    # suggested Jake Edits. Talk to him soon.
    #mesh = meshgrid(arange(cols.shape[1]), arange(rows.shape[0]))

    #print 'mesh', mesh

    #northings, eastings = [(c,r)* T1 for c, r in mesh.T]

    #northings, eastings = (p1*mesh.T).T

    #print 'northings', northings
    #print 'eastings', eastings

    # Project all longitudes, latitudes
    p2 = Proj(proj='latlong',datum='WGS84')
    longs, lats = transform(p1, p2, eastings, northings)

    return eastings, northings


if __name__ == "__main__":

    drive_path = os.path.join('/', 'Volumes', 'Seagate Expansion Drive')
    tiff_path = os.path.join(drive_path, 'ETRM_Inputs', 'statics', 'taw_mod_4_21_10_0.tif')
    coord_getter(tiff_path)
