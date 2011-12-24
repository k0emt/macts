__author__ = 'k0emt'

# the intent of this spike exploration is to show how incoming traffic data
# can be aggregated by the planning agent from multiple sources

# sources poll their own sensors once per system tick
# the sources then publish their data to a direct exchange
# the aggregator receives data from all of the public topic queues that are relevant
# once it has all the information it sends a summary/digest to the direct exchange

class Aggregation:

    def __init__(self):
        self.blah = ''

