#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railWayPanelMap.py
#
# Purpose:     This module is used to provide different function panels for the 
#              rail way hub function.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import wx
import math
import railwayGlobal as gv 
import railwayPanel as rwp
import railwayAgent as agent

class MapMgr(object):
    """ Map Manager to init an calculate differet element in the map.
    """
    def __init__(self, parent):
        """ Init all the element on the map. All the parameters are public to other 
            module.
        """ 
        self.signalDict = {} # name follow the
        self.dockCount = []



        # Add the inside railway and the train (A).
        self.trackA = [(300, 50), (140, 50),
                       (100, 90), (100, 150), (100, 210), (100, 330),
                       (140, 370), (300, 370), (460, 370),
                       (500, 330), (500, 210), (500, 90), (460, 50)]
        headPosA = [320, 50]
        self.trainA = agent.AgentTrain(self, -1, headPosA, self.trackA)
        # Add the outside railway and the train (B).
        self.trackB = [(300, 30), (140, 30),
                       (80, 90), (80, 150), (80, 210), (80, 330),
                       (140, 390), (300, 390), (460, 390),
                       (520, 330), (520, 210), (520, 90), (460, 30)]
        headPosB = [320, 30]
        self.trainB = agent.AgentTrain(self, -1, headPosB, self.trackB)
        # Add the inside railway fork (A). 
        forkAPts = [(100, 150), (100, 210), (80,210)]
        self.forkA = agent.AgentFork(self, -1, forkAPts, True)
        self.signalDict['S301 - Track A Fork Power'] = self.createSignals(
            [(120, 150)], gv.FSPNG_PATH, gv.FAPNG_PATH, self.forkA.getState(), True)
        
        # Add the outside railway fork (B).
        forkBPts = [(80, 150), (80,210), (100, 210)]
        self.forkB = agent.AgentFork(self, -1, forkBPts, True)
        self.signalDict['S302 - Track B Fork Power'] = self.createSignals(
            [(60, 150)], gv.FSPNG_PATH, gv.FBPNG_PATH, self.forkB.getState(), True)


        self.gateLockA = False
        self.gateLockB = False
        # Add the inside gate (A).
        self.gate1 = agent.AgentGate(self, -1, (300, 365), True, True)
        
        self.signalDict['Gate1Ppl'] = self.createSignals(
            [(270, 350)], gv.PPPNG_PATH, gv.PSPNG_PATH, True, False)
        
        self.signalDict['Gate1Car'] = self.createSignals(
            [(330, 350)], gv.CPPNG_PATH, gv.CSPNG_PATH, True, True)
        
        # Add the inside gate (B).
        
        self.gate2 = agent.AgentGate(self, -1, (300, 395), True, True)

        self.signalDict['Gate2Ppl'] = self.createSignals(
            [(330, 408)], gv.PPPNG_PATH, gv.PSPNG_PATH, True, False)
        
        self.signalDict['Gate2Car'] = self.createSignals(
            [(270, 408)], gv.CPPNG_PATH, gv.CSPNG_PATH, True, True)

        # Add the station A signal light. 

        self.signalDict['StationA signal'] = self.createSignals(
            [(465, 240)], gv.SOPNG_PATH, gv.SFPNG_PATH, False, False)        
        
        self.signalDict['StationB signal'] = self.createSignals(
            [(555, 240)], gv.SOPNG_PATH, gv.SFPNG_PATH, False, False)        
   

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

        self.sensorList = []
        self.rwAsensorId = self.rwBsensorId = -1
        # define all the sensors.
        self.addSensors()

    def addSensors(self):
        """ added the train detection sensors in the sensor List 
        """
        # Add the rail way sensors.
        for item in self.trackA:
            sensor = agent.AgentSensor(self, -1, item)
            self.sensorList.append(sensor)

        for item in self.trackB:
            sensor = agent.AgentSensor(self, -1, item)
            self.sensorList.append(sensor)


    #-----------------------------------------------------------------------------
    def checkSensor(self):
        """ Check which sensor has detected the train pass."""
        sensorIDfb = [-1, -1] # Feed back sensor ID.

        for sensor in self.sensorList:
            if sensorIDfb[0] < 0:
                for trainPts in self.trainA.getPos():
                    if sensor.checkNear(trainPts[0], trainPts[1], 10):
                        sensorIDfb[0] = sensor.sensorID
                        break
            if sensorIDfb[1] < 0:
                for trainPts in self.trainB.getPos():
                    if sensor.checkNear(trainPts[0], trainPts[1], 10):
                        sensorIDfb[1] = sensor.sensorID
                        break

        return sensorIDfb # return [-1, -1] if there is no sensor detected. 

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

    def setSignalPwr(self, sKey, sValue):
        value = True if sValue else False
        if sKey in self.signalDict.keys():
            for signalObj in self.signalDict[sKey]:
                # Set the signal statues.
                signalObj.setState(value)

    def setCompState(self, sKey, sValue):
        value = True if sValue else False
        if sKey == 'S301 - Track A Fork Power':
            self.forkA.forkOn = value
        elif sKey == 'S302 - Track B Fork Power':
            self.forkB.forkOn = value


    def changeGateState(self, openFlag):
        self.gate1.moveDoor(openFg=openFlag)
        gate1Psignal = self.signalDict['Gate1Ppl'][0]
        gate1Psignal.setState(openFlag)
        gate1Csignal = self.signalDict['Gate1Car'][0]
        gate1Csignal.setState(openFlag)

        self.gate2.moveDoor(openFg=openFlag)
        gate2Psignal = self.signalDict['Gate2Ppl'][0]
        gate2Psignal.setState(openFlag)
        gate2Csignal = self.signalDict['Gate2Car'][0]
        gate2Csignal.setState(openFlag)


    def periodic(self , now):
        self.trainA.updateTrainPos()
        self.trainB.updateTrainPos()
        [crtAsensorId, crtBsensorId] = self.checkSensor()
        if self.rwAsensorId != crtAsensorId:
            if self.rwAsensorId > 0 and crtAsensorId < 0:
                self.sensorList[self.rwAsensorId].setSensorState(0)
            self.rwAsensorId = crtAsensorId
            if self.rwAsensorId == 10:
                self.trainA.setDockCount(2)

        if self.rwAsensorId == 6:
            self.gateLockA = True
            self.changeGateState(False)
        elif self.rwAsensorId == 8:
            self.gateLockA = False
            if not (self.gateLockA or self.gateLockB):
                self.changeGateState(True)



        if self.rwBsensorId != crtBsensorId:
            if self.rwBsensorId > 0 and crtBsensorId < 0:
                self.sensorList[self.rwBsensorId].setSensorState(0)
            self.rwBsensorId = crtBsensorId
            if self.rwBsensorId == 23:
                self.trainB.setDockCount(2)

        if crtBsensorId>0:
            print(crtBsensorId)

        if self.rwBsensorId == 19: #?
            self.gateLockB = True
            self.changeGateState(False)
        elif self.rwBsensorId == 21:#?
            self.gateLockB = False
            if not (self.gateLockA or self.gateLockB):
                self.changeGateState(True)
        

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """RailWay top view map panel to show the rail way contorl situaiton."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(600, 480))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.bitmap = wx.Bitmap(gv.BGPNG_PATH)      # background bitmap
        self.wkbitmap = wx.Bitmap(gv.WKJPG_PATH)    # pedestrians wald bitmap.
        self.hitbitmap = wx.Bitmap(gv.HTPNG_PATH)
        self.passbitmap = wx.Bitmap(gv.LPJPG_PATH)
        self.stopbitmap = wx.Bitmap(gv.LSJPG_PATH)
        self.clashbitmap = wx.Bitmap(gv.CLPNG_PATH)


        self.mapMgr = MapMgr(self)
        gv.iMapMgr = self.mapMgr
        #self.leftTimge = wx.Image(png)
        self.toggle = False     # Display flash toggle flag.
        # gate contorl parameters.(The 0-total close, 15-total open)

        





        #self.trainA = agent.AgentTrain(self, -1, headPosA, self.trackA)
        gv.iRailWay = self.mapMgr.trainA


        # set the sensor position.
        # Id of the sensor which detected the train passing.
        self.dockCount = 0       # flag to identify train in the station. 
        self.stationRg = (110, 210) # train station range.
        self.attackPts = [(340, 110), (145, 80), (90, 177), (156, 272), (286, 272), (412, 272), (350,380)]
        self.selectedPts = None
        self.sensorid = -1
        self.msgPop = True
        self.infoWindow = None
        self.gateDanger = False
        self.hakedSensorID = -2 # The hacked sensorID
        self.tranState = 0  # state of the train.0 normal -1: freezed.
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.onClick)
        self.timeCount = 166 # 50 second.
        self.lightOn = True
        self.forkSt = False # Railway fork control.
        self.fordWide = 4

        self.trainBLock = False   
        self.trainClash = False


        self.dcDefPen = None

        # define the gates




        






        



        self.SetDoubleBuffered(True)


    def onClick(self, event):
        x1, y1 = event.GetPosition()
        print("The user has clicked the pos"+str((x1, y1 )))
        for idx, point in enumerate(self.attackPts):
            (x2, y2) = point
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if dist <= 20:
                self.selectedPts = point
                # Set the hacked sensor id 
                self.showDetail(idx)


    def setHackedPt(self, id):
        """ Set the hacked point in the railway system. """
        self.hakedSensorID = id
        if id < 0:
            self.selectedPts = None


    #--PanelBaseInfo---------------------------------------------------------------
    def showDetail(self, idx):
        """ Pop up the detail window to show all the sensor parameters value."""
        if self.infoWindow is None and gv.iDetailPanel is None:
            posF = gv.iMainFrame.GetPosition()
            x = posF[0]
            y = posF[1]+300
            if not self.selectedPts is None:
                x += self.selectedPts[0]
                y += self.selectedPts[1]
            self.infoWindow = wx.MiniFrame(gv.iMainFrame, -1,
                'Attack Point', pos=(x+10, y+10), size=(150, 150),
                style=wx.DEFAULT_FRAME_STYLE)
            gv.iDetailPanel = rwp.PanelAttackSet(self.infoWindow, idx)
            gv.iDetailPanel.updateState(idx=idx, state='Normal', origalV=0, changedV=0)
            gv.iAttackCtrlPanel.loatAttPtState(idx)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()
        else:
            posF = gv.iMainFrame.GetPosition()
            x = posF[0]
            y = posF[1]+300
            if not self.selectedPts is None:
                x += self.selectedPts[0]
                y += self.selectedPts[1]
            self.infoWindow.SetPosition(wx.Point(x+10,y+10))
            gv.iDetailPanel.updateState(idx=idx, state='Normal', origalV=0, changedV=0)

    #--PanelBaseInfo---------------------------------------------------------------
    def infoWinClose(self, event):
        """ Close the pop-up detail information window"""
        if self.infoWindow:
            self.infoWindow.Destroy()
            gv.iDetailPanel = None
            self.infoWindow = None

    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        self.dcDefPen = dc.GetPen()
        self._drawRailWay(dc)
        self._drawTrains(dc)
        # High light the sensor which detected the train.
        dc.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        dc.SetBrush(wx.Brush('GRAY'))
        for sensor in self.mapMgr.sensorList:
            sensorPos = sensor.pos
            dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)
            dc.DrawText("s"+str(sensor.sensorID), sensorPos[0]+3, sensorPos[1]+3)
        penColor = 'GREEN' if self.toggle else 'RED'
        dc.SetBrush(wx.Brush(penColor))
        if self.sensorid >= 0:
            sensor = self.mapMgr.sensorList[self.sensorid]
            sensorPos = sensor.pos
            dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)
        # draw all the sensors: 

        #self.DrawAttackPt(dc)
        self.DrawGate(dc)
        self.DrawStation(dc)
        self._drawSignal(dc)
        #if self.toggle:
        #    if self.forkSt: 
        #        dc.DrawBitmap(self.forkStbitmap, 105, 321)
        #    else:
        #        dc.DrawBitmap(self.forkRtbitmap, 105, 321)
        
        # Update the display flash toggle flag. 
        self.toggle = not self.toggle

    def _drawSignal(self, dc):
        """ draw the signals on the map.
        """
        dc.SetBrush(wx.Brush(wx.Colour('LIGHT GRAY')))
        for signalObjs in self.mapMgr.signalDict.values():
            for signalObj in signalObjs:
                _, flash, bitmap = signalObj.getState()
                pos = signalObj.getPos()
                size = signalObj.getSize()
                dc.DrawRectangle(pos[0]-3-size[0]//2,
                                 pos[1]-3-size[1]//2, size[0]+6, size[1]+6)
                if bitmap and ((not flash) or self.toggle):
                    dc.DrawBitmap(bitmap, pos[0]-size[0]//2, pos[1]-size[1]//2)
        return

    def _drawRailWay(self, dc):
        # Draw the railway. 
        dc.SetPen(wx.Pen('WHITE', width=4, style=wx.PENSTYLE_SOLID))
        for i in range(len(self.mapMgr.trackA)-1):
            fromPt, toPt = self.mapMgr.trackA[i], self.mapMgr.trackA[i+1]
            dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])
        fromPt, toPt = self.mapMgr.trackA[0], self.mapMgr.trackA[-1]
        dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])

        for i in range(len(self.mapMgr.trackB)-1):
            fromPt, toPt = self.mapMgr.trackB[i], self.mapMgr.trackB[i+1]
            dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])
        fromPt, toPt = self.mapMgr.trackB[0], self.mapMgr.trackB[-1]
        dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])
        
        # Draw the railway fork block part.
        dc.SetPen(wx.Pen('WHITE', width=4, style=wx.PENSTYLE_SOLID))
        [pt1, _, pt3] = self.mapMgr.forkA.getPos() 
        dc.DrawLine(pt1[0], pt1[1], pt3[0], pt3[1])
        
        [pt1, _, pt3] = self.mapMgr.forkB.getPos() 
        dc.DrawLine(pt1[0], pt1[1], pt3[0], pt3[1])

        # Draw the railway fork open part.
        dc.SetPen(wx.Pen('GREEN', width=4, style=wx.PENSTYLE_SOLID))
        pt = self.mapMgr.forkA.getForkPts()
        dc.DrawLine(pt[0], pt[1], pt[2], pt[3])

        pt = self.mapMgr.forkB.getForkPts()
        dc.DrawLine(pt[0], pt[1], pt[2], pt[3])

    def _drawTrains(self, dc):
        dc.SetPen(self.dcDefPen)
        # Draw the train1 on the map.
        trainColor = 'RED' if self.tranState == -1 else '#CE8349'
        dc.SetBrush(wx.Brush(trainColor))
        for point in self.mapMgr.trainA.getPos():
            dc.DrawRectangle(point[0]-5, point[1]-5, 10, 10)
        # Draw the train2 on the map.
        trainColor = 'RED' if (self.trainBLock or self.trainClash) else '#FFC000'
        dc.SetBrush(wx.Brush(trainColor))
        for i, point in enumerate(self.mapMgr.trainB.getPos()):
            dc.DrawRectangle(point[0]-5, point[1]-5, 10, 10)
            if self.trainClash and i ==1:
                dc.DrawBitmap(self.clashbitmap, point[0]-15, point[1]-15)


    #-----------------------------------------------------------------------------
    def DrawAttackPt(self, dc):
        """ Draw the attack points. """
        #print("this is the ")
        if (not self.selectedPts is None) and self.toggle:
            dc.SetBrush(wx.Brush('GRAY'))
            dc.DrawCircle(self.selectedPts[0], self.selectedPts[1], 8)
        #color = 'RED' if self.hakedSensorID >=0 else 'BLUE'
        #dc.SetBrush(wx.Brush(color))
        for idx, attackPt in enumerate(self.attackPts):
            color = 'RED' if self.hakedSensorID == idx else 'BLUE'
            dc.SetBrush(wx.Brush(color))
            dc.DrawCircle(attackPt[0], attackPt[1], 5)
        
        if self.hakedSensorID ==0:
            dc.SetPen(wx.Pen('RED', width=1, style=wx.PENSTYLE_DOT))
            dc.DrawLine(130, 110, 335, 110)

    #-----------------------------------------------------------------------------
    def DrawGate(self, dc):
        """ Draw the pedestrians walking gate for passing the railway."""
        # Draw the bridge(left and right)
        #if self.gate1.gateCount == 15 :
        #    dc.SetPen(wx.Pen('BLACK', width=1, style=wx.PENSTYLE_DOT))
        #    dc.SetBrush(wx.Brush(wx.Colour('Black')))
        #    dc.DrawRectangle(250, 9, 30, 30)
        #    dc.DrawBitmap(self.passbitmap, 280, 50)
        #else:
        #    dc.DrawBitmap(self.stopbitmap, 280, 50)

        #if self.lightOn == 1:
        #    dc.DrawBitmap(self.passbitmap, 280, 50)
        #elif self.lightOn == 2:
        #    dc.DrawBitmap(self.stopbitmap, 280, 50)

        dc.SetPen(wx.Pen('GREEN', width=1, style=wx.PENSTYLE_SOLID))
        dc.DrawLine(294, 80, 294, 110)

        penColor = 'RED' if self.mapMgr.gate1.gateCount == 0 else 'GREEN'
        dc.SetPen(wx.Pen(penColor, width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(285, 340, 285, 420)
        dc.DrawLine(315, 340, 315, 420)



        # Draw the pedestrians block door
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        [li,ri,lo,ro] = self.mapMgr.gate1.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])
        
        [li,ri,lo,ro] = self.mapMgr.gate2.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])

        return

        penColor = 'RED' if not self.forkSt else 'GREEN'
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        [li,ri,lo,ro] = self.gate4.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])

        #dc.DrawLine(265+self.gateCount, 7, 265+self.gateCount+15, 7)
        #dc.DrawLine(265-self.gateCount, 7, 265-self.gateCount-15, 7)
        #dc.DrawLine(265+self.gateCount, 37, 265+self.gateCount+15, 37)
        #dc.DrawLine(265-self.gateCount, 37, 265-self.gateCount-15, 37)
        # Draw the pedestrians signal.
        #print(self.sensorid)
        if self.toggle and self.mapMgr.gate1.gateCount == 15:
            if self.sensorid == 11 or self.gateDanger:
                dc.DrawBitmap(self.hitbitmap, 250, 7)
                if not self.gateDanger: 
                    self.gateDanger = True
                    if self.msgPop:
                        self.msgPop = False
                        gv.iEmgStop = True
                        wx.MessageBox('Train Accident Happened!', 'Caution!', wx.OK | wx.ICON_ERROR)
                        gv.iEmgStop = False
            else:
                dc.DrawBitmap(self.wkbitmap, 250, 7)
       
    #-----------------------------------------------------------------------------
    def DrawStation(self, dc):
        """ Draw the station part"""

        dc.SetPen(self.dcDefPen)
        dc.SetBrush(wx.Brush(wx.Colour('LIGHT GRAY')))
        
        dc.DrawRectangle(480, 200, 15, 60)
        dc.SetBrush(wx.Brush(wx.Colour('GRAY')))
        dc.DrawRectangle(525, 200, 15, 60)
        
        return





        dc.SetPen(wx.Pen('BLACK', width=1, style=wx.PENSTYLE_DOT))
        dc.SetBrush(wx.Brush(wx.Colour('Black')))
        if self.dockCount == 0:    
            dc.DrawRectangle(568, 110, 30, 30)
            dc.DrawRectangle(568, 180, 30, 30)
            if not self.toggle:
                dc.DrawBitmap(self.stopbitmap, 564, 145)
            else:
                dc.SetBrush(wx.Brush(wx.Colour('LIGHT GRAY')))
                dc.DrawRectangle(564, 145, 30, 30)
                dc.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
                dc.DrawText( str(self.timeCount//2).zfill(2)+"S", 568, 150)
        else:
            y = 110 if self.toggle else 180
            dc.DrawRectangle(568, y, 30, 30)
            dc.SetPen(wx.Pen('#FFC000', width=1, style=wx.PENSTYLE_SOLID))
            dc.SetBrush(wx.Brush(wx.Colour('#FFC000')))
            dc.DrawRectangle(536, 116, 29, 90)
            points = [(530, 114), (565, 114), (565, 208), (530, 208), (530, 114)]
            dc.SetPen(wx.Pen('Green', width=2, style=wx.PENSTYLE_SOLID))
            for i in range(len(points)-1):
                dc.DrawLine(points[i], points[i+1])
            dc.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            dc.DrawText( str(self.dockCount//2).zfill(2)+"S", 535, 130)
            img = self.passbitmap if self.toggle else self.wkbitmap
            dc.DrawBitmap(img, 564, 145)
            self.timeCount = 166



    def checkClash(self):
        for trainPts in self.mapMgr.trainA.getPos():
            for trainPts2 in self.mapMgr.trainB.getPos():
                clashSensor = agent.AgentTarget(self, -1, trainPts2, 'T')
                if clashSensor.checkNear(trainPts[0], trainPts[1], 10):
                    return True
                clashSensor = None
        return False



    #-----------------------------------------------------------------------------
    def getTrainPos(self):
        """ return the current train position."""
        return self.trainPts

    #-----------------------------------------------------------------------------
    def periodic(self , now):
        """ periodicly call back to do needed calcualtion/panel update"""
        # Set the detect sensor status related to PLC status

        self.mapMgr.periodic(now)

        
        # Check whether 2 train clashed.
        if not self.forkSt: 
            self.trainClash = self.checkClash()
            if self.trainClash:
                gv.iEmgStop = True
                wx.MessageBox('Train Accident Happened!', 'Caution!', wx.OK | wx.ICON_ERROR)
                gv.iEmgStop = False

        #if self.sensorid != sensorid:
        #    [idx, state] =[self.sensorid, 0] if self.sensorid >= 0 and sensorid <= 0 else [sensorid, 1]
        #    # get related plc Idx 
        #    plcidx = idx//8 
        #    if gv.iPlcPanelList[plcidx]: gv.iPlcPanelList[plcidx].updateInput(idx%8, state)

            #if self.sensorid > 0:
            #    self.mapMgr.sensorList[self.sensorid].setSensorState(0)
            #self.sensorid = sensorid




        #if self.sensorid == 0:
        #    if gv.iDetailPanel:
        #        gv.iDetailPanel.updateState(origalV=1)
        #if  self.hakedSensorID == 0 and sensorid == -1:
        #    if gv.iDetailPanel:
        #        gv.iDetailPanel.updateState(origalV=0)


            



        #self.updateTrainState(self.sensorid)
        #if self.gateDanger and self.sensorid == 1:
        #    self.gateDanger = False


        # make the count in side the range. 
        #self.gateCount = min(15, max(0, self.gateCount))

        # Check whether train in side the station.
        #head = self.trainPts[0]
        # Update the panel.
        self.updateDisplay()

    #-----------------------------------------------------------------------------
    def OnClick(self, event):
        """ Handle the click on the map event."""
        x, y = event.GetPosition()
        pass
    
               
    #-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(False)
        self.Update()

    def updateTrainState(self, sensorID): 
        """ Update the sensor status based on the sensor's detection state.
        """
        if self.dockCount != 0: 
            gv.iTrainPanel.setState(4)
        elif sensorID == 0 or sensorID == 6:
            gv.iTrainPanel.setState(1)
        elif sensorID == 1: 
            gv.iTrainPanel.setState(2)
        elif 2 <= sensorID <= 5:
            gv.iTrainPanel.setState(0)
        elif 7 <= sensorID <= 10:
            gv.iTrainPanel.setState(3)
        else:
            gv.iTrainPanel.setState(0)
