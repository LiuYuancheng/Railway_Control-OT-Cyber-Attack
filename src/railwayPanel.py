#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railWayPanel.py
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
import wx.grid
import time
import random
import railwayGlobal as gv 
import railwayAgentPLC as agent

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPlaceHolder(wx.Panel):
    """ Place Holder Panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        wx.StaticText(self, -1, "Place Holder:", (20, 20))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelInfoGrid(wx.Panel):
    """ Panel provides three Grids to show/set the all the PLCs' I/O data."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.nameLbList = []    # PLC name/type list 
        self.gpioLbList = []    # PLC GPIO display list
        self.gridList = []      # PLC data display grid list 
        hsizer = self.buidUISizer()
        self.initData()
        self.SetSizer(hsizer)

#-----------------------------------------------------------------------------
    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(3):
            vSizer = wx.BoxSizer(wx.VERTICAL)
            # Row idx = 0 : show the PLC name/type and the I/O usage.
            nameLb = wx.StaticText(self, label="PLC Name: ".ljust(15))
            self.nameLbList.append(nameLb)
            vSizer.Add(nameLb, flag=flagsR, border=2)
            vSizer.AddSpacer(10)
            gpioLbN = wx.StaticText(self, label="PLC I/O usage: ".ljust(15))
            vSizer.Add(gpioLbN, flag=flagsR, border=2)
            self.gpioLbList.append(gpioLbN)
            vSizer.AddSpacer(10)
            vSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
            vSizer.AddSpacer(10)
            # Row idx =1 : show the PLC data.
            grid = wx.grid.Grid(self, -1)
            grid.CreateGrid(8, 4)
            grid.SetRowLabelSize(30)
            grid.SetColLabelSize(22)
            grid.SetColSize(0, 40)
            grid.SetColSize(1, 40)
            grid.SetColSize(2, 40)
            grid.SetColSize(3, 40)
            # Set the column label. 
            grid.SetColLabelValue(0, 'IN')
            grid.SetColLabelValue(1, 'Val')
            grid.SetColLabelValue(2, 'OUT')
            grid.SetColLabelValue(3, 'Val')
            vSizer.Add(grid, flag=flagsR, border=2)
            self.gridList.append(grid)
            hsizer.Add(vSizer, flag=flagsR, border=2)
            hsizer.AddSpacer(5)
        return hsizer
    #-----------------------------------------------------------------------------
    def initData(self):
        """ Init all the data which will display on the panel."""
        for i in range(3):
            dataTuple = gv.PLC_CFG['PLC'+str(i)]
            self.setName(i, 'PLC'+str(i) + dataTuple[0])
            self.setIOLB(i, dataTuple[3], dataTuple[4])
            for j in range(8):
                self.gridList[i].SetCellValue(j, 0, '%I0.'+str(j))
                self.gridList[i].SetCellValue(j, 1, '0')
                self.gridList[i].SetCellValue(j, 2, '%Q0.'+str(j))
                self.gridList[i].SetCellValue(j, 3, '0')

    #-----------------------------------------------------------------------------
    def setName(self, idx , name):
        """ Set the PLC name, idx:(int) PLC index, name:(str) name/type """
        self.nameLbList[idx].SetLabel("PLC Name:".ljust(15)+str(name))

    #-----------------------------------------------------------------------------
    def setIOLB(self, idx, inputN, outputN):
        """ Set the PLC I/O usage display. idx(int), inputN(int), outputN(int)"""
        lbStr = "PLC I/O usage:  [ " + str(inputN)+'/'+str(outputN)+' ]'
        self.gpioLbList[idx].SetLabel(lbStr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPLC(wx.Panel):
    """ PLC panel to show the PLC feedback and contorl the related relay.
    """
    def __init__(self, parent, name, ipAddr):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.plcName = name
        self.ipAddr = ipAddr
        self.connected = {'0': 'Unconnected', '1': 'Connected'}
        self.gpioInList = [0]*8 # PLC GPIO input stuation list.
        self.gpioLbList = []    # input GPIO data lable display list.
        self.gpioOuList = [False]*8  # PLC GPIO output situation list.
        mainUISizer = self.buidUISizer()
        self.SetSizer(mainUISizer)
        #self.Layout() # must call the layout if the panel size is set to fix.

    #-----------------------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI sizer"""
        mSizer = wx.BoxSizer(wx.VERTICAL) # main sizer
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer.AddSpacer(5)
        # Row idx = 0 : set the basic PLC informaiton.
        self.nameLb = wx.StaticText(self, label="PLC Name: ".ljust(15)+self.plcName)
        mSizer.Add(self.nameLb, flag=flagsR, border=2)
        self.ipaddrLb = wx.StaticText(self, label="PLC IPaddr: ".ljust(15)+self.ipAddr)
        mSizer.Add(self.ipaddrLb, flag=flagsR, border=2)
        self.connLb = wx.StaticText(self, label="Connection:".ljust(15)+self.connected['0'])
        mSizer.Add(self.connLb, flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        # Row idx = 1: set the GPIO and feed back of the PLC. 
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        # - row line structure: Input indicator | output label | output button with current status.
        for i in range(8):
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            # M221 doc: IO 0:3 are regular input, IO 4:7 are fast input.
            # Col idx = 0: PLC input indicators.
            lbtext = "R_%I0."+str(i) if i < 4 else "F_%I0."+str(i)
            inputLb = wx.StaticText(self, label=lbtext.center(10))
            inputLb.SetBackgroundColour(wx.Colour(120, 120, 120))
            hsizer.Add(inputLb, flag=flagsR, border=2)
            self.gpioLbList.append(inputLb)
            # Col idx =1: OLC output labels.
            hsizer.AddSpacer(15)
            hsizer.Add(wx.StaticText(self, label=str("%Q0."+str(i)+':').center(10)), flag=flagsR, border=2)
            # Col idx =2: OLC output ON/OFF contorl buttons.
            hsizer.AddSpacer(5)
            outputBt = wx.Button(self, label='OFF', size=(50, 17), name=self.plcName+':'+str(i))
            outputBt.Bind(wx.EVT_BUTTON, self.relayOn)
            hsizer.Add(outputBt, flag=flagsR, border=2)
            mSizer.Add(hsizer, flag=flagsR, border=2)
            mSizer.AddSpacer(3)
        return mSizer

    #-----------------------------------------------------------------------------
    def updateInput(self, idx, status): 
        """ Update the input status for each PLC input indicator."""
        if idx >= 8 or not status in [0,1]: 
            print("PLC panel:   the input parameter is not valid") 
            return
        elif self.gpioInList[idx] != status:
            self.gpioInList[idx] = status
            # Change the indicator status.
            color = wx.Colour('GREEN') if status else wx.Colour(120, 120, 120)
            self.gpioLbList[idx].SetBackgroundColour(color)
            self.Refresh(False) # needed after the status update.

    #-----------------------------------------------------------------------------
    def relayOn(self, event): 
        """ Turn on the related ralay based on the user's action and update the 
            button's display situation.
        """
        obj = event.GetEventObject()
        print("PLC panel:   Button idx %s" % str(obj.GetName()))
        idx = int(obj.GetName().split(':')[-1])
        self.gpioOuList[idx] = not self.gpioOuList[idx]
        [lbtext, color] = ['ON', wx.Colour('Green')] if self.gpioOuList[idx] else [
            'OFF', wx.Colour(200, 200, 200)]
        obj.SetLabel(lbtext)
        obj.SetBackgroundColour(color)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """RailWay top view map panel to show the rail way contorl situaiton."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(600, 360))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.bitmap = wx.Bitmap(gv.BGPNG_PATH)      # background bitmap
        self.wkbitmap = wx.Bitmap(gv.WKJPG_PATH)    # pedestrians wald bitmap.
        #self.leftTimge = wx.Image(png)
        self.toggle = False     # Display flash toggle flag.
        # gate contorl parameters.(The 0-total close, 15-total open)
        self.gateCount = 15
        # Set the tain head and body position.
        headPos = [550, 160]  # train station start point(train head)
        self.trainPts = [headPos] + \
            [[headPos[0], headPos[1] + 20*(i+1)] for i in range(5)]
        # set the train moving range.
        self.left, self.top, self.right, self.btm = 20, 20, 550, 330
        # set the sensor position.
        # Id of the sensor which detected the train passing.
        self.dockCount = 0       # flag to identify train in the station. 
        self.stationRg = (110, 210) # train station range.
        self.sensorid = -1
        self.sensorList = []
        self.addSensors()
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    #-----------------------------------------------------------------------------
    def addSensors(self):
        """ added the train detection sensors in the sensor List 
        """
        # Add the rail way sensors.
        sensorList = [(405, 20, 0), (145, 20, 0), (20, 180, 1),
                      (156, 330, 2), (286, 330, 2), (412, 330, 2)]
        for item in sensorList:
            sensor = agent.AgentSensor(self, -1, (item[:2]), item[-1])
            self.sensorList.append(sensor)
        # Add the station sensors.
        stSensorList = [(550, 100, 3), (550, 230, 3)]
        for item in stSensorList:
            sensor = agent.AgentSensor(self, -1, (item[:2]), item[-1])
            self.sensorList.append(sensor)
        # Add the train turn sensors.
        conerSenList = [(550, 20, 3), (20, 20, 0), (20, 330, 1), (550, 330, 2)]
        for item in conerSenList:
            sensor = agent.AgentSensor(self, -1, (item[:2]), item[-1])
            self.sensorList.append(sensor)

    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        # Draw the train on the map.
        dc.SetBrush(wx.Brush('#CE8349'))
        for point in self.trainPts:
            dc.DrawRectangle(point[0]-7, point[1]-7, 19, 19)
        # High light the sensor which detected the train.
        penColor = 'GREEN' if self.toggle else 'RED'
        dc.SetBrush(wx.Brush(penColor))
        if self.sensorid >= 0:
            sensor = self.sensorList[self.sensorid]
            sensorPos = sensor.pos
            dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)
        
        self.DrawGate(dc)
        self.DrawStation(dc)
        # Update the display flash toggle flag. 
        self.toggle = not self.toggle
    
    #-----------------------------------------------------------------------------
    def DrawGate(self, dc):
        """ Draw the pedestrians walking gate for passing the railway."""
        # Draw the bridge(left and right)
        if self.gateCount == 15:
            dc.SetPen(wx.Pen('BLACK', width=1, style=wx.PENSTYLE_DOT))
            dc.SetBrush(wx.Brush(wx.Colour('Black')))
            dc.DrawRectangle(250, 9, 30, 30)
        penColor = 'GREEN' if self.gateCount == 0 else 'RED'
        dc.SetPen(wx.Pen(penColor, width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(250, 0, 250, 45)
        dc.DrawLine(280, 0, 280, 45)
        # Draw the pedestrians block door
        penColor = 'RED' if self.gateCount == 0 else 'GREEN'
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        dc.DrawLine(265+self.gateCount, 7, 265+self.gateCount+15, 7)
        dc.DrawLine(265-self.gateCount, 7, 265-self.gateCount-15, 7)
        dc.DrawLine(265+self.gateCount, 37, 265+self.gateCount+15, 37)
        dc.DrawLine(265-self.gateCount, 37, 265-self.gateCount-15, 37)
        # Draw the pedestrians signal.
        if self.toggle and self.gateCount == 15:
            dc.DrawBitmap(self.wkbitmap, 250, 7)
    
    #-----------------------------------------------------------------------------
    def DrawStation(self, dc):
        """ Draw the station part"""
        dc.SetPen(wx.Pen('BLACK', width=1, style=wx.PENSTYLE_DOT))
        dc.SetBrush(wx.Brush(wx.Colour('Black')))
        if self.dockCount == 0:    
            dc.DrawRectangle(568, 110, 30, 30)
            dc.DrawRectangle(568, 180, 30, 30)
        else:
            y = 110 if self.toggle else 180
            dc.DrawRectangle(568, y, 30, 30)
            dc.SetPen(wx.Pen('#FFC000', width=1, style=wx.PENSTYLE_SOLID))
            dc.SetBrush(wx.Brush(wx.Colour('#FFC000')))
            dc.DrawRectangle(536, 116, 29, 90)
            points = [(530, 114), (565, 114), (565, 208), (530, 208), (530, 114)]
            dc.SetPen(wx.Pen('Green', width=4, style=wx.PENSTYLE_SOLID))
            for i in range(len(points)-1):
                dc.DrawLine(points[i], points[i+1])

    #-----------------------------------------------------------------------------
    def checkSensor(self):
        """ Check which sensor has detected the train pass."""
        head, tail = self.trainPts[0], self.trainPts[-1]
        l, r = min(head[0], tail[0]), max(head[0], tail[0])
        t, b = min(head[1], tail[1]), max(head[1], tail[1])

        for sensor in self.sensorList:
            sensorPos = sensor.pos
            if  l <= sensorPos[0] <= r and t<= sensorPos[1] <=b:
                sensor.setSensorState(1)
                return sensor.sensorID # return the sensor index
        return -1 # return -1 if there is no sensor detected. 

    #-----------------------------------------------------------------------------
    def getTrainPos(self):
        """ return the current train position."""
        return self.trainPts

    #-----------------------------------------------------------------------------
    def periodic(self , now):
        """ periodicly call back to do needed calcualtion/panel update"""
        # Set the detect sensor status related to PLC status
        self.updateTrainPos()
        sensorid = self.checkSensor()
        if self.sensorid != sensorid:
            [idx, state] =[self.sensorid, 0] if self.sensorid >= 0 and sensorid <= 0 else [sensorid, 1]
            # get related plc Idx 
            plcidx = idx//8 
            if gv.iPlcPanelList[plcidx]: gv.iPlcPanelList[plcidx].updateInput(plcidx%8, state)

            if self.sensorid > 0:
                self.sensorList[self.sensorid].setSensorState(0)
            self.sensorid = sensorid
        # Start to close the gate.
        if self.sensorid == 0: 
            self.gateCount -= 3
        elif self.sensorid == 1: 
            self.gateCount += 3
        # make the count in side the range. 
        self.gateCount = min(15, max(0, self.gateCount))
        # Check whether train in side the station.
        head = self.trainPts[0]

        if head[0] == self.right and head[1] == self.stationRg[0] and self.dockCount == 0: 
            print("Train has got to the station.wait for 10s for people get in.")
            self.dockCount = 20
        if self.dockCount > 0: self.dockCount-=1
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
        for point in self.trainPts: 
            if point[0] == self.right and point[1] != self.top:
                point[1] -= 10
            elif point[1] == self.top and point[0] != self.left:
                point[0] -= 10
            elif point[0] == self.left and point[1] != self.btm:
                point[1] += 10
            elif point[1] == self.btm and point[0] != self.right:
                point[0] += 10
        
    #-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(False)
        self.Update()
