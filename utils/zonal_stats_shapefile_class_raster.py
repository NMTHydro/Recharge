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
import ogr, gdal, osr
import numpy as np
import pandas as pd
import glob

# ============= local library imports ===========================


def raster_sieve(masking_arr, target_masked_arr, iterator):

    masking_arr[masking_arr != iterator] = 0
    masking_arr[masking_arr == 1] = 1

    objective_arr = target_masked_arr * masking_arr

    print "good values", objective_arr

    print "mean of sieved values", objective_arr.mean()

    print "new mean of the changed masking_arr", masking_arr.mean()

    return objective_arr


def main():
    """"""

    # === Paths to shapefile, classified raster and target raster data set ===

    # todo - Get this all as form-based application

    root = '/Users/Gabe/Desktop/wrri_stuff/NM_raster_zonal_stats'

    shapefile_path = os.path.join(root, 'test_polygon_file/test_polygon.shp')
    shapefile_name = 'test_polygon'

    class_raster = os.path.join(root, 'classified_raster/1985_mc_uniquevals_colors_final_9_nad83_13n.tif')

    rasters_path = os.path.join(root, 'rasters')

    output_path = os.path.join(root, 'output_tables')

    # what string do all the raster files have in common?
    search_string = 'water_fraction'

    # TODO - take this main() function and divvy it up so that tasks are compartmentalized....
    # reading in the geotransform should be a separate function...
    # getting offsets should be a separate function.
    # need to rename the 'data' rasters and distinguish better from the class rasters...

    # mainly, add a feature where you can just do a shapefile, just do a class raster or both. But this is a good start.

    # === First let's just read in the class raster based on the path...

    # the raster
    ras_datasource = gdal.Open(class_raster)

    # the vector
    shape_datasource = ogr.Open(shapefile_path)
    layer_obj = shape_datasource.GetLayer()

    # get number of features in the layer
    num_features = layer_obj.GetFeatureCount()

    # ====== iterate through features =========

    for i in range(num_features):

        feature = layer_obj.GetFeature(i)
        print "feature id {}".format(feature.GetField('id'))

        # this name is used for the naming convention of the output tables...
        feature_name = 'polygonid{}'.format(feature.GetField('id'))


        # take the feature and read in it's extent
        geom = feature.GetGeometryRef()

        # get the ring, which contains the nodes...
        ring = geom.GetGeometryRef(0)

        # how many points in the ring?
        number_points = ring.GetPointCount()
        x_points = []
        y_points = []
        for i in range(number_points):
            x, y, z = ring.GetPoint(i)
            x_points.append(x)
            y_points.append(y)

        # now you have the x's and y's of the nodes, you'll need the max and min extents of each
        xmin = min(x_points)
        xmax = max(x_points)
        ymin = min(y_points)
        ymax = max(y_points)

        # get the pixel widths from the raster (and other shape info)
        geotrans = ras_datasource.GetGeoTransform()
        # This pattern makes no sense by the way but it seems to be correct.
        xorigin = geotrans[0]
        yorigin = geotrans[3]
        pix_w = geotrans[1]
        pix_h = geotrans[5]
        print 'pix_h', pix_h

        # get the offsets -> you should figure out what the offset is and why it's calculated this way...
        x_off = int((xmin - xorigin)/pix_w)
        y_off = int((yorigin - ymax)/pix_w)

        # get the counts
        x_count = int((xmax - xmin) / pix_w) + 1 # add 1 bc index starts at zero, perhaps?
        y_count = int((ymax - ymin) / pix_w) + 1

        # create memory target raster -> What's a memory raster?
        # The target dataset is an empty shell that we burn the vector onto when we rasterize
        print "test xcxc", x_count, y_count
        target_ds = gdal.GetDriverByName('MEM').Create('', x_count, y_count, 1, gdal.GDT_Byte) # why not float 32?

        print 'target_ds', target_ds

        target_ds.SetGeoTransform((xmin, pix_w, 0, ymax, 0, pix_h, )) # why the blank space?!?!?!?

        # the target raster needs the same projection as the original raster
        raster_srs = osr.SpatialReference()
        raster_srs.ImportFromWkt(ras_datasource.GetProjectionRef())
        target_ds.SetProjection(raster_srs.ExportToWkt())

        # Rasterize the polygon to a raster
        gdal.RasterizeLayer(target_ds, [1], layer_obj, burn_values=[1])

        # read raster as arrays
        bandraster = ras_datasource.GetRasterBand(1)
        # when you read it as an array, you read it in starting with the offests from your shapefile
        data_raster = bandraster.ReadAsArray(x_off, y_off, x_count, y_count).astype(np.float)

        bandmask = target_ds.GetRasterBand(1)
        # For the mask, since we made it with the counts, we use those for reading, and we have zero x and y offset.
        data_mask = bandmask.ReadAsArray(0, 0, x_count, y_count).astype(np.float)

        # mask the raster with numpy
        masked_raster_arr = np.ma.masked_array(data_raster, np.logical_not(data_mask))
        # print "first masked arr", masked_raster_arr
        print "mean same ol", np.mean(masked_raster_arr)

        # make this batch-file capable for a rasters path with many rasters....
        # try to use glob to get the job done here....

        for raster_path_string in glob.glob('{}/*{}.img'.format(rasters_path, search_string)):

            print 'raster path string', raster_path_string

            filename = raster_path_string.split('/')[-1]
            raster_name = filename.split('_')[0]

        # now you've clipped the class raster, do the same with the primary dataset!

            ras_datasource_primary = gdal.Open(raster_path_string)

            # get the geotransform
            geo_prime = ras_datasource_primary.GetGeoTransform()
            x_origin_prime = geo_prime[0]
            y_origin_prime = geo_prime[3]
            pix_w_prime = geo_prime[1]
            pix_h_prime = geo_prime[5]

            # new offsets
            x_off_prime = int((xmin - x_origin_prime) / pix_w_prime)
            y_off_prime = int((y_origin_prime - ymax) / pix_w_prime)

            # # get the counts
            # x_count = int((xmax - xmin) / pix_w_prime) + 1  # add 1 bc index starts at zero, perhaps?
            # y_count = int((ymax - ymin) / pix_w_prime) + 1


            # read in prime raster with the correct offsets

            bandrasterprime = ras_datasource_primary.GetRasterBand(1)
            data_raster_prime = bandrasterprime.ReadAsArray(x_off_prime, y_off_prime, x_count, y_count).astype(np.float)

            # print "raster array", data_raster_prime
            # print "the regular raster mean", np.mean(data_raster_prime)

            masked_raster_arr_prime = np.ma.masked_array(data_raster_prime, np.logical_not(data_mask))
            # print 'masked arr raster', masked_raster_arr_prime
            print "mean", np.mean(masked_raster_arr_prime)

            # you've got two masked arrays, time to iterate through the class one
            # need to ravel(), set to list, take the set of the list, and iterate through set.
            rav_arr = masked_raster_arr.ravel()
            list_arr = rav_arr.tolist()
            set_arr = set(list_arr)

            print "set, finally -> {}".format(set_arr)

            print "how does this look \n {}".format(masked_raster_arr)
            print "same ol mean?", masked_raster_arr.mean()

            # so we don't mess up our good array as we iterate and change values in-place
            masked_raster_arr

            # so to output the stats to a table, a good way to do it would be a dictionary
            ids = []
            headers = ['mean', 'standard_deviation', 'minimum', 'maximum', 'range', 'variance']
            shape_class_stats = {}
            for i in set_arr:

                class_stats = {'mean': [], 'standard_deviation': [], 'minimum': [], 'maximum': [], 'range': [],
                                     'variance': []}

                if i != None:

                    print "now we'll take care of this class {}".format(i)
                    # keep track of the order you process the classes.
                    ids.append(i)

                    # do this to not mess up the masked_raster_arr by modifying it in-place in the function.
                    mra = np.copy(masked_raster_arr)

                    class_filtered_array = raster_sieve(mra, masked_raster_arr_prime, iterator=i)

                    # use the class filtered array to add statistics do the dictionary


                    # class_stats['mean'] = class_filtered_array.mean()
                    # class_stats['standard deviation'] = class_filtered_array.std()
                    # maximum = class_filtered_array.max()
                    # minimum = class_filtered_array.min()
                    # class_stats['minimum'] = class_filtered_array.min()
                    # class_stats['maximum'] = class_filtered_array.max()
                    # class_stats['range'] = maximum - minimum
                    # class_stats['variance'] = class_filtered_array.var()

                    class_stats['mean'].append(class_filtered_array.mean())
                    class_stats['standard_deviation'].append(class_filtered_array.std())
                    maximum = class_filtered_array.max()
                    minimum = class_filtered_array.min()
                    class_stats['minimum'].append(class_filtered_array.min())
                    class_stats['maximum'].append(class_filtered_array.max())
                    class_stats['range'].append(maximum-minimum)
                    class_stats['variance'].append(class_filtered_array.var())


                    # mean = class_filtered_array.mean()
                    # std_dev = class_filtered_array.std()
                    # minimum = class_filtered_array.min()
                    # maximum = class_filtered_array.max()
                    # range = maximum - minimum
                    # # median = class_filtered_array
                    # variance = class_filtered_array.var()



                    # make a dictionary with the statistics.
                    # #todo - re evaluate this later...
                    # class_stats = {'class label': 'class_{}'.format(i), 'mean': mean,
                    #                      'standard deviation': std_dev, 'minimum': minimum, 'maximum': maximum,
                    #                      'range': range, 'variance': variance}


                else:
                    pass

                if i != None:
                    shape_class_stats['{}'.format(i)] = class_stats

                # todo - let's try some test outputs to figure out how to format the table that will be output for each feature

                print shape_class_stats

                # cols = pd.MultiIndex.from_product([headers, ids])
                #
                # cols = headers + ids
                # print 'cols', cols

                # pandas wants (inner key, outer key) : [data] in order to format the dataframe correctly.
                #shape_class_stats_format = {('{}'.format(outer_key), inner_key) : lst for outer_key, nested_dictionary in shape_class_stats.iteritems() for inner_key, lst in nested_dictionary.iteritems() }

                shape_class_stats_format = {}
                for key in ids:
                    nested_dict = shape_class_stats['{}'.format(key)]

                    for nest_key in headers:

                        lst = nested_dict['{}'.format(nest_key)]

                        shape_class_stats_format[('{}'.format(key), '{}'.format(nest_key))] = lst


            print "reformatted nested dictionary \n {}".format(shape_class_stats_format)


            df = pd.DataFrame(shape_class_stats_format)

            # tODO - see the stack overflow article on how to solve this one...

            table_output = os.path.join(output_path, 'shape_{}_{}_imageidentifier_{}.csv'.format(shapefile_name, feature_name, raster_name))

            df.to_csv(table_output)

            print "let's see that df!\n ", df


if __name__ == "__main__":
    main()

    # ======== EOF ==============\n