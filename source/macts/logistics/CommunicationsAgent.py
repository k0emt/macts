#!/usr/bin/env python
"""
@file    CommunicationsAgent.py
@author  Bryan Nehl
@date    2012.03.17
"""
from Tix import MAX

import os
import subprocess
import sys


class CommunicationsAgent:
    """
    This agent is used to:
    * launch the SUMO-GUI with the selected configuration
    * obtain and publish per iteration metrics
    *
    * request the next simulation step be run, up to MAXIMUM_ITERATIONS
    * close the session
    """

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

    def launch_sumo(self, sysArgs):
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

    def __init__(self, sysArgs):
        self.network_set = False
        self.iterations_set = False
        self.launch_sumo(sysArgs)

        if self.network_set and self.iterations_set:
            import traci
            traci.init(CommunicationsAgent.PORT)
            counter = 0
            while  counter < self.MAXIMUM_ITERATIONS:
                veh = traci.simulationStep(CommunicationsAgent.ONE_SECOND)
                # SR5/SR10 are there any command requests from MAS?
                # SR6/SR11 submits any received plans
                # SR7 don't continue until all MAS have reported in
                # and their instructions sent
                # SR8 parse out data for individual intersections
                # SR9 publish the individual intersection data to RabbitMQ
                # SR9b gather and publish metrics data

                counter += 1
            traci.close()

if __name__ == "__main__":
    CommunicationsAgent(sys.argv)
