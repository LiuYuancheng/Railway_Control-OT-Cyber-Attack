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
        self.pos = [[pos[0]+ 10*i, pos[1]] for i in range(5)]
        # The train next distination index for each train body.
        self.trainDistList = [0]*len(self.pos)
        self.trainSpeed = 10    # train speed: pixel/periodic loop
        self.dockCount = 0 

    def changedir(self):
        """ Change the train running direction."""
        self.railwayPts = self.railwayPts[::-1]
        self.trainDistList = self.trainDistList[::-1]

    def checkNear(self, posX, posY, threshold):
        """ Check whether a point is near the selected point with the 
            input threshold value (unit: pixel).
        """
        for pos in self.pos:
            dist = math.sqrt((pos[0] - posX)**2 + (pos[1] - posY)**2)
            if  dist <= threshold: return True
        return False

    def setDockCount(self, count):
        self.dockCount = count

    def setTrainSpeed(self, speed):
        self.trainSpeed = speed

    def setRailWayPts(self, railwayPts):
        self.railwayPts = railwayPts

    def updateTrainPos(self):
        """ Update the current train position on the map."""
        if self.dockCount == 0:
            for i, trainPt in enumerate(self.pos):
                # The next railway point idx train going to approch.
                nextPtIdx = self.trainDistList[i]
                nextPt = self.railwayPts[nextPtIdx]
                dist = math.sqrt((trainPt[0] - nextPt[0])**2 + (trainPt[1] - nextPt[1])**2)
                if dist < self.trainSpeed:
                    trainPt[0] = nextPt[0]
                    trainPt[1] = nextPt[1]
                    # Update the next train distination if the train already get its next dist.
                    nextPtIdx = self.trainDistList[i] = (nextPtIdx + 1) % len(self.railwayPts)
                    nextPt = self.railwayPts[nextPtIdx]
                else:
                    scale = float(self.trainSpeed)/float(dist)
                    trainPt[0] += int((nextPt[0]-trainPt[0])*scale)
                    trainPt[1] += int((nextPt[1]-trainPt[1])*scale)
        else:
            self.dockCount -= 1

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentGate(AgentTarget): 
    def __init__(self, parent, idx, pos, direc, opened):
        AgentTarget.__init__(self, parent, idx, pos, gv.GATE_TYPE)
        self.direcH = direc # True - Horizontal, False - Vertical.
        self.gateCount = 15 if opened else 0
        self.doorPts = []
        self.getGatePts()

    def getGatePts(self):
        """ Return the current door gate position on the map.  
            Position list: [lift_iside, right_inside, left_outside, right_outside]
        """
        x, y = self.pos[0], self.pos[1]
        if self.direcH:
            self.doorPts = [(x-self.gateCount, y), 
                            (x+self.gateCount, y), 
                            (x-self.gateCount-18, y), 
                            (x+self.gateCount+18, y)] 
        else:
            self.doorPts = [(x, y-self.gateCount),
                            (x, y+self.gateCount),
                            (x, y-self.gateCount-18),
                            (x, y+self.gateCount+18)]
        return self.doorPts

    def moveDoor(self, openFg=None):
        """ Move the door to the input state. return True if can move 
            return false if the door has got the limitation position.
        """
        if openFg is None:
            return False
        elif openFg:
            if self.gateCount == 12: return False
            self.gateCount += 3
        else:
            if self.gateCount == 0: return False
            self.gateCount -= 3
        return True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentSensor(AgentTarget):
    """ Object hook to control the sensor."""
    def __init__(self, parent, idx, pos, plc=None):
        AgentTarget.__init__(self, parent, idx, pos, gv.SENSOR_TYPE)
        # sensor unique ID -1 for auto set.
        self.sensorID = gv.iSensorCount if idx < gv.iSensorCount else idx 
        gv.iSensorCount += 1 
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

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentSignal(AgentTarget):
    """ Object hook to control signal."""
    def __init__(self, parent, idx, pos, onBitMap=None, offBitMap=None):
        AgentTarget.__init__(self, parent, idx, pos, gv.SIGNAL_TYPE)
        self.state = False
        self.flashOn = False
        self.onBitMap = onBitMap
        self.offBitMap = offBitMap
        self.size = self.onBitMap.GetSize() if self.onBitMap else (0,0)

    def getSize(self):
        return self.size

    def setFlash(self, flashOn):
        self.flashOn = flashOn

    def setState(self, onFlag):
        self.state = onFlag

    def getState(self):
        bitmap = self.onBitMap if self.state else self.offBitMap
        return (self.state, self.flashOn, bitmap)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentFork(AgentTarget):
    """ Object hook to control signal."""
    def __init__(self, parent, idx, pos, onFlag):
        AgentTarget.__init__(self, parent, idx, pos, gv.FORK_TYPE)
        self.forkOn = onFlag
        self.startPt = pos[0]
        self.endOnPt = pos[1]
        self.endOffPt = pos[2]

    def getForkPts(self):
        pts = self.endOnPt if self.forkOn else self.endOffPt
        return self.startPt + pts

    def getState(self):
        return self.forkOn