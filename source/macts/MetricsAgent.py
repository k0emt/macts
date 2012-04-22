__author__ = 'k0emt'
import json

from pymongo import Connection

from Core import Agent
from Core import Metric
from Core import MactsExchange


class MetricsAgent(Agent):
    """
    Agent which gathers simulation run metrics
    Aggregates simulation run metrics
    on receipt of new simulation id:
        persist summary metrics
        reset summary metrics
    """

    verbose_level = 2

    total_CO2_mg = 0.0
    total_CO_mg = 0.0
    total_HC_mg = 0.0
    total_PMx_mg = 0.0
    total_NOx_mg = 0.0

    total_Fuel_ml = 0.0
    total_Noise_dBA = 0.0
    total_Halting_vehicles = 0
    total_MeanSpeed_m_per_s = 0.0

    simulation_steps = 0
    visible_network_agents = []

    def sim_init(self):
        self.verbose_display("sim_init: %s", "metrics RESET", 1)
        self.visible_network_agents = []

        self.total_CO2_mg = 0.0
        self.total_CO_mg = 0.0
        self.total_HC_mg = 0.0
        self.total_PMx_mg = 0.0
        self.total_NOx_mg = 0.0

        self.total_Fuel_ml = 0.0
        self.total_Noise_dBA = 0.0
        self.total_Halting_vehicles = 0
        self.total_MeanSpeed_m_per_s = 0.0

    # SR 21
    def gatherRawMetrics(self, channel, method, header, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)

        #        if self.isStopProcessingMessage(body):
        #            channel.basic_cancel(consumer_tag=self.name)
        #            channel.stop_consuming()
        #        else:
        newMetric = Metric(json.loads(body))
        self.verbose_display("NM: %s", newMetric.observed, 3)
        self.aggregateMetrics(newMetric)

    # SR 22
    def aggregateMetrics(self, metric):
        # TODO verify that the SimulationId matches this agent?
        # "SimulationStep": 1,
        # "SimulationId": "20120417|205827",

        self.total_CO2_mg += metric.observed.get("CO2")
        self.total_CO_mg += metric.observed.get("CO")
        self.total_HC_mg += metric.observed.get("HC")
        self.total_PMx_mg += metric.observed.get("PMx")
        self.total_NOx_mg += metric.observed.get("NOx")

        self.total_Fuel_ml += metric.observed.get("Fuel")
        self.total_Noise_dBA += metric.observed.get("Noise")
        self.total_Halting_vehicles += metric.observed.get("Halting")
        self.total_MeanSpeed_m_per_s += metric.observed.get("MeanSpeed")

        # TODO better approach to capturing number of simulation steps?
        self.simulation_steps = metric.observed.get("SimulationStep")

    def enhanced_command_consumer(self, message_received):
        # SR 23 -- need the network configuration information
        # command is network configuration information
        self.verbose_display("ECC: %s", "pre-parse", 2)
        command = message_received.get(Agent.COMMAND_KEY, "")
        self.verbose_display("ECC cmd: %s", command, 2)
        if Agent.COMMAND_NET_CONFIG_INFO == command:
            self.verbose_display("E CmdC sim id %s", self.simulationId, 2)
            self.visible_network_agents = message_received.get(
                Agent.COMMAND_PARAMETERS_KEY, [])
            self.verbose_display("E CmdC net agents %s",
                self.visible_network_agents, 2)

    # SR 23
    def sim_end(self):
        self.verbose_display("sim_end %s", "called", 1)
        self.persistSimulation()

    # SR 23
    def persistSimulation(self):
        # TODO include the result from getEnvironmentInformation
        simulationTotals = {
            "SimulationId": self.simulationId,
            "CO2": self.total_CO2_mg,
            "CO": self.total_CO_mg,
            "HC": self.total_HC_mg,
            "PMx": self.total_PMx_mg,
            "NOx": self.total_NOx_mg,
            "Fuel": self.total_Fuel_ml,
            "Noise": self.total_Noise_dBA,
            "Halting": self.total_Halting_vehicles,
            "MeanSpeed": self.total_MeanSpeed_m_per_s,
            "SimulationSteps": self.simulation_steps,
            "NetworkConfiguration" : self.visible_network_agents
        }
        self.verbose_display("Simulation Totals: %s", simulationTotals, 1)

        # TODO the actual save to MongoDB
        # include: self.simulationId, simulationTotals and
        # self.visible_network_agents
        cn = Connection('localhost')
        db = cn.macts
        metrics = db.metrics
        metrics.insert(simulationTotals)
        cn.disconnect()

    def __init__(self):
        self.name = Agent.METRICS_AGENT_NAME
        self.password = Agent.METRICS_AGENT_PASSWORD
        self.agent_name = "MetricsAgent"

        print self.agent_name + " Agent ONLINE"

        # SR21 Gather simulation metrics from TraCI via the System Liaison.
        # SR22 Do any internal processing necessary for computing metrics.
        self.Connect_RabbitMQ()
        self.establish_connection("metrics", self.gatherRawMetrics,
            MactsExchange.METRICS)

        self.establish_connection("commands", self.command_consumer,
            MactsExchange.COMMAND_DISCOVERY)

        self.start_consuming()

        # SR23 On simulation run completion, persist the run metrics to MongoDB
        # network configuration information will be stored with the metrics
        self.persistSimulation()

        print self.name + " Agent OFFLINE"

if __name__ == "__main__":
    MetricsAgent()
