# ===============================================================================
# Copyright 2017 ross
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

# ============= enthought library imports =======================
# ============= standard library imports ========================
from numpy import where

from recharge.raster import Raster


def generate_rew_tiff(sand_tif, clay_tif, output):
    sand = Raster(sand_tif)
    clay = Raster(clay_tif)

    # From ASCE pg 195, equations from Ritchie et al., 1989
    rew = 8 + 0.08 * clay
    rew = where(sand > 80.0, 20.0 - 0.15 * sand, rew)
    rew = where(clay > 50, 11 - 0.06 * clay, rew)

    out = Raster.fromarray(rew, sand.geo)
    out.save(output)

# ============= EOF =============================================
