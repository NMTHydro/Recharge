# ===============================================================================
# Copyright 2016 dgketchum
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
#
try:
    from osgeo import gdal, ogr
except ImportError:
    pass


def get_static_inputs_at_point(coords, full_path):

    mx, my = coords.split(' ')
    mx, my = int(mx), int(my)
    aws_open = gdal.Open(full_path)
    gt = aws_open.GetGeoTransform()
    rb = aws_open.GetRasterBand(1)
    px = abs(int((mx - gt[0]) / gt[1]))
    py = int((my - gt[3]) / gt[5])
    obj = rb.ReadAsArray(px, py, 1, 1)
    return obj[0][0]


def save_point_static_inputs_to_csv(coords, static_inputs_path, save_path):
    pass


def save_point_daily_inputs_to_csv(coords, save_path):
    pass


def get_static_inputs_by_shapefile(shp_path, static_inputs_path):
    shapefile = ogr.Open(shp_path)
    layer = shapefile.GetLayer()
    for feature in layer:
        name = feature.GetField('Name')
        # print name
        geometry = feature.GetGeometryRef()
        xx, yy = geometry.GetX(), geometry.GetY()
        obj = get_static_inputs_at_point('{} {}'.format(xx, yy), static_inputs_path)
        return obj
# ============= EOF =============================================
