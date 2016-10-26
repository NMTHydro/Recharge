# ===============================================================================
# Copyright 2016 ross
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


# ============= local library imports  ==========================


class RechargeConfiguration(object):
    simulation_period = None
    save_csv = None
    initial_path = None
    static_inputs = None
    inputs = None

    def __init__(self):
        self.inputs = os.path.join('F:\\', 'ETRM_Inputs')
        self.static_inputs_path = os.path.join(self.inputs, 'statics')
        self.initial_conditions_path = os.path.join(self.inputs, 'initialize')

    def print_config(self):
        print '------------- {} Config -----------------'.format(self.__class__.__name__)

        for attr in ('inputs', 'static_inputs_path', 'initial_conditions_path') + self._get_printable_attributes():
            print '{:<30s} {}'.format(attr, getattr(self, attr))

        print '-----------------------------------------'

    def _get_printable_attributes(self):
        pass


class CMBConfiguration(RechargeConfiguration):
    cmb_shapefile = None
    extract_path = None

    def __init__(self, *args, **kw):
        super(CMBConfiguration, self).__init__(*args, **kw)

        cmb_path = os.path.join(self.inputs, 'chloride_mass_balance')
        self.save_csv = os.path.join(cmb_path, 'CMB_ETRM_output', 'CMB_trackers')

        self.cmb_shapefile = os.path.join(cmb_path, 'shapefiles', 'CMB_sites_27SEP16.shp')
        self.extract_path = os.path.join(cmb_path, 'CMB_extracts')

    def _get_printable_attributes(self):
        return 'cmb_shapefile', 'extract_path'


class AmerifluxConfiguration(RechargeConfiguration):
    base_amf_dict = None
    amf_file_path = None
    save_cleaned_data = True
    etrm_extract = None
    save_combo = None

    def __init__(self, *args, **kw):
        super(AmerifluxConfiguration, self).__init__(*args, **kw)

        amf_path = os.path.join(self.inputs, 'ameriflux_sites')
        self.save_csv = os.path.join(amf_path, 'AMF_ETRM_output', 'trackers')

        # csv_output = os.path.join(amf_path, 'AMF_ETRM_output')
        # amf_obs_processed = os.path.join(amf_path, 'AMF_obs_processed')

        self.save_combo = os.path.join(amf_path, 'AMF_results_combo')
        self.amf_file_path = os.path.join(amf_path, 'AMF_Data')
        self.etrm_extract = os.path.join(amf_path, 'AMF_extracts')

        self.base_amf_dict = {'1': {'Coords': '361716 3972654', 'Name': 'Valles_Coniferous'},
                              '2': {'Coords': '355774 3969864', 'Name': 'Valles_Ponderosa'},
                              '3': {'Coords': '339552 3800667', 'Name': 'Sevilleta_Shrub'},
                              '4': {'Coords': '343495 3803640', 'Name': 'Sevilleta_Grass'},
                              '5': {'Coords': '386288 3811461', 'Name': 'Heritage_Pinyon_Juniper'},
                              '6': {'Coords': '420840 3809672', 'Name': 'Tablelands_Juniper_Savanna'}}

    def _get_printable_attributes(self):
        return 'amf_file_path', 'etrm_extract', 'save_combo', 'base_amf_dict'

# ============= EOF =============================================
