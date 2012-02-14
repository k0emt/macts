# -*- coding: utf-8 -*-
"""
@file    edge.py
@author  Michael Behrisch
@date    2011-03-17
@version $Id: edge.py 11663 2012-01-06 09:47:01Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2011 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import struct, traci
import traci.constants as tc

_RETURN_VALUE_FUNC = {tc.ID_LIST:                   traci.Storage.readStringList,
                      tc.ID_COUNT:                  traci.Storage.readInt,
                      tc.VAR_EDGE_TRAVELTIME:       traci.Storage.readDouble,
                      tc.VAR_EDGE_EFFORT:           traci.Storage.readDouble,
                      tc.VAR_CO2EMISSION:           traci.Storage.readDouble,
                      tc.VAR_COEMISSION:            traci.Storage.readDouble,
                      tc.VAR_HCEMISSION:            traci.Storage.readDouble,
                      tc.VAR_PMXEMISSION:           traci.Storage.readDouble,
                      tc.VAR_NOXEMISSION:           traci.Storage.readDouble,
                      tc.VAR_FUELCONSUMPTION:       traci.Storage.readDouble,
                      tc.VAR_NOISEEMISSION:         traci.Storage.readDouble,
                      tc.LAST_STEP_MEAN_SPEED:      traci.Storage.readDouble,
                      tc.LAST_STEP_OCCUPANCY:       traci.Storage.readDouble,
                      tc.LAST_STEP_LENGTH:          traci.Storage.readDouble,
                      tc.VAR_CURRENT_TRAVELTIME:    traci.Storage.readDouble,
                      tc.LAST_STEP_VEHICLE_NUMBER:  traci.Storage.readInt,
                      tc.LAST_STEP_VEHICLE_HALTING_NUMBER: traci.Storage.readInt,
                      tc.LAST_STEP_VEHICLE_ID_LIST: traci.Storage.readStringList}
subscriptionResults = {}

def _getUniversal(varID, edgeID):
    result = traci._sendReadOneStringCmd(tc.CMD_GET_EDGE_VARIABLE, varID, edgeID)
    return _RETURN_VALUE_FUNC[varID](result)

def getIDList():
    """getIDList() -> list(string)
    
    Returns a list of all edges in the network.
    """
    return _getUniversal(tc.ID_LIST, "")

def getIDCount():
    """getIDCount() -> integer
    
    Returns the number of edges in the network.
    """
    return _getUniversal(tc.ID_COUNT, "")

def getAdaptedTraveltime(edgeID, time):
    """getAdaptedTraveltime(string, double) -> double
    
    Returns the travel time value (in s) used for (re-)routing 
    which is valid on the edge at the given time.
    """
    traci._beginMessage(tc.CMD_GET_EDGE_VARIABLE, tc.VAR_EDGE_TRAVELTIME,
                        edgeID, 1+4)
    traci._message.string += struct.pack("!Bi", tc.TYPE_INTEGER,
                                         traci._TIME2STEPS(time))
    return traci._checkResult(tc.CMD_GET_EDGE_VARIABLE,
                              tc.VAR_EDGE_TRAVELTIME, edgeID).readDouble()

def getEffort(edgeID, time):
    """getEffort(string, double) -> double
    
    Returns the effort value used for (re-)routing 
    which is valid on the edge at the given time.
    """
    traci._beginMessage(tc.CMD_GET_EDGE_VARIABLE, tc.VAR_EDGE_EFFORT,
                        edgeID, 1+4)
    traci._message.string += struct.pack("!Bi", tc.TYPE_INTEGER,
                                         traci._TIME2STEPS(time))
    return traci._checkResult(tc.CMD_GET_EDGE_VARIABLE,
                              tc.VAR_EDGE_EFFORT, edgeID).readDouble()

def getCO2Emission(edgeID):
    """getCO2Emission(string) -> double
    
    Returns the CO2 emission in mg for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_CO2EMISSION, edgeID)

def getCOEmission(edgeID):
    """getCOEmission(string) -> double
    
    Returns the CO emission in mg for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_COEMISSION, edgeID)

def getHCEmission(edgeID):
    """getHCEmission(string) -> double
    
    Returns the HC emission in mg for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_HCEMISSION, edgeID)

def getPMxEmission(edgeID):
    """getPMxEmission(string) -> double
    
    Returns the particular matter emission in mg for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_PMXEMISSION, edgeID)

def getNOxEmission(edgeID):
    """getNOxEmission(string) -> double
    
    Returns the NOx emission in mg for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_NOXEMISSION, edgeID)

def getFuelConsumption(edgeID):
    """getFuelConsumption(string) -> double
    
    Returns the fuel consumption in ml for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_FUELCONSUMPTION, edgeID)

def getNoiseEmission(edgeID):
    """getNoiseEmission(string) -> double
    
    Returns the noise emission in db for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_NOISEEMISSION, edgeID)

def getLastStepMeanSpeed(edgeID):
    """getLastStepMeanSpeed(string) -> double
    
    Returns the average speed in m/s for the last time step on the given edge.
    """
    return _getUniversal(tc.LAST_STEP_MEAN_SPEED, edgeID)

def getLastStepOccupancy(edgeID):
    """getLastStepOccupancy(string) -> double
    
    Returns the occupancy in % for the last time step on the given edge.
    """
    return _getUniversal(tc.LAST_STEP_OCCUPANCY, edgeID)

def getLastStepLength(edgeID):
    """getLastStepLength(string) -> double
    
    Returns the total vehicle length in m for the last time step on the given edge.
    """
    return _getUniversal(tc.LAST_STEP_LENGTH, edgeID)

def getTraveltime(edgeID):
    """getTraveltime(string) -> double
    
    Returns the estimated travel time in s for the last time step on the given edge.
    """
    return _getUniversal(tc.VAR_CURRENT_TRAVELTIME, edgeID)

def getLastStepVehicleNumber(edgeID):
    """getLastStepVehicleNumber(string) -> integer
    
    Returns the total number of vehicles for the last time step on the given edge.
    """
    return _getUniversal(tc.LAST_STEP_VEHICLE_NUMBER, edgeID)

def getLastStepHaltingNumber(edgeID):
    """getLastStepHaltingNumber(string) -> integer
    
    Returns the total number of halting vehicles for the last time step on the given edge.
    A speed of less than 0.1 m/s is considered a halt.
    """
    return _getUniversal(tc.LAST_STEP_VEHICLE_HALTING_NUMBER, edgeID)

def getLastStepVehicleIDs(edgeID):
    """getLastStepVehicleIDs(string) -> list(string)
    
    Returns the ids of the vehicles for the last time step on the given edge.
    """
    return _getUniversal(tc.LAST_STEP_VEHICLE_ID_LIST, edgeID)


def subscribe(edgeID, varIDs=(tc.LAST_STEP_VEHICLE_NUMBER,), begin=0, end=2**31-1):
    """subscribe(string, list(integer), double, double) -> None
    
    Subscribe to one or more edge values for the given interval.
    A call to this method clears all previous subscription results.
    """
    _resetSubscriptionResults()
    traci._subscribe(tc.CMD_SUBSCRIBE_EDGE_VARIABLE, begin, end, edgeID, varIDs)

def _resetSubscriptionResults():
    subscriptionResults.clear()

def _addSubscriptionResult(edgeID, varID, data):
    if edgeID not in subscriptionResults:
        subscriptionResults[edgeID] = {}
    subscriptionResults[edgeID][varID] = _RETURN_VALUE_FUNC[varID](data)

def getSubscriptionResults(edgeID=None):
    """getSubscriptionResults(string) -> dict(integer: <value_type>)
    
    Returns the subscription results for the last time step and the given edge.
    If no edge id is given, all subscription results are returned in a dict.
    If the edge id is unknown or the subscription did for any reason return no data,
    'None' is returned.
    It is not possible to retrieve older subscription results than the ones
    from the last time step.
    """
    if edgeID == None:
        return subscriptionResults
    return subscriptionResults.get(edgeID, None)


def adaptTraveltime(edgeID, time):
    """adaptTraveltime(string, double) -> None
    
    Adapt the travel time value (in s) used for (re-)routing for the given edge.
    """
    traci._sendDoubleCmd(tc.CMD_SET_EDGE_VARIABLE, tc.VAR_EDGE_TRAVELTIME, edgeID, time)

def setEffort(edgeID, effort):
    """setEffort(string, double) -> None
    
    Adapt the effort value used for (re-)routing for the given edge.
    """
    traci._sendDoubleCmd(tc.CMD_SET_EDGE_VARIABLE, tc.VAR_EDGE_EFFORT, edgeID, effort)

def setMaxSpeed(edgeID, speed):
    """setMaxSpeed(string, double) -> None
    
    Set a new maximum speed (in m/s) for all lanes of the edge..
    """
    traci._sendDoubleCmd(tc.CMD_SET_EDGE_VARIABLE, tc.VAR_MAXSPEED, edgeID, speed)
