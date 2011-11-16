__author__ = 'Owner'

import unittest
from OffenderData import *

TEST_RECORD = "00000001SMITH             PAUL                       Black                         Male                          19290622         1265D                   STLC090410021040TC: MURDER 1ST - FIST                                                     Y  1956031699999999999999999999999900000000   00000000"

class OffenderDataTests(unittest.TestCase):
    def test_rawrecord(self):
        offenderData = OffenderData(TEST_RECORD)
        self.assertEqual(offenderData.rawData(),
                         TEST_RECORD,
                         'not as expected message')

    def test_extractLastName(self):
        offenderData = OffenderData(TEST_RECORD)
        self.assertEqual(offenderData.lastName,
                         "SMITH",
                         offenderData.lastName)

    def test_extractFirstName(self):
        offenderData = OffenderData(TEST_RECORD)

        self.assertEqual(offenderData.firstName,
                         "PAUL",
                         offenderData.firstName)

if __name__ == '__main__':
    unittest.main()