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
# ============= local library imports  ==========================
import os
import sys

from datetime import datetime


class PathsNotSetExecption(BaseException):
    def __str__(self):
        return 'paths.build(in_root, out_root) needs to be called before the model will run'


class Paths:
    etrm_input_root = None
    etrm_output_root = None
    prism = None
    penman = None
    ndvi = None
    ndvi_std_all = None
    ndvi_individ = None
    ndvi_spline = None
    ndvi_statics = None
    static_inputs = None
    initial_inputs = None
    polygons = None
    mask = None #'/Volumes/Seagate Expansion Drive/ETRM_inputs/new_inputs/Mask/test_2_final_rast.tif' #'/Volumes/Seagate Expansion Drive/ETRM_inputs/Mask/unioned_raster_output.tif' # TODO temporary
    amf_sites = None
    amf_extract = None
    amf_output_root = None
    amf_combo_root = None
    amf_ex_sac = None
    amf_ex_sac_extract = None
    amf_ex_sac_output_root = None
    amf_ex_sac_trackers = None
    results_root = None
    point_shape = None # TODO point_tracker

    def __init__(self):
        self._is_set = False
        self.config = os.path.join(os.path.expanduser('~'), 'ETRM_CONFIG.yml')

    def build(self, input_root, output_root=None):
        self._is_set = True
        self.etrm_input_root = etrm_input_root = input_root
        if output_root is None:
            output_root = os.path.join(input_root, 'ETRM_Results')

        self.etrm_output_root = output_root

        now = datetime.now()
        tag = now.strftime('%y%m%d_%H_%M')

        self.results_root = results_rt = os.path.join(self.etrm_output_root, tag)

        self.prism = os.path.join(etrm_input_root, 'PRISM')
        self.ndvi = os.path.join(etrm_input_root, 'NDVI')
        self.ndvi_statics = os.path.join(etrm_input_root, 'NDVI_statics')
        self.ndvi_std_all = os.path.join(self.ndvi, 'NDVI_std_all')
        self.ndvi_individ = os.path.join(self.ndvi, 'NDVI')
        self.ndvi_spline = os.path.join(self.ndvi, 'NDVI_spline')

        self.penman = os.path.join(etrm_input_root, 'PM_RAD')
        self.static_inputs = os.path.join(etrm_input_root, 'statics')
        self.initial_inputs = os.path.join(etrm_input_root, 'initialize')

        amf_root = os.path.dirname(etrm_input_root)
        print 'amf_root: {}'.format(amf_root)
        self.amf_sites = amf_path = os.path.join(amf_root, 'ETRM_inputs_Ameriflux', 'ameriflux_sites')  # OK
        self.amf_extract = os.path.join(amf_path, 'AMF_extracts')
        self.amf_output_root = os.path.join(amf_path, 'AMF_ETRM_output')
        self.amf_combo_root = os.path.join(amf_path, 'AMF_results_combo')

        self.amf_ex_sac = ex_sac = os.path.join(etrm_input_root, 'ameriflux_ex_sac')
        self.amf_ex_sac_output_root = ex_sac_out = os.path.join(ex_sac, 'AMF_ETRM_output')
        self.amf_ex_sac_extract = os.path.join(ex_sac, 'AMF_extracts')

        mem = os.path.join(output_root, "mem000.txt")

        cnt = 1
        while os.path.isfile(mem):
            mem = os.path.join(output_root, "mem{:03n}.txt".format(cnt))
            cnt += 1

        self.mem_file = mem

        self.tracker_csv_path = os.path.join(results_rt, 'point_trackers')

        # self.pixel_tracker_output = os.path.join(results_rt)

        # use me

    def set_mask_path(self, path):
        if path:
            self.mask = self.input_path(path)
            print 'here is the mask path {}'.format(self.mask)

    def set_point_shape_path(self, path):
        self.point_shape = self.input_path(path)
        print 'here is the shapefile path {}'.format(self.point_shape)

    def input_path(self, path):
        return os.path.join(self.etrm_input_root, path)

    def set_polygons_path(self, p):
        self.polygons = self.input_path(p)

    def verify(self):
        attrs = ('etrm_input_root',
                 'etrm_output_root',
                 'prism',
                 'ndvi',
                 'ndvi_individ',
                 'penman',
                 'static_inputs',
                 'initial_inputs')

        # GELP removed  'ndvi_spline', 'ndvi_std_all' on Nov 9, 2018

        nonfound = []
        for attr in attrs:
            v = getattr(self, attr)
            if not os.path.exists(v):
                print 'NOT FOUND {}: {}'.format(attr, v)
                nonfound.append((attr, v))

        if nonfound:
            sys.exit(1)

    def is_set(self):
        return self._is_set

paths = Paths()


# ============= EOF =============================================
