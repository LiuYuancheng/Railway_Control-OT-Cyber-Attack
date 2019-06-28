#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        XAKAsensor reader.py
#
# Purpose:     This function is used to read the data from XAKA people counting
#              sensor and show the data in the UI list.
#              - register the sensor to the server.
#
# Author:      Yuancheng Liu
#
# Created:     2019/03/27
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------

import platform
import io, sys
import glob
import wx # use wx to build the UI.
import time
import serial
import threading
from struct import *
import random
from functools import partial
import firmwMsgMgr
import firmwTLSclient as SSLC
import firmwGlobal as gv
import XAKAsensorPanel as xsp

PERIODIC = 500
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """ Draw the office top view map with the data. The background Image setting 
        example may be useful in the future: 
        http://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
    """
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(600, 360))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.bitmap = wx.Bitmap("firmwSign\\Trainbg.png")
        self.bitmapSZ = self.bitmap.GetSize()
        self.toggle = True      # Display toggle flag.     
        self.pplNum = 0         # Number of peopel.
        self.highLightIdx = 0   # High light area. 
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.startPoint = [550, 160]
        
        self.headPos = self.startPoint
        self.bodypos = []
        for i in range(5):
            point = [self.startPoint[0], self.startPoint[1]]
            point[1] += 20*(i+1)
            self.bodypos.append(point)

        self.left = 20
        self.top = 20
        self.right= 550
        self.btm = 330
        # id, position
        self.sensorList = [(0, 400, 20), (1, 140, 20), (2, 20, 180),
                           (3, 156, 330), (4, 286, 330), (5, 412, 330)]
        self.toggle = False

        #self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        
        if self.headPos[0] == self.right and self.headPos[1]!=self.top:
            self.headPos[1] -= 10
        elif  self.headPos[1] ==self.top and self.headPos[0] != self.left:
            self.headPos[0] -= 10
        elif self.headPos[0] == self.left and self.headPos[1]!=self.btm:
            self.headPos[1] += 10
        elif  self.headPos[1]==self.btm and self.headPos[0] != self.right:
            self.headPos[0] += 10

        dc.SetBrush(wx.Brush('#CE8349'))
        dc.DrawRectangle(self.headPos[0]-5, self.headPos[1]-5, 15, 15)
        
        for point in self.bodypos:
            if point[0] == self.right and point[1]!=self.top:
                point[1] -= 10
            elif  point[1] ==self.top and point[0] != self.left:
                point[0] -= 10
            elif point[0] == self.left and point[1]!=self.btm:
                point[1] += 10
            elif  point[1]==self.btm and point[0] != self.right:
                point[0] += 10
            dc.SetBrush(wx.Brush('#CE8349'))
            dc.DrawRectangle(point[0]-5, point[1]-5, 15, 15)

        penColor = 'BLUE' if self.toggle else 'RED'
        dc.SetPen(wx.Pen(penColor, width=4, style=wx.PENSTYLE_LONG_DASH))
        # high light the sensor:
        l = min(self.headPos[0], self.bodypos[-1][0])
        r = max(self.headPos[0], self.bodypos[-1][0])
        t = min(self.headPos[1], self.bodypos[-1][1])
        b = max(self.headPos[1], self.bodypos[-1][1])

        for sensorPos in self.sensorList: 
            if  l <= sensorPos[1] <= r and  t<= sensorPos[2] <=b:
                if sensorPos[0]<2:
                    dc.DrawLine(sensorPos[1]+5, sensorPos[2]+10, sensorPos[1]+5, sensorPos[2]+40)
                elif 2 < sensorPos[0]:
                    dc.DrawLine(sensorPos[1]-5, sensorPos[2], sensorPos[1]-5, sensorPos[2]-40)
                else:
                    dc.DrawLine(sensorPos[1], sensorPos[2], sensorPos[1]+30, sensorPos[2])
        self.toggle = not self.toggle
        return
        
    #-----------------------------------------------------------------------------
    def DrawHighLight(self, dc, w, h):
        """ High light the area user clicked"""
        # set the position: l-left t-top r-right b-bottum x_offset y_offset.
        l, t, r, b, x_offset, y_offset = 1, 1, w, h, 0, 0 
        
        if self.highLightIdx == 1:
            x_offset = w
        elif self.highLightIdx == 2:
            y_offset = h
        elif self.highLightIdx == 3:
            x_offset = w
            y_offset = h
        # Hight list area by draw a rectangle.
        dc.DrawLine(l+x_offset, t+y_offset, r+x_offset, t+y_offset)
        dc.DrawLine(l+x_offset, t+y_offset, l+x_offset, b+y_offset)
        dc.DrawLine(r+x_offset, t+y_offset, r+x_offset, b+y_offset)
        dc.DrawLine(l+x_offset, b+y_offset, r+x_offset, b+y_offset)

    #-----------------------------------------------------------------------------
    def OnClick(self, event):
        """ High light the user clicked area."""
        x, y = event.GetPosition()
        w, h = self.bitmapSZ[0]//2, self.bitmapSZ[1]//2
        if x < w and y < h:
            self.highLightIdx = 0
        elif x >= w and y < h:
            self.highLightIdx = 1
        elif x < w and y >= h:
            self.highLightIdx = 2
        else:
            self.highLightIdx = 3
        self.updateDisplay()
        # mark the line in the sensor information grid.
        self.Parent.markSensorRow(self.highLightIdx)

    #-----------------------------------------------------------------------------
    def updateNum(self, number):
        """ Udpate the self people number."""
        self.pplNum = int(number)

    #-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(True)
        self.Update()

class PanelPLC(wx.Panel):
    """ Draw the office top view map with the data. The background Image setting 
        example may be useful in the future: 
        http://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
    """
    def __init__(self, parent, name):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(190, 240))
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.plcName = name
        self.ipAddr = '127.0.0.1'
        #self.bitmap = wx.Bitmap("firmwSign\\images.jpg")
        #self.bitmapSZ = self.bitmap.GetSize()
        self.toggle = True      # Display toggle flag.     
        self.pplNum = 0         # Number of peopel.
        self.highLightIdx = 0   # High light area. 
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        mainUISizer = self.buidUISizer()
        self.SetSizer(mainUISizer)
        self.Refresh(True)
        self.Layout()

    def buidUISizer(self):
        """ Build the UI with 2 columns.left: Map, right: sensor data Grid."""
        flagsT = wx.RIGHT
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.nameLb = wx.StaticText(self, label="PLC Name: "+self.plcName)
        vsizer.Add(self.nameLb, flag=flagsR, border=2)
        self.ipaddrLb = wx.StaticText(self, label="PLC IPaddr: "+self.ipAddr)
        vsizer.Add(self.ipaddrLb, flag=flagsR, border=2)
        self.connLb = wx.StaticText(self, label="Connection: [connected]")
        vsizer.Add(self.connLb, flag=flagsR, border=2)
        vsizer.AddSpacer(10)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(10)
        for i in range(8):
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            # Added the input indicator.
            lbtext = "R_%I0."+str(i) if i <4 else "F_%I0."+str(i)
            inputLb = wx.StaticText(self, label=lbtext.center(10))
            inputLb.SetBackgroundColour(wx.Colour(120, 120, 120))
            hsizer.Add(inputLb, flag=flagsR, border=2)
            hsizer.AddSpacer(15)
            hsizer.Add(wx.StaticText(self, label=str("%Q0."+str(i)+':').center(10)), flag=flagsR, border=2)
            hsizer.AddSpacer(5)
            hsizer.Add(wx.Button(self, label='OFF', size=(50, 17)), flag=flagsR, border=2)

            vsizer.Add(hsizer, flag=flagsR, border=2)
            vsizer.AddSpacer(3)
        return vsizer

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
class SensorReaderFrame(wx.Frame):
    """ XAKA people counting sensor reader with sensor registration function. """
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(620, 670))
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        bgPanel = wx.Panel(self) # background panel.
        bgPanel.SetBackgroundColour(wx.Colour(200, 210, 200))
        vsizer = wx.BoxSizer(wx.VERTICAL)
        nb = wx.Notebook(bgPanel)
        plcBgPanel = wx.Panel(nb)
        hbox  = wx.BoxSizer(wx.HORIZONTAL)
        
        hbox.AddSpacer(5)
        plc1Panel = PanelPLC(plcBgPanel, 'PLC1 [m221]')
        hbox.Add(plc1Panel, flag=flagsR, border=2)
        hbox.AddSpacer(5)
        
        plc2Panel = PanelPLC(plcBgPanel, 'PLC2 [m221]')
        hbox.Add(plc2Panel, flag=flagsR, border=2)        
        hbox.AddSpacer(5)

        plc3Panel = PanelPLC(plcBgPanel, 'PLC3 [S7-1200]')
        hbox.Add(plc3Panel, flag=flagsR, border=2)
        plcBgPanel.SetSizer(hbox)

        nb.AddPage(plcBgPanel, "PLC control")
        nb.AddPage(wx.Panel(nb), "Data Display")
        vsizer.Add(nb, flag=flagsR, border=2)

        self.mapPanel = PanelMap(bgPanel)
        vsizer.Add(self.mapPanel, flag=flagsR, border=2)

        bgPanel.SetSizer(vsizer)

        self.lastPeriodicTime = time.time() 
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms

    def periodic(self, event):
        self.mapPanel.updateDisplay()

#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        mainFrame = SensorReaderFrame(None, -1, 'RainWay PLC contorl Hub')
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
