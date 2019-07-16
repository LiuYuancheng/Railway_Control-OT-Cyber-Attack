#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railwayHub.py
#
# Purpose:     This function is used to create a rail control hub to show the 
#              different situation of the cyber-security attack's effect for the 
#              railway PLC system.
#
# Author:      Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------

import wx # use wx to build the UI.
import time
from datetime import datetime
import railwayGlobal as gv 
import railwayPanel as rwp

PERIODIC = 300

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class railWayHubFrame(wx.Frame):
    """ XAKA people counting sensor reader with sensor registration function. """
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(620, 670))

        gv.iMainFrame = self

        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        vsizer = wx.BoxSizer(wx.VERTICAL)
        # Row idx = 0 : Set all hte information and feed in a wx NoteBook
        nb = wx.Notebook(self)
        # Set the PLC contorl panel
        plcBgPanel = wx.Panel(nb, size=(600,250))
        hbox  = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(10)
        plc1Panel = rwp.PanelPLC(plcBgPanel, 'PLC0 [m221]', "192.168.0.101")
        hbox.Add(plc1Panel, flag=flagsR, border=2)
        gv.iPlcPanelList.append(plc1Panel)
        hbox.AddSpacer(10)
        plc2Panel = rwp.PanelPLC(plcBgPanel, 'PLC1 [m221]', "192.168.0.102")
        hbox.Add(plc2Panel, flag=flagsR, border=2)
        gv.iPlcPanelList.append(plc2Panel)  
        hbox.AddSpacer(10)
        plc3Panel = rwp.PanelPLC(plcBgPanel, 'PLC2 [S7-1200]', "192.168.0.103")
        hbox.Add(plc3Panel, flag=flagsR, border=2)
        gv.iPlcPanelList.append(plc3Panel)
        plcBgPanel.SetSizer(hbox)
        nb.AddPage(plcBgPanel, "PLC control")
        # Set the PLC data display panel.
        self.dataPanel = rwp.PanelInfoGrid(nb)
        nb.AddPage(self.dataPanel, "Data Display")

        hbox2  = wx.BoxSizer(wx.HORIZONTAL)
        setBgPanel = wx.Panel(nb)
        
        gv.iTrainPanel = self.setPanel = rwp.PanelTrainCtrl(setBgPanel)
        hbox2.Add(self.setPanel, flag=flagsR, border=2)
        hbox2.AddSpacer(10)

        self.simuPanel = rwp.PanelSimuCtrl(setBgPanel)
        gv.iAttackCtrlPanel = self.simuPanel
        hbox2.Add(self.simuPanel, flag=flagsR, border=2)
        hbox2.AddSpacer(10)
        setBgPanel.SetSizer(hbox2)

        nb.AddPage(setBgPanel, "Setting")

        vsizer.Add(nb, flag=flagsR, border=2)
        # Row idx = 1 : set the train map panel
        self.mapPanel = rwp.PanelMap(self)
        gv.iMapPanel = self.mapPanel
        vsizer.Add(self.mapPanel, flag=flagsR, border=2)
        self.SetSizer(vsizer)

        self.lastPeriodicTime = time.time() 
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    #-----------------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        # Set the title of the frame.
        self.SetTitle( ' '.join((gv.APP_NAME, datetime.now().strftime("[ %m/%d/%Y, %H:%M:%S ]"))))
        if gv.iEmgStop: return
        timeStr = time.time()
        
        self.mapPanel.periodic(timeStr)

    #-----------------------------------------------------------------------------
    def OnClose(self, event):
        #self.ser.close()
        self.Destroy()

#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        mainFrame = railWayHubFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
