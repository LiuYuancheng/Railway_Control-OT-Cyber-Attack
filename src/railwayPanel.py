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

PERIODIC = 500  # how many ms the periodic call back

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
class PanelPLC(wx.Panel):
    """ PLC panel to show the PLC feedback and contorl the related relay.
    """
    def __init__(self, parent, name, ipAddr):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(190, 240))
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.plcName = name
        self.ipAddr = ipAddr
        self.connected = {'0':'Unconnected', '1':'Connected'}
        self.gpioInList = [0]*8 # PLC GPIO input stuation list. 
        self.gpioLbList = []    # input GPIO data lable display list.
        self.gpioOuList = [False]*8 # PLC GPIO output situation list.
        mainUISizer = self.buidUISizer()
        self.SetSizer(mainUISizer)
        self.Layout()
    
#-----------------------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI sizer"""
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.VERTICAL) # main sizer
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
            lbtext = "R_%I0."+str(i) if i < 4 else "F_%I0."+str(i)
            inputLb = wx.StaticText(self, label=lbtext.center(10))
            inputLb.SetBackgroundColour(wx.Colour(120, 120, 120))
            hsizer.Add(inputLb, flag=flagsR, border=2)
            self.gpioLbList.append(inputLb)

            hsizer.AddSpacer(15)
            hsizer.Add(wx.StaticText(self, label=str("%Q0."+str(i)+':').center(10)), flag=flagsR, border=2)
            hsizer.AddSpacer(5)
            outputBt = wx.Button(self, label='OFF', size=(50, 17), name=str(i))
            outputBt.Bind(wx.EVT_BUTTON, self.relayOn)
            hsizer.Add(outputBt, flag=flagsR, border=2)
            mSizer.Add(hsizer, flag=flagsR, border=2)
            mSizer.AddSpacer(3)
        return mSizer

    def updateInput(self, idx, status): 
        """ Update the input status for each PLC input indicator."""
        if idx >= 8 or not status in [0,1]: 
            print("PLC panel: the input parameter is not valid") 
            return
        if self.gpioInList[idx] != status:
            # Change the indicator status.
            color = wx.Colour('Green') if status else wx.Colour(120, 120, 120)
            self.gpioLbList.SetBackgroundColour(color)

    def relayOn(self, event): 
        """ Turn on the related ralay based on the user's action and update the 
            button's display situation.
        """
        obj =  event.GetEventObject()
        print("Button idx %s" %str(obj.GetName()))
        idx = int(obj.GetName())
        self.gpioOuList[idx] = not self.gpioOuList[idx]
        [lbtext, color] = ['ON', wx.Colour('Green')] if self.gpioOuList[idx] else ['OFF', wx.Colour(200, 200, 200)]
        obj.SetLabel(lbtext)
        obj.SetBackgroundColour(color)

    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        #dc.SetFont()
        dc.SetTextForeground('Green')
        dc.SetPen(wx.Pen('#CE8349', width=2, style=wx.PENSTYLE_SOLID))
        dc.DrawText(self.plcName, 15, 15 )
        return

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """RailWay top view map panel to show the rail way contorl situaiton."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(600, 360))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.bitmap = wx.Bitmap(gv.BGPNG_PATH)
        self.bitmapSZ = self.bitmap.GetSize()
        self.toggle = True      # Display toggle flag.     
        self.pplNum = 0         # Number of peopel.
        # Set the tain head and body position.   
        headPos = [550, 160]  # train station start point(train head)
        self.trainPts = [headPos]+[[headPos[0], headPos[1] + 20*(i+1)] for i in range(5)]
        # set the train moving range.
        self.left, self.top, self.right, self.btm = 20, 20, 550, 330
        # set the sensor position.
        self.sensorList = [(0, 400, 20), (1, 140, 20), (2, 20, 180),
                           (3, 156, 330), (4, 286, 330), (5, 412, 330)]
        self.toggle = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        # Draw the train on the map.
        dc.SetBrush(wx.Brush('#CE8349'))
        for point in self.trainPts:
            if point[0] == self.right and point[1] != self.top:
                point[1] -= 10
            elif point[1] == self.top and point[0] != self.left:
                point[0] -= 10
            elif point[0] == self.left and point[1] != self.btm:
                point[1] += 10
            elif point[1] == self.btm and point[0] != self.right:
                point[0] += 10
            dc.DrawRectangle(point[0]-5, point[1]-5, 15, 15)
        # High light the sensor which detected the train.
        penColor = 'BLUE' if self.toggle else 'RED'
        dc.SetPen(wx.Pen(penColor, width=4, style=wx.PENSTYLE_LONG_DASH))
        head, tail = self.trainPts[0], self.trainPts[-1]
        l, r = min(head[0], tail[0]), max(head[0], tail[0])
        t, b = min(head[1], tail[1]), max(head[1], tail[1])
        for sensorPos in self.sensorList: 
            if  l <= sensorPos[1] <= r and  t<= sensorPos[2] <=b:
                if sensorPos[0]<2: # top sensors 
                    dc.DrawLine(sensorPos[1]+5, sensorPos[2]+10, sensorPos[1]+5, sensorPos[2]+40)
                elif 2 < sensorPos[0]: # left sensors
                    dc.DrawLine(sensorPos[1]-5, sensorPos[2], sensorPos[1]-5, sensorPos[2]-40)
                else:   # buttom sensors.
                    dc.DrawLine(sensorPos[1], sensorPos[2], sensorPos[1]+30, sensorPos[2])
        self.toggle = not self.toggle
        
    #-----------------------------------------------------------------------------
    def OnClick(self, event):
        """ Handle the click event."""
        x, y = event.GetPosition()
        pass

    #-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(True)
        self.Update()
