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
import math
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
        self.hitbitmap = wx.Bitmap(gv.HTPNG_PATH)
        self.passbitmap = wx.Bitmap(gv.LPJPG_PATH)
        self.stopbitmap = wx.Bitmap(gv.LSJPG_PATH)

        #self.leftTimge = wx.Image(png)
        self.toggle = False     # Display flash toggle flag.
        # gate contorl parameters.(The 0-total close, 15-total open)
        self.gateCount = 15
        # Set the tain head and body position.
        headPos = [550, 160]  # train station start point(train head)
        self.trainPts = [headPos] + \
            [[headPos[0], headPos[1] + 20*(i+1)] for i in range(4)]
        # set the train moving range.
        self.left, self.top, self.right, self.btm = 20, 20, 550, 330
        # set the sensor position.
        # Id of the sensor which detected the train passing.
        self.dockCount = 0       # flag to identify train in the station. 
        self.stationRg = (110, 210) # train station range.
        self.attackPts = [(340, 110), (145, 80), (90, 177), (156, 272), (286, 272), (412, 272) ]
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
        stSensorList = [(550, 130, 3)]
        for item in stSensorList:
            sensor = agent.AgentSensor(self, -1, (item[:2]), item[-1])
            self.sensorList.append(sensor)
        # Add the train turn sensors.
        conerSenList = [(550, 20, 3), (20, 20, 0), (20, 330, 1), (550, 330, 2)]
        for item in conerSenList:
            sensor = agent.AgentSensor(self, -1, (item[:2]), item[-1])
            self.sensorList.append(sensor)

        gateDetector = agent.AgentSensor(self, -1, (290, 20), 0)
        self.sensorList.append(gateDetector)

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
            gv.iDetailPanel = PanelAttackSet(self.infoWindow, idx)
            gv.iDetailPanel.updateState(idx=idx, state='Normal', origalV=0, changedV=0)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()

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
        # Draw the train on the map.
        trainColor = 'RED' if self.tranState == -1 else '#CE8349'
        dc.SetBrush(wx.Brush(trainColor))
        for point in self.trainPts:
            dc.DrawRectangle(point[0]-7, point[1]-7, 19, 19)
        # High light the sensor which detected the train.
        dc.SetBrush(wx.Brush('GRAY'))
        for sensor in self.sensorList:
            sensorPos = sensor.pos
            dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)

        penColor = 'GREEN' if self.toggle else 'RED'
        dc.SetBrush(wx.Brush(penColor))
        if self.sensorid >= 0:
            sensor = self.sensorList[self.sensorid]
            sensorPos = sensor.pos
            dc.DrawRectangle(sensorPos[0]-4, sensorPos[1]-4, 8, 8)
        # draw all the sensors: 

        self.DrawAttackPt(dc)
        self.DrawGate(dc)
        self.DrawStation(dc)
        # Update the display flash toggle flag. 
        self.toggle = not self.toggle

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
        if self.gateCount == 15:
            dc.SetPen(wx.Pen('BLACK', width=1, style=wx.PENSTYLE_DOT))
            dc.SetBrush(wx.Brush(wx.Colour('Black')))
            dc.DrawRectangle(250, 9, 30, 30)
            dc.DrawBitmap(self.passbitmap, 280, 50)
        else:
            dc.DrawBitmap(self.stopbitmap, 280, 50)
        dc.SetPen(wx.Pen('GREEN', width=1, style=wx.PENSTYLE_SOLID))
        dc.DrawLine(294, 80, 294, 110)

        penColor = 'RED' if self.gateCount == 0 else 'GREEN'
        dc.SetPen(wx.Pen(penColor, width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(250, 0, 250, 80)
        dc.DrawLine(280, 0, 280, 50)
        # Draw the pedestrians block door
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        dc.DrawLine(265+self.gateCount, 7, 265+self.gateCount+15, 7)
        dc.DrawLine(265-self.gateCount, 7, 265-self.gateCount-15, 7)
        dc.DrawLine(265+self.gateCount, 37, 265+self.gateCount+15, 37)
        dc.DrawLine(265-self.gateCount, 37, 265-self.gateCount-15, 37)
        # Draw the pedestrians signal.
        #print(self.sensorid)
        if self.toggle and self.gateCount == 15:
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
            if gv.iPlcPanelList[plcidx]: gv.iPlcPanelList[plcidx].updateInput(idx%8, state)

            if self.sensorid > 0:
                self.sensorList[self.sensorid].setSensorState(0)
            self.sensorid = sensorid
        # Start to close the gate.
        if self.sensorid == 0 and self.hakedSensorID != 0 : 
            self.gateCount -= 3
        elif self.sensorid == 1: 
            self.gateCount += 3
        
        if self.sensorid == 0:
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(origalV=1)
        if  self.hakedSensorID == 0 and sensorid == -1:
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(origalV=0)

        self.updateTrainState(self.sensorid)
        if self.gateDanger and self.sensorid == 1:
            self.gateDanger = False


        # make the count in side the range. 
        self.gateCount = min(15, max(0, self.gateCount))
        # Check whether train in side the station.
        head = self.trainPts[0]

        if head[0] == self.right and head[1] == self.stationRg[0] and self.dockCount == 0: 
            print("Train has got to the station.wait for 10s for people get in.")
            self.dockCount = 20
        if self.dockCount > 0:
            self.dockCount-=1
        else:
            self.timeCount-=1
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

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelTrainCtrl(wx.Panel):
    """ Train contorl panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        
        self.statDict = {
            '0': ('Running',    'GREEN',    80),
            '1': ('ShowDown',   'YELLOW',   40),
            '2': ('Accelerate', '#03AC15',  90),
            '3': ('Turning',    '#93CB8B',  60),
            '4': ('Waiting',    'ORANGE',   0),
            '5': ('Stopped',    'RED',      0)
        }
        hsizer = self.buidUISizer()
        self.SetSizer(hsizer)
        self.setState(0)
    
    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(self, label="Train Control"), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(165, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Row idx = 0: train state control.
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.StaticText(self, label="Train status:"), flag=flagsR, border=2)
        hbox0.AddSpacer(5)
        self.statLb = wx.StaticText(self, label="run".center(16))
        #self.statLb.SetBackgroundColour(wx.Colour('GREEN'))
        

        hbox0.Add(self.statLb, flag=flagsR, border=2)
        vsizer.Add(hbox0, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Row idx = 1: Train speed contorl
        
        vsizer.Add(wx.StaticText(self, label="Train Speed:"), flag=flagsR, border=2)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.speedDisplay = wx.Gauge(self, range = 10, size = (100, 20), style =  wx.GA_HORIZONTAL)
        hbox1.Add(self.speedDisplay, flag=flagsR, border=2)
        hbox1.AddSpacer(5)
        self.speedLb = wx.StaticText(self, label="[ 80km/h ]")
        hbox1.Add(self.speedLb, flag=flagsR, border=2)
        vsizer.Add(hbox1, flag=flagsR, border=2)
        vsizer.AddSpacer(5)


        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(165, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)

        # Row idx = 2: Train direction contorl
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(self, label="Direction :"), flag=flagsR, border=2)
        
        self.dirCtrl = wx.ComboBox(self, -1, choices=['anticlockwise', 'clockwise'], style=wx.CB_READONLY)
        self.dirCtrl.SetSelection(0)
        hbox2.Add(self.dirCtrl, flag=flagsR, border=2)
        vsizer.Add(hbox2, flag=flagsR, border=2)
        vsizer.AddSpacer(5)

        # Row idx =3 : Train speed control
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(self, label="Speed Ctrl [*10km]"), flag=flagsR, border=2)
        self.speedCtrl = wx.SpinCtrl(self, -1, '8', size = (50, -1), min=1, max=10) 
        hbox3.Add(self.speedCtrl, flag=flagsR, border=2)
        hbox3.AddSpacer(5)
        vsizer.Add(hbox3, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        #self.speedDisplay.SetValue(8)
        
        
        # Row idx = 4: Station wait time contorl
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(self, label="Station waitT [sec]:"), flag=flagsR, border=2)
        self.wTimeCtrl = wx.SpinCtrl(self, -1, '10', size = (50, -1), min=1, max=20)
        hbox4.Add(self.wTimeCtrl, flag=flagsR, border=2)
        vsizer.Add(hbox4, flag=flagsR, border=2)


        # Row idx = 5: Station wait time contorl
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.Bitmap(gv.EMGST_PATH, wx.BITMAP_TYPE_ANY)
        self.stopbtn1 = wx.BitmapButton(self, id = wx.ID_ANY, bitmap = bmp,
         size = (bmp.GetWidth()+10, bmp.GetHeight()+10))

        self.stopbtn1.Bind(wx.EVT_BUTTON, self.emgStop)
        
        hbox5.Add(self.stopbtn1, flag=flagsR, border=2)
        hbox5.AddSpacer(10)
        bmp1 = wx.Bitmap(gv.RECOV_PATH, wx.BITMAP_TYPE_ANY)
        self.recbtn1 = wx.BitmapButton(self, id = wx.ID_ANY, bitmap = bmp1,
         size = (bmp1.GetWidth()+10, bmp1.GetHeight()+10))
        self.recbtn1.Bind(wx.EVT_BUTTON, self.emgRec)

        hbox5.Add(self.recbtn1, flag=flagsR, border=2)
        vsizer.Add(hbox5, flag=flagsR, border=2)
        

        return vsizer

    def emgStop(self, event):
        gv.iEmgStop = True
        if gv.iMapPanel:
            gv.iMapPanel.tranState = -1
            gv.iMapPanel.updateDisplay()

        self.setState(5)

    def emgRec(self, event):
        gv.iEmgStop = False
        if gv.iMapPanel:
            gv.iMapPanel.tranState = 0
            gv.iMapPanel.updateDisplay()

    def setState(self, idx): 
        """ Set the train running state. """
        state = self.statDict[str(idx)]
        self.statLb.SetLabel(str(state[0]).center(16))
        self.statLb.SetBackgroundColour(wx.Colour(state[1]))
        self.statLb.Refresh()
        self.speedLb.SetLabel("[ %dkm/h ]" %state[2])
        self.speedDisplay.SetValue(state[2]//10) 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelSimuCtrl(wx.Panel):
    """ Simulation contorl panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        hsizer = self.buidUISizer()
        self.SetSizer(hsizer)

    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(self, label="Active attack simulation:"), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(165, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)

        idLb = wx.StaticText(self, label="Attack point ID: [001] ")
        vsizer.Add(idLb, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticText(self, label="Active attack type:"), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.simuCb1 = wx.CheckBox(self, -1 ,'1. Random some where')
        vsizer.Add(self.simuCb1, flag=flagsR, border=2)
        self.simuCb1.Disable()

        vsizer.AddSpacer(5)
        self.simuCb2 = wx.CheckBox(self, -1 ,'2. Man in middle')
        vsizer.Add(self.simuCb2, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.simuCb3 = wx.CheckBox(self, -1 ,'3. Trojar attack')
        vsizer.Add(self.simuCb3, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.simuCb4 = wx.CheckBox(self, -1 ,'4. Eternal blue')
        vsizer.Add(self.simuCb4, flag=flagsR, border=2)
        self.simuCb4.Disable()
        vsizer.AddSpacer(5)
        self.attackCtrl = wx.ComboBox(self, -1, choices=['Overwrite input', 'Overwrite output'], style=wx.CB_READONLY)
        self.attackCtrl.SetSelection(0)
        vsizer.Add(self.attackCtrl, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(self, label="Overwrite data:"), flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        
        self.tc1 = wx.TextCtrl(self, -1, "", size=(40, -1), style=wx.TE_PROCESS_ENTER)
        self.tc1.SetValue("1")
        hsizer.Add(self.tc1, flag=flagsR, border=2)
        
        vsizer.Add(hsizer, flag=flagsR, border=2)
        vsizer.AddSpacer(10)

        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.simuBt1 = wx.Button(self, label='Set Attack', style=wx.BU_LEFT, size=(60,25))
        self.simuBt1.Bind(wx.EVT_BUTTON, self.setAttck)
        hsizer1.Add(self.simuBt1, flag=flagsR, border=2)
        hsizer1.AddSpacer(5)
        self.simuBt2 = wx.Button(self, label='Clear', style=wx.BU_LEFT, size=(60,25))
        self.simuBt2.Bind(wx.EVT_BUTTON, self.setAttck)
        hsizer1.Add(self.simuBt2, flag=flagsR, border=2)
        vsizer.Add(hsizer1, flag=flagsR, border=2)

        vsizer.AddSpacer(5)
        return vsizer

    def setAttck(self, event):
        buttonLb = event.GetEventObject().GetLabel()
        if buttonLb == 'Set Attack': 
            gv.iMapPanel.setHackedPt(0)
            gv.iMapPanel.updateDisplay()
            hackedV = self.tc1.GetValue()
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(idx=1, state='Man in mid', origalV=0, changedV=hackedV)
        else:
            gv.iMapPanel.setHackedPt(-2)
            gv.iMapPanel.updateDisplay()
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(idx=1, state='Normal', origalV=0, changedV=0)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelAttackSet(wx.Panel):
    def __init__(self, parent, idx, size=(140, 150)):
        """ Set the attack situaltion."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.idx = idx 
        self.hackState = ""
        self.origalV = self.changedV = 0
        hsizer = self.buidUISizer()

        self.SetSizer(hsizer)

    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)

        self.idLb = wx.StaticText(self, label="Attack point ID: [%s] " %str(self.idx).zfill(3))
        vsizer.Add(self.idLb, flag=flagsR, border=2)
        vsizer.AddSpacer(10)

        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(135, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        

        self.stateLb =  wx.StaticText(self, label="Normal")
        self.stateLb.SetBackgroundColour(wx.Colour('GREEN'))
        vsizer.Add(self.stateLb, flag=flagsR, border=2)
        vsizer.AddSpacer(10)

        self.orignLb = wx.StaticText(self, label="Orignal input: ")
        vsizer.Add(self.orignLb, flag=flagsR, border=2)
        vsizer.AddSpacer(10)

        self.hackLb = wx.StaticText(self, label="Hacked input: None")
        vsizer.Add(self.hackLb, flag=flagsR, border=2)
        vsizer.AddSpacer(10)

        return vsizer

    def updateState(self, idx=None, state=None, origalV=None, changedV=None):
        if not idx is None and self.idx!= idx :
            self.idx = idx
            self.idLb.SetLabel("Attack point ID: [%s] " %str(self.idx).zfill(3))
    
        if not state is None and self.hackState != state:
            self.hackState = state
            if self.hackState != 'Normal':
                self.stateLb.SetLabel(self.hackState)
                self.stateLb.SetBackgroundColour(wx.Colour('RED'))
            else: 
                self.stateLb.SetLabel("Normal")
                self.stateLb.SetBackgroundColour(wx.Colour('Green'))
            self.Refresh(False)

        if not origalV is None and self.origalV != origalV:
            self.origalV = origalV
            self.orignLb.SetLabel("Orignal input: %s" %str(origalV))

        if not changedV is None and self.changedV != changedV:
            self.changedV = changedV
            self.hackLb.SetLabel("Hacked input: %s" %str(changedV))