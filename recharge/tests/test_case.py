import unittest
from StringIO import StringIO

from app.config import Config


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        txt = '''---
input_root: /Volumes/Seagate Expansion Drive
output_root: Please Set Me

start_date: 12/1/2013
end_date: 12/31/2013

mask: masks/please_set_me.tif
polygons: Blank_Geo

save_dates: []

daily_outputs:
 - tot_infil
 - tot_etrs
 - tot_eta
 - tot_precip
 - tot_kcb

ro_reinf_frac: 0.0
swb_mode: fao
allen_ceff: 1.0
winter_evap_limiter: 0.3  
'''
        path = StringIO(txt)
        self._cfg = Config(path)

    def test_run_specs(self):
        self.assertEqual(len(self._cfg.runspecs), 1)

    def test_start_year(self):
        r = self._cfg.runspecs[0]
        s, e = r.date_range
        self.assertEqual(s.year, 2013)

    def test_end_year(self):
        r = self._cfg.runspecs[0]
        s, e = r.date_range
        self.assertEqual(e.year, 2013)

    def test_swb_mode(self):
        r = self._cfg.runspecs[0]
        self.assertEqual(r.swb_mode, 'fao')


if __name__ == '__main__':
    unittest.main()
