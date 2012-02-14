# -*- coding: utf-8 -*-
"""
@file    polygon.py
@author  Michael Behrisch
@date    2011-03-16
@version $Id: polygon.py 11453 2011-11-02 09:40:25Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2011 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import struct, traci
import traci.constants as tc

_RETURN_VALUE_FUNC = {tc.ID_LIST:   traci.Storage.readStringList,
                      tc.VAR_TYPE:  traci.Storage.readString,
                      tc.VAR_SHAPE: traci.Storage.readShape,
                      tc.VAR_COLOR: lambda(result): result.read("!BBBB")}
subscriptionResults = {}

def _getUniversal(varID, polygonID):
    result = traci._sendReadOneStringCmd(tc.CMD_GET_POLYGON_VARIABLE, varID, polygonID)
    return _RETURN_VALUE_FUNC[varID](result)

def getIDList():
    """getIDList() -> list(string)
    
    Returns a list of all polygons in the network.
    """
    return _getUniversal(tc.ID_LIST, "")

def getType(polygonID):
    """getType(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_TYPE, polygonID)

def getShape(polygonID):
    """getShape(string) -> list((double, double))
    
    .
    """
    return _getUniversal(tc.VAR_SHAPE, polygonID)

def getColor(polygonID):
    """getColor(string) -> (integer, integer, integer, integer)
    
    .
    """
    return _getUniversal(tc.VAR_COLOR, polygonID)


def subscribe(polygonID, varIDs=(tc.VAR_SHAPE,), begin=0, end=2**31-1):
    """subscribe(string, list(integer), double, double) -> None
    
    Subscribe to one or more polygon values for the given interval.
    A call to this method clears all previous subscription results.
    """
    _resetSubscriptionResults()
    traci._subscribe(tc.CMD_SUBSCRIBE_POLYGON_VARIABLE, begin, end, polygonID, varIDs)

def _resetSubscriptionResults():
    subscriptionResults.clear()

def _addSubscriptionResult(polygonID, varID, data):
    if polygonID not in subscriptionResults:
        subscriptionResults[polygonID] = {}
    subscriptionResults[polygonID][varID] = _RETURN_VALUE_FUNC[varID](data)

def getSubscriptionResults(polygonID=None):
    """getSubscriptionResults(string) -> dict(integer: <value_type>)
    
    Returns the subscription results for the last time step and the given poi.
    If no polygon id is given, all subscription results are returned in a dict.
    If the polygon id is unknown or the subscription did for any reason return no data,
    'None' is returned.
    It is not possible to retrieve older subscription results than the ones
    from the last time step.
    """
    if polygonID == None:
        return subscriptionResults
    return subscriptionResults.get(polygonID, None)


def setType(polygonID, polygonType):
    traci._beginMessage(tc.CMD_SET_POLYGON_VARIABLE, tc.VAR_TYPE, polygonID, 1+4+len(polygonType))
    traci._message.string += struct.pack("!Bi", tc.TYPE_STRING, len(polygonType)) + polygonType
    traci._sendExact()

def setShape(polygonID, shape):
    traci._beginMessage(tc.CMD_SET_POLYGON_VARIABLE, tc.VAR_SHAPE, polygonID, 1+1+len(shape)*(8+8))
    traci._message.string += struct.pack("!BB", tc.TYPE_POLYGON, len(shape))
    for p in shape:
        traci._message.string += struct.pack("!dd", p)
    traci._sendExact()

def setColor(polygonID, color):
    traci._beginMessage(tc.CMD_SET_POLYGON_VARIABLE, tc.VAR_COLOR, polygonID, 1+1+1+1+1)
    traci._message.string += struct.pack("!BBBBB", tc.TYPE_COLOR, int(color[0]), int(color[1]), int(color[2]), int(color[3]))
    traci._sendExact()

def add(polygonID, shape, color, fill=False, polygonType="", layer=0):
    traci._beginMessage(tc.CMD_SET_POLYGON_VARIABLE, tc.ADD, polygonID, 1+4 + 1+4+len(polygonType) + 1+1+1+1+1 + 1+1 + 1+4 + 1+1+len(shape)*(8+8))
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 5)
    traci._message.string += struct.pack("!Bi", tc.TYPE_STRING, len(polygonType)) + polygonType
    traci._message.string += struct.pack("!BBBBB", tc.TYPE_COLOR, int(color[0]), int(color[1]), int(color[2]), int(color[3]))
    traci._message.string += struct.pack("!BB", tc.TYPE_UBYTE, int(fill))
    traci._message.string += struct.pack("!Bi", tc.TYPE_INTEGER, layer)
    traci._message.string += struct.pack("!BB", tc.TYPE_POLYGON, len(shape))
    for p in shape:
        traci._message.string += struct.pack("!dd", *p)
    traci._sendExact()

def remove(polygonID, layer=0):
    traci._beginMessage(tc.CMD_SET_POLYGON_VARIABLE, tc.REMOVE, polygonID, 1+4)
    traci._message.string += struct.pack("!Bi", tc.TYPE_INTEGER, layer)
    traci._sendExact()
