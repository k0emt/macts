# -*- coding: utf-8 -*-
"""
@file    vehicle.py
@author  Michael Behrisch
@author  Lena Kalleske
@date    2011-03-09
@version $Id: vehicle.py 11671 2012-01-07 20:14:30Z behrisch $

Python implementation of the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2011 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import struct, traci
import traci.constants as tc

DEPART_TRIGGERED = -1
DEPART_NOW = -2

def _readBestLanes(result):
    result.read("!iB")
    nbLanes = result.read("!i")[0] # Length
    lanes = []
    for i in range(nbLanes):
        result.read("!B")
        laneID = result.readString()
        length, occupation, offset = result.read("!BdBdBb")[1::2]
        allowsContinuation = result.read("!BB")[1]
        nextLanesNo = result.read("!Bi")[1]
        nextLanes = []
        for j in range(nextLanesNo):
            nextLanes.append(result.readString())
        lanes.append( [laneID, length, occupation, offset, allowsContinuation, nextLanes ] )
    return lanes


_RETURN_VALUE_FUNC = {tc.ID_LIST:             traci.Storage.readStringList,
                      tc.VAR_SPEED:           traci.Storage.readDouble,
                      tc.VAR_SPEED_WITHOUT_TRACI: traci.Storage.readDouble,
                      tc.VAR_POSITION:        lambda(result): result.read("!dd"),
                      tc.VAR_ANGLE:           traci.Storage.readDouble,
                      tc.VAR_ROAD_ID:         traci.Storage.readString,
                      tc.VAR_LANE_ID:         traci.Storage.readString,
                      tc.VAR_LANE_INDEX:      traci.Storage.readInt,
                      tc.VAR_TYPE:            traci.Storage.readString,
                      tc.VAR_ROUTE_ID:        traci.Storage.readString,
                      tc.VAR_COLOR:           lambda(result): result.read("!BBBB"),
                      tc.VAR_LANEPOSITION:    traci.Storage.readDouble,
                      tc.VAR_CO2EMISSION:     traci.Storage.readDouble,
                      tc.VAR_COEMISSION:      traci.Storage.readDouble,
                      tc.VAR_HCEMISSION:      traci.Storage.readDouble,
                      tc.VAR_PMXEMISSION:     traci.Storage.readDouble,
                      tc.VAR_NOXEMISSION:     traci.Storage.readDouble,
                      tc.VAR_FUELCONSUMPTION: traci.Storage.readDouble,
                      tc.VAR_NOISEEMISSION:   traci.Storage.readDouble,
                      tc.VAR_EDGE_TRAVELTIME: traci.Storage.readDouble,
                      tc.VAR_EDGE_EFFORT:     traci.Storage.readDouble,
                      tc.VAR_ROUTE_VALID:     lambda(result): bool(result.read("!B")[0]),
                      tc.VAR_EDGES:           traci.Storage.readStringList,
                      tc.VAR_SIGNALS:         traci.Storage.readInt,
                      tc.VAR_LENGTH:          traci.Storage.readDouble,
                      tc.VAR_MAXSPEED:        traci.Storage.readDouble,
                      tc.VAR_VEHICLECLASS:    traci.Storage.readString,
                      tc.VAR_SPEED_FACTOR:    traci.Storage.readDouble,
                      tc.VAR_SPEED_DEVIATION: traci.Storage.readDouble,
                      tc.VAR_EMISSIONCLASS:   traci.Storage.readString,
                      tc.VAR_WIDTH:           traci.Storage.readDouble,
                      tc.VAR_MINGAP:          traci.Storage.readDouble,
                      tc.VAR_SHAPECLASS:      traci.Storage.readString,
                      tc.VAR_ACCEL:           traci.Storage.readDouble,
                      tc.VAR_DECEL:           traci.Storage.readDouble,
                      tc.VAR_IMPERFECTION:    traci.Storage.readDouble,
                      tc.VAR_TAU:             traci.Storage.readDouble,
                      tc.VAR_BEST_LANES:      _readBestLanes,
                      tc.DISTANCE_REQUEST:    traci.Storage.readDouble}
subscriptionResults = {}

def _getUniversal(varID, vehID):
    result = traci._sendReadOneStringCmd(tc.CMD_GET_VEHICLE_VARIABLE, varID, vehID)
    return _RETURN_VALUE_FUNC[varID](result)

def getIDList():
    """getIDList() -> list(string)
    
    Returns a list of all known vehicles.
    """
    return _getUniversal(tc.ID_LIST, "")

def getSpeed(vehID):
    """getSpeed(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_SPEED, vehID)

def getSpeedWithoutTraCI(vehID):
    """getSpeedWithoutTraCI(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_SPEED_WITHOUT_TRACI, vehID)

def getPosition(vehID):
    """getPosition(string) -> (double, double)
    
    Returns the position of the named vehicle within the last step [m,m].
    """
    return _getUniversal(tc.VAR_POSITION, vehID)

def getAngle(vehID):
    """getAngle(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_ANGLE, vehID)

def getRoadID(vehID):
    """getRoadID(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_ROAD_ID, vehID)

def getLaneID(vehID):
    """getLaneID(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_LANE_ID, vehID)

def getLaneIndex(vehID):
    """getLaneIndex(string) -> integer
    
    .
    """
    return _getUniversal(tc.VAR_LANE_INDEX, vehID)

def getTypeID(vehID):
    """getTypeID(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_TYPE, vehID)

def getRouteID(vehID):
    """getRouteID(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_ROUTE_ID, vehID)

def getRoute(vehID):
    """getRoute(string) -> list(string)
    
    .
    """
    return _getUniversal(tc.VAR_EDGES, vehID)

def getLanePosition(vehID):
    """getLanePosition(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_LANEPOSITION, vehID)

def getColor(vehID):
    """getColor(string) -> (integer, integer, integer, integer)
    
    .
    """
    return _getUniversal(tc.VAR_COLOR, vehID)

def getCO2Emission(vehID):
    """getCO2Emission(string) -> double
    
    Returns the CO2 emission in mg for the last time step.
    """
    return _getUniversal(tc.VAR_CO2EMISSION, vehID)

def getCOEmission(vehID):
    """getCOEmission(string) -> double
    
    Returns the CO emission in mg for the last time step.
    """
    return _getUniversal(tc.VAR_COEMISSION, vehID)

def getHCEmission(vehID):
    """getHCEmission(string) -> double
    
    Returns the HC emission in mg for the last time step.
    """
    return _getUniversal(tc.VAR_HCEMISSION, vehID)

def getPMxEmission(vehID):
    """getPMxEmission(string) -> double
    
    Returns the particular matter emission in mg for the last time step.
    """
    return _getUniversal(tc.VAR_PMXEMISSION, vehID)

def getNOxEmission(vehID):
    """getNOxEmission(string) -> double
    
    Returns the NOx emission in mg for the last time step.
    """
    return _getUniversal(tc.VAR_NOXEMISSION, vehID)

def getFuelConsumption(vehID):
    """getFuelConsumption(string) -> double
    
    Returns the fuel consumption in ml for the last time step.
    """
    return _getUniversal(tc.VAR_FUELCONSUMPTION, vehID)

def getNoiseEmission(vehID):
    """getNoiseEmission(string) -> double
    
    Returns the noise emission in db for the last time step.
    """
    return _getUniversal(tc.VAR_NOISEEMISSION, vehID)

def getAdaptedTraveltime(vehID, time, edgeID):
    """getAdaptedTraveltime(string, double, string) -> double
    
    .
    """
    traci._beginMessage(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_EDGE_TRAVELTIME, vehID, 1+4+1+4+1+4+len(edgeID))
    traci._message.string += struct.pack("!BiBiBi", tc.TYPE_COMPOUND, 2, tc.TYPE_INTEGER, time,
                                         tc.TYPE_STRING, len(edgeID)) + edgeID
    return traci._checkResult(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_EDGE_TRAVELTIME, vehID).readDouble()

def getEffort(vehID, time, edgeID):
    """getEffort(string, double, string) -> double
    
    .
    """
    traci._beginMessage(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_EDGE_EFFORT, vehID, 1+4+1+4+1+4+len(edgeID))
    traci._message.string += struct.pack("!BiBiBi", tc.TYPE_COMPOUND, 2, tc.TYPE_INTEGER, time,
                                         tc.TYPE_STRING, len(edgeID)) + edgeID
    return traci._checkResult(tc.CMD_GET_VEHICLE_VARIABLE, tc.VAR_EDGE_EFFORT, vehID).readDouble()

def isRouteValid(vehID):
    return _getUniversal(tc.VAR_ROUTE_VALID, vehID)

def getSignals(vehID):
    """getSignals(string) -> integer
    
    .
    """
    return _getUniversal(tc.VAR_SIGNALS, vehID)

def getLength(vehID):
    """getLength(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_LENGTH, vehID)

def getMaxSpeed(vehID):
    """getMaxSpeed(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_MAXSPEED, vehID)

def getVehicleClass(vehID):
    """getVehicleClass(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_VEHICLECLASS, vehID)

def getSpeedFactor(vehID):
    """getSpeedFactor(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_SPEED_FACTOR, vehID)

def getSpeedDeviation(vehID):
    """getSpeedDeviation(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_SPEED_DEVIATION, vehID)

def getEmissionClass(vehID):
    """getEmissionClass(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_EMISSIONCLASS, vehID)

def getWidth(vehID):
    """getWidth(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_WIDTH, vehID)

def getMinGap(vehID):
    """getMinGap(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_MINGAP, vehID)

def getShapeClass(vehID):
    """getShapeClass(string) -> string
    
    .
    """
    return _getUniversal(tc.VAR_SHAPECLASS, vehID)

def getAccel(vehID):
    """getAccel(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_ACCEL, vehID)

def getDecel(vehID):
    """getDecel(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_DECEL, vehID)

def getImperfection(vehID):
    """getImperfection(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_IMPERFECTION, vehID)

def getTau(vehID):
    """getTau(string) -> double
    
    .
    """
    return _getUniversal(tc.VAR_TAU, vehID)

def getBestLanes(vehID):
    """getBestLanes(string) -> 
    
    .
    """
    return _getUniversal(tc.VAR_BEST_LANES, vehID)

def getDrivingDistance(vehID, edgeID, pos, laneID=0):
    """getDrivingDistance(string, string, double, integer) -> double
    
    .
    """
    traci._beginMessage(tc.CMD_GET_VEHICLE_VARIABLE, tc.DISTANCE_REQUEST, vehID, 1+4+1+4+len(edgeID)+4+1+1)
    traci._message.string += struct.pack("!BiBi", tc.TYPE_COMPOUND, 2,
                                         tc.POSITION_ROADMAP, len(edgeID)) + edgeID
    traci._message.string += struct.pack("!dBB", pos, laneID, REQUEST_DRIVINGDIST)
    return traci._checkResult(tc.CMD_GET_VEHICLE_VARIABLE, tc.DISTANCE_REQUEST, vehID).readDouble()

def getDrivingDistance2D(vehID, x, y):
    """getDrivingDistance2D(string, double, double) -> integer
    
    .
    """
    traci._beginMessage(tc.CMD_GET_VEHICLE_VARIABLE, tc.DISTANCE_REQUEST, vehID, 1+4+1+4+4+1)
    traci._message.string += struct.pack("!BiBddB", tc.TYPE_COMPOUND, 2,
                                         tc.POSITION_2D, x, y, REQUEST_DRIVINGDIST)
    return traci._checkResult(tc.CMD_GET_VEHICLE_VARIABLE, tc.DISTANCE_REQUEST, vehID).readDouble()


def subscribe(vehID, varIDs=(tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION), begin=0, end=2**31-1):
    """subscribe(string, list(integer), double, double) -> None
    
    Subscribe to one or more vehicle values for the given interval.
    A call to this method clears all previous subscription results.
    """
    _resetSubscriptionResults()
    traci._subscribe(tc.CMD_SUBSCRIBE_VEHICLE_VARIABLE, begin, end, vehID, varIDs)

def _resetSubscriptionResults():
    subscriptionResults.clear()

def _addSubscriptionResult(vehID, varID, data):
    if vehID not in subscriptionResults:
        subscriptionResults[vehID] = {}
    subscriptionResults[vehID][varID] = _RETURN_VALUE_FUNC[varID](data)

def getSubscriptionResults(vehID=None):
    """getSubscriptionResults(string) -> dict(integer: <value_type>)
    
    Returns the subscription results for the last time step and the given vehicle.
    If no vehicle id is given, all subscription results are returned in a dict.
    If the vehicle id is unknown or the subscription did for any reason return no data,
    'None' is returned.
    It is not possible to retrieve older subscription results than the ones
    from the last time step.
    """
    if vehID == None:
        return subscriptionResults
    return subscriptionResults.get(vehID, None)


def setMaxSpeed(vehID, speed):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_MAXSPEED, vehID, speed)

def setStop(vehID, edgeID, pos=1., laneIndex=0, duration=2**31-1):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.CMD_STOP, vehID, 1+4+1+4+len(edgeID)+1+8+1+1+1+4)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 4)
    traci._message.string += struct.pack("!Bi", tc.TYPE_STRING, len(edgeID)) + edgeID
    traci._message.string += struct.pack("!BdBBBi", tc.TYPE_DOUBLE, pos, tc.TYPE_BYTE, laneIndex, tc.TYPE_INTEGER, duration)
    traci._sendExact()

def changeLane(vehID, laneIndex, duration):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.CMD_CHANGELANE, vehID, 1+4+1+1+1+4)
    traci._message.string += struct.pack("!BiBBBi", tc.TYPE_COMPOUND, 2, tc.TYPE_BYTE, laneIndex, tc.TYPE_INTEGER, duration)
    traci._sendExact()

def slowDown(vehID, speed, duration):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.CMD_SLOWDOWN, vehID, 1+4+1+8+1+4)
    traci._message.string += struct.pack("!BiBdBi", tc.TYPE_COMPOUND, 2, tc.TYPE_DOUBLE, speed, tc.TYPE_INTEGER, duration)
    traci._sendExact()

def changeTarget(vehID, edgeID):
    traci._sendStringCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.CMD_CHANGETARGET, vehID, edgeID)

def setRouteID(vehID, routeID):
    traci._sendStringCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_ROUTE_ID, vehID, routeID)

def setRoute(vehID, edgeList):
    """
    changes the vehicle route to given edges list.
    The first edge in the list has to be the one that the vehicle is at at the moment.
    
    example usage:
    setRoute('1', ['1', '2', '4', '6', '7'])
    
    this changes route for vehicle id 1 to edges 1-2-4-6-7
    """
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_ROUTE, vehID,
                        1+4+sum(map(len, edgeList))+4*len(edgeList))
    traci._message.string += struct.pack("!Bi", tc.TYPE_STRINGLIST, len(edgeList))
    for edge in edgeList:
        traci._message.string += struct.pack("!i", len(edge)) + edge
    traci._sendExact()

def setAdaptedTraveltime(vehID, begTime, endTime, edgeID, time):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_EDGE_TRAVELTIME, vehID, 1+4+1+4+1+4+1+4+len(edgeID)+1+8)
    traci._message.string += struct.pack("!BiBiBiBi", tc.TYPE_COMPOUND, 4, tc.TYPE_INTEGER, begTime,
                                         tc.TYPE_INTEGER, endTime, tc.TYPE_STRING, len(edgeID)) + edgeID
    traci._message.string += struct.pack("!Bd", tc.TYPE_DOUBLE, time)
    traci._sendExact()

def setEffort(vehID, begTime, endTime, edgeID, effort):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_EDGE_EFFORT, vehID, 1+4+1+4+1+4+1+4+len(edgeID)+1+4)
    traci._message.string += struct.pack("!BiBiBiBi", tc.TYPE_COMPOUND, 4, tc.TYPE_INTEGER, begTime,
                                         tc.TYPE_INTEGER, endTime, tc.TYPE_STRING, len(edgeID)) + edgeID
    traci._message.string += struct.pack("!Bd", tc.TYPE_DOUBLE, effort)
    traci._sendExact()

def rerouteTraveltime(vehID):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.CMD_REROUTE_TRAVELTIME, vehID, 1+4)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 0)
    traci._sendExact()

def rerouteEffort(vehID):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.CMD_REROUTE_EFFORT, vehID, 1+4)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 0)
    traci._sendExact()

def setSignals(vehID, signals):
    traci._sendIntCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_SIGNALS, vehID, signals)

def moveTo(vehID, laneID, pos):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_MOVE_TO, vehID, 1+4+1+4+len(laneID)+8)
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 2)
    traci._message.string += struct.pack("!Bi", tc.TYPE_STRING, len(laneID)) + laneID
    traci._message.string += struct.pack("!Bd", tc.TYPE_DOUBLE, pos)
    traci._sendExact()

def setSpeed(vehID, speed):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_SPEED, vehID, speed)

def setColor(vehID, color):
    """setColor(string, (integer, integer, integer, integer))
    sets color for vehicle with the given ID.
    i.e. (255,0,0,0) for the color red. 
    The fourth integer (alpha) is currently ignored
    """
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_COLOR, vehID, 1+1+1+1+1)
    traci._message.string += struct.pack("!BBBBB", tc.TYPE_COLOR, int(color[0]), int(color[1]), int(color[2]), int(color[3]))
    traci._sendExact()

def setLength(vehID, length):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_LENGTH, vehID, length)

def setVehicleClass(vehID, clazz):
    traci._sendStringCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_VEHICLECLASS, vehID, clazz)

def setSpeedFactor(vehID, factor):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_SPEED_FACTOR, vehID, factor)

def setSpeedDeviation(vehID, deviation):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_SPEED_DEVIATION, vehID, deviation)

def setEmissionClass(vehID, clazz):
    traci._sendStringCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_EMISSIONCLASS, vehID, clazz)

def setWidth(vehID, width):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_WIDTH, vehID, width)

def setMinGap(vehID, minGap):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_MINGAP, vehID, minGap)

def setShapeClass(vehID, clazz):
    traci._sendStringCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_SHAPECLASS, vehID, clazz)

def setAccel(vehID, accel):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_ACCEL, vehID, accel)

def setDecel(vehID, decel):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_DECEL, vehID, decel)

def setImperfection(vehID, imperfection):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_IMPERFECTION, vehID, imperfection)

def setTau(vehID, tau):
    traci._sendDoubleCmd(tc.CMD_SET_VEHICLE_VARIABLE, tc.VAR_TAU, vehID, tau)

def add(vehID, routeID, depart=DEPART_NOW, pos=0, speed=0, lane=0, typeID="DEFAULT_VEHTYPE"):
    traci._beginMessage(tc.CMD_SET_VEHICLE_VARIABLE, tc.ADD, vehID,
                        1+4 + 1+4+len(typeID) + 1+4+len(routeID) + 1+4 + 1+8 + 1+8 + 1+1)
    if depart > 0:
        depart *= 1000
    traci._message.string += struct.pack("!Bi", tc.TYPE_COMPOUND, 6)
    traci._message.string += struct.pack("!Bi", tc.TYPE_STRING, len(typeID)) + typeID
    traci._message.string += struct.pack("!Bi", tc.TYPE_STRING, len(routeID)) + routeID
    traci._message.string += struct.pack("!Bi", tc.TYPE_INTEGER, depart)
    traci._message.string += struct.pack("!BdBd", tc.TYPE_DOUBLE, pos, tc.TYPE_DOUBLE, speed)
    traci._message.string += struct.pack("!BB", tc.TYPE_BYTE, lane)
    traci._sendExact()
