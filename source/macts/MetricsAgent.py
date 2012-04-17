__author__ = 'k0emt'
import json

from Core import Agent
from Core import Metric


class MetricsAgent(Agent):
    """
    Agent which gathers simulation run metrics
    Aggregates simulation run metrics
    on receipt of new simulation id:
        persist summary metrics
        reset summary metrics
    """

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

    def __init__(self):
        self.NAME = Agent.METRICS_AGENT_NAME
        self.PASSWORD = Agent.METRICS_AGENT_PASSWORD

        self.spike()

        # SR21 Gather simulation metrics from TraCI via the System Liaison.

        # SR22 Do any internal processing necessary for computing metrics.

        # SR23 On simulation run completion, persist the run metrics to MongoDB
        # network configuration information will be stored with the metrics

if __name__ == "__main__":
    MetricsAgent()
