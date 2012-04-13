__author__ = 'k0emt'
from Core import Agent

class CollaborationAgent(Agent):
    """

    """

    # SR12
    # Collaboration agents include a discovery interface which is used to
    # self-identify when an agent sends a broadcast querying for agents that
    # are associated with intersections that send traffic into their intersection
    # or receive traffic from their intersection. Agents respond with a list of
    # queues where their outbound traffic information can be found.

    # SR13
    # Collaboration agents share information regarding traffic leaving their
    # intersection by putting it in distribution queues.

    # SR14 The Collaboration agent creates information regarding traffic
    # leaving their intersection.
