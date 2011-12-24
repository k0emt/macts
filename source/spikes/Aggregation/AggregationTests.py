__author__ = 'k0emt'

import unittest

class AggregationTests(unittest.TestCase):
    def test_monitoringTwoSensors(self):
        aggregator = Aggregation
        # push 1 to topic Odd
        # push 2 to topic Even
        # see that aggregator makes a call to publish "{Odd:1,Even:2}" on topic Agent
        # can mock this call
