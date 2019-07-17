#-----------------------------------------------------------------------------
# Name:        railwayAgentPLC.py
#
# Purpose:     This module is the agent module to communicate to PLC or make 
#              communication to the sensor.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/07/02
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import math
import railwayGlobal as gv 

#-----------------------------------------------------------------------------
class AgentPLC(object):
    """ Object hook to control the PLC."""
    def __init__(self, parent, idx, name, ipAddr, port):
        self.parent = parent
        self.idx = idx
        self.plcName = name
        self.ipAddr = ipAddr
        self.port = port
        self.SensorCount = 0 # current free index can be hook a sensor.
        self.sensorIDList = [-1]*6 # list to 
        self.inputStates = [0]*8
        self.outputStates = [0]*8
    
    #-----------------------------------------------------------------------------
    def hookSensor(self, sensorID, ioInPos):
        """ Hook sensor to the PLC. """
        if self.SensorCount > 8 or ioInPos > 7: 
            print("AgentPLC:    All the GPIO input has been hooked to sensor." ) 
            return
        if ioInPos < 0:
            ioInPos = self.SensorCount 
        self.sensorIDList[ioInPos] = sensorID
        self.SensorCount+=1

    #-----------------------------------------------------------------------------
    def updateInput(self, sensorID, state):
        """ Update the sensor input state."""
        try:
            idx = self.sensorIDList.index(sensorID)
            self.inputStates[idx] = state
        except:
            print("AgentPLC:    The sensor with %s is not hooked to this PLC" %str(sensorID))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentTarget(object):

    def __init__(self, parent, tgtID, pos):
        self.parent = parent
        self.id = tgtID
        self.pos = pos 

    def getID(self):
        return self.id
    
    def getPos(self):
        return self.pos
    
    def checkNear(self, posX, posY, threshold):
        """ Check whether a point is near the selected point."""
        dist = math.sqrt((self.pos[0] - posX)**2 + (self.pos[1] - posY)**2)
        return dist <= threshold


class AgentRailWay(AgentTarget):

    def __init__(self, parent, idx, pos, railwayPts):
        """
        """
        AgentTarget.__init__(self, parent, idx, pos)
        self.railwayPts = railwayPts
        # init the train points
        self.pos = [pos] + [[pos[0], pos[1] + 10*(i+1)] for i in range(6)]
        # The train next distination index
        self.trainDistList = [0]*len(self.pos)
        self.trainSpeed = 10    # train speed: pixel/periodic loop
        self.direction = 0      # 0 - clockwise, 1 - anticlockwise

    def setTrainSpeed(self, speed, direction=None):
        if not direction is None: 
            self.direction = direction
        self.trainSpeed = speed

    def updateTrainPos(self):
        for i, trainPt in enumerate(self.pos):
            nextPtIdx = self.trainDistList[i]
            nextPt = list(self.railwayPts[nextPtIdx])
            if trainPt == nextPt:
                # Update the next train distination.
                nextPtIdx = self.trainDistList[i] = (nextPtIdx + 1) % len(self.railwayPts)
                nextPt = self.railwayPts[nextPtIdx]

            # move the train to the point.
            x, y = 0, 0
            if nextPt[0] > trainPt[0]:
                x = self.trainSpeed
            elif nextPt[0] < trainPt[0]:
                x = -self.trainSpeed

            if nextPt[1] > trainPt[1]:
                y = self.trainSpeed
            elif nextPt[1] < trainPt[1]:
                y = -self.trainSpeed
                
            trainPt[0] += x 
            trainPt[1] += y 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentSensor(AgentTarget):
    """ Object hook to control the sensor."""
    def __init__(self, parent, idx, pos, lineIdx, plc=None):
        AgentTarget.__init__(self, parent, idx, pos)
        # sensor unique ID -1 for auto set.
        self.sensorID = gv.iSensorCount if idx < gv.iSensorCount else idx 
        gv.iSensorCount += 1 
        self.lineIdx = lineIdx
        self.plc = plc # The PLC sensor hooked to. 
        self.actFlag = 0 # sensor active flag.

    #-----------------------------------------------------------------------------
    def setSensorState(self, flag):
        """ Set sensor status, flag(int) 0-OFF 1~9 ON"""
        if flag != self.actFlag: 
            self.actFlag = flag
            self.feedBackPLC()

    #-----------------------------------------------------------------------------
    def getSensorState(self):
        return self.actFlag

    #-----------------------------------------------------------------------------
    def feedBackPLC(self):
        if not self.plc is None: 
            self.plc.updateInput(self.sensorID, self.actFlag)

