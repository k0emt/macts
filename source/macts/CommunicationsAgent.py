#!/usr/bin/env python
"""
@file    CommunicationsAgent.py
@author  Bryan Nehl
@date    2012.03.17
"""
# from Tix import MAX

import os
import subprocess
import sys
import datetime

import pika
import json

import Core
from Core import Agent
from Core import MactsExchange
from Core import MactsExchangeType
from Core import Metric
from Core import SensorState


class CommunicationsAgent(Agent):
    """
    This agent is used to:
    * create the needed RabbitMQ exchanges
    * launch the SUMO-GUI with the selected configuration
    * obtain and publish per iteration metrics
    *
    * request the next simulation step be run, up to MAXIMUM_ITERATIONS
    * close the session
    """

    verbose_level = 0

    PORT = 8813
    ONE_SECOND = 1000

    def set_network_configuration(self, sysArgs):
        """
        determine/set the network configuration to use
        """
        if sysArgs[1] == "low":
            self.sumoConfig = "double_t_low.sumo.cfg"
            self.network_set = True
        if sysArgs[1] == "medium":
            self.sumoConfig = "double_t_medium.sumo.cfg"
            self.network_set = True
        if sysArgs[1] == "full":
            self.sumoConfig = "double_t.sumo.cfg"
            self.network_set = True

    def set_maximum_iterations(self, sysArgs):
        """
        determine and set the maximum number of simulation steps/iterations
        """
        try:
            self.MAXIMUM_ITERATIONS = int(sysArgs[2])
            if self.MAXIMUM_ITERATIONS > 0:
                self.iterations_set = True
        except ValueError:
            print("Couldn't convert %s to an integer for Max Iterations" %
                  sysArgs[2])

    def initiateSimulation(self, sysArgs):
        """
        single argument: low is 10%, medium is 50% and
        full is 100% of load specification.
        Providing no argument results in a usage display
        """
        sumoExe = "sumo-gui"
        if "SUMO" in os.environ:
            sumoExe = os.path.join(os.environ["SUMO"], "sumo-gui")
        else:
            print("SUMO environ/sumo-gui not set")

        if len(sysArgs) > 2:
            self.set_maximum_iterations(sysArgs)

            self.set_network_configuration(sysArgs)

            if "SUMO_HOME" in os.environ:
                sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
            else:
                print("SUMO_HOME environ/sumo-gui not set")

            sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "..",
                "..", "..", "tools"))

        if self.network_set and self.iterations_set:
            print("Launching SUMO with config file: %s" % self.sumoConfig)
            sumoProcess = subprocess.Popen("%s -c %s" %
                                           (sumoExe, self.sumoConfig),
                shell=True, stdout=sys.stdout)
        else:
            print(
                "Usage is: %s [low|medium|full] MAX_NUMBER_SIMULATION_STEPS" %
                sysArgs[0])
            print("configuration set: %s" % self.network_set)
            print("max iterations set: %s" % self.iterations_set)

    def setup_message_exchanges(self):
        """
        set up the needed messaging exchanges
        """

        print("setting up RabbitMQ exchanges")
        credentials = pika.PlainCredentials(self.NAME, self.PASSWORD)
        conn_params = pika.ConnectionParameters(host=Core.MQ_SERVER,
            virtual_host=Core.VIRTUAL_HOST,
            credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        self.publishChannel = conn.channel()

        # Metrics exchange
        self.publishChannel.exchange_declare(exchange=MactsExchange.METRICS,
            type=MactsExchangeType.FANOUT,
            passive=False,
            durable=False,
            auto_delete=False
        )

        # Sensor Data exchanges
        self.publishChannel.exchange_declare(
            exchange=MactsExchange.SENSOR_PREFIX +
                     SensorState.ST_SAVIORS_JUNCTION,
            type=MactsExchangeType.FANOUT,
            passive=False,
            durable=False,
            auto_delete=False
        )

        self.publishChannel.exchange_declare(
            exchange=MactsExchange.SENSOR_PREFIX +
                     SensorState.RKL_JUNCTION,
            type=MactsExchangeType.FANOUT,
            passive=False,
            durable=False,
            auto_delete=False
        )

    def gatherRawMetrics(self, traci, networkSegments):
        """
        gather all of the metrics we are interested in and put them together
        """

        # Metric container for every segment
        metrics = [Metric({"SimulationId": self.simulationId,
                           "SimulationStep": self.simulationStep,
                           "Observed": segment,
                           "CO2": traci.lane.getCO2Emission(segment),
                           "CO": traci.lane.getCOEmission(segment),
                           "HC": traci.lane.getHCEmission(segment),
                           "PMx": traci.lane.getPMxEmission(segment),
                           "NOx": traci.lane.getNOxEmission(segment),
                           "Fuel": traci.lane.getFuelConsumption(segment),
                           "Noise": traci.lane.getNoiseEmission(segment),
                           "MeanSpeed": traci.lane.getLastStepMeanSpeed(segment),
                           "Halting": traci.lane.getLastStepHaltingNumber(
                               segment)})
                   for segment in networkSegments]

        self.verbose_display("Metrics: %s", metrics, 4)

        for metric_check in metrics:
            self.verbose_display("grm_MC post: %s", metric_check.observed, 3)

        return metrics

    def gatherDetectorInformation(self, traci, junction_sensor_list,
                                  junction_name):
        """
        gather the sensor data for a junction
        """
        sensorState = SensorState(self.simulationId, self.simulationStep,
            junction_name)

        for sensor in junction_sensor_list:
            sensorState.sensed.update({
                sensor: traci.inductionloop.getLastStepVehicleNumber(sensor)})

        return sensorState

    def publishRawMetrics(self, metrics):
        """
        send metrics to the metrics exchange
        """
        self.verbose_display("prm MO OBJ: %s", metrics, 4)
        for metric in metrics:
            self.verbose_display("prm MO: %s", metric.observed, 3)
            self.sendMessage(metric.observed, MactsExchange.METRICS)

    def shareDetectorInformation(self, traci, sensor_data, junction):
        """
        send a sensor data to the appropriate junction exchange
        """
        self.sendMessage(sensor_data.sensed,
            MactsExchange.SENSOR_PREFIX + junction)

    #        msg = repr(json.dumps(sensor_data.sensed))
    #        msg_props = pika.BasicProperties()
    #        msg_props.content_type = "text/plain"
    #
    #        self.channel.basic_publish(body=msg,
    #            exchange=MactsExchange.SENSOR_PREFIX + junction,
    #            properties=msg_props,
    #            routing_key="")

    def sendStopMessage(self):
        self.sendMessage(Core.STOP_PROCESSING_MESSAGE,
            MactsExchange.METRICS)
        self.sendMessage(Core.STOP_PROCESSING_MESSAGE,
            MactsExchange.SENSOR_PREFIX + SensorState.ST_SAVIORS_JUNCTION)
        self.sendMessage(Core.STOP_PROCESSING_MESSAGE,
            MactsExchange.SENSOR_PREFIX + SensorState.RKL_JUNCTION)

    def __init__(self, sysArgs):
        self.network_set = False
        self.iterations_set = False
        self.initiateSimulation(sysArgs)

        if self.network_set and self.iterations_set:
            import traci

            traci.init(CommunicationsAgent.PORT)
            counter = 0

            self.NAME = Agent.COMM_AGENT_NAME
            self.PASSWORD = Agent.COMM_AGENT_PASSWORD
            self.setup_message_exchanges()

            # SR 4b the liaison creates a run id and shares it with the MACTS
            self.simulationId = datetime.datetime.now().strftime(
                "%Y%m%d|%H%M%S")
            # TODO share it

            roadNetworkSegments = traci.lane.getIDList()
            self.verbose_display("segments: %s", roadNetworkSegments, 2)

            while  self.simulationStep <= self.MAXIMUM_ITERATIONS:
                veh = traci.simulationStep(CommunicationsAgent.ONE_SECOND)

                # SR 8 parse out data for individual intersections
                ss_sensors = self.gatherDetectorInformation(traci,
                    SensorState.SS_JUNCTION_SENSORS,
                    SensorState.ST_SAVIORS_JUNCTION)

                rkl_sensors = self.gatherDetectorInformation(traci,
                    SensorState.RKL_JUNCTION_SENSORS,
                    SensorState.RKL_JUNCTION)

                # SR 9 publish intersection data to RabbitMQ
                self.shareDetectorInformation(traci, ss_sensors,
                    SensorState.ST_SAVIORS_JUNCTION)

                self.shareDetectorInformation(traci, rkl_sensors,
                    SensorState.RKL_JUNCTION)

                # SR 9b gather and publish metrics data
                stepMetrics = self.gatherRawMetrics(traci, roadNetworkSegments)
                self.publishRawMetrics(stepMetrics)

                # TODO SR 5/SR 10 are there any command requests from MAS?

                # TODO SR 6/SR 11 submits any received plans

                # TODO SR 7 don't continue until all MAS have reported in
                # TODO SR 7  and their instructions sent

                self.simulationStep += 1
            traci.close()

            self.sendStopMessage()

if __name__ == "__main__":
    CommunicationsAgent(sys.argv)
