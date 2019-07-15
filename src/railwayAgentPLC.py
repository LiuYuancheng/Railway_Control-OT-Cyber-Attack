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
class AgentSensor(object):
    """ Object hook to control the sensor."""
    def __init__(self, parent, idx, pos, lineIdx, plc=None):
        self.parent = parent
        # sensor unique ID -1 for auto set.
        self.sensorID = gv.iSensorCount if idx < gv.iSensorCount else idx 
        gv.iSensorCount += 1 
        self.pos = pos
        self.lineIdx = lineIdx
        self.plc = plc # The PLC sensor hooked to. 
        self.actFlag = 0 # sensor active flag.

    #-----------------------------------------------------------------------------
    def setSensorState(self, flag):
        """ Set sensor status, flag(int) 0-OFF 1~9 ON"""
        if flag != self.actFlag: 
            self.actFlag = flag
            self.feedBackPLC()

    def getSensorPos(self):
        return self.pos

    #-----------------------------------------------------------------------------
    def getSensorState(self):
        return self.actFlag

    #-----------------------------------------------------------------------------
    def feedBackPLC(self):
        if not self.plc is None: 
            self.plc.updateInput(self.sensorID, self.actFlag)

