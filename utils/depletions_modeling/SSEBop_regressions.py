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
from matplotlib import pyplot as plt
import numpy as np
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

    print 'transform', transform
    print 'shape', image.shape
    # plt.imshow(image[0])
    # plt.show()
    return image[0]

def main(predict_raster, path_dictionary, aoi):
    """"""
    # pull in the rasters and read in as arrays use shapefile_extract()

    et_precip_ratio = shapefile_extract(aoi, predict_raster)
    # et_precip_ratio = et_precip_ratio[et_precip_ratio > -3000000000000]
    et_precip_ratio = et_precip_ratio[3:-3, 3:-3]
    et_precip_ratio = et_precip_ratio.flatten()

    target = pd.DataFrame({'et_precip_ratio': et_precip_ratio})

    p_dict = {}
    for k, v in path_dictionary.iteritems():
        clipped = shapefile_extract(aoi, v)
        # get rid of nulls
        # clipped = clipped[clipped > -3000000000000]
        clipped = clipped[3:-3, 3:-3]
        clipped = clipped.flatten()
        p_dict[k] = clipped

    p_frame = pd.DataFrame.from_dict(p_dict)
    # print 'the p_dict \n', p_dict
    print 'et_precip ratio not list \n', et_precip_ratio
    # print 'et_precip ratio \n', et_precip_ratio
    print 'length', len(et_precip_ratio)

    # do a linear model
    # y = et_precip_ratio
    # x1 = p_dict['aspect']
    # x2 = p_dict['slope']
    # # x3 = p_dict['dem']

    X = p_frame[['aspect', 'slope']]
    print 'xshape', X.shape
    # X = sm.add_constant(X)
    Y = target['et_precip_ratio']
    print 'yshape', Y.shape

    # ==== multiple ====
    print '\n\n ========= \n Multiple \n ========= \n \n '

    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    print 'summary \n', model.summary()

    # ==== aspect single ====
    print '\n\n ========= \n aspect \n ========= \n \n '
    aspect_x = p_frame['aspect']

    plt.scatter(aspect_x, Y)
    plt.show()

    aspect_x = sm.add_constant(aspect_x)
    aspect_model = sm.OLS(Y, aspect_x).fit()
    print aspect_model.summary()
    print aspect_x.shape, Y.shape



    # ==== slope single ====
    print '\n\n ========= \n slope \n ========= \n \n '


    slope_x = p_frame['slope']

    plt.scatter(slope_x, Y)
    plt.show()

    slope_x = sm.add_constant(slope_x)
    slope_model = sm.OLS(Y, slope_x).fit()
    print slope_model.summary()



    # ==== eta single ====
    print '\n\n ========= \n eta \n ========= \n \n '
    eta_x = p_frame['eta']

    plt.scatter(eta_x, Y)
    plt.show()

    eta_x = sm.add_constant(eta_x)
    eta_model = sm.OLS(Y, eta_x).fit()
    print eta_model.summary()

    # ==== DEM single ====
    print '\n\n ========= \n DEM \n ========= \n \n '
    dem_x = p_frame['dem']

    plt.scatter(dem_x, Y)
    plt.show()

    dem_x = sm.add_constant(dem_x)
    dem_model = sm.OLS(Y, dem_x).fit()
    print eta_model.summary()



    plt.scatter(p_frame['eta'], p_frame['eta2'])
    plt.show()



if __name__ == "__main__":

    # todo - shoud do the analysis with WGS84 original SSEBop, but for convenience we'll do the first cut with PyRANA
    #  scale and res

    # get the sseb/PRISM ratio raster
    # ratio = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_prism_sseb_ratio/ct_sseb_p_ratio_2013_12_QGIS.tif'
    ratio = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/cumulative_SSEB/ct_ssebop_2013_12.tif'

    # get the aspect raster
    aspect = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/aspect_nm60mdem_pyrana_warp.tif'

    # get the slope raster
    slope = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/slope_nm60mdem_pyrana_warp.tif'

    # get the DEM raster
    dem = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/nm60mdem_pyrana_warp.tif'

    # throw eta in there to test the algorithm
    eta = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/NDVI/NDVI_std_all/2000_207.tif'

    eta2 = '/Volumes/Seagate_Expansion_Drive/ETRM_inputs/NDVI/NDVI_std_all/2000_207.tif'

    # get the shapefile of the AOI <-needs to be correct crs
    study_area = '/Volumes/Seagate_Expansion_Drive/SSEBop_research/terrain/terrain_regresion_aoi.shp'

    # TODO - get the NDVI raster

    params_test = {'aspect': aspect, 'slope': slope, 'eta': eta, 'eta2': eta2, 'dem': dem} #'dem': dem

    main(predict_raster=ratio, path_dictionary=params_test, aoi=study_area)