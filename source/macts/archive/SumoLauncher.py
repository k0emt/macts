#!/usr/bin/env python
"""
@file    sumo_launcher.py
@author  Bryan Nehl
@date    2012.03.17
"""

import os
import subprocess
import sys


class SumoLauncher:
    """
    This code is used to launch the SUMO-GUI with the selected configuration
    """

    def __init__(self, sysArgs):
        """
        single argument: low is 10%, medium is 50% and
        full is 100% of load specification.
        Providing no argument results in a usage display
        """
        sumoExe = "sumo-gui"
        if "SUMO" in os.environ:
            sumoExe = os.path.join(os.environ["SUMO"], "sumo-gui")
        if len(sysArgs) > 1:
            if sysArgs[1] == "low":
                self.sumoConfig = "double_t_low.sumo.cfg"
            if sysArgs[1] == "medium":
                self.sumoConfig = "double_t_medium.sumo.cfg"
            if sysArgs[1] == "full":
                self.sumoConfig = "double_t.sumo.cfg"

            if "SUMO_HOME" in os.environ:
                sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
            sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "..",
                "..", "..", "tools"))
            import traci

            print("Launching SUMO with config file: %s" % self.sumoConfig)
            sumoProcess = subprocess.Popen("%s -c %s" %
                                           (sumoExe, self.sumoConfig),
                shell=True, stdout=sys.stdout)
        else:
            print("Usage is: %s [low|medium|full]" % sysArgs[0])

if __name__ == "__main__":
    SumoLauncher(sys.argv)
