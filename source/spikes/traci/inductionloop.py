# -*- coding: utf-8 -*-
"""
@file    inductionloop.py
@author  Michael Behrisch
@author  Daniel Krajzewicz
@date    2011-03-16
@version $Id: inductionloop.py 11671 2012-01-07 20:14:30Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2011 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import traci
import traci.constants as tc

def readVehicleData(result):
    result.readLength()
    nbData = result.readInt()
    data = []
    for i in range(nbData):
        result.read("!B")
        vehID = result.readString()
        result.read("!B")
        length = result.readDouble()
        result.read("!B")
        entryTime = result.readDouble()
        result.read("!B")
        leaveTime = result.readDouble()
        result.read("!B")
        typeID = result.readString()
        data.append( [ vehID, length, entryTime, leaveTime, typeID ] ) 
    return data

_RETURN_VALUE_FUNC = {tc.ID_LIST:                        traci.Storage.readStringList,
                     tc.VAR_POSITION:       traci.Storage.readDouble,
                     tc.VAR_LANE_ID:       traci.Storage.readString,
                     tc.LAST_STEP_VEHICLE_NUMBER:       traci.Storage.readInt,
                     tc.LAST_STEP_MEAN_SPEED:           traci.Storage.readDouble,
                     tc.LAST_STEP_VEHICLE_ID_LIST:      traci.Storage.readStringList,
                     tc.LAST_STEP_OCCUPANCY:            traci.Storage.readDouble,
                     tc.LAST_STEP_LENGTH:               traci.Storage.readDouble,
                     tc.LAST_STEP_TIME_SINCE_DETECTION: traci.Storage.readDouble,
                     tc.LAST_STEP_VEHICLE_DATA:         readVehicleData}
subscriptionResults = {}

def _getUniversal(varID, loopID):
    result = traci._sendReadOneStringCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, varID, loopID)
    return _RETURN_VALUE_FUNC[varID](result)

def getIDList():
    """getIDList() -> list(string)
    
    Returns a list of all induction loops in the network.
    """
    return _getUniversal(tc.ID_LIST, "")

def getPosition(loopID):
    """getPosition(string) -> double
    
    Returns the position measured from the beginning of the lane.
    """
    return _getUniversal(tc.VAR_POSITION, loopID)

def getLaneID(loopID):
    """getLaneID(string) -> string
    
    Returns the id of the lane the loop is on.
    """
    return _getUniversal(tc.VAR_LANE_ID, loopID)

def getLastStepVehicleNumber(loopID):
    """getLastStepVehicleNumber(string) -> integer
    
    .
    """
    return _getUniversal(tc.LAST_STEP_VEHICLE_NUMBER, loopID)

def getLastStepMeanSpeed(loopID):
    """getLastStepMeanSpeed(string) -> double
    
    .
    """
    return _getUniversal(tc.LAST_STEP_MEAN_SPEED, loopID)

def getLastStepVehicleIDs(loopID):
    """getLastStepVehicleIDs(string) -> list(string)
    
    .
    """
    return _getUniversal(tc.LAST_STEP_VEHICLE_ID_LIST, loopID)

def getLastStepOccupancy(loopID):
    """getLastStepOccupancy(string) -> double
    
    .
    """
    return _getUniversal(tc.LAST_STEP_OCCUPANCY, loopID)

def getLastStepMeanLength(loopID):
    """getLastStepMeanLength(string) -> double
    
    .
    """
    return _getUniversal(tc.LAST_STEP_LENGTH, loopID)

def getTimeSinceDetection(loopID):
    """getTimeSinceDetection(string) -> double
    
    .
    """
    return _getUniversal(tc.LAST_STEP_TIME_SINCE_DETECTION, loopID)

def getVehicleData(loopID):
    """getVehicleData(string) -> integer
    
    .
    """
    return _getUniversal(tc.LAST_STEP_VEHICLE_DATA, loopID)


def subscribe(loopID, varIDs=(tc.LAST_STEP_VEHICLE_NUMBER,), begin=0, end=2**31-1):
    """subscribe(string, list(integer), double, double) -> None
    
    Subscribe to one or more induction loop values for the given interval.
    A call to this method clears all previous subscription results.
    """
    _resetSubscriptionResults()
    traci._subscribe(tc.CMD_SUBSCRIBE_INDUCTIONLOOP_VARIABLE, begin, end, loopID, varIDs)

def _resetSubscriptionResults():
    subscriptionResults.clear()

def _addSubscriptionResult(loopID, varID, data):
    if loopID not in subscriptionResults:
        subscriptionResults[loopID] = {}
    subscriptionResults[loopID][varID] = _RETURN_VALUE_FUNC[varID](data)

def getSubscriptionResults(loopID=None):
    """getSubscriptionResults(string) -> dict(integer: <value_type>)
    
    Returns the subscription results for the last time step and the given loop.
    If no loop id is given, all subscription results are returned in a dict.
    If the loop id is unknown or the subscription did for any reason return no data,
    'None' is returned.
    It is not possible to retrieve older subscription results than the ones
    from the last time step.
    """
    if loopID == None:
        return subscriptionResults
    return subscriptionResults.get(loopID, None)
