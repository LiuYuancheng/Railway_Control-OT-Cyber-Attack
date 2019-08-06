#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railwayHub.py
#
# Purpose:     This function is used to create a rail control hub to show the 
#              different situation of the cyber-security attack's influence for
#              the railway HMI and PLC system.
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
import railwayAgent as agent
import railwayMgr as manager
import railwayGlobal as gv 
import railwayPanel as rwp
import railwayPanelMap as rwpm 

PERIODIC = 300

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class railWayHubFrame(wx.Frame):
    """ Railway system control hub."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(620, 740))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.TTICO_PATH))
        gv.iMainFrame = self
        gv.iAgentMgr =  manager.managerPLC(self)
        
        # Init all the UI components: 
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        # Row idx = 0 : Set all the control and information display panel in a wx NoteBook.
        nb = wx.Notebook(self)
        
        # Tab 0: System power control + train control.
        sysBgPanel = wx.Panel(nb)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.AddSpacer(10)
        gv.iPowCtrlPanel = self.setPanel0 = rwp.PanelSysCtrl(sysBgPanel)
        hbox0.Add(self.setPanel0, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        gv.iTrainAPanel = self.trainACtPanel = rwp.PanelTrainCtrl(sysBgPanel, 'TrainA')
        hbox0.Add(self.trainACtPanel, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        gv.iTrainBPanel = self.trainBCtPanel = rwp.PanelTrainCtrl(sysBgPanel, 'TrainB')
        hbox0.Add(self.trainBCtPanel, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        sysBgPanel.SetSizer(hbox0)
        nb.AddPage(sysBgPanel, "System ")

        # Tab 1: PLC contorl panel.
        plcBgPanel = wx.Panel(nb)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.AddSpacer(10)
        for i in range(3):
            plcPanel = self.initPLC(i, plcBgPanel)
            hbox1.Add(plcPanel, flag=flagsR, border=2)
            gv.iPlcPanelList.append(plcPanel)
            hbox1.AddSpacer(10)

        plcBgPanel.SetSizer(hbox1)
        nb.AddPage(plcBgPanel, "PLC Control")
        
        # Tab 2: PLC detail grid display panel.
        gv.iDataPanel = dataPanel = rwp.PanelInfoGrid(nb)
        nb.AddPage(dataPanel, "Data Display")

        # Tab 3: Program setting and attack simulation panel.
        setBgPanel = wx.Panel(nb)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.AddSpacer(10)

        self.attackPanel = rwp.PanelAttackSimu(setBgPanel)
        hbox3.Add(self.attackPanel, flag=flagsR, border=2)

        gv.iAttackCtrlPanel = self.simuPanel = rwp.PanelSimuCtrl(setBgPanel)
        hbox3.Add(self.simuPanel, flag=flagsR, border=2)
        hbox3.AddSpacer(10)
        setBgPanel.SetSizer(hbox3)
        nb.AddPage(setBgPanel, "Setting")

        # Tab 4: Help message tag.

        vsizer.Add(nb, flag=flagsR, border=2)
        
        # Row idx = 1: set the train map display panel. 
        gv.iMapPanel = self.mapPanel = rwpm.PanelMap(self)
        vsizer.Add(self.mapPanel, flag=flagsR, border=2)
        
        self.SetSizer(vsizer)
        # Set the periodic feedback: 
        self.lastPeriodicTime = time.time() 
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Refresh(False)

#-----------------------------------------------------------------------------
    def initPLC(self, idx, plcBgPanel):
        """ Init the PLC agent to connect to the hardware and the PLC panel to display 
            the PLC state.
        """
        (name, ip, port, _, _) = gv.PLC_CFG['PLC'+str(idx)]
        plcAgent = agent.AgentPLC(self, idx, name, ip, port)
        plcPanel = rwp.PanelPLC(plcBgPanel, 'PLC'+str(idx)+name, ip+':'+port)
        plcPanel.setConnection(0)
        gv.iAgentMgr.appendPLC(plcAgent, plcPanel)
        return plcPanel

    #-----------------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        # Set the title of the frame.
        self.SetTitle( ' '.join((gv.APP_NAME, datetime.now().strftime("[ %m/%d/%Y, %H:%M:%S ]"))))
        if gv.iEmgStop: return
        timeStr = time.time()
        self.mapPanel.periodic(timeStr)
        self.attackPanel.periodic(timeStr)

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
