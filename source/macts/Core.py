__author__ = 'k0emt'


class Agent:
    """
    Base class for all Agents in the system
    """
    NAME = None
    PASSWORD = None
    VIRTUAL_HOST = "macts"
    MQ_SERVER = "localhost"

    COMM_AGENT_NAME = "liaison"
    COMM_AGENT_PASSWORD = "talker"

    METRICS_AGENT_NAME = "metrics"
    METRICS_AGENT_PASSWORD = "countem"

    simulationId = "NotSet"
    simulationStep = 1


class MactsExchange:
    METRICS = "metrics"
    SENSOR_PREFIX = "sensor-"


class MactsExchangeType:
    FANOUT = "fanout"


class Metric:
    observed = {}

    @classmethod
    def displayList(cls, metricsList):
        for metric in metricsList:
            metric.display()

    def display(self):
        print "METRIC: %s %d %s" % (
            self.observed.get('SimulationId'),
            self.observed.get('SimulationStep'),
            self.observed.get('Observed'))
        print self.observed

    def __init__(self, observationData):
        self.observed.update(observationData)


class SensorState:
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

    SIMULATION_ID = "SimulationId"
    SIMULATION_STEP = "SimulationStep"
    JUNCTION = "Junction"

    sensed = {}

    def display(self):
        print "SENSORS: %s %d %s" % (
            self.sensed.get(self.SIMULATION_ID),
            self.sensed.get(self.SIMULATION_STEP),
            self.sensed.get(self.JUNCTION))
        print self.sensed

    def __init__(self, simulationId, simulationStep, associatedJunction):
        self.sensed.update({
            self.SIMULATION_ID: simulationId,
            self.SIMULATION_STEP: simulationStep,
            self.JUNCTION: associatedJunction
        })

        self.junction = associatedJunction
