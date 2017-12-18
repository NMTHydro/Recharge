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
import fiona
import rasterio
import rasterio.tools.mask
# ============= local library imports ===========================

# TODO- not working


def run():

    with fiona.open("/Volumes/SeagateExpansionDrive/jan_metric/created_images/ag_ravation.shp", "r") as shapefile:
        features = [feature["geometry"] for feature in shapefile]

    with rasterio.open("/Volumes/SeagateExpansionDrive/jan_metric/created_images/nlcd_align_path35_dixon_wy.tif") as src:
        out_image, out_transform = rasterio.tools.mask.mask(src, features, crop=True)
        out_meta = src.meta.copy()

        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
    with rasterio.open("/Volumes/SeagateExpansionDrive/jan_metric/created_images/nlcd_masked_ag_ravation.tif", "w", **out_meta) as dest:
       dest.write(out_image)


if __name__ == "__main__":

    run()
