__author__ = 'k0emt'
import pika
import json

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

    total_CO2_mg = 0.0
    total_CO_mg = 0.0
    total_HC_mg = 0.0
    total_PMx_mg = 0.0
    total_NOx_mg = 0.0

    total_Fuel_ml = 0.0
    total_Noise_dBA = 0.0
    total_Halting_vehicles = 0
    total_MeanSpeed_m_per_s = 0.0

    # "CO": 6.37156111111111,
    # "PMx": 0.02126148611111111,
    # "Occupancy": 0.01923385157877865,
    # "CO2": 601.6927777777778,
    # "NOx": 0.83951,
    # "Fuel": 0.23988551336146277,
    # "HC": 0.34941999999999995,
    # "Halting": 1,
    # "Noise": 55.94027641010837,
    # "MeanSpeed": 0.0,
    # "TravelTime": 1000000.0}'

    def spike(self):
        metrics = []

        for segment in {"segA", "segB", "segC"}:
            metric = Metric({
                "SimulationId": "spike",
                "SimulationStep": 0,
                "Observed": segment,
                "CO2": 1.1,
                "CO": 2.2,
                "HC": 3.3,
                "PMx": 4.4,
                "NOx": 5.5,
                "Noise": 6.006,
                "Fuel": 7.00007,
                "TravelTime": 8.8,
                "MeanSpeed": 9.09,
                "Occupancy": 10.010,
                "Halting": 11.11
            })
            metrics.append(metric)
            json_out = json.dumps(metric.observed)
            repr_json_out = repr(json_out)
#            print json_out
#            print repr(json_out)
#            print metric.observed.get('SimulationId')

            metric_received = Metric(json.loads(json_out))
            metric_received.display()

    def gatherRawMetrics(self, channel, method, header, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)

        print body

        if self.isStopProcessingMessage(body):
            channel.basic_cancel(consumer_tag=self.NAME)
            channel.stop_consuming()
        else:
            newMetric = Metric(json.loads(body))
            self.verbose_display("NM: %s", newMetric.observed, 2)
            self.aggregateMetrics(newMetric)

    def aggregateMetrics(self, metric):
        # add these values to our running sums
        # '{
        # "Observed": "SteS~SB_0",
        # "SimulationStep": 1,
        # "SimulationId": "20120417|205827",
        # "CO": 6.37156111111111,
        # "PMx": 0.02126148611111111,
        # "Occupancy": 0.01923385157877865,
        # "CO2": 601.6927777777778,
        # "NOx": 0.83951,
        # "Fuel": 0.23988551336146277,
        # "HC": 0.34941999999999995,
        # "Halting": 1,
        # "Noise": 55.94027641010837,
        # "MeanSpeed": 0.0,
        # "TravelTime": 1000000.0}'
        pass

    def getEnvironmentInformation(self):
        pass

    def persistStep(self):
        pass

    def persistSimulation(self):
        pass

    def __init__(self):
        self.NAME = Agent.METRICS_AGENT_NAME
        self.PASSWORD = Agent.METRICS_AGENT_PASSWORD

        print self.NAME + " Agent ONLINE"

        # self.spike()
        self.verbose_level = 3
        consumer = self.gatherRawMetrics
        Agent.establish_connection(self, consumer, MactsExchange.METRICS)

        # SR21 Gather simulation metrics from TraCI via the System Liaison.

        # SR22 Do any internal processing necessary for computing metrics.

        # SR23 On simulation run completion, persist the run metrics to MongoDB
        # network configuration information will be stored with the metrics

        print self.NAME + " Agent OFFLINE"

if __name__ == "__main__":
    MetricsAgent()
