__author__ = 'k0emt'
from Core import Agent


class BasePlanningAgent(Agent):
    """

    """

    # SR 15 Planning Agent plans
    def createPlan(self, sensor_data):
        pass

    # SR 16 Planning Agent submits plan to Safety Agent for Review
    def submitToSafetyAgentForReview(self, safety_agent, plan):
        pass

    def gatherSafetyAgentResponse(self):
        pass

    # TODO SR 17 Incorporates data that was shared from a collaboration agent
    def incorporateSharedData(self, collaboration_agent):
        pass

    def __init__(self):
        pass
