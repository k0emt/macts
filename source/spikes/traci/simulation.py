# -*- coding: utf-8 -*-
"""
@file    simulation.py
@author  Michael Behrisch
@date    2011-03-15
@version $Id: simulation.py 11671 2012-01-07 20:14:30Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import traci, struct
import traci.constants as tc

_RETURN_VALUE_FUNC = {tc.VAR_TIME_STEP:                         traci.Storage.readInt,
                      tc.VAR_LOADED_VEHICLES_NUMBER:            traci.Storage.readInt,
                      tc.VAR_LOADED_VEHICLES_IDS:               traci.Storage.readStringList,
                      tc.VAR_DEPARTED_VEHICLES_NUMBER:          traci.Storage.readInt,
                      tc.VAR_DEPARTED_VEHICLES_IDS:             traci.Storage.readStringList,
                      tc.VAR_ARRIVED_VEHICLES_NUMBER:           traci.Storage.readInt,
                      tc.VAR_ARRIVED_VEHICLES_IDS:              traci.Storage.readStringList,
                      tc.VAR_MIN_EXPECTED_VEHICLES:             traci.Storage.readInt,
                      tc.VAR_TELEPORT_STARTING_VEHICLES_NUMBER: traci.Storage.readInt,
                      tc.VAR_TELEPORT_STARTING_VEHICLES_IDS:    traci.Storage.readStringList,
                      tc.VAR_TELEPORT_ENDING_VEHICLES_NUMBER:   traci.Storage.readInt,
                      tc.VAR_TELEPORT_ENDING_VEHICLES_IDS:      traci.Storage.readStringList,
                      tc.VAR_DELTA_T:                           traci.Storage.readInt,
                      tc.VAR_NET_BOUNDING_BOX:                  lambda(result): (result.read("!dd"), result.read("!dd"))}
subscriptionResults = {}

def _getUniversal(varID):
    result = traci._sendReadOneStringCmd(tc.CMD_GET_SIM_VARIABLE, varID, "")
    return _RETURN_VALUE_FUNC[varID](result)

def getCurrentTime():
    """getCurrentTime() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_TIME_STEP)

def getLoadedNumber():
    """getLoadedNumber() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_LOADED_VEHICLES_NUMBER)

def getLoadedIDList():
    """getLoadedIDList() -> list(string)
    
    .
    """
    return _getUniversal(tc.VAR_LOADED_VEHICLES_IDS)

def getDepartedNumber():
    """getDepartedNumber() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_DEPARTED_VEHICLES_NUMBER)

def getDepartedIDList():
    """getDepartedIDList() -> list(string)
    
    .
    """
    return _getUniversal(tc.VAR_DEPARTED_VEHICLES_IDS)

def getArrivedNumber():
    """getArrivedNumber() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_ARRIVED_VEHICLES_NUMBER)

def getArrivedIDList():
    """getArrivedIDList() -> list(string)
    
    .
    """
    return _getUniversal(tc.VAR_ARRIVED_VEHICLES_IDS)

def getMinExpectedNumber():
    """getMinExpectedNumber() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_MIN_EXPECTED_VEHICLES)

def getStartingTeleportNumber():
    """getStartingTeleportNumber() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_TELEPORT_STARTING_VEHICLES_NUMBER)

def getStartingTeleportIDList():
    """getStartingTeleportIDList() -> list(string)
    
    .
    """
    return _getUniversal(tc.VAR_TELEPORT_STARTING_VEHICLES_IDS)

def getEndingTeleportNumber():
    """getEndingTeleportNumber() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_TELEPORT_ENDING_VEHICLES_NUMBER)

def getEndingTeleportIDList():
    """getEndingTeleportIDList() -> list(string)
    
    .
    """
    return _getUniversal(tc.VAR_TELEPORT_ENDING_VEHICLES_IDS)

def getDeltaT():
    """getDeltaT() -> integer
    
    .
    """
    return _getUniversal(tc.VAR_DELTA_T)

def getNetBoundary():
    """getNetBoundary() -> ((double, double), (double, double))
    
    .
    """
    return _getUniversal(tc.VAR_NET_BOUNDING_BOX)

def convert2D(edgeID, pos, laneIndex=0, toGeo=False):
    posType = tc.POSITION_2D
    if toGeo:
        posType = tc.POSITION_LAT_LON
    traci._beginMessage(tc.CMD_GET_SIM_VARIABLE, tc.POSITION_CONVERSION, "", 1+4 + 1+4+len(edgeID)+8+1 + 1+8+8)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 2)
    traci._message.string += struct.pack("!Bi", tc.POSITION_ROADMAP, len(edgeID)) + edgeID
    traci._message.string += struct.pack("!dBBdd", pos, laneIndex, posType, 0., 0.)
    return traci._checkResult(tc.CMD_GET_SIM_VARIABLE, tc.POSITION_CONVERSION, "").read("!dd")

def convertRoad(x, y, isGeo=False):
    posType = tc.POSITION_2D
    if isGeo:
        posType = tc.POSITION_LAT_LON
    traci._beginMessage(tc.CMD_GET_SIM_VARIABLE, tc.POSITION_CONVERSION, "", 1+4 + 1+8+8 + 1+4+8+1)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 2)
    traci._message.string += struct.pack("!Bdd", posType, x, y)
    traci._message.string += struct.pack("!BidB", tc.POSITION_ROADMAP, 0, 0., 0)
    result = traci._checkResult(tc.CMD_GET_SIM_VARIABLE, tc.POSITION_CONVERSION, "")
    return result.readString(), result.readDouble(), result.read("!B")[0]

def getDistance2D(x1, y1, x2, y2, isGeo=False, isDriving=False):
    """getDistance2D(double, double, double, double, boolean, boolean) -> double
    
    .
    """
    posType = tc.POSITION_2D
    if isGeo:
        posType = tc.POSITION_LAT_LON
    distType = tc.REQUEST_AIRDIST
    if isDriving:
        distType = tc.REQUEST_DRIVINGDIST
    traci._beginMessage(tc.CMD_GET_SIM_VARIABLE, tc.DISTANCE_REQUEST, "", 1+4 + 1+8+8 + 1+8+8 + 1)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 3)
    traci._message.string += struct.pack("!Bdd", posType, x1, y1)
    traci._message.string += struct.pack("!BddB", posType, x2, y2, distType)
    return traci._checkResult(tc.CMD_GET_SIM_VARIABLE, tc.DISTANCE_REQUEST, "").readDouble()

def getDistanceRoad(edgeID1, pos1, edgeID2, pos2, isDriving=False):
    """getDistanceRoad(string, double, string, double, boolean) -> double
    
    .
    """
    distType = tc.REQUEST_AIRDIST
    if isDriving:
        distType = tc.REQUEST_DRIVINGDIST
    traci._beginMessage(tc.CMD_GET_SIM_VARIABLE, tc.DISTANCE_REQUEST, "", 1+4 + 1+4+len(edgeID1)+8+1 + 1+4+len(edgeID2)+8+1 + 1)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 3)
    traci._message.string += struct.pack("!Bi", tc.POSITION_ROADMAP, len(edgeID1)) + edgeID1
    traci._message.string += struct.pack("!dBBi", pos1, 0, tc.POSITION_ROADMAP, len(edgeID2)) + edgeID2
    traci._message.string += struct.pack("!dBB", pos2, 0, distType)
    return traci._checkResult(tc.CMD_GET_SIM_VARIABLE, tc.DISTANCE_REQUEST, "").readDouble()


def subscribe(varIDs=(tc.VAR_DEPARTED_VEHICLES_IDS,), begin=0, end=2**31-1):
    """subscribe(list(integer), double, double) -> None
    
    Subscribe to one or more simulation values for the given interval.
    A call to this method clears all previous subscription results.
    """
    _resetSubscriptionResults()
    traci._subscribe(tc.CMD_SUBSCRIBE_SIM_VARIABLE, begin, end, "x", varIDs)

def _resetSubscriptionResults():
    subscriptionResults.clear()

def _addSubscriptionResult(objectID, varID, data):
    subscriptionResults[varID] = _RETURN_VALUE_FUNC[varID](data)

def getSubscriptionResults():
    """getSubscriptionResults() -> dict(integer: <value_type>)
    
    Returns the subscription results for the last time step.
    It is not possible to retrieve older subscription results than the ones
    from the last time step.
    """
    return subscriptionResults
