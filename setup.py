# ===============================================================================
# Copyright 2018 dgketchum
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
# ============= local library imports  ==========================

try:
      from setuptools import setup
except ImportError:
      from distutils.core import setup

tag = '0.0.1'

setup(name='etrm',
      version=tag,
      description='Model evapotranspiraton using soil, remote sensing, and meteorology inputs',
      long_description='',
      setup_requires=[],
      py_modules=['app', 'etrm', 'runners'],
      license='Apache',
      classifiers=[
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: GIS',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.6'],
      keywords='landsat gridded meteorology hydrology remote sensing soil water balance',
      author='David Ketchum',
      author_email='dgketchum@gmail.com',
      platforms='Posix; MacOS X; Windows',
      packages=['app', 'etrm', 'runners'],
      download_url='https://github.com/{}/{}/archive/dgk.zip'.format('nmthydro', 'recharge', tag),
      url='https://github.com/nmthydro/Recharge/tree/dgk',
      test_suite='tests.test_suite.suite',
      install_requires=['numpy', 'pandas', 'requests', 'future', 'xarray', 'pyproj', 'gdal', 'xlrd',
                        'netcdf4'],
      )

# ============= EOF =============================================
