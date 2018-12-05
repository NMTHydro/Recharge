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
import fiona
import rasterio
from rasterio import mask
import pandas as pd
import statsmodels.api as sm
import numpy.ma as ma
# ============= local library imports ===========================

def shapefile_extract(shapefile, raster_image):
    """
    pulls out an array of a raster vs shapefile
    :param shapefile:
    :param raster_image:
    :return:
    """

    with fiona.open(shapefile) as shp:
        geometry = [feature['geometry'] for feature in shp]

    with rasterio.open(raster_image) as rast:
        image, transform = rasterio.mask.mask(rast, geometry, crop=True)
    image = image[image.mask == False]

    image = image.flatten

    print 'compressed image \n', image
    # flat_image = image.
    # print 'flat image \n', flat_image

    # return flat_image
    return image

def main(predict_raster, path_dictionary, aoi):
    """"""
    # pull in the rasters and read in as arrays use shapefile_extract()

    et_precip_ratio = shapefile_extract(aoi, predict_raster)

    p_dict = {}
    for k, v in path_dictionary.iteritems():
        p_dict[k] = shapefile_extract(aoi, v)

    print 'the p_dict \n', p_dict

    # do a linear model
    x = et_precip_ratio
    y1 = p_dict['aspect']
    y2 = p_dict['slope']
    y3 = p_dict['dem']

    model = sm.OLS(x, y1, y2, y3)
    linfit = model.fit()

    print 'summary \n', linfit.summary()

if __name__ == "__main__":

    # todo - shoud do the analysis with WGS84 original SSEBop, but for convenience we'll do the first cut with PyRANA
    #  scale and res

    # get the sseb/PRISM ratio raster
    ratio = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_prism_sseb_ratio/ct_sseb_p_ratio_2013_12_QGIS.tif'

    # get the aspect raster
    aspect = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/aspect_nm60mdem_pyrana_warp.tif'

    # get the slope raster
    slope = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/slope_nm60mdem_pyrana_warp.tif'

    # get the DEM raster
    dem = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/nm60mdem_pyrana_warp.tif'

    # get the shapefile of the AOI <-needs to be correct crs
    study_area = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/terrain_regresion_aoi.shp'

    # TODO - get the NDVI raster

    params_test = {'aspect': aspect, 'slope': slope, 'dem': dem}

    main(predict_raster=ratio, path_dictionary=params_test, aoi=study_area)