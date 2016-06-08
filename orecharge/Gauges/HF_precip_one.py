import datetime
from dateutil import rrule
import arcpy, os
from arcpy import env
import numpy as np


#  Set workspace to GIS gauge data location, loop through individual watersheds

arcpy.env.workspace = "C:\\Recharge_GIS\\nm_gauges.gdb"
fc = "nm_wtrs_11DEC15"
field = "USGS_Code"
cursor = arcpy.SearchCursor(fc)

#  List csv gauge data, create list of gauge codes

folder = 'C:\\Users\David\\Documents\\Recharge\\Gauges\\Gauge_Data_HF_csv'
os.chdir(folder)
csvList = os.listdir(folder)
# make sure that this is getting the right string from the file name
files = [int(name[:8]) for name in csvList]

#  Create layer from polygon feature class so it is selectable by attribute

arcpy.env.workspace = "C:\\Recharge_GIS\\nm_gauges.gdb"
arcpy.MakeFeatureLayer_management("C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrs_11DEC15", "wtr_layer")

#  Loop through polygon features in watersheds layer, select polygon geometry by attribute

for row in cursor:
    gPoly = row.getValue(field)
    polyStr = str(gPoly)
    print gPoly
    gstr = arcpy.AddFieldDelimiters("C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrs_11DEC15", field)
    sqlExp = gstr + " = " + polyStr
    print sqlExp
    geo = arcpy.SelectLayerByAttribute_management("wtr_layer", "NEW_SELECTION", sqlExp)

#  Get csv data from gauges and identify time interval of needed precip data

    if int(polyStr) in files:
        print "true"
        folder = 'C:\\Users\David\\Documents\\Recharge\\Gauges\\Gauge_Data_HF_csv'
        os.chdir(folder)
        pos = files.index(int(gPoly))
        recs = []
        fid = open(csvList[pos])
        lines = fid.readlines()[0:]
        fid.close()
        rows = [line.split(',') for line in lines]
        for line in rows:
            recs.append([datetime.datetime.strptime(line[2], '%m/%d/%Y %H:%M'),  # date
            float(line[6])])  # discharge
        print "Data points: " + str(len(recs))
        qRecs = np.array(recs)

    #  Make start and end dates correspond with available PRISM data (i.e., 1984-01-01 to 2013-12-31)

        start = qRecs[0, 0]
        beginPrecip = datetime.datetime(1984, 1, 1)
        if start < beginPrecip:
            start = beginPrecip
        print "Data start: " + str(start)
        end = qRecs[len(qRecs)-1, 0]
        endPrecip = datetime.datetime(2013, 12, 31)
        if end > endPrecip:
            end = endPrecip
        print "Data end: " + str(end)

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
                        mask = "C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrs_11DEC15"
                        rasPart = arcpy.sa.ExtractByMask(ras, geo)
                        if day == beginPrecip:
                            rasPart.save(folder + str(day.year) + "a\\" + str(gPoly) + "_rasterClipTest.tif")
                        arr = arcpy.RasterToNumPyArray(rasPart, nodata_to_value=0)
                        arrVal = np.multiply(arr, rasSq)
                        arrSum = arrVal.sum()
                        print "Sum of precip on " + str(day) + ":  " + str(arrSum)
                        precip.append(arrSum)
                        date.append(day)
                    except:
                        pass
            if yr > 1991:
                arcpy.env.workspace = folder + str(day.year)
                ras = folder + str(day.year) + "\\" + "PRISM_NMHW2Buff_" + str(day.year) + day.strftime('%m') + day.strftime('%d') + ".tif"
                if arcpy.Exists(ras):
                    try:
                        arcpy.CheckOutExtension("Spatial")
                        mask = "C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrs_11DEC15"
                        rasPart = arcpy.sa.ExtractByMask(ras, geo)
                        if day == beginPrecip:
                            rasPart.save(folder + str(day.year) + str(gPoly) + "_rasterClipTest.tif")
                        arr = arcpy.RasterToNumPyArray(rasPart, nodata_to_value=0)
                        arrVal = np.multiply(arr, rasSq)
                        arrSum = arrVal.sum()
                        print "Sum of precip on " + str(day) + ":  " + str(arrSum)
                        precip.append(arrSum)
                        date.append(day)
                    except:
                        pass

        ppt = np.array(precip, dtype=float)
        date = [rec.strftime('%Y/%m/%d') for rec in date]

        add_precip = []
    for rec in qRecs[:, 0]:
            dday = rec.strftime('%Y/%m/%d')
            try:
                if rec.hour == 17 and rec.minute == 00:
                    pos = date.index(dday)
                    ppt_apnd = ppt[pos]
                    add_precip.append(ppt_apnd)
                else:
                    add_precip.append(0.0)
            except:
                pass
        ppt_arr = np.array(add_precip, dtype=float)

        data = np.column_stack((qRecs[:, 0], qRecs[:, 1], ppt_arr))
        # print data
        np.savetxt(('C:\\Users\David\\Documents\\Recharge\\Gauges\\Gauge_ppt_HF_csv\\' + str(gPoly) + "_date_q_ppt.csv"),
                   data, fmt=['%s', '%1.3f', '%1.3f'], delimiter=',')
        print "You have been saved!"







