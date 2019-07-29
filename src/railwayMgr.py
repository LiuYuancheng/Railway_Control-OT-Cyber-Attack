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
import wx
import railwayGlobal as gv  
import railwayAgent as agent

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MapMgr(object):
    """ Map Manager to init an calculate differet element in the map.
    """
    def __init__(self, parent):
        """ Init all the element on the map. All the parameters are public to other 
            module.
        """ 
        self.signalDict = {} # name follow the <PanelSysCtrl.powerLabel>
        self.dockCount = []
        self.gateAct = False
        # Add the inside railway and the train (A).
        self.trackA = [(300, 50), (140, 50),
                       (100, 90), (100, 150), (100, 210), (100, 330),
                       (140, 370), (300, 370), (460, 370),
                       (500, 330), (500, 210), (500, 90), (460, 50)]
        # railway from A -> B
        self.trackAB = [(300, 50), (140, 50),
                (100, 90), (100, 150), (80, 210), (80, 330),
                (140, 390), (300, 390), (460, 390),
                (520, 330), (520, 210), (520, 90), (460, 30)]
        headPosA = [320, 50]
        self.trainA = agent.AgentTrain(self, 0, headPosA, self.trackA)

        # Add the outside railway and the train (B).
        self.trackB = [(300, 30), (140, 30),
                       (80, 90), (80, 150), (80, 210), (80, 330),
                       (140, 390), (300, 390), (460, 390),
                       (520, 330), (520, 210), (520, 90), (460, 30)]
        # railway from B -> A
        self.trackBA = [(300, 50), (140, 50),
                (80, 90), (80, 150),(100, 210), (100, 330),
                (140, 370), (300, 370), (460, 370),
                (500, 330), (500, 210), (500, 90), (460, 50)]
        headPosB = [320, 30]
        self.trainB = agent.AgentTrain(self, 1, headPosB, self.trackB)

        # Add the inside railway fork (A). 
        forkAPts = [(100, 150), (100, 210), (80,210)]
        self.forkA = agent.AgentFork(self, 2, forkAPts, True)
        self.signalDict['S301 - Track A Fork Power'] = self.createSignals(
            [(120, 150)], gv.FSPNG_PATH, gv.FAPNG_PATH, self.forkA.getState(), True)
        self.gateLockA = False

        # Add the outside railway fork (B).
        forkBPts = [(80, 150), (80,210), (100, 210)]
        self.forkB = agent.AgentFork(self, -1, forkBPts, True)
        self.signalDict['S302 - Track B Fork Power'] = self.createSignals(
            [(60, 150)], gv.FSPNG_PATH, gv.FBPNG_PATH, self.forkB.getState(), True)
        self.gateLockB = False

        # Add the inside gate (A) with its signal lights.
        self.gate1 = agent.AgentGate(self, -1, (300, 365), True, True)
        self.signalDict['Gate1Ppl'] = self.createSignals(
            [(270, 350)], gv.PPPNG_PATH, gv.PSPNG_PATH, True, False)
        self.signalDict['Gate1Car'] = self.createSignals(
            [(330, 350)], gv.CPPNG_PATH, gv.CSPNG_PATH, True, True)
        
        # Add the inside gate (B) with its signal lights.
        self.gate2 = agent.AgentGate(self, -1, (300, 395), True, True)
        self.signalDict['Gate2Ppl'] = self.createSignals(
            [(330, 408)], gv.PPPNG_PATH, gv.PSPNG_PATH, True, False)
        self.signalDict['Gate2Car'] = self.createSignals(
            [(270, 408)], gv.CPPNG_PATH, gv.CSPNG_PATH, True, True)

        # Add the station and the signal light for railway A and B. 
        self.signalDict['StationA signal'] = self.createSignals(
            [(465, 240)], gv.SOPNG_PATH, gv.SFPNG_PATH, False, False)        
        self.signalDict['StationB signal'] = self.createSignals(
            [(550, 240)], gv.SOPNG_PATH, gv.SFPNG_PATH, False, False)        
        self.signalDict['S200 - Station Lights'] = self.createSignals(
            [(485, 210)], gv.STONPNG_PATH, gv.STOFPNG_PATH, True, False) 

        # Define the environment items.
        # Power Plant
        self.signalDict['S100 - Powerplant Lights'] = self.createSignals(
            [(210, 130)], gv.POPNG_PATH, gv.PFPNG_PATH, True, False)
        # Industrial Area
        self.signalDict['S102 - Industrial Lightbox'] = self.createSignals(
            [(35, 250), (35, 315), (35, 380)], gv.INOPNG_PATH, gv.INFPNG_PATH, True, False)
        # City Area
        self.signalDict['S303 - City LightBox'] = self.createSignals(
            [(300+32, 210-32), (300+32, 210+32), (300-32, 210+32)], gv.CTOPNG_PATH, gv.CTFPNG_PATH, True, False)
        # Residential Area
        self.signalDict['S202 - Residential Lightbox'] = self.createSignals(
            [(300+100, 210-32), (300+100, 210+32), (550, 380)], gv.RDOPNG_PATH, gv.RDFPNG_PATH, True, False)
        # Airport Area
        self.signalDict['S101 - Airport Lights'] = self.createSignals(
            [(565, 110)], gv.APOPNG_PATH, gv.APFPNG_PATH, True, False)

        # define all the sensors.
        self.sensorList = []
        self.rwAsensorId = self.rwBsensorId = -1
        self.addSensors()

#-----------------------------------------------------------------------------
    def addSensors(self):
        """ added the train detection sensors in the sensor List """
        # Add the rail way sensors.
        for pos in self.trackA + self.trackB:
            sensor = agent.AgentSensor(self, -1, pos)
            gv.iAgentMgr.hookSernsor(sensor.sensorID)
            self.sensorList.append(sensor)

#-----------------------------------------------------------------------------
    def checkSensor(self):
        """ Check which sensor has detected the train pass."""
        sensorIDfb = [-1, -1] # Feed back sensor ID.
        for sensor in self.sensorList:
            if sensorIDfb[0] < 0:
                for trainPts in self.trainA.getPos():
                    if sensor.checkNear(trainPts[0], trainPts[1], 1):
                        sensor.setSensorState(1)
                        sensorIDfb[0] = sensor.sensorID
                        break
            if sensorIDfb[1] < 0:
                for trainPts in self.trainB.getPos():
                    if sensor.checkNear(trainPts[0], trainPts[1], 1):
                        sensor.setSensorState(1)
                        sensorIDfb[1] = sensor.sensorID
                        break
        return sensorIDfb # return [-1, -1] if there is no sensor detected. 

#-----------------------------------------------------------------------------
    def createSignals(self, posList, onImgPath, offImgPath, state, flash):
        """ Create a signal object list. 
        """
        signalObjList = []
        for pos in posList:
            signalObj =  agent.AgentSignal(self, -1, pos,
                            onBitMap=wx.Bitmap(onImgPath),
                            offBitMap=wx.Bitmap(offImgPath))
            signalObj.setState(state)
            if flash: signalObj.setFlash(flash)
            signalObjList.append(signalObj)
        return signalObjList

#-----------------------------------------------------------------------------
    def setSignalPwr(self, sKey, sValue):
        """ Set the signal power on/off based on the signal's key
        """ 
        value = True if sValue else False
        if sKey in self.signalDict.keys():
            for signalObj in self.signalDict[sKey]:
                # Set the signal statues.
                signalObj.setState(value)

#-----------------------------------------------------------------------------
    def setCompState(self, sKey, sValue):
        """ Set the signal componenets's state.
        """
        value = True if sValue else False
        if sKey == 'S301 - Track A Fork Power':
            self.forkA.forkOn = value
        elif sKey == 'S302 - Track B Fork Power':
            self.forkB.forkOn = value

#-----------------------------------------------------------------------------
    def changeGateState(self, openFlag):
        """ Change the gate states"""
        # track A gate:
        self.gate1.moveDoor(openFg=openFlag)
        gate1Psignal = self.signalDict['Gate1Ppl'][0]
        gate1Psignal.setState(openFlag)
        gate1Csignal = self.signalDict['Gate1Car'][0]
        gate1Csignal.setState(openFlag)
        # track B gate:
        self.gate2.moveDoor(openFg=openFlag)
        gate2Psignal = self.signalDict['Gate2Ppl'][0]
        gate2Psignal.setState(openFlag)
        gate2Csignal = self.signalDict['Gate2Car'][0]
        gate2Csignal.setState(openFlag)
        # Update the current gate action states.
        self.gateAct = True
    
#-----------------------------------------------------------------------------
    def setTAact(self, crtAsensorId):
        """ Set the train A's action base on the sensor ID
        """
        if self.rwAsensorId != crtAsensorId:
            # Clear the old sensor state if the train has passed it.
            if self.rwAsensorId >= 0 and crtAsensorId < 0:
                self.sensorList[self.rwAsensorId].setSensorState(0)
            self.rwAsensorId = crtAsensorId
            # Get the curret position(railway) the train stay on.
            #rwId = self.trainA.getID()
            if self.trainA.getID() == 0:
                if self.rwAsensorId == 10:
                    self.trainA.setDockCount(5)
                    gv.iMapMgr.setSignalPwr('StationA signal', 1)
                elif self.rwAsensorId == 6:
                    self.gateLockA = True
                    self.changeGateState(False)
                elif self.rwAsensorId == 8:
                    self.gateLockA = False
                    if not (self.gateLockA or self.gateLockB):
                        self.changeGateState(True)
                elif self.rwAsensorId == 3 and not self.forkA.forkOn:
                    self.trainA.setRailWayPts(self.trackAB)
                elif self.rwAsensorId == 17:
                    self.trainA.setRailWayPts(self.trackB)
                    self.trainA.id = 1
            else:
                if self.rwAsensorId == 23:
                    self.trainA.setDockCount(5)
                    gv.iMapMgr.setSignalPwr('StationB signal', 1)
                elif self.rwAsensorId == 19:
                    self.gateLockA = True
                    self.changeGateState(False)
                elif self.rwAsensorId == 21:
                    self.gateLockA = False
                    if not (self.gateLockA or self.gateLockB):
                        self.changeGateState(True)
                elif self.rwAsensorId == 16 and not self.forkB.forkOn:
                    self.trainA.setRailWayPts(self.trackBA)
                elif self.rwAsensorId == 4:
                    self.trainA.setRailWayPts(self.trackA)
                    self.trainA.id = 0

            self.updatePnlADisplay(0, crtAsensorId)

#-----------------------------------------------------------------------------
    def setTBact(self, crtBsensorId):
        if self.rwBsensorId != crtBsensorId:
            if self.rwBsensorId >= 0 and crtBsensorId < 0:
                self.sensorList[self.rwBsensorId].setSensorState(0)
            self.rwBsensorId = crtBsensorId
            #rwId = self.trainA.getID()
            if self.trainB.getID() == 0:
                if self.rwBsensorId == 10:
                    self.trainB.setDockCount(5)
                    gv.iMapMgr.setSignalPwr('StationA signal', 1)
                elif self.rwBsensorId == 6:
                    self.gateLockB = True
                    self.changeGateState(False)
                elif self.rwBsensorId == 8:
                    self.gateLockB = False
                    if not (self.gateLockA or self.gateLockB):
                        self.changeGateState(True)
                elif self.rwBsensorId == 3 and not self.forkA.forkOn:
                    self.trainB.setRailWayPts(self.trackAB)
                elif self.rwBsensorId == 17:
                    self.trainB.setRailWayPts(self.trackB)
                    self.trainB.id = 1
            else:
                if self.rwBsensorId == 23:
                    self.trainB.setDockCount(5)
                    gv.iMapMgr.setSignalPwr('StationB signal', 1)
                elif self.rwBsensorId == 19:
                    self.gateLockB = True
                    self.changeGateState(False)
                elif self.rwBsensorId == 21:
                    self.gateLockB = False
                    if not (self.gateLockA or self.gateLockB):
                        self.changeGateState(True)
                elif self.rwBsensorId == 16 and not self.forkB.forkOn:
                    self.trainB.setRailWayPts(self.trackBA)
                elif self.rwBsensorId == 4:
                    self.trainB.setRailWayPts(self.trackA)
                    self.trainB.id = 0
            
            self.updatePnlADisplay(1, crtBsensorId)

#-----------------------------------------------------------------------------
    def updatePnlADisplay(self, trainID ,sensorId):
        if sensorId < 0: return 
        dispalyPnl = gv.iTrainAPanel if trainID == 0 else gv.iTrainBPanel
        state= 0 # state idx refer to <PanelTrainCtrl:self.statDict >
        if sensorId in (10, 23):
            state = 4
        elif sensorId in (3, 16, 6, 19, 9, 22):
            state = 1
        elif sensorId in (4, 17, 0, 13):
            state = 2
        elif sensorId in (1, 14, 5, 18, 8, 21, 11, 24):
            state = 3
        elif sensorId in (12, 25, 2, 15, 7, 20):
            state = 0 
        rwIdx = 0 if sensorId <13 else 1
        dispalyPnl.setState(state, rwIdx)

#-----------------------------------------------------------------------------
    def periodic(self , now):
        self.trainA.updateTrainPos()
        self.trainB.updateTrainPos()
        [crtAsensorId, crtBsensorId] = self.checkSensor()

        self.updatePLCIn((crtAsensorId, crtBsensorId)) # need to run before setTACT/setBAct

        self.setTAact(crtAsensorId)
        self.setTBact(crtBsensorId)
        
        # update if the train left station
        if self.trainA.getDockCount() == 1:
            gv.iTrainAPanel.setState(0, self.trainA.getID())
            gv.iMapMgr.setSignalPwr('StationA signal', 0)

        if self.trainB.getDockCount() == 1:
            gv.iTrainBPanel.setState(0, self.trainB.getID())
            gv.iMapMgr.setSignalPwr('StationB signal', 0)

        # Update the gate action.
        if self.gateAct:
            self.gate1.moveDoor(openFg= not(self.gateLockA or self.gateLockB))
            self.gateAct = self.gate2.moveDoor(openFg= not(self.gateLockA or self.gateLockB))

#-----------------------------------------------------------------------------
    def setEmgStop(self, trainName, state):
        if trainName == 'TrainA':
            self.trainA.setEmgStop(state)
        elif trainName == 'TrainB':
            self.trainB.setEmgStop(state)

#-----------------------------------------------------------------------------
    def updatePLCIn(self, idList):
        (crtAsensorId, crtBsensorId) = idList
        idList, stateList= [], []
        if self.rwAsensorId != crtAsensorId:
            if self.rwAsensorId >= 0 and crtAsensorId < 0:
                idList.append(self.rwAsensorId)
                stateList.append(0)
            elif crtAsensorId >= 0 and self.rwAsensorId < 0:
                idList.append(crtAsensorId)
                stateList.append(1)

        if self.rwBsensorId != crtBsensorId:
            if self.rwBsensorId >= 0 and crtBsensorId < 0:
                idList.append(self.rwBsensorId)
                stateList.append(0)
            elif crtBsensorId >= 0 and self.rwBsensorId < 0:
                idList.append(crtBsensorId)
                stateList.append(1)

        if len(idList) >0:
            gv.iAgentMgr.updatePLC(idList, stateList)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
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
            #print(plcIdx, plcPos)
            self.plcAgentList[plcIdx].hookSensor(sensorId, plcPos)








    



