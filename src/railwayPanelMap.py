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

        #self.leftTimge = wx.Image(png)
        self.toggle = False     # Display flash toggle flag.
        # gate contorl parameters.(The 0-total close, 15-total open)

        # Set the railway track A and B
        self.trackA = [ (300, 50), (140,50), 
                        (100, 90), (100, 150), (100, 210), (100, 330), 
                        (140, 370), (300,370), (460, 370), 
                        (500, 330), (500, 210), (500, 90),(460, 50)]
        headPosA = [320, 50]

        self.trackB = [ (300, 30), (140, 30), 
                        (80, 90), (80, 150), (80,210), (80,330), 
                        (140, 390), (300, 390), (460,390), 
                        (520, 330), (520, 210), (520, 90), (460, 30)]

        headPosB = [320, 30]

        self.forkA = [(100, 150), (100, 210)]
        self.forkAOn = True
        self.forkB = [(80, 150), (80,210)]
        self.forkBOn = True

        self.forkASignal = agent.AgentSignal(self, -1, (55, 150), onBitMap=wx.Bitmap(gv.FSPNG_PATH), offBitMap=wx.Bitmap(gv.FBPNG_PATH))
        self.forkASignal.setState(True)
        self.forkBSignal = agent.AgentSignal(self, -1, (110, 150), onBitMap=wx.Bitmap(gv.FSPNG_PATH), offBitMap=wx.Bitmap(gv.FAPNG_PATH))
        self.forkBSignal.setState(True)



        self.trainA = agent.AgentTrain(self, -1, headPosA, self.trackA)
        gv.iRailWay = self.trainA


        headPos = [130, 390]  # train station start point(train head)
        self.trainPts = [[headPos[0]-10*(i), headPos[1] ] for i in range(4)]
        self.trainB = agent.AgentTrain(self, -1, headPosB, self.trackB)

        # set the sensor position.
        # Id of the sensor which detected the train passing.
        self.dockCount = 0       # flag to identify train in the station. 
        self.stationRg = (110, 210) # train station range.
        self.attackPts = [(340, 110), (145, 80), (90, 177), (156, 272), (286, 272), (412, 272), (350,380)]
        self.selectedPts = None
        self.sensorid = -1
        self.msgPop = True
        self.sensorList = []
        self.addSensors()
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
        self.gate1 = agent.AgentGate(self, -1, (300, 365), True, True )

        self.gate1PSignal = agent.AgentSignal( self, -1, (270, 350), 
            onBitMap=wx.Bitmap(gv.PPPNG_PATH), 
            offBitMap=wx.Bitmap(gv.PSPNG_PATH))
        self.gate1PSignal.setState(True)

        self.gate1CSignal = agent.AgentSignal( self, -1, (330, 350), 
            onBitMap=wx.Bitmap(gv.CPPNG_PATH), 
            offBitMap=wx.Bitmap(gv.CSPNG_PATH))
        self.gate1CSignal.setState(True)

        self.gate2 = agent.AgentGate(self, -1, (300, 395), True, True)

        self.gate2PSignal = agent.AgentSignal(self, -1, (330, 410),
            onBitMap=wx.Bitmap(gv.PPPNG_PATH), 
            offBitMap=wx.Bitmap(gv.PSPNG_PATH))
        self.gate2PSignal.setState(True)

        self.gate2CSignal = agent.AgentSignal(self, -1, (270, 410),
            onBitMap=wx.Bitmap(gv.CPPNG_PATH),
            offBitMap=wx.Bitmap(gv.CSPNG_PATH))
        self.gate2CSignal.setState(True)
        
        self.gate3 = agent.AgentGate(self, -1, (145, 346), True, False )
        self.gate4 = agent.AgentGate(self, -1, (165, 330), False, True )
        
        self.stationASignal = agent.AgentSignal(self, -1, (470, 240),
            onBitMap=wx.Bitmap(gv.SOPNG_PATH),
            offBitMap=wx.Bitmap(gv.SFPNG_PATH))
        self.stationASignal.setState(False)

        self.stationBSignal = agent.AgentSignal(self, -1, (553, 240),
            onBitMap=wx.Bitmap(gv.SOPNG_PATH),
            offBitMap=wx.Bitmap(gv.SFPNG_PATH))
        self.stationBSignal.setState(False)



        self.SetDoubleBuffered(True)

    #-----------------------------------------------------------------------------
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


        # Add the station sensors.
        #stSensorList = [(550, 130, 3)]
        #for item in stSensorList:
        #    sensor = agent.AgentSensor(self, -1, (item[:2]), item[-1])
        #    self.sensorList.append(sensor)
        # Add the train turn sensors.
        #conerSenList = [(550, 20, 3), (20, 20, 0), (20, 330, 1), (550, 330, 2)]
        #for item in conerSenList:
        #    sensor = agent.AgentSensor(self, -1, (item[:2]), item[-1])
        #    self.sensorList.append(sensor)

        #gateDetector = agent.AgentSensor(self, -1, (290, 20), 0)
        #self.sensorList.append(gateDetector)

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
        for sensor in self.sensorList:
            sensorPos = sensor.pos
            dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)
            dc.DrawText("s"+str(sensor.sensorID), sensorPos[0]+3, sensorPos[1]+3)
        penColor = 'GREEN' if self.toggle else 'RED'
        dc.SetBrush(wx.Brush(penColor))
        if self.sensorid >= 0:
            sensor = self.sensorList[self.sensorid]
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
        _, bitmap = self.forkASignal.getState()
        pos = self.forkASignal.getPos()
        dc.DrawRectangle(pos[0]-2, pos[1]-2, 22, 22)
        if bitmap and self.toggle:
            dc.DrawBitmap(bitmap, pos[0], pos[1])

        _, bitmap = self.forkBSignal.getState()
        pos = self.forkBSignal.getPos()
        dc.DrawRectangle(pos[0]-2, pos[1]-2, 22, 22)
        if bitmap and self.toggle:
            dc.DrawBitmap(bitmap, pos[0], pos[1])

        _, bitmap = self.gate1PSignal.getState()
        pos = self.gate1PSignal.getPos()
        dc.DrawRectangle(pos[0]-12, pos[1]-12, 22, 22)
        if bitmap:
            dc.DrawBitmap(bitmap, pos[0]-10, pos[1]-10)

        _, bitmap = self.gate1CSignal.getState()
        pos = self.gate1CSignal.getPos()
        dc.DrawRectangle(pos[0]-12, pos[1]-12, 22, 22)
        if bitmap and self.toggle:
            dc.DrawBitmap(bitmap, pos[0]-10, pos[1]-10)
        

        _, bitmap = self.gate2PSignal.getState()
        pos = self.gate2PSignal.getPos()
        dc.DrawRectangle(pos[0]-12, pos[1]-12, 22, 22)
        if bitmap:
            dc.DrawBitmap(bitmap, pos[0]-10, pos[1]-10)

        _, bitmap = self.gate2CSignal.getState()
        pos = self.gate2CSignal.getPos()
        dc.DrawRectangle(pos[0]-12, pos[1]-12, 22, 22)
        if bitmap and not self.toggle:
            dc.DrawBitmap(bitmap, pos[0]-10, pos[1]-10)

        _, bitmap = self.stationASignal.getState()
        pos = self.stationASignal.getPos()
        dc.DrawRectangle(pos[0]-12, pos[1]-12, 22, 22)
        if bitmap :
            dc.DrawBitmap(bitmap, pos[0]-10, pos[1]-10)


        _, bitmap = self.stationBSignal.getState()
        pos = self.stationBSignal.getPos()
        dc.DrawRectangle(pos[0]-12, pos[1]-12, 22, 22)
        if bitmap:
            dc.DrawBitmap(bitmap, pos[0]-10, pos[1]-10)





    def _drawRailWay(self, dc):
        # Draw the railway. 
        dc.SetPen(wx.Pen('WHITE', width=4, style=wx.PENSTYLE_SOLID))
        for i in range(len(self.trackA)-1):
            fromPt, toPt = self.trackA[i], self.trackA[i+1]
            dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])
        fromPt, toPt = self.trackA[0], self.trackA[-1]
        dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])

        for i in range(len(self.trackB)-1):
            fromPt, toPt = self.trackB[i], self.trackB[i+1]
            dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])
        fromPt, toPt = self.trackB[0], self.trackB[-1]
        dc.DrawLine(fromPt[0], fromPt[1],toPt[0], toPt[1])
        
        # Draw the railway fork block part.
        dc.SetPen(wx.Pen('WHITE', width=4, style=wx.PENSTYLE_SOLID))
        if self.forkAOn:
            dc.DrawLine(self.forkA[0][0], self.forkA[0][1], self.forkB[1][0], self.forkB[1][1])
        else:
            dc.DrawLine(self.forkA[0][0], self.forkA[0][1], self.forkA[1][0], self.forkA[1][1])
        
        if self.forkBOn:
            dc.DrawLine(self.forkB[0][0], self.forkB[0][1], self.forkA[1][0], self.forkA[1][1])
        else:
            dc.DrawLine(self.forkB[0][0], self.forkB[0][1], self.forkB[1][0], self.forkB[1][1])

        # Draw the railway fork open part.
        dc.SetPen(wx.Pen('GREEN', width=4, style=wx.PENSTYLE_SOLID))
        if self.forkAOn:
            dc.DrawLine(self.forkA[0][0], self.forkA[0][1], self.forkA[1][0], self.forkA[1][1])
        else:
            dc.DrawLine(self.forkA[0][0], self.forkA[0][1], self.forkB[1][0], self.forkB[1][1])
        
        if self.forkBOn:
            dc.DrawLine(self.forkB[0][0], self.forkB[0][1], self.forkB[1][0], self.forkB[1][1])
        else:
            dc.DrawLine(self.forkB[0][0], self.forkB[0][1], self.forkA[1][0], self.forkA[1][1])
        

    def _drawTrains(self, dc):
        dc.SetPen(self.dcDefPen)
        # Draw the train1 on the map.
        trainColor = 'RED' if self.tranState == -1 else '#CE8349'
        dc.SetBrush(wx.Brush(trainColor))
        for point in self.trainA.getPos():
            dc.DrawRectangle(point[0]-5, point[1]-5, 10, 10)
        # Draw the train2 on the map.
        trainColor = 'RED' if (self.trainBLock or self.trainClash) else '#FFC000'
        dc.SetBrush(wx.Brush(trainColor))
        for i, point in enumerate(self.trainB.getPos()):
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

        penColor = 'RED' if self.gate1.gateCount == 0 else 'GREEN'
        dc.SetPen(wx.Pen(penColor, width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(285, 340, 285, 420)
        dc.DrawLine(315, 340, 315, 420)



        # Draw the pedestrians block door
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        [li,ri,lo,ro] = self.gate1.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])
        
        [li,ri,lo,ro] = self.gate2.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])

        return
        penColor = 'RED' if self.forkSt else 'GREEN'
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        [li,ri,lo,ro] = self.gate3.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])

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
        if self.toggle and self.gate1.gateCount == 15:
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

   #-----------------------------------------------------------------------------
    def checkSensor(self):
        """ Check which sensor has detected the train pass."""
        for trainPts in self.trainA.getPos():
            for sensor in self.sensorList:
                if sensor.checkNear(trainPts[0], trainPts[1], 10):
                    return sensor.sensorID # return the sensor index
        return -1 # return -1 if there is no sensor detected. 

    def checkClash(self):
        for trainPts in self.trainA.getPos():
            for trainPts2 in self.trainB.getPos():
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
        self.updateTrainPos()
        if not self.trainBLock and not self.trainClash:
            self.trainB.updateTrainPos()

        sensorid = self.checkSensor()
        # Check whether 2 train clashed.
        if not self.forkSt: 
            self.trainClash = self.checkClash()
            if self.trainClash:
                gv.iEmgStop = True
                wx.MessageBox('Train Accident Happened!', 'Caution!', wx.OK | wx.ICON_ERROR)
                gv.iEmgStop = False

        if self.sensorid != sensorid:
            [idx, state] =[self.sensorid, 0] if self.sensorid >= 0 and sensorid <= 0 else [sensorid, 1]
            # get related plc Idx 
            plcidx = idx//8 
            if gv.iPlcPanelList[plcidx]: gv.iPlcPanelList[plcidx].updateInput(idx%8, state)

            if self.sensorid > 0:
                self.sensorList[self.sensorid].setSensorState(0)
            self.sensorid = sensorid
        # Start to close the gate.
        if self.sensorid == 6 and self.hakedSensorID != 0 : 
            self.gate1.moveDoor(openFg=False)
            self.gate1PSignal.setState(False)
            self.gate1CSignal.setState(False)
            #self.gateCount -= 3
            self.gate2.moveDoor(openFg=False)
            self.gate2PSignal.setState(False)
            self.gate2CSignal.setState(False)

        elif self.sensorid == 8:
            self.gate1.moveDoor(openFg=True)
            self.gate1PSignal.setState(True)
            self.gate1CSignal.setState(True)
            #self.gateCount += 3
            self.gate2.moveDoor(openFg=True)
            self.gate2PSignal.setState(True)
            self.gate2CSignal.setState(True)

        
        if self.forkSt:
            self.gate3.moveDoor(openFg=False)
            self.gate4.moveDoor(openFg=True)
        else:
            self.gate3.moveDoor(openFg=True)
            self.gate4.moveDoor(openFg=False)


        if self.sensorid == 0:
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(origalV=1)
        if  self.hakedSensorID == 0 and sensorid == -1:
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(origalV=0)

        if self.sensorid == 10 or self.sensorid == 23:
            self.dockCount = 10

        if self.dockCount > 0:
            self.dockCount -= 1


        self.updateTrainState(self.sensorid)
        if self.gateDanger and self.sensorid == 1:
            self.gateDanger = False


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
    
    def updateTrainPos(self):
        """ update the train position."""
        if self.dockCount != 0: return
        self.trainA.updateTrainPos()
        
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
