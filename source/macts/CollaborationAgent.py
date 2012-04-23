__author__ = 'k0emt'
from Core import Agent


class CollaborationAgent(Agent):
    """

    """

    # SR12 - was redefined for Network Discovery, used with Metrics
    # This network is small enough, we know what to share with whom
    # as well as what to import from where

    # SR13
    # Collaboration agents share information regarding traffic leaving their
    # intersection by putting it in distribution exchange.
    def shareData(self):
        pass

    # SR14 The Collaboration agent creates information regarding traffic
    # leaving their intersection.
    def collectDataToShare(self):
        pass

    # SR 17 gather shared data for use by planning agent
    def importData(self):
        pass
