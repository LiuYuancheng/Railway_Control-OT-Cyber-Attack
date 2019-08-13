#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railWayPanelMap.py
#
# Purpose:     This module is used to show the top view of the  main city map in
#              the railway system.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import wx
import math
import railwayGlobal as gv 
import railwayPanel as rwp
import railwayAgent as agent
import railwayMgr as manager

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """ RailWay top view map panel to show the rail way control situation."""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(600, 480))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        # Init the map component manager.
        gv.iMapMgr = self.mapMgr = manager.MapMgr(self)
        self.toggle = False     # Display flash toggle flag.
        self.selectedPts = None # components' position selected by user.
        self.infoMsgPop = True  # pop-up alert message.
        self.infoWindow = None  # pop-up window(wx.Frame)
        self.hakedSensorID = -2 # The hacked sensorID
        self.trainBLock = False # flag(train is block)
        self.trainClash = False # flag(train clash happened)
        self.dcDefPen = None    # device context default pen style.
        # Bind the event handler.
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
        # Set the panel double buffer.
        self.SetDoubleBuffered(True)  # Avoid the panel flash during update.

#--PanelMap--------------------------------------------------------------------
    def _checkClash(self):
        """ Check whether the train clash happens."""
        for trainPts in self.mapMgr.trainA.getPos():
            for trainPts2 in self.mapMgr.trainB.getPos():
                # Create a new agent target object at the check trainB body position.
                clashSensor = agent.AgentTarget(self, -1, trainPts2, 'T')
                if clashSensor.checkNear(trainPts[0], trainPts[1], 10):
                    self.trainClash = True
                    return True
                clashSensor = None
        self.trainClash = False
        return False

#--PanelMap--------------------------------------------------------------------
    def _drawAttackPt(self, dc):
        """ Hight light the attack sensor and signal.(Currently not used.)"""
        if (not self.selectedPts is None) and self.toggle:
            dc.SetBrush(wx.Brush('GRAY'))
            dc.DrawCircle(self.selectedPts[0], self.selectedPts[1], 8)
        for idx, attackPt in enumerate(self.attackPts):
            color = 'RED' if self.hakedSensorID == idx else 'BLUE'
            dc.SetBrush(wx.Brush(color))
            dc.DrawCircle(attackPt[0], attackPt[1], 5)
        if self.hakedSensorID ==0:
            dc.SetPen(wx.Pen('RED', width=1, style=wx.PENSTYLE_DOT))
            dc.DrawLine(130, 110, 335, 110)

#--PanelMap--------------------------------------------------------------------
    def _drawGate(self, dc):
        """ Draw the pedestrians walking gate for passing the railway."""
        penColor = 'RED' if self.mapMgr.gate1.gateCount == 0 else 'GREEN'
        # Draw the pedenstrains walking way.
        dc.SetPen(wx.Pen(penColor, width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(285, 340, 285, 420)
        dc.DrawLine(315, 340, 315, 420)
        # Draw the pedestrians block gate/bearing.
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        # Gate 1:
        [li,ri,lo,ro] = self.mapMgr.gate1.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])
        # Gate 2:
        [li,ri,lo,ro] = self.mapMgr.gate2.getGatePts()
        dc.DrawLine(li[0], li[1], lo[0], lo[1])
        dc.DrawLine(ri[0], ri[1], ro[0], ro[1])
        # Draw the accident situation.
        if gv.iSensorAttack and self.toggle:
            if self.mapMgr.rwAsensorId in (7, 20) or self.mapMgr.rwBsensorId in (7,20):
                dc.DrawBitmap(wx.Bitmap(gv.HTPNG_PATH), 300-15, 380-15)
                if self.infoMsgPop: 
                    self.infoMsgPop = False # map the alert window pop up once.
                    gv.iMapMgr.setEmgStop('TrainA', True)
                    gv.iMapMgr.setEmgStop('TrainB', True)
                    wx.MessageBox('Train Accident Happened!', 'Caution!', wx.OK | wx.ICON_ERROR)
                    gv.iMapMgr.setEmgStop('TrainA', False)
                    gv.iMapMgr.setEmgStop('TrainB', False)

#--PanelMap--------------------------------------------------------------------
    def _drawRailWay(self, dc):
        """ Draw the background and the railway."""
        dc.DrawBitmap(wx.Bitmap(gv.BGPNG_PATH), 1, 1)  # draw the background.
        # Draw the railway.
        dc.SetPen(wx.Pen('WHITE', width=4, style=wx.PENSTYLE_SOLID))
        # Draw the track A
        for i in range(len(self.mapMgr.trackA)-1):
            fromPt, toPt = self.mapMgr.trackA[i], self.mapMgr.trackA[i+1]
            dc.DrawLine(fromPt[0], fromPt[1], toPt[0], toPt[1])
        fromPt, toPt = self.mapMgr.trackA[0], self.mapMgr.trackA[-1]
        dc.DrawLine(fromPt[0], fromPt[1], toPt[0], toPt[1])
        # Draw the track B
        for i in range(len(self.mapMgr.trackB)-1):
            fromPt, toPt = self.mapMgr.trackB[i], self.mapMgr.trackB[i+1]
            dc.DrawLine(fromPt[0], fromPt[1], toPt[0], toPt[1])
        fromPt, toPt = self.mapMgr.trackB[0], self.mapMgr.trackB[-1]
        dc.DrawLine(fromPt[0], fromPt[1], toPt[0], toPt[1])
        # Draw the railway fork block default position.
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

#--PanelMap--------------------------------------------------------------------
    def _drawSensors(self, dc):
        """ Draw the sensors on the map. """
        # Show the overwritten sensor under man in mid attack.        
        dc.SetPen(self.dcDefPen)
        if gv.iSensorAttack and self.toggle:
            senIdlist = (6, 8, 19, 21)  # sensor before/after the gate.
            dc.SetBrush(wx.Brush('RED'))
            for i in senIdlist:
                sensorPos = self.mapMgr.sensorList[i].pos # get sensor position.
                dc.DrawRectangle(sensorPos[0]-7, sensorPos[1]-7, 14, 14)
        # Draw all the sensor and high light the sensor which detected the train.
        dc.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        dc.SetBrush(wx.Brush('GRAY'))
        for sensor in self.mapMgr.sensorList:
            sensorPos = sensor.pos
            dc.DrawText("s"+str(sensor.sensorID), sensorPos[0]+3, sensorPos[1]+3)
            if sensor.getSensorState():
                color = 'YELLOW' if self.toggle else 'GREEN'
                dc.SetBrush(wx.Brush(color))
                dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)
                dc.SetBrush(wx.Brush('GRAY'))
            else:
                dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)

#--PanelMap--------------------------------------------------------------------
    def _drawSignal(self, dc):
        """ draw the signals set on/off the map."""
        dc.SetPen(self.dcDefPen)
        dc.SetBrush(wx.Brush(wx.Colour('LIGHT GRAY')))
        for signalObjs in self.mapMgr.signalDict.values():
            for signalObj in signalObjs: # signal set.
                _, flash, bitmap = signalObj.getState()
                pos, size = signalObj.getPos(), signalObj.getSize()
                dc.DrawRectangle(pos[0]-3-size[0]//2,
                                 pos[1]-3-size[1]//2, size[0]+6, size[1]+6)
                if bitmap and ((not flash) or self.toggle):
                    dc.DrawBitmap(bitmap, pos[0]-size[0]//2, pos[1]-size[1]//2)

#--PanelMap--------------------------------------------------------------------
    def _drawSpecialItem(self, dc):
        """ Draw the specical items used by other components"""
        # Draw the camera view line.
        dc.SetPen(wx.Pen('GREEN', width=1, style=wx.PENSTYLE_SOLID))
        camPos = gv.iMapMgr.signalDict['Monitoring Cam'][0].getPos()
        dc.DrawLine(camPos[0], camPos[1], camPos[0]-10, camPos[1]-50)
        dc.DrawLine(camPos[0], camPos[1], camPos[0]+10, camPos[1]-50)
        # Draw the outside track station as a gray box
        dc.SetPen(self.dcDefPen)
        dc.SetBrush(wx.Brush(wx.Colour('GRAY')))
        dc.DrawRectangle(525, 155, 9, 110)

#--PanelMap--------------------------------------------------------------------
    def _drawTrains(self, dc):
        """ Draw the 2 trains on the map."""
        dc.SetPen(self.dcDefPen)
        clashPt = None
        # Draw the train1 on the map.
        trainColor = 'RED' if self.mapMgr.trainA.emgStop else '#CE8349'
        dc.SetBrush(wx.Brush(trainColor))
        for point in self.mapMgr.trainA.getPos():
            dc.DrawRectangle(point[0]-5, point[1]-5, 10, 10)
        # Draw the train2 on the map.
        trainColor = 'RED' if self.mapMgr.trainB.emgStop else '#FFC000'
        dc.SetBrush(wx.Brush(trainColor))
        for i, point in enumerate(self.mapMgr.trainB.getPos()):
            dc.DrawRectangle(point[0]-5, point[1]-5, 10, 10)
            if i == 1: clashPt = point
        # Draw the train clash image.
        if self.trainClash and clashPt:
            dc.DrawBitmap(wx.Bitmap(gv.CLPNG_PATH), clashPt[0]-15, clashPt[1]-15)

#--PanelMap--------------------------------------------------------------------
    def infoWinClose(self, event):
        """ Close/Destroy the pop-up detail information window."""
        if self.infoWindow:
            self.infoWindow.Destroy()
            gv.iDetailPanel = self.infoWindow = None 

#--PanelMap--------------------------------------------------------------------
    def onLeftClick(self, event):
        """ Handle the left mouse button click on the map panel."""
        x, y = event.GetPosition()
        print("PanelMap:    The user has clicked the pos %s" %str((x, y)))
        # Chech the clicked components.
        if gv.iMapMgr.signalDict['Monitoring Cam'][0].checkNear(x, y, 20):
            if self.infoWindow is None and gv.iDetailPanel is None:
                posF = gv.iMainFrame.GetPosition()
                PosShow = (x + posF[0] + 30, y + posF[1]+30)
                # Pop up the camera display window.
                self.infoWindow = wx.MiniFrame(gv.iMainFrame, -1,
                    'Monitoring Camera View', pos=PosShow, size=(300, 230),
                    style=wx.DEFAULT_FRAME_STYLE)
                gv.iDetailPanel = rwp.PanelCameraView(self.infoWindow, 0)
                self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
                self.infoWindow.Show()

#--PanelMap--------------------------------------------------------------------
    def onPaint(self, event):
        """ Draw the whole panel by using the wx device context."""
        dc = wx.PaintDC(self)
        self.dcDefPen = dc.GetPen()
        # Draw the railway as background.
        self._drawRailWay(dc)
        # Draw the trains on the railway.
        self._drawTrains(dc)
        # Draw the train detection sensors.
        self._drawSensors(dc)
        # Draw the gates
        self._drawGate(dc)
        #self._drawAttackPt(dc)
        # Draw all the signal
        self._drawSignal(dc)
        # Draw the specical item which we may add in the future.
        self._drawSpecialItem(dc)
        # Change the display toggle flag.
        self.toggle = not self.toggle

#--PanelMap--------------------------------------------------------------------
    def setHackedPt(self, itemId):
        """ Set the hacked point in the railway system. """
        self.hakedSensorID = itemId
        if itemId < 0: self.selectedPts = None

#--PanelMap--------------------------------------------------------------------
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
            gv.iDetailPanel = rwp.PanelDetailInfo(self.infoWindow, idx)
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

#--PanelMap--------------------------------------------------------------------
    def periodic(self , now):
        """ periodicly call back to do needed calcualtion/panel update"""
        # Update the mapManger's periodic function.
        self.mapMgr.periodic(now)

        # Check whether 2 train clashed.
        if self._checkClash() and self.infoMsgPop:
            gv.iMapMgr.setEmgStop('TrainA', True)
            gv.iMapMgr.setEmgStop('TrainB', True)
            wx.MessageBox('Train Clash Accident Happened!', 'Caution!', wx.OK | wx.ICON_ERROR)
            self.infoMsgPop = False
        
        # Call the onPaint to update the map display.
        self.updateDisplay()
               
#--PanelMap--------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(False)
        self.Update()