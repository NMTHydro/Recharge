from datetime import datetime
from dateutil import rrule
from osgeo import gdal, ogr
import numpy as np

start, end = datetime(2000, 1, 1), datetime(2013, 12, 31)
sWin, eWin = datetime(start.year, 11, 1), datetime(end.year, 3, 30)
sMon, eMon = datetime(start.year, 6, 1), datetime(start.year, 10, 1)

shp_filename = 'C:\\Recharge_GIS\\qgis_layers\\sensitivity_points\\SA_pnts29APR16_UTM.shp'

ds = ogr.Open(shp_filename)
lyr = ds.GetLayer()
defs = lyr.GetLayerDefn()
x = 0
already_done = ['Bateman']
for feat in lyr:
    name = feat.GetField("Name")

    if name in already_done:
        pass
    else:
        print name
        x += 1
        point_id_obj = x
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()

        for month in rrule.rrule(rrule.MONTHLY, dtstart=start, until=end):
            path = 'C:\\Recharge_GIS\\OSG_Data\\current_use'
            raster = 'aws_mod_4_21_10_0'

            aws_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            gt = aws_open.GetGeoTransform()
            rb = aws_open.GetRasterBand(1)
            px = abs(int((mx - gt[0]) / gt[1]))
            py = int((my - gt[3]) / gt[5])
            aws_obj = rb.ReadAsArray(px, py, 1, 1)

            raster = 'nlcd_root_dpth_15apr'
            nlcd_rt_z_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = nlcd_rt_z_open.GetRasterBand(1)
            nlcd_rt_obj = rb.ReadAsArray(px, py, 1, 1)
            nlcd_rt_z_open = []

            raster = 'nlcd_plnt_hgt1_250_m_degraded1'
            nlcd_plt_hgt_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = nlcd_plt_hgt_open.GetRasterBand(1)
            nlcd_plt_hgt_obj = rb.ReadAsArray(px, py, 1, 1)
            nlcd_plt_hgt_open = []

            raster = 'Soil_Ksat_15apr'  # convert from micrometer/sec to mm/day
            ksat_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = ksat_open.GetRasterBand(1)
            ksat_obj = rb.ReadAsArray(px, py, 1, 1)
            ksat_open = []

            raster = 'tew_250_15apr'
            tew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = tew_open.GetRasterBand(1)
            tew_obj = rb.ReadAsArray(px, py, 1, 1)
            tew_open = []

            path = 'C:\\Recharge_GIS\\Array_Results\\initialize'
            raster = 'dr_4_18_2_49'
            dr_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = dr_open.GetRasterBand(1)
            dr_obj = rb.ReadAsArray(px, py, 1, 1)
            dr_open = []

            raster = 'de_4_18_2_49'
            de_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = de_open.GetRasterBand(1)
            de_obj = rb.ReadAsArray(px, py, 1, 1)
            de_open = []

            raster = 'drew_4_19_23_11'
            drew_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = drew_open.GetRasterBand(1)
            drew_obj = rb.ReadAsArray(px, py, 1, 1)
            drew_open = []

            path = 'C:\\Recharge_GIS\\OSG_Data\\not_in_use'
            raster = 'FC_Ras_SSGO1'
            fc_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = fc_open.GetRasterBand(1)
            fc_obj = rb.ReadAsArray(px, py, 1, 1)
            fc_open = []

            raster = 'WP_Ras_SSGO1'
            wp_open = gdal.Open('{a}\\{b}.tif'.format(a=path, b=raster))
            rb = wp_open.GetRasterBand(1)
            wp_obj = rb.ReadAsArray(px, py, 1, 1)
            wp_open = []
        print ''
        print point_id_obj
        print name
        print mx, my

        point_id = []
        date = []
        ksat = []
        soil_ksat = []
        kcb = []
        rlin = []
        rg =[]
        etrs_Pm = []
        p_hgt = []
        minTemp = []
        maxTemp = []
        temp = []
        ppt = []
        fc = []
        wp = []
        taw = []
        aws = []
        rt_z = []

        for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            # prDe.append(pDe)
            # prDr.append(pDr)
            date.append(dday)
            taw.append(aws_obj)
            aws.append(aws_obj)
            fc.append(fc_obj)
            wp.append(wp_obj)
            point_id.append(point_id_obj)
            p_hgt.append(nlcd_plt_hgt_obj)
            rt_z.append(nlcd_rt_obj)

            if dday in rrule.rrule(rrule.DAILY, dtstart=sMon, until=eMon):
                ksat.append(ksat_obj * 2/24)
                soil_ksat.append(ksat_obj * 2/24)
            else:
                ksat.append(ksat_obj * 6/24)
                soil_ksat.append(ksat_obj * 6/24)

    # Daily Values
    # NDVI
        for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                doy = dday.timetuple().tm_yday
                if dday.year == 2000:
                    path = 'F:\\NDVI\\NDVI_std_all'
                    obj = [1, 49, 81, 113, 145, 177, 209, 241, 273, 305, 337]
                    if doy < 49:
                        strt = 1
                        band = doy
                        nd = 48
                        raster = '{a}\\T{b}_{c}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(a=path,
                                                                                         b=str(strt).rjust(3, '0'),
                                                                                         c=str(nd).rjust(3, '0'),
                                                                                         d=band)
                        kcb_open = gdal.Open(raster)
                        rb = kcb_open.GetRasterBand(band)
                        kcb_obj = rb.ReadAsArray(px, py, 1, 1) * 1.25
                        kcb.append(kcb_obj)
                        kcb_open = []

                    else:
                        for num in obj[1:]:
                            diff = doy - num
                            if 0 <= diff <= 31:
                                pos = obj.index(num)
                                strt = obj[pos]
                                band = diff + 1
                                if num == 337:
                                    nd = num + 29
                                else:
                                    nd = num + 31
                                raster = '{a}\\T{b}_{c}_2000_etrf_subset_001_048_ndvi_daily.tif'.format(a=path,
                                                                                        b=str(strt).rjust(3, '0'),
                                                                                        c=str(nd).rjust(3, '0'),
                                                                                        d=str(doy - num + 1))
                                kcb_open = gdal.Open(raster)
                                rb = kcb_open.GetRasterBand(band)
                                kcb_obj = rb.ReadAsArray(px, py, 1, 1) * 1.25
                                kcb.append(kcb_obj)
                                kcb_open = []

                elif dday.year == 2001:
                    path = "F:\\NDVI\\NDVI_std_all"
                    pathyear = path + "\\" + str(dday.year)
                    obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
                           225, 241, 257, 273, 289, 305, 321, 337, 353]
                    for num in obj:
                        diff = doy - num
                        if 0 <= diff <= 15:
                                pos = obj.index(num)
                                strt = obj[pos]
                                band = diff + 1
                                if num == 353:
                                    nd = num + 12
                                else:
                                    nd = num + 15
                                raster = '{a}\\{b}_{c}_{d}.tif'.format(a=path, b=dday.year, c=strt, d=nd, e=band)
                                kcb_open = gdal.Open(raster)
                                rb = kcb_open.GetRasterBand(band)
                                kcb_obj = rb.ReadAsArray(px, py, 1, 1) * 1.25
                                kcb.append(kcb_obj)
                                kcb_open = []

                else:
                    path = "F:\\NDVI\\NDVI_std_all"
                    obj = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
                               225, 241, 257, 273, 289, 305, 321, 337, 353]
                    for num in obj:
                        diff = doy - num
                        if 0 <= diff <= 15:
                                pos = obj.index(num)
                                strt = obj[pos]
                                band = diff + 1
                                if num == 353:
                                    nd = num + 12
                                else:
                                    nd = num + 15
                                raster = '{a}\\{b}_{c}.tif'.format(a=path, b=dday.year, c=pos+1, d=nd, e=band)
                                kcb_open = gdal.Open(raster)
                                rb = kcb_open.GetRasterBand(band)
                                kcb_obj = rb.ReadAsArray(px, py, 1, 1) * 1.25
                                kcb.append(kcb_obj)
                                kcb_open = []

        x = 0
        for element in kcb:
            if element < 0.001 or element > 1.5:
                kcb[x] = kcb[x - 1]
                print 'found bad value'
            x += 1

        print 'NDVI point extract at {a} {b} done'.format(a=point_id_obj, b=name)

    # RLIN net longwave radiation
        for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            doy = dday.timetuple().tm_yday
            doy_str = str(doy)
            path = "F:\\PM_RAD"
            raster = '{a}\\PM{d}\\RLIN_NM_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
            rlin_open = gdal.Open(raster)
            rb = rlin_open.GetRasterBand(1)
            rlin_obj = rb.ReadAsArray(px, py, 1, 1)
            rlin.append(rlin_obj)
            rlin_open = []
        print 'RLIN extract at {a} {b} done'.format(a=point_id_obj, b=name)


    # RTOT net shortwave radiation
        for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            doy = dday.timetuple().tm_yday
            doy_str = str(doy)
            path = "F:\\PM_RAD"
            raster = '{a}\\rad{d}\\RTOT_{b}_{c}.tif'.format(a=path, b=dday.year, c=str(doy).rjust(3, '0'), d=dday.year)
            rg_open = gdal.Open(raster)
            rb = rg_open.GetRasterBand(1)
            rg_obj = rb.ReadAsArray(px, py, 1, 1)
            rg.append(rg_obj)
            rg_open = []
        print 'RG extract at {a} {b} done'.format(a=point_id_obj, b=name)

    # refET PM
        for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            doy = dday.timetuple().tm_yday
            doy_str = str(doy)
            raster = '{a}\\PM{d}\\PM_NM_{b}_{c}.tif'.format(a=path, b=dday.year,c=str(doy).rjust(3, '0'), d=dday.year)
            etrs_open = gdal.Open(raster)
            rb = etrs_open.GetRasterBand(1)
            etrs_obj = rb.ReadAsArray(px, py, 1, 1)
            etrs_Pm.append(etrs_obj)
            etrs_open = []
        print 'refET PM  extract at at {a} {b} done'.format(a=point_id_obj, b=name)

    # TEMP
        for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            path = "F:\\PRISM\\Temp\\Minimum_standard"
            month_str = str(dday.month)
            day_str = str(dday.day)
            if dday.year in [2002, 2004, 2005]:
                raster = '{a}\\TempMin_NMHW2Buff_{b}{c}{d}.tif'.format(a=path, b=dday.year, c=month_str.rjust(2, '0'),
                                                                       d=day_str.rjust(2, '0'))
            else:
                raster = '{a}\\cai_tmin_us_us_30s_{b}{c}{d}.tif'.format(a=path, b=dday.year, c=month_str.rjust(2, '0'),
                                                                        d=day_str.rjust(2, '0'))
            min_temp_open = gdal.Open(raster)
            rb = min_temp_open.GetRasterBand(1)
            min_temp_obj = rb.ReadAsArray(px, py, 1, 1)
            minTemp.append(min_temp_obj)
            min_temp_open = []

            path = "F:\\PRISM\\Temp\\Maximum_standard"
            raster = '{a}\\TempMax_NMHW2Buff_{b}{c}{d}.tif'.format(a=path,b=dday.year, c=month_str.rjust(2, '0'),
                                                                            d=day_str.rjust(2, '0'))
            max_temp_open = gdal.Open(raster)
            rb = max_temp_open.GetRasterBand(1)
            max_temp_obj = rb.ReadAsArray(px, py, 1, 1)
            maxTemp.append(max_temp_obj)
            max_temp_open = []

            rslt = (max_temp_obj + min_temp_obj)/2
            temp.append(rslt)
        print 'TEMP extract at at {a} {b} done'.format(a=point_id_obj, b=name)

    # Precipitation
        for dday in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            path = 'F:\\PRISM\\Precip\\800m_std_all'
            month_str = str(dday.month)
            day_str = str(dday.day)
            raster = '{a}\\PRISMD2_NMHW2mi_{b}{c}{d}.tif'.format(a=path, b=dday.year, c=month_str.rjust(2, '0'),
                                                                 d=day_str.rjust(2, '0'))
            ppt_open = gdal.Open(raster)
            rb = ppt_open.GetRasterBand(1)
            ppt_obj = rb.ReadAsArray(px, py, 1, 1)
            ppt.append(ppt_obj)
            ppt_open = []
        print 'Precip extract at at {a} {b} done'.format(a=point_id_obj, b=name)

        point_id = np.array(point_id).squeeze()
        date = [rec.strftime('%Y/%m/%d') for rec in date]
        date = np.array(date, object)
        ksat = np.array(ksat, dtype=float).squeeze()
        soil_ksat = np.array(soil_ksat, dtype=float).squeeze()
        kcb = np.array(kcb, dtype=float).squeeze()
        etrs_Pm = np.array(etrs_Pm, dtype=float).squeeze()
        rlin = np.array(rlin, dtype=float).squeeze()
        rg = np.array(rg, dtype=float).squeeze()
        p_hgt = np.array(p_hgt, dtype=float).squeeze()
        minTemp = np.array(minTemp, dtype=float).squeeze()
        maxTemp = np.array(maxTemp, dtype=float).squeeze()
        temp = np.array(temp, dtype=float).squeeze()
        ppt = np.array(ppt, dtype=float).squeeze()
        taw = np.array(taw, dtype=float).squeeze()
        aws = np.array(aws, dtype=float).squeeze()
        fc = np.array(fc, dtype=float).squeeze()
        wp = np.array(wp, dtype=float).squeeze()
        rt_z = np.array(rt_z, dtype=float).squeeze()

        # b = np.array([['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
        #                'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z']])

        recs = np.column_stack((date, ksat, soil_ksat, kcb, rlin, rg, etrs_Pm, p_hgt, minTemp,
                                maxTemp, temp, ppt, fc, wp, taw, aws, rt_z))

        # data = np.concatenate((b, recs), axis=0)
        name = name.replace(' ', '_')
        path = 'C:\Users\David\Documents\Recharge\Sensitivity_analysis\SA_extracts'
        np.savetxt('{f}\\{g}_extract.csv'.format(f=path, g=name),
                   recs, fmt=['%s', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f',
                   '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f', '%1.3f'],
                   delimiter=',')
        print "You have been saved!"

