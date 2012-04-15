__author__ = 'k0emt'


class Agent:
    """
    Base class for all Agents in the system
    """
    NAME = None
    PASSWORD = None
    VIRTUAL_HOST = "macts"
    MQ_SERVER = "localhost"

    simulationId = "NotSet"
    simulationStep = 1


class MactsExchange:
    METRICS = "metrics"


class MactsExchangeType:
    FANOUT = "fanout"


class Metric:
    simulationId = ""
    simulationStep = 0
    subject = ""
    observed = {}

    def __init__(self, simulation_id, simulation_step, observed_subject):
        self.simulationId = simulation_id
        self.simulationStep = simulation_step
        self.subject = observed_subject

## deprecated ?
#class RoadNetwork:
#    SEGMENTS = ['BAve~EB_0','BAve~EB_1','BAve~WB_0','BAve~WB_1',
#                    'Best~EB_0','Best~EB_1','Best~WB_0','Best~WB_1',
#                    'Pell~EB_0','Pell~EB_1','Pell~WB_0','Pell~WB_1',
#                    'RKL~NB_0','RKL~NB_1','RKL~SB_0','RKL~SB_1',
#                    'SteS~NB_0','SteS~SB_0']
