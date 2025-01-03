#!/usr/bin/env python
"""
@file    CommunicationsAgent.py
@author  Bryan Nehl
@date    2012.03.17
"""
import os
import subprocess
import sys
import datetime
import time
import json
import pika
import thread
import threading
from warnings import simplefilter

from Core import Agent
from Core import MactsExchange
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
    TRACI = None
    PORT = 8813
    ONE_SECOND = 1000
    SAFETY_AGENTS = ["JRKL_SafetyAgent", "JSS_SafetyAgent"]
    FIXED_PLAN_NO_SAFETY_AGENTS = False

    # NOTE: SET TO THE CORRECT NUMBER OF SAFETY AGENTS ~~~~~~~~~~~~~~~~~~~~~~~
    EXPECTED_NUMBER_SAFETY_AGENT_COMMANDS = 2

    verbose_level = 2

    network_agents = []
    safety_agents_commands_received = 0
    do_move_next_step = True
    network_set = False
    iterations_set = False

    traci_free = threading.Event()

    def set_network_configuration(self, sysArgs):
        """
        determine/set the network configuration to use
        """
        if sysArgs[1].lower() == "low":
            self.sumoConfig = "double_t_low.sumo.cfg"
            self.network_set = True
        if sysArgs[1].lower() == "medium":
            self.sumoConfig = "double_t_medium.sumo.cfg"
            self.network_set = True
        if sysArgs[1].lower() == "full":
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
            self.set_network_configuration(sysArgs)
            self.set_maximum_iterations(sysArgs)

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
            sys.exit()

    def gatherRawMetrics(self, traci, networkSegments):
        """
        gather all of the metrics we are interested in and put them together
        """
        self.traci_free.wait()
        self.traci_free.clear()
        # Metric container for every segment
        metrics = [
        Metric({
            "SimulationId": self.simulationId,
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
            "Halting": traci.lane.getLastStepHaltingNumber(segment)
        })
        for segment in networkSegments]
        self.traci_free.set()

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

        self.traci_free.wait()
        self.traci_free.clear()
        for sensor in junction_sensor_list:
            sensorState.sensed.update({
                sensor: traci.inductionloop.getLastStepVehicleNumber(sensor)})
        self.traci_free.set()

        return sensorState

    def publishRawMetrics(self, metrics, channel):
        """
        send metrics to the metrics exchange
        """
        self.verbose_display("prm MO OBJ: %s", metrics, 4)
        for metric in metrics:
            self.verbose_display("prm MO: %s", metric.observed, 3)
            self.sendMessage(metric.observed, MactsExchange.METRICS, channel)

    def shareDetectorInformation(self, sensor_data, junction, channel):
        """
        send a sensor data to the appropriate junction exchange
        """
        self.sendMessage(sensor_data.sensed,
            MactsExchange.SENSOR_PREFIX + junction, channel)

    def sendStopMessage(self, channel):
        self.sendCommand(channel, Agent.COMMAND_END)

    def command_response_consumer(self, channel, method, header, body):
        """
        SR 5/SR 10 are there any command requests from MAS?
        SR 6/SR 11 submits any received plans
        SR 7 don't continue until all MAS have reported in
            and their instructions sent
        """
        channel.basic_ack(delivery_tag=method.delivery_tag)

        message_received = json.loads(body)
        self.verbose_display("Cmd Resp C: %s", message_received, 2)

        response = message_received.get(Agent.RESPONSE_PONG, "")

        if response:
            self.network_agents.append(response)
            self.verbose_display("CRC Agents: %s", self.network_agents, 1)
            self.sendCommand(channel, Agent.COMMAND_NET_CONFIG_INFO,
                self.network_agents)

        cmd = message_received.get(Agent.COMMAND_KEY, "")
        self.verbose_display("CRC cmd: %s", cmd, 3)

        if Agent.COMMAND_PLAN == cmd:
            # get the junction and plan from the parameters
            plan = message_received.get(Agent.PLAN_KEY, "").encode('utf-8')
            junction = message_received.get(Agent.PLAN_JUNCTION_KEY, "").\
            encode('utf-8')
            self.verbose_display("TLS Junction %s Plan %s ", (junction, plan),
                3)
            if junction and plan:
                self.verbose_display(" calling %s Plan %s ", (junction, plan),
                    3)

                self.traci_free.wait()
                self.traci_free.clear()
                self.TRACI.trafficlights.setRedYellowGreenState(junction, plan)
                self.traci_free.set()

                self.verbose_display("TLS %s %s", (junction, plan), 2)
            self.safety_agents_commands_received += 1
            if self.safety_agents_commands_received ==\
               CommunicationsAgent.EXPECTED_NUMBER_SAFETY_AGENT_COMMANDS:
                self.safety_agents_commands_received = 0
                self.do_move_next_step = True

    def command_response_handler(self):
        # SR 12 Network Configuration Discovery
        self.verbose_display("%s", "CRH - setting up", 1)
        self.establish_connection(self.name + "_command_response",
            self.command_response_consumer,
            MactsExchange.COMMAND_RESPONSE)
        self.verbose_display("%s", "CRH - consuming", 1)

        self.start_consuming()
        self.verbose_display("%s", "CRH - DONE", 1)

    def working_loop(self, traci):
        roadNetworkSegments = traci.lane.getIDList()
        self.verbose_display("segments: %s", roadNetworkSegments, 2)

        # set up local channel for working with RabbitMQ
        print "Working Loop connecting to RabbitMQ...",
        credentials = pika.PlainCredentials(self.name, self.password)
        conn_params = pika.ConnectionParameters(
            host=MactsExchange.MQ_SERVER,
            virtual_host=MactsExchange.VIRTUAL_HOST,
            credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        localChannel = conn.channel()
        print "CONNECTED"

        simplefilter("ignore", "user")

        print "sending PING"
        time.sleep(1)
        self.sendCommand(localChannel, Agent.COMMAND_PING)

        self.TRACI = traci
        self.traci_free.set()

        while  self.simulationStep <= self.MAXIMUM_ITERATIONS:
            self.verbose_display("Sim Step %d", self.simulationStep, 1)

            if self.FIXED_PLAN_NO_SAFETY_AGENTS:
                self.do_move_next_step = True

            if self.do_move_next_step:
                self.do_move_next_step = False
                veh = traci.simulationStep(CommunicationsAgent.ONE_SECOND)

                # SR 8 parse out data for individual intersections
                # SR 9 publish intersection data to RabbitMQ
                ss_sensors = self.gatherDetectorInformation(traci,
                    SensorState.SS_JUNCTION_SENSORS,
                    SensorState.ST_SAVIORS_JUNCTION)

                self.shareDetectorInformation(ss_sensors,
                    SensorState.ST_SAVIORS_JUNCTION, localChannel)

                rkl_sensors = self.gatherDetectorInformation(traci,
                    SensorState.RKL_JUNCTION_SENSORS,
                    SensorState.RKL_JUNCTION)

                self.shareDetectorInformation(rkl_sensors,
                    SensorState.RKL_JUNCTION, localChannel)

                # SR 9b gather and publish metrics data
                stepMetrics = self.gatherRawMetrics(traci, roadNetworkSegments)
                self.publishRawMetrics(stepMetrics, localChannel)

                self.simulationStep += 1
        traci.close()
        self.sendStopMessage(localChannel)

    def __init__(self, sysArgs):
        self.network_set = False
        self.iterations_set = False
        self.initiateSimulation(sysArgs)

        if self.network_set and self.iterations_set:
            import traci

            traci.init(CommunicationsAgent.PORT)
            counter = 0

            self.name = Agent.COMM_AGENT_NAME
            self.agent_name = "CommAgent"
            self.password = Agent.COMM_AGENT_PASSWORD
            self.respond_to_ping = False

            self.Connect_RabbitMQ()

            # SR 4b the liaison creates a run id and shares it with the MACTS
            self.simulationId = datetime.datetime.now().strftime(
                "%Y%m%d|%H%M%S")
            self.sendCommand(self.publishChannel, Agent.COMMAND_BEGIN)

            # spin up the main working loop in its own thread
            thread.start_new_thread(self.working_loop, (traci, ))

            # SR 12 Network Configuration Discovery / Command Response Handler
            self.command_response_handler()

        self.sendStopMessage(self.publishChannel)

if __name__ == "__main__":
    CommunicationsAgent(sys.argv)
