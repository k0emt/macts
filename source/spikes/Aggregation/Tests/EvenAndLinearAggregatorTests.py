__author__ = 'k0emt'

import unittest
from Aggregation.Infrastructure import MessageContainer
from Aggregation.EvenAndLinearAggregator import EvenAndLinearAggregator

class MyTestCase(unittest.TestCase):
    def test_transform_extracts_systemTickId(self):
        received_body = '[{"agentValue": "5", "systemTickId": "3", "agent": "testAgent"}]'
        transformed = EvenAndLinearAggregator.transform(received_body)
        self.assertEqual("3",transformed.system_tick_id)

    def test_aggregate_value_loaded(self):
        received_body = MessageContainer("3","testAgent","5").getJSON()
        transformed = EvenAndLinearAggregator.transform(received_body)
        self.assertEqual("testAgent:5",transformed.agent_value)

    # TODO revise when have aggregating code in place
    def test_aggregate_agent_name_loaded(self):
        received_body = MessageContainer("3","testAgent","5").getJSON()
        transformed = EvenAndLinearAggregator.transform(received_body)
        self.assertEqual(EvenAndLinearAggregator.AGENT_NAME,transformed.agent_name)

    # TODO additional test case(s) for aggregating code

if __name__ == '__main__':
    unittest.main()
