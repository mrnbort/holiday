import unittest
from parser import holiday_parser
import os
from datetime import datetime


testdata_filename = os.path.join(os.path.dirname('/Users/marynabort/Desktop/Umputun_project/holiday/testdata/'),
                                 'response.html')


class TestParser(unittest.TestCase):
    def setUp(self):
        self.testfile = open(testdata_filename)
        self.testdata = self.testfile.read()
        self.output = holiday_parser(self.testdata)

    def tearDown(self):
        self.testfile.close()

    def test_parser(self):
        self.assertEqual(self.output[0][0], 'Martin Luther King, Jr. Day')
        self.assertEqual(self.output[0][1], datetime.strptime('2022-01-17', '%Y-%m-%d').date())
        self.assertEqual(self.output[-1][0], 'Christmas Day')
        self.assertEqual(self.output[-1][1], datetime.strptime('2024-12-25', '%Y-%m-%d').date())
        self.assertEqual(self.output[12][0], 'Good Friday')
        self.assertEqual(self.output[12][1], datetime.strptime('2023-04-07', '%Y-%m-%d').date())


if __name__ == '__main__':
    unittest.main()
