#-----------------------------------------------------------------------------
# Name:        railwayAgentPLC.py
#
# Purpose:     This module is the agent module to init different items in the 
#              railway system or create the interface to connect to the hardware. 
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
    """ Interface to store the PLC information and control the PLC through 
        by hooking to the ModBus(TCPIP).
    """
    def __init__(self, parent, idx, name, ipAddr, port):
        self.parent = parent
        self.idx = idx
        self.plcName = name
        self.ipAddr = ipAddr
        self.port = port
        self.devCount = 0           # input device count hook to the PLC.
        self.ctrlCount = 0          # ouput device count hook to the PLC.
        self.devIDList = [-1]*8     # input device ID list.
        self.ctrlIDList = [-1]*8    # output device ID list.
        self.inputStates = [0]*8    # PLC input plug states list.
        self.outputStates = [0]*8   # PLC ouput plug states list.
    
#-----------------------------------------------------------------------------
    def InitConnection_UnderEditting(self):
        """ Init the connection to the PLC from Mode bus. """
        pass

#-----------------------------------------------------------------------------
    def hookSensor(self, sensorID, ioInPos):
        """ Hook a sensor to the specilic plug position on the PLC."""
        if self.devCount >= 8 or ioInPos > 7: 
            print("AgentPLC:    All the GPIO input has been hooked to sensor." ) 
            return False
        self.devIDList[ioInPos] = sensorID
        self.devCount+=1
        return True

#-----------------------------------------------------------------------------
    def checkDev(self, idx):
        """ Check whether the device is connection this PLC. reture the 
            connect position if connected, else -1.
        """
        result = self.devIDList.index(idx) if idx in self.devIDList else -1
        return result

#-----------------------------------------------------------------------------
    def getDevIds(self, sIdx, eIdx):
        """ Get the PLC device state from startIdx(sIdx) to endIdx(eIdx)."""
        return self.devIDList[sIdx:eIdx]

#-----------------------------------------------------------------------------
    def getInputs(self, sIdx, eIdx):
        """ Get the PLC input state from startIdx(sIdx) to endIdx(eIdx)."""
        return self.inputStates[sIdx:eIdx]

#-----------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------
    def setOutput(self, sensorID, state):
        """ Update the sensor output state."""
        try:
            idx = self.ctrlIDList.index(sensorID)
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
        """ The point we can manipulate the attack."""
        AgentTarget.__init__(self, parent, idx, pos, gv.ATTPT_TYPE)
        self.attType = attType  # Attack point
        self.attFlag = False    # The point has been attacked.

    def clear(self):
        self.attFlag = False

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentFork(AgentTarget):
    """ Create a fork object to do the wailway change for the trains."""
    def __init__(self, parent, idx, pos, onFlag):
        AgentTarget.__init__(self, parent, idx, pos, gv.FORK_TYPE)
        self.forkOn = onFlag
        self.startPt = pos[0]   # railway fork start position.
        self.endOnPt = pos[1]   # railway fork on end position.
        self.endOffPt = pos[2]  # railway fork off end position.

    def getForkPts(self):
        pts = self.endOnPt if self.forkOn else self.endOffPt
        return self.startPt + pts

    def getState(self):
        return self.forkOn

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentGate(AgentTarget):
    """ Create a gain object which can open/close its doors. """
    def __init__(self, parent, idx, pos, direc, opened):
        AgentTarget.__init__(self, parent, idx, pos, gv.GATE_TYPE)
        self.direcH = direc # True - Horizontal, False - Vertical.
        self.gateCount = 15 if opened else 0
        self.doorPts = []
        self.getGatePts()

#-----------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------
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
    """ Creat the sensor to show the sensor detection state."""
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
        """ Feed back the sensor state to the PLC it hooked to."""
        if not self.plc is None: 
            self.plc.updateInput(self.sensorID, self.actFlag)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentSignal(AgentTarget):
    """ Create a signal to show the light/signal arrow/ building object."""
    def __init__(self, parent, idx, pos, onBitMap=None, offBitMap=None):
        AgentTarget.__init__(self, parent, idx, pos, gv.SIGNAL_TYPE)
        self.state = False
        self.flashOn = False    # flag to identify whether the signal flash.
        self.onBitMap = onBitMap    # signal on bitmap.
        self.offBitMap = offBitMap  # signal off bitmap.
        self.size = self.onBitMap.GetSize() if self.onBitMap else (0, 0)

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
class AgentTrain(AgentTarget):
    """ Create a train object with its init railway array.
        input:
        pos - The init position of the train head.
        railwayPts - list of railway points.(train will also run under the list sequence.)
    """
    def __init__(self, parent, idx, pos, railwayPts):
        AgentTarget.__init__(self, parent, idx, pos, gv.RAYWAY_TYPE)
        self.railwayPts = railwayPts
        # Init the train head and tail points
        self.pos = [[pos[0] + 10*i, pos[1]] for i in range(5)]
        # The train next distination index for each train body.
        self.trainDistList = [0]*len(self.pos)
        self.trainSpeed = 10    # train speed: pixel/periodic loop
        self.dockCount = 0      # time to stop in the station.
        self.emgStop = False

#-----------------------------------------------------------------------------
    def changedir(self):
        """ Change the train running direction."""
        self.railwayPts = self.railwayPts[::-1]
        self.trainDistList = self.trainDistList[::-1]

#-----------------------------------------------------------------------------
    def checkNear(self, posX, posY, threshold):
        """ Overwrite the pareant checknear function to check whether a point
            is near the train.
        """
        for pos in self.pos:
            dist = math.sqrt((pos[0] - posX)**2 + (pos[1] - posY)**2)
            if dist <= threshold: return True
        return False

#-----------------------------------------------------------------------------
    def getDockCount(self):
        return self.dockCount

#-----------------------------------------------------------------------------
    def setDockCount(self, count):
        self.dockCount = count

    def setTrainSpeed(self, speed):
        self.trainSpeed = speed

    def setRailWayPts(self, railwayPts):
        self.railwayPts = railwayPts

    def setEmgStop(self, emgStop):
        self.emgStop = emgStop

#-----------------------------------------------------------------------------
    def updateTrainPos(self):
        """ Update the current train positions on the map."""
        if self.emgStop: return
        if self.dockCount == 0:
            # Train running on the railway:
            for i, trainPt in enumerate(self.pos):
                # The next railway point idx train going to approch.
                nextPtIdx = self.trainDistList[i]
                nextPt = self.railwayPts[nextPtIdx]
                dist = math.sqrt((trainPt[0] - nextPt[0])**2 + (trainPt[1] - nextPt[1])**2)
                if dist < self.trainSpeed:
                    # Go to the next check point if the distance is less than 1 speed unit.
                    trainPt[0], trainPt[1] = nextPt[0], nextPt[1]
                    # Update the next train distination if the train already get its next dist.
                    nextPtIdx = self.trainDistList[i] = (nextPtIdx + 1) % len(self.railwayPts)
                    nextPt = self.railwayPts[nextPtIdx]
                else:
                    # Move one speed unit.
                    scale = float(self.trainSpeed)/float(dist)
                    trainPt[0] += int((nextPt[0]-trainPt[0])*scale)
                    trainPt[1] += int((nextPt[1]-trainPt[1])*scale)
        else: # Train stop at the station.
            self.dockCount -= 1