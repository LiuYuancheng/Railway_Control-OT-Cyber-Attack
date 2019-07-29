#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railwayMgr.py
#
# Purpose:     This function is the railway function manager to connect the 
#              agent element with their control panel.
#
# Author:      Yuancheng Liu
#
# Created:     2019/07/29
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import railwayGlobal as gv  

class managerPLC(object):
    """ Object hook to control the PLC through the ModBus(TCPIP)."""
    def __init__(self, parent):
        self.parent = parent
        self.sensorPosCount = 0
        self.plcAgentList = []
        self.plcPanelList = []

    def appendPLC(self, plcAgent, plcPanel):
        self.plcAgentList.append(plcAgent)
        self.plcPanelList.append(plcPanel)

    def findDevPLC(self, devIdx):
        """ Find the Agent PLC and the PLC display panel based on the device id.
        """
        for i, agent in enumerate(self.plcAgentList):
            plcInterfaceID = agent.checkDev(devIdx)
            if  plcInterfaceID >=0 :
                return (self.plcAgentList[i], self.plcPanelList[i], plcInterfaceID)
        return (None, None, -1)

    def updatePLC(self, devIDList, stateList):
        for i in range(len(devIDList)):
            devId, devS = devIDList[i], stateList[i]
            (plcA, plcP, devP) = self.findDevPLC(devIDList[i])
            if plcA:
                plcA.setInput(devId, devS)
            if plcP:
                plcP.updateInput(devP, devS)
    
    def hookSernsor(self, sensorId):
        if sensorId <= 23:
            plcIdx, plcPos = sensorId//8, sensorId%8
            print(plcIdx, plcPos)
            self.plcAgentList[plcIdx].hookSensor(sensorId, plcPos)








    



