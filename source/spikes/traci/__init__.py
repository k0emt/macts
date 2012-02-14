# -*- coding: utf-8 -*-
"""
@file    __init__.py
@author  Michael Behrisch
@author  Lena Kalleske
@date    2008-10-09
@version $Id: __init__.py 11671 2012-01-07 20:14:30Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import socket, time, struct
try:
    import traciemb
    _embedded = True
except ImportError:
    _embedded = False

_RESULTS = {0x00: "OK", 0x01: "Not implemented", 0xFF: "Error"}

def isEmbedded():
    return _embedded

def _STEPS2TIME(step):
    """Conversion from time steps in milliseconds to seconds as float"""
    return step/1000.

def _TIME2STEPS(time):
    """Conversion from (float) time in seconds to milliseconds as int"""
    return int(time*1000)

class FatalTraCIError(Exception):
    """Exception class for all TraCI errors"""
    def __init__(self, desc):
        self._desc = desc

class Message:
    """ A named tuple for internal usage.
    
    Simple "struct" for the composed message string
    together with a list of TraCI commands which are inside.
    """
    string = ""
    queue = []

class Storage:
    def __init__(self, content):
        self._content = content
        self._pos = 0

    def read(self, format):
        oldPos = self._pos
        self._pos += struct.calcsize(format)
        return struct.unpack(format, self._content[oldPos:self._pos])

    def readInt(self):
        return self.read("!i")[0]

    def readDouble(self):
        return self.read("!d")[0]

    def readLength(self):
        length = self.read("!B")[0]
        if length > 0:
            return length
        return self.read("!i")[0]

    def readString(self):
        length = self.read("!i")[0]
        return self.read("!%ss" % length)[0]

    def readStringList(self):
        n = self.read("!i")[0]
        list = []
        for i in range(n):
            list.append(self.readString())
        return list

    def readShape(self):
        length = self.read("!B")[0]
        return [self.read("!dd") for i in range(length)]


    def ready(self):
        return self._pos < len(self._content) 


import constants
import inductionloop, multientryexit, trafficlights
import lane, vehicle, vehicletype, route
import poi, polygon, junction, edge, simulation, gui

_modules = {constants.RESPONSE_SUBSCRIBE_INDUCTIONLOOP_VARIABLE: inductionloop,
            constants.RESPONSE_SUBSCRIBE_MULTI_ENTRY_EXIT_DETECTOR_VARIABLE:\
            multientryexit,
            constants.RESPONSE_SUBSCRIBE_TL_VARIABLE: trafficlights,
            constants.RESPONSE_SUBSCRIBE_LANE_VARIABLE: lane,
            constants.RESPONSE_SUBSCRIBE_VEHICLE_VARIABLE: vehicle,
            constants.RESPONSE_SUBSCRIBE_VEHICLETYPE_VARIABLE: vehicletype,
            constants.RESPONSE_SUBSCRIBE_ROUTE_VARIABLE: route,
            constants.RESPONSE_SUBSCRIBE_POI_VARIABLE: poi,
            constants.RESPONSE_SUBSCRIBE_POLYGON_VARIABLE: polygon,
            constants.RESPONSE_SUBSCRIBE_JUNCTION_VARIABLE: junction,
            constants.RESPONSE_SUBSCRIBE_EDGE_VARIABLE: edge,
            constants.RESPONSE_SUBSCRIBE_SIM_VARIABLE: simulation,
            constants.RESPONSE_SUBSCRIBE_GUI_VARIABLE: gui}
_connections = {}
_message = Message()

def _recvExact():
    try:
        result = ""
        while len(result) < 4:
            t = _connections[""].recv(4 - len(result))
            if not t:
                return None
            result += t
        length = struct.unpack("!i", result)[0] - 4
        result = ""
        while len(result) < length:
            t = _connections[""].recv(length - len(result))
            if not t:
                return None
            result += t
        return Storage(result)
    except socket.error:
        return None

def _sendExact():
    if _embedded:
        result = Storage(traciemb.execute(_message.string))
    else:
        length = struct.pack("!i", len(_message.string)+4)
        _connections[""].send(length + _message.string)
        result = _recvExact()
    if not result:
        _connections[""].close()
        del _connections[""]
        raise FatalTraCIError("connection closed by SUMO")
    for command in _message.queue:
        prefix = result.read("!BBB")
        err = result.readString()
        if prefix[2] or err:
            print prefix, _RESULTS[prefix[2]], err
        elif prefix[1] != command:
            print "Error! Received answer %s for command %s." % (prefix[1],
                                                                 command)
        elif prefix[1] == constants.CMD_STOP:
            length = result.read("!B")[0] - 1
            result.read("!%sx" % length)
    _message.string = ""
    _message.queue = []
    return result

def _beginMessage(cmdID, varID, objID, length=0):
    _message.queue.append(cmdID)
    length += 1+1+1+4+len(objID)
    if length<=255:
        _message.string += struct.pack("!BBBi", length,
                                       cmdID, varID, len(objID)) + objID
    else:
        _message.string += struct.pack("!BiBBi", 0, length+4,
                                       cmdID, varID, len(objID)) + objID

def _sendReadOneStringCmd(cmdID, varID, objID):
    _beginMessage(cmdID, varID, objID)
    return _checkResult(cmdID, varID, objID)

def _sendIntCmd(cmdID, varID, objID, value):
    _beginMessage(cmdID, varID, objID, 1+4)
    _message.string += struct.pack("!Bi", constants.TYPE_INTEGER, value)
    _sendExact()

def _sendDoubleCmd(cmdID, varID, objID, value):
    _beginMessage(cmdID, varID, objID, 1+8)
    _message.string += struct.pack("!Bd", constants.TYPE_DOUBLE, value)
    _sendExact()

def _sendStringCmd(cmdID, varID, objID, value):
    _beginMessage(cmdID, varID, objID, 1+4+len(value))
    _message.string += struct.pack("!Bi", constants.TYPE_STRING,
                                   len(value)) + value
    _sendExact()

def _checkResult(cmdID, varID, objID):
    result = _sendExact()
    result.readLength()
    response, retVarID = result.read("!BB")
    objectID = result.readString()
    if response - cmdID != 16 or retVarID != varID or objectID != objID:
        print "Error! Received answer %s,%s,%s for command %s,%s,%s."\
              % (response, retVarID, objectID, cmdID, varID, objID)
    result.read("!B")     # Return type of the variable
    return result

def _readSubscription(result):
    result.readLength()
    response = result.read("!B")[0]
    objectID = result.readString()
    numVars = result.read("!B")[0]
    while numVars > 0:
        varID = result.read("!B")[0]
        status, varType = result.read("!BB")
        if status:
            print "Error!", result.readString()
        elif response in _modules:
            _modules[response]._addSubscriptionResult(objectID, varID, result)
        numVars -= 1
    return response, objectID

def _subscribe(cmdID, begin, end, objID, varIDs):
    _message.queue.append(cmdID)
    length = 1+1+4+4+4+len(objID)+1+len(varIDs)
    if length<=255:
        _message.string += struct.pack("!B", length)
    else:
        _message.string += struct.pack("!Bi", 0, length+4)
    _message.string += struct.pack("!Biii", cmdID,
                                   begin, end, len(objID)) + objID
    _message.string += struct.pack("!B", len(varIDs))
    for v in varIDs:
        _message.string += struct.pack("!B", v)
    result = _sendExact()
    response, objectID = _readSubscription(result)
    if response - cmdID != 16 or objectID != objID:
        print "Error! Received answer %s,%s for subscription command %s,%s."\
              % (response, objectID, cmdID, objID)

def init(port=8813, numRetries=10, host="localhost", label="default"):
    if _embedded:
        return getVersion()
    _connections[""] = _connections[label] = socket.socket()
    for wait in range(numRetries):
        try:
            _connections[label].connect((host, port))
            _connections[label].setsockopt(socket.IPPROTO_TCP,
                                           socket.TCP_NODELAY, 1)
            break
        except socket.error:
            time.sleep(wait)
    return getVersion()

def simulationStep(step=0):
    """
    Make simulation step and simulate up to "step" second in sim time.
    """
    _message.queue.append(constants.CMD_SIMSTEP2)
    _message.string += struct.pack("!BBi", 1+1+4, constants.CMD_SIMSTEP2, step)
    result = _sendExact()
    for module in _modules.itervalues():
        module._resetSubscriptionResults()
    numSubs = result.readInt()
    while numSubs > 0:
        _readSubscription(result)
        numSubs -= 1

def getVersion():
    command = constants.CMD_GETVERSION
    _message.queue.append(command)
    _message.string += struct.pack("!BB", 1+1, command)
    result = _sendExact()
    result.readLength()
    response = result.read("!B")[0]
    if response != command:
        print "Error! Received answer %s for command %s." % (response, command)
    return result.readInt(), result.readString()

def close():
    if "" in _connections:
        _message.queue.append(constants.CMD_CLOSE)
        _message.string += struct.pack("!BB", 1+1, constants.CMD_CLOSE)
        _sendExact()
        _connections[""].close()
        del _connections[""]

def switch(label):
    _connections[""] = _connections[label]
