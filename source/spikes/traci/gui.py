# -*- coding: utf-8 -*-
"""
@file    gui.py
@author  Michael Behrisch
@author  Daniel Krajzewicz
@date    2011-03-09
@version $Id: gui.py 11671 2012-01-07 20:14:30Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2011 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import struct, traci
import traci.constants as tc

DEFAULT_VIEW = 'View #0'
_RETURN_VALUE_FUNC = {tc.ID_LIST:           traci.Storage.readStringList,
                      tc.VAR_VIEW_ZOOM:     traci.Storage.readDouble,
                      tc.VAR_VIEW_OFFSET:   lambda(result): result.read("!dd"),
                      tc.VAR_VIEW_SCHEMA:   traci.Storage.readString,
                      tc.VAR_VIEW_BOUNDARY: lambda(result): (result.read("!dd"), result.read("!dd"))}
subscriptionResults = {}

def _getUniversal(varID, viewID):
    result = traci._sendReadOneStringCmd(tc.CMD_GET_GUI_VARIABLE, varID, viewID)
    return _RETURN_VALUE_FUNC[varID](result)

def getIDList():
    """getIDList(): -> list(string)
    
    Returns the list of available views (open windows).
    """
    return _getUniversal(tc.ID_LIST, "")

def getZoom(viewID=DEFAULT_VIEW):
    """getZoom(string): -> double
    
    Returns the current zoom factor.
    """
    return _getUniversal(tc.VAR_VIEW_ZOOM, viewID)

def getOffset(viewID=DEFAULT_VIEW):
    """getOffset(string): -> (double, double)
    
    Returns the x and y offset of the center of the current view.
    """
    return _getUniversal(tc.VAR_VIEW_OFFSET, viewID)

def getSchema(viewID=DEFAULT_VIEW):
    """getSchema(string): -> string
    
    Returns the name of the current coloring scheme.
    """
    return _getUniversal(tc.VAR_VIEW_SCHEMA, viewID)

def getBoundary(viewID=DEFAULT_VIEW):
    """getBoundary(string): -> ((double, double), (double, double))
    
    Returns the coordinates of the lower left and the upper right corner of the currently visible view.
    """
    return _getUniversal(tc.VAR_VIEW_BOUNDARY, viewID)


def subscribe(viewID, varIDs=(tc.VAR_VIEW_OFFSET,), begin=0, end=2**31-1):
    """subscribe(string, list(integer), double, double) -> None
    
    Subscribe to one or more gui values for the given interval.
    A call to this method clears all previous subscription results.
    """
    _resetSubscriptionResults()
    traci._subscribe(tc.CMD_SUBSCRIBE_GUI_VARIABLE, begin, end, viewID, varIDs)

def _resetSubscriptionResults():
    subscriptionResults.clear()

def _addSubscriptionResult(viewID, varID, data):
    if viewID not in subscriptionResults:
        subscriptionResults[viewID] = {}
    subscriptionResults[viewID][varID] = _RETURN_VALUE_FUNC[varID](data)

def getSubscriptionResults(viewID=None):
    """getSubscriptionResults(string) -> dict(integer: <value_type>)
    
    Returns the subscription results for the last time step and the given view.
    If no view id is given, all subscription results are returned in a dict.
    If the view id is unknown or the subscription did for any reason return no data,
    'None' is returned.
    It is not possible to retrieve older subscription results than the ones
    from the last time step.
    """
    if viewID == None:
        return subscriptionResults
    return subscriptionResults.get(viewID, None)


def setZoom(viewID, zoom):
    """setZoom(string, double) -> None
    
    Set the current zoom factor for the given view.
    """
    traci._sendDoubleCmd(tc.CMD_SET_GUI_VARIABLE, tc.VAR_VIEW_ZOOM, viewID, zoom)

def setOffset(viewID, x, y):
    """setOffset(string, double, double) -> None
    
    Set the current offset for the given view.
    """
    traci._beginMessage(tc.CMD_SET_GUI_VARIABLE, tc.VAR_VIEW_OFFSET, viewID, 1+8+8)
    traci._message.string += struct.pack("!Bdd", tc.POSITION_2D, x, y)
    traci._sendExact()

def setSchema(viewID, schemeName):
    """setSchema(string, string) -> None
    
    Set the current coloring scheme for the given view.
    """
    traci._sendStringCmd(tc.CMD_SET_GUI_VARIABLE, tc.VAR_VIEW_SCHEMA, viewID, schemeName)

def setBoundary(viewID, xmin, ymin, xmax, ymax):
    """setBoundary(string, double, double, double, double) -> None
    
    Set the current boundary for the given view (see getBoundary()).
    """
    traci._beginMessage(tc.CMD_SET_GUI_VARIABLE, tc.VAR_VIEW_BOUNDARY, viewID, 1+8+8+8+8)
    traci._message.string += struct.pack("!Bdddd", tc.TYPE_BOUNDINGBOX, xmin, ymin, xmax, ymax)
    traci._sendExact()

def screenshot(viewID, filename):
    """screenshot(string, string) -> None
    
    Save a screenshot for the given view to the given filename.
    The fileformat is guessed from the extension, the available 
    formats differ from platform to platform but should at least
    include ps, svg and pdf, on linux probably gif, png and jpg as well.
    """
    traci._sendStringCmd(tc.CMD_SET_GUI_VARIABLE, tc.VAR_SCREENSHOT, viewID, filename)

def trackVehicle(viewID, vehID):
    """trackVehicle(string, string) -> None
    
    Start visually tracking the given vehicle on the given view.
    """
    traci._sendStringCmd(tc.CMD_SET_GUI_VARIABLE, tc.VAR_TRACK_VEHICLE, viewID, vehID)
