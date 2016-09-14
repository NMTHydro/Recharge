# ===============================================================================
# Copyright 2016 ross
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= standard library imports ========================
import datetime
import os
import logging
from dateutil import rrule
from arcpy import env
from numpy import array, multiply, column_stack, savetxt

# ============= local library imports  ==========================


def precip(watershed, path, output, daily, field='USGS_Code'):
    # make sure that this is getting the right string from the file name
    files = os.listdir(path)
    files_names = [str(name[1:8]) for name in files]

    env.overwriteOutput = True  # Ensure overwrite capability

    for row in arcpy.SearchCursor(watershed):
        gPoly = row.getValue(field)

        gstr = arcpy.AddFieldDelimiters(watershed, field)

        sql = '{} = {}'.format(gstr, gPoly)

        geo = arcpy.SelectLayerByAttribute_management('wtrshds_lyr', 'NEW_SELECTION', sql)

        logging.info('USGS code: {}'.format(gPoly))

        #  Get csv data from gauges and identify time interval of needed precip data

        if str(gPoly) in files_names:
            pos = files_names.index(gPoly)
            p = files[pos]
            recs = []
            with open(p, 'r') as rfile:
                for line in rfile:
                    row = line.split(',')
                    dt = datetime.strptime(row[2], '%m/%d/%Y')
                    try:
                        recs.append((dt,  # date
                                     float(row[3])))  # discharge
                    except ValueError:
                        recs.append((dt,  # date
                                     0.0))  # discharge

            logging.info('Data points: {}'.format(len(recs)))
            qRecs = array(recs)

            #  Make start and end dates correspond with available PRISM data (i.e., 1984-01-01 to 2013-12-31)

            start = qRecs[0, 0]
            beginPrecip = datetime(1984, 1, 1)
            if start < beginPrecip:
                start = beginPrecip
            logging.info('Data start: {}'.format(start))
            end = qRecs[len(qRecs) - 1, 0]
            endPrecip = datetime(2013, 12, 31)
            if end > endPrecip:
                end = endPrecip
            logging.info('Data end: {}'.format(end))

            #  Loop through raster data, clipping and creating arrays of data:  Date Q Ppt
            rasSq = 1013.02 ** 2 / 1000  # ppt [mm -> m] and cellsize (x*y) [m*m]
            precip = []
            date = []
            q = []

            for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                # region = 'C:\\Recharge_GIS\\Precip\\800m\\Daily\\'
                yr = day.year
                d = day.strftime('%y%m%d')

                if yr <= 1991:

                    ws = os.path.join(daily, str(yr), 'a')
                    # env.workspace = ws

                    ras = os.path.join(ws, 'PRISM_NM_{}.tif'.format(d))
                    if arcpy.Exists(ras):
                        try:
                            arcpy.CheckOutExtension('Spatial')
                            # mask = 'C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrshds'
                            ras_part = arcpy.sa.ExtractByMask(ras, geo)
                            if day == beginPrecip:
                                op = os.path.join(ws, '{}_rasterClipTest.tif'.format(gPoly))
                                ras_part.save(op)

                            arr = arcpy.RasterToNumPyArray(ras_part, nodata_to_value=0)
                            arrVal = multiply(arr, rasSq)
                            arrSum = arrVal.sum()
                            logging.info('Sum of precip on {}: {}'.format(day, arrSum))
                            precip.append(arrSum)
                            date.append(day)
                            for rec in qRecs:
                                if rec[0] == day:
                                    q.append(rec[1])
                        except BaseException, e:
                            logging.info('Exception pre1991 {}'.format(e))

                if yr > 1991:
                    ws = os.path.join(daily, str(yr))
                    # env.workspace = ws

                    ras = os.path.join(ws, 'PRISM_NMHW2Buff_{}.tif'.format(d))

                    if arcpy.Exists(ras):
                        try:
                            arcpy.CheckOutExtension('Spatial')
                            # mask = 'C:\\Recharge_GIS\\nm_gauges.gdb\\nm_wtrshds'
                            ras_part = arcpy.sa.ExtractByMask(ras, geo)
                            if day == beginPrecip:
                                op = os.path.join(ws, '{}_rasterClipTest.tif'.format(gPoly))
                                ras_part.save(op)

                            arr = arcpy.RasterToNumPyArray(ras_part, nodata_to_value=0)
                            arrVal = multiply(arr, rasSq)
                            arrSum = arrVal.sum()
                            logging.info('Sum of precip on {}: {}'.format(day, arrSum))
                            precip.append(arrSum)
                            date.append(day)
                            for rec in qRecs:
                                if rec[0] == day:
                                    q.append(rec[1])
                        except BaseException, e:
                            logging.info('Exception post1991 {}'.format(e))

            #  Create numpy arrays, convert time objects to strings, stack columns, save as CSV
            q = array(q)
            ppt = array(precip)
            date = [rec.strftime('%Y/%m/%d') for rec in date]
            date = array(date)
            data = column_stack((date, q, ppt))

            savetxt(os.path.join(output, '{}.csv'.format(gPoly)), data, fmt=['%s', '%1.1f', '%1.3f'], delimiter=',')
            logging.info('You have been saved!')


if __name__ == '__main__':
    p = os.path.join('C:', 'Users', 'David', 'Documents', 'Recharge', 'Gauges', 'Gauge_Data_HF_csv')
    op = os.path.join('C:', 'Users', 'David', 'Documents', 'Recharge', 'Gauges', 'Gauge_ppt_csv')
    sp = os.path.join('C:', 'Recharge_GIS', 'Watersheds', 'nm_wtrs_11DEC15.shp')
    dr = os.path.join('C:', 'Recharge_GIS', 'Precip', '800m', 'Daily')
    precip(sp, p, op, dr)

# ============= EOF =============================================
