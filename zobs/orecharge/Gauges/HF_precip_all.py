import datetime
from dateutil import rrule
import arcpy, os, sys
from arcpy import env
import numpy as np
##import matplotlib.pyplot as plt

#  Set workspace to GIS gauge data location, loop through individual watersheds

arcpy.env.workspace = "C:\\Recharge_GIS\\Watersheds"
fc = "nm_wtrs_11DEC15.shp"
field = "USGS_Code"
cursor = arcpy.SearchCursor(fc)

#  List csv gauge data, create list of gauge codes

folder = 'C:\\Users\David\\Documents\\Recharge\\Gauges\\Gauge_Data_HF_csv'
os.chdir(folder)
csvList = os.listdir(folder)
# make sure that this is getting the right string from the file name
files = [str(name[1:8]) for name in csvList]
print(files)
print(len(files))
print(csvList)

#  Create layer from polygon fc so it is selectable by attribute

arcpy.env.workspace = "C:\\Recharge_GIS\Watersheds\\Watersheds"
arcpy.MakeFeatureLayer_management("C:\\Recharge_GIS\\Watersheds\\nm_wtrs_11DEC15.shp", "wtrshds_lyr")

#  Loop through polygon features in watersheds layer, select polygon geometry by attribute

for row in cursor:
    gPoly = row.getValue(field)
    polyStr = str(gPoly)
    print(gPoly)
    gstr = arcpy.AddFieldDelimiters("C:\\Recharge_GIS\\Watersheds\\nm_wtrs_11DEC15.shp", field)
    sqlExp = gstr + " = " + polyStr
    print(sqlExp)
    geo = arcpy.SelectLayerByAttribute_management("wtrshds_lyr", "NEW_SELECTION", sqlExp)
    print("USGS code: " + str(gPoly))

#  Get csv data from gauges and identify time interval of needed precip data

    if polyStr in files:
        print("true")
        folder = 'C:\\Users\David\\Documents\\Recharge\\Gauges\\Gauge_Data_HF_csv'
        os.chdir(folder)
        pos = files.index(gPoly)
        recs = []
        fid = open(csvList[pos])
        lines = fid.readlines()[0:]
        fid.close()
        rows = [line.split(',') for line in lines]
        for line in rows:
            try:
                recs.append([datetime.datetime.strptime(line[2], '%m/%d/%Y'),  # date
                float(line[3])])  # discharge
            except ValueError:
                recs.append([datetime.datetime.strptime(line[2], '%m/%d/%Y'),  # date
                float(0.0)])  # discharge
        print("Data points: " + str(len(recs)))
        qRecs = np.array(recs)

#  Make start and end dates correspond with available PRISM data (i.e., 1984-01-01 to 2013-12-31)

        start = qRecs[0, 0]
        beginPrecip = datetime.datetime(1984, 1, 1)
        if start < beginPrecip:
            start = beginPrecip
        print("Data start: " + str(start))
        end = qRecs[len(qRecs)-1, 0]
        endPrecip = datetime.datetime(2013, 12, 31)
        if end > endPrecip:
            end = endPrecip
        print("Data end: " + str(end))

#  Loop through raster data, clipping and creating arrays of data:  Date Q Ppt
        rasSq = 1013.02**2/1000  # ppt [mm -> m] and cellsize (x*y) [m*m]
        precip = []
        date = []
        q = []

        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            folder = "C:\\Recharge_GIS\\Precip\\800m\\Daily\\"
            yr = day.year
            if yr <= 1991:
                arcpy.env.overwriteOutput = True      # Ensure overwrite capability
                arcpy.env.workspace = folder + str(day.year) + "a"
                ras = folder + str(day.year) + "a\\" + "PRISM_NM_" + str(day.year) + day.strftime('%m') + day.strftime('%d') + ".tif"
                if arcpy.Exists(ras):
                    try:
                        arcpy.CheckOutExtension("Spatial")
                        mask = "C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrshds"
                        rasPart = arcpy.sa.ExtractByMask(ras, geo)
                        if day == beginPrecip:
                            rasPart.save(folder + str(day.year) + "a\\" + str(gPoly) + "_rasterClipTest.tif")
                        arr = arcpy.RasterToNumPyArray(rasPart, nodata_to_value=0)
                        arrVal = np.multiply(arr, rasSq)
                        arrSum = arrVal.sum()
                        print("Sum of precip on " + str(day) + ":  " + str(arrSum))
                        precip.append(arrSum)
                        date.append(day)
                        for rec in qRecs:
                            if rec[0] == day:
                                q.append(rec[1])
                    except:
                        pass
            if yr > 1991:
                arcpy.env.workspace = folder + str(day.year)
                ras = folder + str(day.year) + "\\" + "PRISM_NMHW2Buff_" + str(day.year) + day.strftime('%m') + day.strftime('%d') + ".tif"
                if arcpy.Exists(ras):
                    try:
                        arcpy.CheckOutExtension("Spatial")
                        mask = "C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrshds"
                        rasPart = arcpy.sa.ExtractByMask(ras, geo)
                        if day == beginPrecip:
                            rasPart.save(folder + str(day.year) + str(gPoly) + "_rasterClipTest.tif")
                        arr = arcpy.RasterToNumPyArray(rasPart, nodata_to_value=0)
                        arrVal = np.multiply(arr,rasSq)
                        arrSum = arrVal.sum()
                        print("Sum of precip on " + str(day) + ":  " + str(arrSum))
                        precip.append(arrSum)
                        date.append(day)
                        for rec in qRecs:
                            if rec[0] == day:
                                q.append(rec[1])
                    except:
                        pass

#  Create numpy arrays, convert time objects to strings, stack columns, save as CSV

        q = np.array(q,dtype=float)
        ppt = np.array(precip,dtype=float)
        date = [rec.strftime('%Y/%m/%d') for rec in date]
        date = np.array(date,object)
        data = np.column_stack((date,q,ppt))
        print(data)
        np.savetxt(('C:\\Users\David\\Documents\\Recharge\\Gauges\\Gauge_ppt_csv\\' + str(gPoly) + ".csv"),
                   data, fmt=['%s', '%1.1f', '%1.3f'], delimiter=',')
        print("You have been saved!")


        




