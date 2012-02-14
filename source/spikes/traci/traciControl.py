# -*- coding: utf-8 -*-
"""
@file    traciControl.py
@author  Michael Behrisch
@author  Lena Kalleske
@author  Daniel Krajzewicz
@date    2008-10-09
@version $Id: traciControl.py 11671 2012-01-07 20:14:30Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import socket, time, struct
import traciconstants as tc

RESULTS = {0x00: "OK", 0x01: "Not implemented", 0xFF: "Error"}

class FatalTraCIError:
    def __init__(self, desc):
        self._desc = desc

class Phase:
    def __init__(self, duration, duration1, duration2, phaseDef):
        self._duration = duration
        self._duration1 = duration1
        self._duration2 = duration2
        self._phaseDef = phaseDef
        
    def write(self):
        print("Phase:")
        print("duration: ", self._duration)
        print("duration1: ", self._duration1)
        print("duration2: ", self._duration2)
        print("phaseDef: ", self._phaseDef)
        
class Logic:
    def __init__(self, subID, type, subParameter, currentPhaseIndex, phases):
        self._subID = subID
        self._type = type
        self._subParameter = subParameter
        self._currentPhaseIndex = currentPhaseIndex
        self._phases = phases
        
    def write(self):
        print("Logic:")
        print("subID:", self._subID)
        print("type:", self._type)
        print("subParameter:", self._subParameter)
        print("currentPhaseIndex:", self._currentPhaseIndex)
        for i in range(len(self._phases)):
            self._phases[i].write()

class Message:
    string = ""
    queue = []



_socket = socket.socket()
_message = Message()

class Storage:
    def __init__(self, content):
        self._content = content
        self._pos = 0

    def read(self, format):
        oldPos = self._pos
        self._pos += struct.calcsize(format)
        return struct.unpack(format, self._content[oldPos:self._pos])

    def readString(self):
        length = self.read("!i")[0]
        return self.read("!%ss" % length)[0]
    
    def readStringList(self):
        n = self.read("!i")[0]
        list = []
        for i in range(n):
            list.append(self.readString())
        return list     
    
    def ready(self):
        return self._pos < len(self._content) 


def _recvExact():
    global _socket
    try:
        result = ""
        while len(result) < 4:
            t = _socket.recv(4 - len(result))
            if not t:
                return None
            result += t
        length = struct.unpack("!i", result)[0] - 4
        result = ""
        while len(result) < length:
            t = _socket.recv(length - len(result))
            if not t:
                return None
            result += t
        return Storage(result)
    except socket.error:
        return None

def _sendExact():
    global _socket
    length = struct.pack("!i", len(_message.string)+4)
    _socket.send(length)
    _socket.send(_message.string)
    _message.string = ""
    result = _recvExact()
    if not result:
        _socket.close()
        _socket = None
        raise FatalTraCIError("connection closed by SUMO")
    for command in _message.queue:
        prefix = result.read("!BBB")
        err = result.readString()
        if prefix[2] or err:
            print prefix, RESULTS[prefix[2]], err
        elif prefix[1] != command:
            print "Error! Received answer %s for command %s." % (prefix[1], command)
        elif prefix[1] == tc.CMD_STOP:
            length = result.read("!B")[0] - 1
            result.read("!%sx" % length)
    _message.queue = []
    return result

def readHead(result):
    length = result.read("!B")[0]     # Length
    if length==0:
        length = result.read("!i")[0]
    result.read("!B")     # Identifier
    result.read("!B")     # Variable
    result.readString()   # Induction Loop ID // Multi-Entry/Multi-Exit Detector ID // Traffic Light ID
    result.read("!B")     # Return type of the variable
    

def buildSendReadNew1StringParamCmd(domainID, cmdID, objID):
    _message.queue.append(domainID)
    length = 1+1+1+4+len(objID)
    if length<=255:
        _message.string += struct.pack("!BBBi", length, domainID, cmdID, len(objID)) + objID
    else:
        _message.string += struct.pack("!BiBBi", 0, length+4, domainID, cmdID, len(objID)) + objID
    result = _sendExact()
    readHead(result)
    return result

def beginChangeMessage(domainID, length, cmdID, objID):
    _message.queue.append(domainID)
    if length<=255:
        _message.string += struct.pack("!BBBi", length, domainID, cmdID, len(objID)) + objID
    else:
        _message.string += struct.pack("!BiBBi", 0, length+4, domainID, cmdID, len(objID)) + objID

def initTraCI(port, numRetries=10):
    global _socket
    _socket = socket.socket()
    for wait in range(numRetries):
        try:
            _socket.connect(("localhost", port))
            _socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            break
        except socket.error:
            time.sleep(wait)


def cmdSimulationStep(step, position=True):
    """
    Make simulation step and simulate up to "step" second in sim time.
    If *position* is True, then roadmap position coordinates (vehicle number,
    edge number, distance from start) will be returned.
    If *position* is False - step is made and only empty list is returned.
    """
    if position:
        return_type = tc.POSITION_ROADMAP
    else:
        return_type = tc.POSITION_NONE

    _message.queue.append(tc.CMD_SIMSTEP)
    _message.string += struct.pack("!BBiB", 1+1+4+1, tc.CMD_SIMSTEP, step, return_type)
    result = _sendExact()
    updates = []
    while result.ready():
        if result.read("!BB")[1] == tc.CMD_MOVENODE:
            updates.append((result.read("!iiB")[0], result.readString(), result.read("!dB")[0]))
    return updates

def cmdSimulationStep2(step):
    """
    Make simulation step and simulate up to "step" second in sim time.
    """
    _message.queue.append(tc.CMD_SIMSTEP2)
    _message.string += struct.pack("!BBi", 1+1+4, tc.CMD_SIMSTEP2, step)
    result = _sendExact()
    subscriptions = []
#    while result.ready():
#        if result.read("!BB")[1] == tc.CMD_MOVENODE:
#            updates.append((result.read("!iiB")[0], result.readString(), result.read("!dB")[0]))
    return subscriptions

def cmdSubscribeDomainVehicle_Position(position=True):
    if position:
        return_type = tc.POSITION_ROADMAP
    else:
        return_type = tc.POSITION_NONE

    _message.queue.append(tc.CMD_SIMSTEP)
    _message.string += struct.pack("!BBiB", 1+1+8+1, tc.CMD_SIMSTEP, step, return_type)
    result = _sendExact()
    updates = []
    while result.ready():
        if result.read("!BB")[1] == tc.CMD_MOVENODE:
            updates.append((result.read("!iiB")[0], result.readString(), result.read("!dB")[0]))
    return updates

# ===================================================
# induction loop interaction
# ===================================================
def cmdGetInductionLoopVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.ID_LIST, "x")
    return result.readStringList() # Variable value 

def cmdGetInductionLoopVariable_position(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.VAR_POSITION, IndLoopID)
    return result.read("!d")[0] # Variable value

def cmdGetInductionLoopVariable_laneID(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.VAR_LANE_ID, IndLoopID)
    return result.readString()

def cmdGetInductionLoopVariable_lastStepVehicleNumber(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.LAST_STEP_VEHICLE_NUMBER, IndLoopID)
    return result.read("!i")[0] # Variable value

def cmdGetInductionLoopVariable_lastStepMeanSpeed(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.LAST_STEP_MEAN_SPEED, IndLoopID)
    return result.read("!d")[0] # Variable value    

def cmdGetInductionLoopVariable_vehicleIds(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.LAST_STEP_VEHICLE_ID_LIST, IndLoopID)
    return result.readStringList() # Variable value
  
def cmdGetInductionLoopVariable_lastStepOccupancy(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.LAST_STEP_OCCUPANCY, IndLoopID)
    return result.read("!d")[0] # Variable value
  
def cmdGetInductionLoopVariable_lastMeanLength(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.LAST_STEP_LENGTH, IndLoopID)
    return result.read("!d")[0] # Variable value
  
def cmdGetInductionLoopVariable_timeSinceDetection(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.LAST_STEP_TIME_SINCE_DETECTION, IndLoopID)
    return result.read("!d")[0] # Variable value
  
def cmdGetInductionLoopVariable_vehicleData(IndLoopID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_INDUCTIONLOOP_VARIABLE, tc.LAST_STEP_VEHICLE_DATA, IndLoopID)
    q = result.read("!Bi")[1] # Length
    print q
    nbData = result.read("!i")[0]    # Number of data
    print "%s %s", (IndLoopID, nbData)
    data = []
    for i in range(nbData):
        result.read("!B")
        vehID = result.readString()
        print " " + vehID 
        result.read("!B")
        length = result.read("!d")[0]
        print " %s" % length
        result.read("!B")
        entryTime = result.read("!d")[0]
        print " %s" % entryTime
        result.read("!B")
        leaveTime = result.read("!d")[0]
        print " %s" % leaveTime
        result.read("!B")
        typeID = result.readString()
        print " %s" % typeID 
        data.append( [ vehID, length, entryTime, leaveTime, typeID ] ) 
    return data


# ===================================================
# multi-entry/multi-exit detector interaction
# ===================================================
def cmdGetMultiEntryExitDetectorVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_MULTI_ENTRY_EXIT_DETECTOR_VARIABLE, tc.ID_LIST, "x")
    return result.readStringList() # Variable value 

def cmdGetMultiEntryExitDetectorVariable_lastStepVehicleNumber(MultiEntryExitDetID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_MULTI_ENTRY_EXIT_DETECTOR_VARIABLE, tc.LAST_STEP_VEHICLE_NUMBER, MultiEntryExitDetID)
    return result.read("!i")[0] # Variable value

def cmdGetMultiEntryExitDetectorVariable_lastStepMeanSpeed(MultiEntryExitDetID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_MULTI_ENTRY_EXIT_DETECTOR_VARIABLE, tc.LAST_STEP_MEAN_SPEED, MultiEntryExitDetID)
    return result.read("!d")[0] # Variable value    

def cmdGetMultiEntryExitDetectorVariable_vehicleIds(MultiEntryExitDetID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_MULTI_ENTRY_EXIT_DETECTOR_VARIABLE, tc.LAST_STEP_VEHICLE_ID_LIST, MultiEntryExitDetID)
    return result.readStringList() # Variable value

def cmdGetMultiEntryExitDetectorVariable_haltingNumber(MultiEntryExitDetID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_MULTI_ENTRY_EXIT_DETECTOR_VARIABLE, tc.LAST_STEP_VEHICLE_HALTING_NUMBER, MultiEntryExitDetID)
    return result.read("!i")[0] # Variable value



# ===================================================
# traffic lights interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetTrafficLightsVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.ID_LIST, "x")
    return result.readStringList()  # Variable value 

def cmdGetTrafficLightsVariable_stateRYG(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_RED_YELLOW_GREEN_STATE, TLID)
    return result.readString() # Variable value 

def cmdGetTrafficLightsVariable_statePBY(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_PHASE_BRAKE_YELLOW_STATE, TLID)
    return result.readStringList() # Variable value     

def cmdGetTrafficLightsVariable_completeDefinitionRYG(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_COMPLETE_DEFINITION_RYG, TLID)
    result.read("!i") # Length
    result.read("!B") # Type of Number of logics
    nbLogics = result.read("!i")[0]    # Number of logics
    logics = []
    for i in range(nbLogics):
        result.read("!B")                       # Type of SubID
        subID = result.readString()
        result.read("!B")                       # Type of Type
        type = result.read("!i")[0]             # Type
        result.read("!B")                       # Type of SubParameter
        subParameter = result.read("!i")[0]     # SubParameter
        result.read("!B")                       # Type of Current phase index
        currentPhaseIndex = result.read("!i")[0]    # Current phase index
        result.read("!B")                       # Type of Number of phases
        nbPhases = result.read("!i")[0]         # Number of phases
        phases = []
        for j in range(nbPhases):
            result.read("!B")                   # Type of Duration
            duration = result.read("!i")[0]     # Duration
            result.read("!B")                   # Type of Duration1
            duration1 = result.read("!i")[0]    # Duration1
            result.read("!B")                   # Type of Duration2
            duration2 = result.read("!i")[0]    # Duration2
            result.read("!B")                   # Type of Phase Definition
            phaseDef = result.readString()      # Phase Definition
            phase = Phase(duration, duration1, duration2, phaseDef)
            phases.append(phase)
        logic = Logic(subID, type, subParameter, currentPhaseIndex, phases)
        logics.append(logic)
    return logics

def cmdGetTrafficLightsVariable_controlledLanes(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_CONTROLLED_LANES, TLID)
    return result.readStringList() # Variable value 

def cmdGetTrafficLightsVariable_controlledLinks(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_CONTROLLED_LINKS, TLID)
    result.read("!iB")
    nbSignals = result.read("!i")[0] # Length
    signals = []
    for i in range(nbSignals):
        result.read("!B")                           # Type of Number of Controlled Links
        nbControlledLinks = result.read("!i")[0]    # Number of Controlled Links
        controlledLinks = []
        for j in range(nbControlledLinks):
            result.read("!B")                       # Type of Link j
            link = result.readStringList()          # Link j
            controlledLinks.append(link)
        signals.append(controlledLinks)
    return signals


def cmdGetTrafficLightsVariable_program(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_CURRENT_PROGRAM, TLID)
    return result.readString() # Variable value 

def cmdGetTrafficLightsVariable_phase(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_CURRENT_PHASE, TLID)
    return result.read("!i")[0] # Variable value

def cmdGetTrafficLightsVariable_nextSwitchTime(TLID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_TL_VARIABLE, tc.TL_NEXT_SWITCH, TLID)
    return result.read("!i")[0] # Variable value


# ---------------------------------------------------
# change state
# ---------------------------------------------------
def cmdChangeTrafficLightsVariable_stateRYG(TLID, state):
    beginChangeMessage(tc.CMD_SET_TL_VARIABLE, 1+1+1+4+len(TLID)+1+4+len(state), tc.TL_RED_YELLOW_GREEN_STATE, TLID)
    _message.string += struct.pack("!B", tc.TYPE_STRING)
    _message.string += struct.pack("!i", len(state)) + state
    _sendExact()

def cmdChangeTrafficLightsVariable_phaseIndex(TLID, index):
    beginChangeMessage(tc.CMD_SET_TL_VARIABLE, 1+1+1+4+len(TLID)+1+4, tc.TL_PHASE_INDEX, TLID)
    _message.string += struct.pack("!Bi", tc.TYPE_INTEGER, index)
    _sendExact()

def cmdChangeTrafficLightsVariable_programID(TLID, programID):
    beginChangeMessage(tc.CMD_SET_TL_VARIABLE, 1+1+1+4+len(TLID)+1+4+len(programID), tc.TL_PROGRAM, TLID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(programID)) + programID
    _sendExact()

def cmdChangeTrafficLightsVariable_phaseDuration(TLID, phaseDuration):
    beginChangeMessage(tc.CMD_SET_TL_VARIABLE, 1+1+1+4+len(TLID)+1+4, tc.TL_PHASE_DURATION, TLID)
    _message.string += struct.pack("!Bi", tc.TYPE_INTEGER, phaseDuration)
    _sendExact()

def cmdChangeTrafficLightsVariable_completeRYG(TLID, tls):
    length = 1+1+1+4+len(TLID) # basic
    itemNo = 0
    length = length + 1+4 + 1+4+len(tls._subID) + 1+4 + 1+4 + 1+4 + 1+4 # tls parameter
    itemNo = 1+1+1+1+1
    for p in tls._phases:
        length = length + 1+4 + 1+4 + 1+4 + 1+4+len(p._phaseDef)
        itemNo = itemNo + 4
    beginChangeMessage(tc.CMD_SET_TL_VARIABLE, length, tc.TL_COMPLETE_PROGRAM_RYG, TLID)
    _message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, itemNo) # itemNo
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(tls._subID)) + tls._subID # programID
    _message.string += struct.pack("!Bi", tc.TYPE_INTEGER, 0) # type
    _message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 0) # subitems
    _message.string += struct.pack("!Bi", tc.TYPE_INTEGER, tls._currentPhaseIndex) # index
    _message.string += struct.pack("!Bi", tc.TYPE_INTEGER, len(tls._phases)) # phaseNo
    for p in tls._phases:
        _message.string += struct.pack("!BiBiBi", tc.TYPE_INTEGER, p._duration, tc.TYPE_INTEGER, p._duration1, tc.TYPE_INTEGER, p._duration2)
        _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(p._phaseDef)) + p._phaseDef
    _sendExact()
    
    


# ===================================================
# vehicle interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetVehicleVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.ID_LIST, "")
    return result.readStringList()  # Variable value 

def cmdGetVehicleVariable_speed(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_SPEED, vehID)
    return result.read("!d")[0] # Variable value

def cmdGetVehicleVariable_position(vehID):
    """
    Returns the position of the named vehicle within the last step [m,m]
    """
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_POSITION, vehID)
    return result.read("!dd")

def cmdGetVehicleVariable_angle(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_ANGLE, vehID)
    return result.read("!d")[0] # Variable value

def cmdGetVehicleVariable_roadID(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_ROAD_ID, vehID)
    return result.readString() # Variable value

def cmdGetVehicleVariable_laneID(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_LANE_ID, vehID)
    return result.readString() # Variable value

def cmdGetVehicleVariable_laneIndex(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_LANE_INDEX, vehID)
    return result.read("!i")[0] # Variable value

def cmdGetVehicleVariable_typeID(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_TYPE, vehID)
    return result.readString() # Variable value

def cmdGetVehicleVariable_routeID(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_ROUTE_ID, vehID)
    return result.readString() # Variable value

def cmdGetVehicleVariable_lanePosition(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_LANEPOSITION, vehID)
    return result.read("!d")[0] # Variable value

def cmdGetVehicleVariable_color(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_COLOR, vehID)
    return result.read("!BBBB") # Variable value

def cmdGetVehicleVariable_bestLanes(vehID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_BEST_LANES, vehID)
    result.read("!iB")
    nbLanes = result.read("!i")[0] # Length
    lanes = []
    for i in range(nbLanes):
        result.read("!B")
        laneID = result.readString()
        length = result.read("!Bf")[1]
        occupation = result.read("!Bf")[1]
        offset = result.read("!Bb")[1]
        allowsContinuation = result.read("!BB")[1]
        nextLanesNo = result.read("!Bi")[1]
        nextLanes = []
        for j in range(nextLanesNo):
            nextLanes.append(result.readString())
        lanes.append( [laneID, length, occupation, offset, allowsContinuation, nextLanes ] )
    return lanes


# ---------------------------------------------------
# change state
# ---------------------------------------------------
def cmdChangeVehicleVariable_maxSpeed(vehID, speed):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4, tc.CMD_SETMAXSPEED, vehID)
    _message.string += struct.pack("!Bf", tc.TYPE_FLOAT, speed)
    _sendExact()

def cmdChangeVehicleVariable_speed(vehID, speed):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+8, tc.VAR_SPEED, vehID)
    _message.string += struct.pack("!Bd", tc.TYPE_DOUBLE, speed)
    _sendExact()

def cmdChangeVehicleVariable_lanePosition(vehID, position):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+8, tc.VAR_LANEPOSITION, vehID)
    _message.string += struct.pack("!Bd", tc.TYPE_DOUBLE, position)
    _sendExact()

def cmdChangeVehicleVariable_stop(vehID, edgeID, pos, laneIndex, duration):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4+1+4+len(edgeID)+1+4+1+1+1+4, tc.CMD_STOP, vehID)
    _message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 4)
    _message.string += struct.pack("!B", tc.TYPE_STRING)
    _message.string += struct.pack("!i", len(edgeID)) + edgeID
    _message.string += struct.pack("!BfBBBi", tc.TYPE_FLOAT, pos, tc.TYPE_BYTE, laneIndex, tc.TYPE_INTEGER, duration)
    _sendExact()

def cmdChangeVehicleVariable_changeLane(vehID, laneIndex, duration):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4+1+1+1+4, tc.CMD_CHANGELANE, vehID)
    _message.string += struct.pack("!BiBBBi", tc.TYPE_COMPOUND, 2, tc.TYPE_BYTE, laneIndex, tc.TYPE_INTEGER, duration)
    _sendExact()

def cmdChangeVehicleVariable_slowDown(vehID, speed, duration):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4+1+4+1+4, tc.CMD_SLOWDOWN, vehID)
    _message.string += struct.pack("!BiBfBi", tc.TYPE_COMPOUND, 2, tc.TYPE_FLOAT, speed, tc.TYPE_INTEGER, duration)
    _sendExact()

def cmdChangeVehicleVariable_changeTarget(vehID, edgeID):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4+len(edgeID), tc.CMD_CHANGETARGET, vehID)
    _message.string += struct.pack("!B", tc.TYPE_STRING)
    _message.string += struct.pack("!i", len(edgeID)) + edgeID
    _sendExact()

def cmdChangeVehicleVariable_changeRoute(vehID, edgeList):
    """
    changes the vehicle route to given edges list.
    The first edge in the list has to be the one that the vehicle is at at the moment.
    
    example usasge:
    cmdChangeVehicleVariable_changeRoute('1', ['1', '2', '4', '6', '7'])
    
    this changes route for vehicle id 1 to edges 1-2-4-6-7
    """
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4+sum(map(len, edgeList))+4*len(edgeList), tc.VAR_ROUTE, vehID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRINGLIST, len(edgeList))
    for edge in edgeList:
        _message.string += struct.pack("!i", len(edge)) + edge
    _sendExact()

def cmdChangeVehicleVariable_moveTo(vehID, laneID, pos):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4+1+4+len(laneID)+8, tc.VAR_MOVE_TO, vehID)
    _message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 2)
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(laneID)) + laneID
    _message.string += struct.pack("!Bd", tc.TYPE_DOUBLE, pos)
    _sendExact()

def cmdChangeVehicleVariable_reroute(vehID):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+5, tc.CMD_REROUTE_TRAVELTIME, vehID)
    _message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 0)
    _sendExact()

def cmdChangeVehicleVariable_color(vehID, color):
    beginChangeMessage(tc.CMD_SET_VEHICLE_VARIABLE, 1+1+1+4+len(vehID)+1+4, tc.VAR_COLOR, vehID)
    _message.string += struct.pack("!BBBBB", tc.TYPE_COLOR, int(color[0]), int(color[1]), int(color[2]), int(color[3]))
    _sendExact()


# ===================================================
# vehicle type interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetVehicleTypeVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLETYPE_VARIABLE, tc.ID_LIST, "x")
    return result.readStringList()  # Variable value 

def cmdGetVehicleTypeVariable_length(vTypeID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_VEHICLETYPE_VARIABLE, tc.VAR_LENGTH, vTypeID)
    return result.read("!d")[0] # Variable value



# ===================================================
# route interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetRouteVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_ROUTE_VARIABLE, tc.ID_LIST, "x")
    return result.readStringList() # Variable value 

def cmdGetRouteVariable_edges(routeID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_ROUTE_VARIABLE, tc.VAR_EDGES, routeID)
    return result.readStringList() # Variable value 


# ===================================================
# poi interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetPoiVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POI_VARIABLE, tc.ID_LIST, "")
    return result.readStringList() # Variable value 

def cmdGetPoiVariable_type(poiID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POI_VARIABLE, tc.VAR_TYPE, poiID)
    return result.readString() # Variable value

def cmdGetPoiVariable_color(poiID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POI_VARIABLE, tc.VAR_COLOR, poiID)
    return result.read("!BBBB") # Variable value

def cmdGetPoiVariable_position(poiID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POI_VARIABLE, tc.VAR_POSITION, poiID)
    return result.read("!dd") # Variable value 


# ===================================================
# polygon interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetPolygonVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POLYGON_VARIABLE, tc.ID_LIST, "")
    return result.readStringList() # Variable value 

def cmdGetPolygonVariable_type(polyID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POLYGON_VARIABLE, tc.VAR_TYPE, poiID)
    return result.readString() # Variable value

def cmdGetPolygonVariable_color(polyID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POLYGON_VARIABLE, tc.VAR_COLOR, poiID)
    return result.read("!BBBB") # Variable value

def cmdGetPolygonVariable_shape(polyID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_POLYGON_VARIABLE, tc.VAR_SHAPE, poiID)
    length = result.read("!B")[0]
    shape = []
    for i in length:
       shape.append(result.read("!dd"))


# ---------------------------------------------------
# change state
# ---------------------------------------------------
def cmdChangePolygonVariable_type(polyID, type):
    beginChangeMessage(tc.CMD_SET_POLYGON_VARIABLE, 1+1+1+4+len(polyID)+1+4+len(type), tc.VAR_TYPE, polyID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(type)) + type
    _sendExact()

def cmdChangePolygonVariable_color(polyID, color):
    beginChangeMessage(tc.CMD_SET_POLYGON_VARIABLE, 1+1+1+4+len(polyID)+1+4, tc.VAR_COLOR, polyID)
    _message.string += struct.pack("!BBBBB", tc.TYPE_COLOR, int(color[0]), int(color[1]), int(color[2]), int(color[3]))
    _sendExact()

def cmdChangePolygonVariable_shape(polyID, shape):
    beginChangeMessage(tc.CMD_SET_POLYGON_VARIABLE, 1+1+1+4+len(polyID)+1+1+8*len(shape), tc.VAR_SHAPE, polyID)
    _message.string += struct.pack("!BB", tc.TYPE_POLYGON, len(shape))
    for p in shape:
        _message.string += struct.pack("!dd", p[0], p[1])
    _sendExact()

def cmdChangePolygonVariable_add(polyID, type, color, fill, layer, shape):
    length = 1+1+1+4+len(polyID)+ 1+4 + 1+4+len(type) + 1+4 + 1+1 + 1+4 + 1+1+len(shape)*8
    beginChangeMessage(tc.CMD_SET_POLYGON_VARIABLE, length, tc.ADD, polyID)
    _message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 5)
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(type)) + type
    _message.string += struct.pack("!BBBBB", tc.TYPE_COLOR, int(color[0]), int(color[1]), int(color[2]), int(color[3]))
    if fill:
        _message.string += struct.pack("!BB", tc.TYPE_UBYTE, 1)
    else:
        _message.string += struct.pack("!BB", tc.TYPE_UBYTE, 0)
    _message.string += struct.pack("!Bi", tc.TYPE_INTEGER, layer)
    _message.string += struct.pack("!BB", tc.TYPE_POLYGON, len(shape))
    for p in shape:
        _message.string += struct.pack("!dd", p[0], p[1])
    _sendExact()



# ===================================================
# nodes (junction/intersection) interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetJunctionVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_JUNCTION_VARIABLE, tc.ID_LIST, "x")
    return result.readStringList()  # Variable value 

def cmdGetJunctionVariable_position(nodeID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_JUNCTION_VARIABLE, tc.VAR_POSITION, nodeID)
    return result.read("!dd") # Variable value



# ===================================================
# lanes interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetLaneVariable_idList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.ID_LIST, "x")
    return result.readStringList()  # Variable value 

def cmdGetLaneVariable_length(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_LENGTH, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_speed(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_MAXSPEED, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_allowed(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.LANE_ALLOWED, laneID)
    return result.readStringList()  # Variable value 

def cmdGetLaneVariable_disallowed(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.LANE_DISALLOWED, laneID)
    return result.readStringList()  # Variable value 

def cmdGetLaneVariable_linkNumber(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.LANE_LINK_NUMBER, laneID)
    return result.read("!B")[0] # Variable value

def cmdGetLaneVariable_edgeID(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.LANE_EDGE_ID, laneID)
    return result.readString() # Variable value

def cmdGetLaneVariable_speed(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_MAXSPEED, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_CO2emission(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_CO2EMISSION, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_COemission(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_COEMISSION, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_HCemission(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_HCEMISSION, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_PMxemission(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_PMXEMISSION, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_NOxemission(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_NOXEMISSION, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_fuelConsumption(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_FUELCONSUMPTION, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_noiseEmission(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.VAR_NOISEEMISSION, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_meanSpeed(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.LAST_STEP_MEAN_SPEED, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_occupancy(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.LAST_STEP_OCCUPANCY, laneID)
    return result.read("!d")[0] # Variable value

def cmdGetLaneVariable_vehicleIDs(laneID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_LANE_VARIABLE, tc.LAST_STEP_VEHICLE_ID_LIST, laneID)
    return result.readStringList()  # Variable value 


# ---------------------------------------------------
# change state
# ---------------------------------------------------
def cmdChangeLaneVariable_allowed(laneID, allowedClasses):
    beginChangeMessage(tc.CMD_SET_LANE_VARIABLE, 1+1+1+4+len(laneID)+1+4+sum(map(len, allowedClasses))+4*len(allowedClasses), tc.LANE_ALLOWED, laneID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRINGLIST, len(allowedClasses))
    for c in allowedClasses:
        _message.string += struct.pack("!i", len(c)) + c
    _sendExact()

def cmdChangeLaneVariable_disallowed(laneID, disallowedClasses):
    beginChangeMessage(tc.CMD_SET_LANE_VARIABLE, 1+1+1+4+len(laneID)+1+4+sum(map(len, disallowedClasses))+4*len(disallowedClasses), tc.LANE_DISALLOWED, laneID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRINGLIST, len(disallowedClasses))
    for c in disallowedClasses:
        _message.string += struct.pack("!i", len(c)) + c
    _sendExact()

def cmdChangeLaneVariable_maxSpeed(laneID, speed):
    beginChangeMessage(tc.CMD_SET_LANE_VARIABLE, 1+1+1+4+len(laneID)+1+4, tc.VAR_MAXSPEED, laneID)
    _message.string += struct.pack("!Bf", tc.TYPE_FLOAT, speed)
    _sendExact()

def cmdChangeLaneVariable_length(laneID, length):
    beginChangeMessage(tc.CMD_SET_LANE_VARIABLE, 1+1+1+4+len(laneID)+1+4, tc.VAR_LENGTH, laneID)
    _message.string += struct.pack("!Bf", tc.TYPE_FLOAT, length)
    _sendExact()



# ===================================================
# simulation interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetSimulationVariable_currentTime():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_SIM_VARIABLE, tc.VAR_TIME_STEP, "x")
    return result.read("!i")[0] # Variable value

def cmdGetSimulationVariable_departedIDList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_SIM_VARIABLE, tc.VAR_DEPARTED_VEHICLES_IDS, "x")
    return result.readStringList()  # Variable value 

def cmdGetSimulationVariable_arrivedIDList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_SIM_VARIABLE, tc.VAR_ARRIVED_VEHICLES_IDS, "x")
    return result.readStringList()  # Variable value 

def cmdGetSimulationVariable_startingTeleportIDList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_SIM_VARIABLE, tc.VAR_TELEPORT_STARTING_VEHICLES_IDS, "x")
    return result.readStringList()  # Variable value 

def cmdGetSimulationVariable_endingTeleportIDList():
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_SIM_VARIABLE, tc.VAR_TELEPORT_ENDING_VEHICLES_IDS, "x")
    return result.readStringList()  # Variable value 



# ===================================================
# view interaction
# ===================================================
# ---------------------------------------------------
# get state
# ---------------------------------------------------
def cmdGetViewVariable_zoom(viewID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_GUI_VARIABLE, tc.VAR_VIEW_ZOOM, viewID)
    return result.read("!d")[0] # Variable value

def cmdGetViewVariable_offset(viewID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_GUI_VARIABLE, tc.VAR_VIEW_OFFSET, viewID)
    return result.read("!dd") # Variable value

def cmdGetViewVariable_netSize(viewID):
    result = buildSendReadNew1StringParamCmd(tc.CMD_GET_GUI_VARIABLE, tc.VAR_NET_SIZE, viewID)
    return result.read("!dd") # Variable value


# ---------------------------------------------------
# change state
# ---------------------------------------------------
def cmdChangeViewVariable_scheme(viewID, schemeName):
    beginChangeMessage(tc.CMD_SET_GUI_VARIABLE, 1+1+1+4+len(viewID)+1+4+len(schemeName), tc.VAR_VIEW_SCHEMA, viewID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(schemeName)) + schemeName
    _sendExact()

def cmdChangeViewVariable_zoom(viewID, zoom):
    beginChangeMessage(tc.CMD_SET_GUI_VARIABLE, 1+1+1+4+len(viewID)+1+4, tc.VAR_VIEW_ZOOM, viewID)
    _message.string += struct.pack("!Bf", tc.TYPE_FLOAT, zoom)
    _sendExact()

def cmdChangeViewVariable_offset(viewID, offset):
    beginChangeMessage(tc.CMD_SET_GUI_VARIABLE, 1+1+1+4+len(viewID)+1+4+4, tc.VAR_VIEW_OFFSET, viewID)
    _message.string += struct.pack("!Bff", tc.POSITION_2D, offset[0], offset[1])
    _sendExact()

def cmdChangeViewVariable_screenshot(viewID, filename):
    beginChangeMessage(tc.CMD_SET_GUI_VARIABLE, 1+1+1+4+len(viewID)+1+4+len(filename), tc.VAR_SCREENSHOT, viewID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(filename)) + filename
    _sendExact()

def cmdChangeViewVariable_track(viewID, vehID):
    beginChangeMessage(tc.CMD_SET_GUI_VARIABLE, 1+1+1+4+len(viewID)+1+4+len(vehID), tc.VAR_TRACK_VEHICLE, viewID)
    _message.string += struct.pack("!Bi", tc.TYPE_STRING, len(vehID)) + vehID
    _sendExact()






# ===================================================
# 
# ===================================================
def cmdStopNode(edge, objectID, pos=1., duration=10000):
    _message.queue.append(tc.CMD_STOP)
    _message.string += struct.pack("!BBiBi", 1+1+4+1+4+len(edge)+4+1+4+8, tc.CMD_STOP, objectID, tc.POSITION_ROADMAP, len(edge)) + edge
    _message.string += struct.pack("!dBdi", pos, 0, 1., duration)

def cmdChangeTarget(edge, objectID):
    _message.queue.append(tc.CMD_CHANGETARGET)
    _message.string += struct.pack("!BBii", 1+1+4+4+len(edge), tc.CMD_CHANGETARGET, objectID, len(edge)) + edge

def cmdClose():
    global _socket
    if _socket:
        _message.queue.append(tc.CMD_CLOSE)
        _message.string += struct.pack("!BB", 1+1, tc.CMD_CLOSE)
        _sendExact()
        _socket.close()

