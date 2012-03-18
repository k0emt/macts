#!/usr/bin/env python
"""
@file    test_agent.py
@author  Bryan Nehl
@date    2012.03.10

Based on:
Tutorial for traffic light control via the TraCI interface.
Copyright (C) 2009-2011 DLR/TS, Germany, Lena Kalleske

<tlLogic id="JunctionRKLN" type="static" programID="0" offset="0">
    <phase duration="31" state="rrrGGGGGg"/>
    <phase duration="2" state="rrryyyyyg"/>
    <phase duration="6" state="rrrrrrrrG"/>
    <phase duration="2" state="rrrrrrrry"/>
    <phase duration="31" state="GGGGrrrrr"/>
    <phase duration="2" state="yyyyrrrrr"/>
</tlLogic>

<junction
    id="JunctionRKLN" type="traffic_light" x="166.00" y="0.00"
    incLanes="RKL~SB_0 RKL~SB_1 Pell~WB_0 Pell~WB_1 BAve~EB_0 BAve~EB_1"
    intLanes=":JunctionRKLN_0_0 :JunctionRKLN_1_0 :JunctionRKLN_9_0
              :JunctionRKLN_3_0 :JunctionRKLN_4_0 :JunctionRKLN_5_0
              :JunctionRKLN_6_0 :JunctionRKLN_7_0 :JunctionRKLN_10_0"
    shape="159.45,8.05 172.55,8.05 174.05,6.55 174.05,-6.55 157.95,
            -6.55 157.95,6.55">
    <request index="0" response="000000000" foes="000110000" cont="0"/>
    <request index="1" response="000000000" foes="000110000" cont="0"/>
    <request index="2" response="000110000" foes="111110000" cont="1"/>
    <request index="3" response="000000000" foes="100000000" cont="0"/>
    <request index="4" response="000000011" foes="100000111" cont="0"/>
    <request index="5" response="000000011" foes="100000111" cont="0"/>
    <request index="6" response="000000100" foes="000000100" cont="0"/>
    <request index="7" response="000000100" foes="000000100" cont="0"/>
    <request index="8" response="000111100" foes="000111100" cont="1"/>
</junction>
"""

import os
import subprocess
import sys
import socket
import time
import struct
import random

if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "..", "..", "..", "tools"))
import traci

PORT = 8813
ONE_SECOND = 1000
MAXSTEPS = 1800
SIG_TRANSITION = 39
SBGREEN_BUMP = 50
MAX_BUMPS = 2

EBGREEN = 'rrrGGGGGg'
EB_NB_WEAK = 'rrryyyyyg'
EB_NB = 'rrrrrrrrG'
RED_MOSTLY = 'rrrrrrrry'
SBGREEN = 'GGGGrrrrr'
CAUTION = 'yyyyrrrrr'

# the default program has EBGREEN and SBGREEN repeating 31 times
PROGRAM = [EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN,
           EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN,
           EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN,
           EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN,
           EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN, EBGREEN,
           EBGREEN,
           EB_NB_WEAK, EB_NB_WEAK,
           EB_NB, EB_NB, EB_NB, EB_NB, EB_NB, EB_NB,
           RED_MOSTLY, RED_MOSTLY,
           SBGREEN, SBGREEN, SBGREEN, SBGREEN, SBGREEN, SBGREEN,
           SBGREEN, SBGREEN, SBGREEN, SBGREEN, SBGREEN, SBGREEN,
           SBGREEN, SBGREEN, SBGREEN, SBGREEN, SBGREEN, SBGREEN,
           CAUTION, CAUTION]

programPointer = 0
veh = []
step = 0
programLength = len(PROGRAM) - 1
bumpCounter = 0

#sumoExe = "sumo-gui"
#if "SUMO" in os.environ:
#    sumoExe = os.path.join(os.environ["SUMO"], "sumo-gui")
#sumoConfig = "double_t.sumo.cfg"
#sumoProcess = subprocess.Popen("%s -c %s" % (sumoExe, sumoConfig), shell=True, stdout=sys.stdout)

traci.init(PORT)

logfile = open("output_log.txt", "w")

print >> logfile, "starting loop"
while step < MAXSTEPS:
    veh = traci.simulationStep(ONE_SECOND)
    programPointer = ((programPointer + 1) % programLength)
    vehCountedOverInduction = traci.inductionloop.getLastStepVehicleNumber("e1det_RKL~SB_0") \
                            + traci.inductionloop.getLastStepVehicleNumber("e1det_RKL~SB_1")
    print >> logfile, "step: %i e1det_RKL~SB_0 & 1 detected: %i" % (step, vehCountedOverInduction)
    print >> logfile, "RKL emissions lane 0: %f  1: %f" % (traci.lane.getCO2Emission('RKL~SB_0') , traci.lane.getCO2Emission('RKL~SB_1'))
    if vehCountedOverInduction == 2:
        print >> logfile, "e1det_RKL~SB inductor(s) tripped"
        if bumpCounter < MAX_BUMPS:
            print >> logfile, "bumping"
            if programPointer < SIG_TRANSITION:
                programPointer = SIG_TRANSITION
                bumpCounter += 1
            elif programPointer > SBGREEN_BUMP:
                programPointer = SBGREEN_BUMP
                bumpCounter += 1
        else:
            print >> logfile, "max bumps reached, continue normal cycle"
            if programPointer <= SIG_TRANSITION:
                print >> logfile, 'resetting bump counter'
                bumpCounter = 0

    print >> logfile, "TLS cmd: %s" % PROGRAM[programPointer]
    traci.trafficlights.setRedYellowGreenState("JunctionRKLN", PROGRAM[programPointer])
    step += 1

print >> logfile, "closing traci"
traci.close()
print >> logfile, "traci closed"

logfile.close()
