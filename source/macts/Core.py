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

    @classmethod
    def displayList(cls, metricsList):
        for metric in metricsList:
            metric.display()

    def display(self):
        print "METRIC: %s %d %s" % (
            self.simulationId, self.simulationStep, self.subject)
        print self.observed

    def __init__(self, simulation_id, simulation_step, observed_subject):
        self.simulationId = simulation_id
        self.simulationStep = simulation_step
        self.subject = observed_subject


class SensorState:
    simulationId = ""
    simulationStep = 0
    junction = ""
    sensed = {}

    ST_SAVIORS_JUNCTION = "SteSaviors"
    SS_JUNCTION_SENSORS = {
        "e1det_Best~EB_0", "e1det_Best~EB_1",
        "e1det_SteS~SB_0",
        "e1det_BAve~WB_0", "e1det_BAve~WB_1"
    }

    RKL_JUNCTION = "RoseKilnLane"
    RKL_JUNCTION_SENSORS = {
        "e1det_BAve~EB_0", "e1det_BAve~EB_1",
        "e1det_RKL~SB_0", "e1det_RKL~SB_1",
        "e1det_Pell~WB_0", 'e1det_Pell~WB_1'
    }

    def display(self):
        print "SENSORS: %s %d %s" % (
            self.simulationId, self.simulationStep, self.junction)
        print self.sensed

    def __init__(self, simulation_id, simulation_step, associated_junction):
        self.simulationId = simulation_id
        self.simulationStep = simulation_step
        self.junction = associated_junction
