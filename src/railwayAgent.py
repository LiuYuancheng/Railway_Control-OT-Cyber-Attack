#-----------------------------------------------------------------------------
# Name:        railwayAgentPLC.py
#
# Purpose:     This module is the agent module to init different items in the 
#              railway system. 
# Author:      Yuancheng Liu
#
# Created:     2019/07/02
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import math
import railwayGlobal as gv 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentPLC(object):
    """ Object hook to control the PLC through the ModBus(TCPIP)."""
    def __init__(self, parent, idx, name, ipAddr, port):
        self.parent = parent
        self.idx = idx
        self.plcName = name
        self.ipAddr = ipAddr
        self.port = port
        self.devCount = 0 # current free index can be hook a sensor.
        self.devIDList = [-1]*8 # list to 
        self.inputStates = [0]*8
        self.outputStates = [0]*8
    
    def InitConnection(self):
        """ Init the connection to the PLC from Mode bus. """
        pass

    #-----------------------------------------------------------------------------
    def hookSensor(self, sensorID, ioInPos):
        """ Hook sensor to the PLC."""
        if self.devCount > 8 or ioInPos > 7: 
            print("AgentPLC:    All the GPIO input has been hooked to sensor." ) 
            return
        self.devIDList[ioInPos] = sensorID
        self.devCount+=1

    #-----------------------------------------------------------------------------
    def getDevIds(self, sIdx, eIdx):
        """ Get the PLC device state from startIdx(sIdx) to endIdx(eIdx)."""
        return self.devIDList[sIdx:eIdx]

    def getInputs(self, sIdx, eIdx):
        """ Get the PLC input state from startIdx(sIdx) to endIdx(eIdx)."""
        return self.inputStates[sIdx:eIdx]

    def getOutputs(self, sIdx, eIdx):
        """ Get the PLC input state from startIdx(sIdx) to endIdx(eIdx)."""
        return self.outputStates[sIdx:eIdx]

    #-----------------------------------------------------------------------------
    def setInput(self, sensorID, state):
        """ Update the sensor input state."""
        try:
            idx = self.devIDList.index(sensorID)
            self.inputStates[idx] = state
        except:
            print("AgentPLC:    The sensor with %s is not hooked to this PLC" %str(sensorID))

    def setOutput(self, sensorID, state):
        """ Update the sensor input state."""
        try:
            idx = self.devIDList.index(sensorID)
            self.outputStates[idx] = state
        except:
            print("AgentPLC:    The sensor with %s is not hooked to this PLC" %str(sensorID))


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentTarget(object):
    """ Create a agent target to generate all the element in the railway system, 
        all the other 'things' in the system will inheritance to this module.
    """
    def __init__(self, parent, tgtID, pos, tType):
        self.parent = parent
        self.id = tgtID
        self.pos = pos
        self.tType = tType # 2 letter agent types.<railwayGlobal.py>

    def getID(self):
        return self.id
    
    def getPos(self):
        return self.pos

    def getType(self):
        return self.tType
    
    def checkNear(self, posX, posY, threshold):
        """ Check whether a point is near the selected point with the 
            input threshold value (unit: pixel).
        """
        dist = math.sqrt((self.pos[0] - posX)**2 + (self.pos[1] - posY)**2)
        return dist <= threshold

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentAttackPt(AgentTarget):

    def __init__(self, parent, idx, pos, attType):
        """ The attack point """
        AgentTarget.__init__(self, parent, idx, pos, gv.ATTPT_TYPE)
        self.attType = attType # Attack point
        self.attFlag = False    # The point has been attacked.

    def clear(self):
        self.attFlag = False 


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentTrain(AgentTarget):
    """ Train object. """
    def __init__(self, parent, idx, pos, railwayPts):
        """ pos: the train head init position.
        """
        AgentTarget.__init__(self, parent, idx, pos, gv.RAYWAY_TYPE)
        self.railwayPts = railwayPts
        # Init the train head and tail points
        self.pos = [[pos[0], pos[1] + 10*i] for i in range(6)]
        # The train next distination index for each train body.
        self.trainDistList = [0]*len(self.pos)
        self.trainSpeed = 10    # train speed: pixel/periodic loop

    def changedir(self):
        """ Change the train running direction."""
        self.railwayPts = self.railwayPts[::-1]
        self.trainDistList = self.trainDistList[::-1]

    def setTrainSpeed(self, speed):
        self.trainSpeed = speed

    def setRailWayPts(self, railwayPts):
        self.railwayPts = railwayPts

    def updateTrainPos(self):
        """ Update the current train position on the map."""
        for i, trainPt in enumerate(self.pos):
            # The next railway point idx train going to approch.
            nextPtIdx = self.trainDistList[i]
            nextPt = self.railwayPts[nextPtIdx]

            dist = math.sqrt((trainPt[0] - nextPt[0])**2 + (trainPt[1] - nextPt[1])**2)
            if dist < self.trainSpeed:
                # Update the next train distination if the train already get its next dist.
                nextPtIdx = self.trainDistList[i] = (nextPtIdx + 1) % len(self.railwayPts)
                nextPt = self.railwayPts[nextPtIdx]
                dist = math.sqrt((trainPt[0] - nextPt[0])**2 + (trainPt[1] - nextPt[1])**2)

            scale = float(self.trainSpeed)/float(dist)

            x = int((nextPt[0]-trainPt[0])*scale)
            y = int((nextPt[1]-trainPt[1])*scale)
            trainPt[0] += x 
            trainPt[1] += y 
            continue

            # move the train toward to the point.
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

    def checkNear(self, posX, posY, threshold):
        """ Check whether a point is near the selected point with the 
            input threshold value (unit: pixel).
        """
        for pos in self.pos:
            dist = math.sqrt((pos[0] - posX)**2 + (pos[1] - posY)**2)
            if  dist <= threshold: return True
        return False


class AgentGate(AgentTarget):
    def __init__(self, parent, idx, pos, direc, opened):
        AgentTarget.__init__(self, parent, idx, pos, gv.GATE_TYPE)
        self.direcH = direc
        self.doorPts = []
        self.gateCount = 15 if opened else 0
        self.getGatePts()

    def getGatePts(self):
        # Horizontal gate
        x, y = self.pos[0], self.pos[1]
        if self.direcH:
            self.doorPts = [(x-self.gateCount, y), (x+self.gateCount, y), (x-self.gateCount-20, y), (x+self.gateCount+20, y)]
        else:
            self.doorPts = [(x, y-self.gateCount), (x, y+self.gateCount), (x, y-self.gateCount-20), (x, y+self.gateCount+20)]
        return self.doorPts

    def moveDoor(self, openFg=None):
        """ return:
            0 - mid.
            1 - total open position
            2 - total closed position
        """
        if openFg is None: return
        
        if openFg:
            if self.gateCount == 15:
                return 1
            self.gateCount += 3
            return 0 
        else:
            if self.gateCount == 0:
                return 2
            self.gateCount -= 3
            return 0 




#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentSensor(AgentTarget):
    """ Object hook to control the sensor."""
    def __init__(self, parent, idx, pos, lineIdx, plc=None):
        AgentTarget.__init__(self, parent, idx, pos, gv.SENSOR_TYPE)
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

