# -*- coding: utf-8 -*-
"""
@file    junction.py
@author  Michael Behrisch
@date    2011-03-17
@version $Id: junction.py 11453 2011-11-02 09:40:25Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2011 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import traci
import traci.constants as tc

_RETURN_VALUE_FUNC = {tc.ID_LIST:      traci.Storage.readStringList,
                     tc.VAR_POSITION: lambda(result): result.read("!dd")}
subscriptionResults = {}

def _getUniversal(varID, junctionID):
    result = traci._sendReadOneStringCmd(tc.CMD_GET_JUNCTION_VARIABLE, varID, junctionID)
    return _RETURN_VALUE_FUNC[varID](result)

def getIDList():
    """getIDList() -> list(string)
    
    Returns a list of all junctions in the network.
    """
    return _getUniversal(tc.ID_LIST, "")

def getPosition(junctionID):
    """getPosition(string) -> (double, double)
    
    Returns the coordinates of the center of the junction.
    """
    return _getUniversal(tc.VAR_POSITION, junctionID)


def subscribe(junctionID, varIDs=(tc.VAR_POSITION,), begin=0, end=2**31-1):
    """subscribe(string, list(integer), double, double) -> None
    
    Subscribe to one or more junction values for the given interval.
    A call to this method clears all previous subscription results.
    """
    _resetSubscriptionResults()
    traci._subscribe(tc.CMD_SUBSCRIBE_JUNCTION_VARIABLE, begin, end, junctionID, varIDs)

def _resetSubscriptionResults():
    subscriptionResults.clear()

def _addSubscriptionResult(junctionID, varID, data):
    if junctionID not in subscriptionResults:
        subscriptionResults[junctionID] = {}
    subscriptionResults[junctionID][varID] = _RETURN_VALUE_FUNC[varID](data)

def getSubscriptionResults(junctionID=None):
    """getSubscriptionResults(string) -> dict(integer: <value_type>)
    
    Returns the subscription results for the last time step and the given junction.
    If no junction id is given, all subscription results are returned in a dict.
    If the junction id is unknown or the subscription did for any reason return no data,
    'None' is returned.
    It is not possible to retrieve older subscription results than the ones
    from the last time step.
    """
    if junctionID == None:
        return subscriptionResults
    return subscriptionResults.get(junctionID, None)
