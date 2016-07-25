import unittest

import datetime
from dateutil import rrule


class ETRMTestCase(unittest.TestCase):
    def test_step_generator(self):
        start = datetime.datetime(2000, 1, 1)
        end = datetime.datetime(2000, 12, 31)
        days = list(rrule.rrule(rrule.DAILY, dtstart=start, until=end))
        self.assertEqual(len(days), 366)


if __name__ == '__main__':
    unittest.main()
