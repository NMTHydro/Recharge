import gdal
import os
from osgeo import ogr, gdal
import sys
from datetime import datetime
from datetime import date, timedelta
import pandas as pd
from matplotlib import pyplot as plt
"""
SCRIPT TO TEST ASSUMPTION of INITIAL CONDITIONS
"""

def x_y_extract(point_path):
    """"""
    # get an appropriate driver
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # open the shapefile. Use 0 for read-only mode.
    datasource_obj = driver.Open(point_path, 0)
    if datasource_obj is None:
        print "cannot open {}".format(point_path)
        sys.exit(1)

    # get the layer object from the datasource
    layer_obj = datasource_obj.GetLayer()

    # get the features in the layer
    feature_count = layer_obj.GetFeatureCount()

    print "there are {} features".format(feature_count)

    # # get the feature of the shapefile. You can loop through features, but there should only be one.
    # feature = layer_obj.GetFeature(2)

    feature_dict = {}
    for i in range(1, feature_count+1, 1):

        feature = layer_obj.GetNextFeature()

        # you could get a features 'fields' like feature.GetField('id')
        field = feature.GetField('id')

        print "field -> {}".format(field)

        # but we just want the geometry of the feature
        geometry = feature.GetGeometryRef()

        # get the x and y
        x = geometry.GetX()
        y = geometry.GetY()

        print "x -> {}, y -> {}".format(x, y)

        feature_dict[field] = (x, y)

        # housekeeping
        feature.Destroy()  # always destroy the feature before the datasource

    # housekeeping
    datasource_obj.Destroy()

    return feature_dict


def raster_extract(raster_path, x, y):
    """

    :param raster_path:
    :param x:
    :param y:
    :return:
    """

    # don't forget to register
    gdal.AllRegister()

    # open the raster datasource
    datasource_obj = gdal.Open(raster_path)
    if datasource_obj is None:
        print "Can't open the datasource from {}".format(raster_path)

        # Here we make a modification, if there is missing data for any reason, just skip and sub in zeroes....
        return 0, False

    # get the size of image (for reading)
    rows = datasource_obj.RasterYSize
    cols = datasource_obj.RasterXSize

    # get georefference info to eventually calculate the offset:
    transform = datasource_obj.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    width_of_pixel = transform[1]
    height_of_pixel = transform[5]

    # read in a band (only one band)
    band = datasource_obj.GetRasterBand(1)
    # ReadAsArray(xoffset, yoffset, xcount, ycount)
    data = band.ReadAsArray(0, 0, cols, rows)



    # get the offsets so you can read the data from the correct position in the array.
    x_offset = int((x - xOrigin) / width_of_pixel)
    y_offset = int((y-yOrigin) / height_of_pixel)

    # is this a [rows, columns] thing?
    value = data[y_offset, x_offset]

    # print "VALUE {}".format(value)

    # # housekeeping
    # datasource_obj.Destroy()

    return value, True

# SWHC in mm
bigtaw = 600
littletaw = 150

# ====== Vcm ======

# extracted PRISM from a wet place

# extracted ET from a wet place

# ======= Seg =======

# extracted ET from a dry place

# extracted Precip from a dry place


def depletion_extract(raster_path, start_date, end_date, filename_key, shape_path, ):

    date_list = []
    file_lst = []
    d = (end_date - start_date)

    for i in range(d.days + 1):
        current_date = start_date
        current_date += timedelta(days=i)
        filename =filename_key.format(current_date.year, current_date.month, current_date.day)
        # print i
        # print filename
        filepath = os.path.join(raster_path, filename)
        file_lst.append(filepath)

        # populate the timeseries here
        date_list.append(date(int(current_date.year), int(current_date.month), int(current_date.day)))

    print 'depletions list', file_lst
    print 'date list', date_list

    # open the shapefile and start extracting

    feature_dictionary = x_y_extract(shape_path)

    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

    # there is only one shapefile so now go and get values for each date within the loop
    vals = []
    missing_vals = []
    for f in file_lst:
        dep_val, t_f = raster_extract(f, x, y)
        vals.append(dep_val)

        # append true or false to missing vals list. True if val present. False if val missing.
        missing_vals.append(t_f)

    # filter out missing values from dep_vals and date_list
    vals_clean = []
    date_list_clean = []
    for dep, dt, bul in zip(vals, date_list, missing_vals):
        if bul:
            # if true, there was a value
            vals_clean.append(dep)
            date_list_clean.append(dt)

    return vals_clean, date_list_clean

def run_time_series_analyst(depletions_path, start_date, end_date, front_matter, shape_path, site_name = ''):


    depletions_lst = []
    date_list = []

    # construct the paths to the files in order
    d = (end_date - start_date)

    for i in range(d.days + 1):
        current_date = start_date
        current_date += timedelta(days=i)
        filename = '{}{}_{}_{}.tif'.format(front_matter, current_date.year, current_date.month, current_date.day)
        # print i
        # print filename
        filepath = os.path.join(depletions_path, filename)
        depletions_lst.append(filepath)

        # populate the timeseries here
        date_list.append(date(int(current_date.year), int(current_date.month), int(current_date.day)))

    print 'depletions list', depletions_lst
    print 'date list', date_list

    # open the shapefile and start extracting

    feature_dictionary = x_y_extract(shape_path)

    for feature, tup in feature_dictionary.iteritems():
        # Get the X and Y coords from the dictionary and unpack them
        x, y = tup
        print x, y

    # there is only one shapefile so now go and get values for each date within the loop
    dep_vals = []
    missing_vals = []
    for f in depletions_lst:
        dep_val, t_f = raster_extract(f, x, y)
        dep_vals.append(dep_val)

        # append true or false to missing vals list. True if val present. False if val missing.
        missing_vals.append(t_f)


    # filter out missing values from dep_vals and date_list
    dep_vals_clean = []
    date_list_clean = []
    for dep, dt, bul in zip(dep_vals, date_list, missing_vals):
        if bul:
            # if true, there was a value
            dep_vals_clean.append(dep)
            date_list_clean.append(dt)


    plt.plot(date_list_clean, dep_vals_clean, label='depletions in mm')

    plt.title(site_name)

    plt.xlabel('Date')
    plt.ylabel('Cumulative Depletions in mm')

    plt.grid(True)

    plt.legend(loc='upper center')

    plt.show()



if __name__ == "__main__":

    jpl_eta_path = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_et_ratio_modified'
    prism_path = '/media/gabriel/Seagate_Expansion_Drive/ETRM_inputs/PRISM/Precip/800m_std_all'




    # eta_output = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_cum_eta_mod'
    # prism_output = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/jpl_cum_prism_mod'

    shape = 2525, 2272

    start_date = date(2002, 01, 01)
    end_date = date(2012, 12, 31)

    start_date = date(2002, 1, 1)
    end_date = date(2013, 12, 31)

    # shape_path = '/Volumes/Seagate_Expansion_Drive/taw_optimization_work_folder/optimization_results_april_8/point_extract.shp'
    # shape_path = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE/qgis_jpl_depletions/Magdalena_mtn_extract.shp'
    # shape_path = '/media/gabriel/6e65776c-face-3d60-b48c-8d2be471814e/academic_docs_II/Ameriflux_data/Vcm_point_extract.shp'
    shape_path= '/media/gabriel/6e65776c-face-3d60-b48c-8d2be471814e/academic_docs_II/Ameriflux_data/Sg_point_extract.shp'
    # shape_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE/qgis_jpl_depletions/sangre_peak_extract.shp'
    # shape_path = '/Volumes/Seagate_Blue/jpl_research/jpl_WE/qgis_jpl_depletions/Sevilleta_plain_extract.shp'
    # print end_date - start_date3
    #
    # d = (end_date - start_date)
    #
    # print start_date + d
    #
    # for i in range(d.days):
    #     print i

    output_location = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/SWHC_initial_condition/'

    filename_key = '{}.{:02d}.{:02d}.PTJPL.ET_daily_kg.MODISsin1km_etrm_ratiomod.tif'
    # filename_key = '2002.01.01.PTJPL.ET_daily_kg.MODISsin1km_etrm_ratiomod.tif'

    eta_vals, eta_dates = depletion_extract(raster_path=jpl_eta_path, start_date=start_date, end_date=end_date,
                                            filename_key=filename_key, shape_path=shape_path)

    outfile = '{}.csv'.format('sg_eta')

    with open(os.path.join(output_location, outfile), 'w') as wfile:
        wfile.write('date,value\n')
        for i, j in zip(eta_dates, eta_vals):
            wfile.write('{},{}\n'.format(i, j))

    filename_key = 'PRISMD2_NMHW2mi_{}{:02d}{:02d}.tif'
    precip_vals, precip_dates = depletion_extract(raster_path=prism_path, start_date=start_date, end_date=end_date,
                                                  filename_key=filename_key, shape_path=shape_path)

    outfile = '{}.csv'.format('sg_precip')

    with open(os.path.join(output_location, outfile), 'w') as wfile:
        wfile.write('date,value\n')
        for i, j in zip(precip_dates, precip_vals):
            wfile.write('{},{}\n'.format(i, j))


