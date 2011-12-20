__author__ = 'Owner'

# the intent of this spike exploration is to show how incoming traffic data
# can be aggregated by the planning agent from multiple sources

# sources poll their own sensors once per system tick
# the sources then publish their data to public topic queues
# the aggregator receives data from all of the public topic queues that are relevant
# once it has all the information it publishes a summary/digest

class Aggregation:

    def __init__(self):
        self.blah = ''

