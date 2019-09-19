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
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import wx # use wx to build the UI.
import time
from datetime import datetime

import railwayGlobal as gv 
import railwayAgent as agent
import railwayMgr as manager
import railwayPanel as rwp
import railwayPanelMap as rwpm 

PERIODIC = 300 # periodicly call by 300ms
FRAME_SIZE = (620, 740) if gv.iDisplayMode == 0 else (1240, 780)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class railWayHubFrame(wx.Frame):
    """ Railway system control hub."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size= FRAME_SIZE)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.TTICO_PATH))
        gv.iMainFrame = self
        gv.iAgentMgr = manager.managerPLC(self)
        # build the user interface.
        uisizer = self.buidUISizerM0() if gv.iDisplayMode == 0 else self.buildUISizerM1()
        self.SetSizer(uisizer)
        # Set the periodic feedback:
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 300 ms
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Refresh(False)

#-----------------------------------------------------------------------------
    def buildUISizerM1(self):
        """ Build the UI under display mode 0 and the return the wx.sizer. """
        # Init all the UI components: 
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Col idx 0: 
        vbox0 = wx.BoxSizer(wx.VERTICAL)
        # Row idx 0: system control panel
        vbox0.Add(wx.StaticText(self, label=" [ Main System Control ] "), flag=flagsR, border=2)
        vbox0.AddSpacer(5)
        sysBgPanel = wx.Panel(self)
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
        sysBgPanel.SetSizerAndFit(hbox0)
        vbox0.Add(sysBgPanel, flag=flagsR, border=2)
        vbox0.Add(wx.StaticLine(self, wx.ID_ANY, size=(590, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vbox0.AddSpacer(5)

        # Row idx 2: PLC contorl panel
        vbox0.Add(wx.StaticText(self, label=" [ PLC Memory/Coils Control ] "), flag=flagsR, border=2)
        vbox0.AddSpacer(5)
        plcBgPanel = wx.Panel(self)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.AddSpacer(10)
        for i in range(3):
            plcPanel = self.initPLC(i, plcBgPanel)
            hbox1.Add(plcPanel, flag=flagsR, border=2)
            gv.iPlcPanelList.append(plcPanel)
            hbox1.AddSpacer(10)
        plcBgPanel.SetSizer(hbox1)
        vbox0.Add(plcBgPanel, flag=flagsR, border=2)
        vbox0.Add(wx.StaticLine(self, wx.ID_ANY, size=(590, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vbox0.AddSpacer(5)

        # Row idx 2: CyberSecurity attack contorl panel
        vbox0.Add(wx.StaticText(self, label=" [ Cyber Security Attack Simultaion Control ] "), flag=flagsR, border=2)
        vbox0.AddSpacer(5)
        self.attackPanel = rwp.PanelAttackSimu(self)
        vbox0.Add(self.attackPanel, flag=flagsR, border=2)
        hsizer.Add(vbox0, flag=flagsR, border=2)
        
        hsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 780), style=wx.LI_VERTICAL), flag=flagsR, border=2)
        hsizer.AddSpacer(10)

        # Col idx 1: 
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        # Row idx 0: Railway simulation display
        vbox1.Add(wx.StaticText(self, label=" [ RailWay System Display ]"), flag=flagsR, border=2)
        vbox1.AddSpacer(10)
        gv.iMapPanel = self.mapPanel = rwpm.PanelMap(self)
        vbox1.Add(self.mapPanel, flag=flagsR, border=2)
        vbox1.AddSpacer(10)
        vbox1.Add(wx.StaticLine(self, wx.ID_ANY, size=(610, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)

        # Row idx 2:
        vbox1.Add(wx.StaticText(self, label=" [ PLC Ladder Diagram Overwrite Control ] "), flag=flagsR, border=2)
        vbox1.AddSpacer(10)
        gv.iDataPanel = self.dataPanel = rwp.PanelInfoGrid(self)
        vbox1.Add(gv.iDataPanel , flag=flagsR, border=2)
        hsizer.Add(vbox1, flag=flagsR, border=2)
        return hsizer

#--railWayHubFrame-------------------------------------------------------------
    def buidUISizerM0(self):
        """ Build the UI under display mode 0 and the return the wx.sizer. """
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
        #sysBgPanel.SetSizer(hbox0)
        sysBgPanel.SetSizerAndFit(hbox0)
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
        gv.iDataPanel = self.dataPanel = rwp.PanelInfoGrid(nb)
        nb.AddPage(self.dataPanel, "Data Display")
        # Tab 3: Program setting and attack simulation panel.
        setBgPanel = wx.Panel(nb)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.AddSpacer(10)
        self.attackPanel = rwp.PanelAttackSimu(setBgPanel)
        hbox3.Add(self.attackPanel, flag=flagsR, border=2)
        #gv.iAttackCtrlPanel = self.simuPanel = rwp.PanelPointAtt(setBgPanel)
        #hbox3.Add(self.simuPanel, flag=flagsR, border=2)
        #hbox3.AddSpacer(10)
        setBgPanel.SetSizer(hbox3)
        nb.AddPage(setBgPanel, "Setting")
        vsizer.Add(nb, flag=flagsR, border=2)

        # Row idx = 1: set the train map display panel.
        gv.iMapPanel = self.mapPanel = rwpm.PanelMap(self)
        vsizer.Add(self.mapPanel, flag=flagsR, border=2)
        return vsizer

#--railWayHubFrame-------------------------------------------------------------
    def initPLC(self, idx, plcBgPanel):
        """ Init the PLC agent to connect to the hardware and the PLC panel to 
            display/control the PLC state.
        """
        (name, ip, plcType, _, _) = gv.PLC_CFG['PLC'+str(idx)]
        plcAgent = agent.AgentPLC(self, idx, name, ip, plcType)
        plcPanel = rwp.PanelPLC(plcBgPanel, 'PLC'+str(idx)+name, ip+':'+'502')
        plcPanel.setConnection(1)
        gv.iAgentMgr.appendPLC(plcAgent, plcPanel)
        return plcPanel

#--railWayHubFrame-------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        # Set the title of the frame.
        self.SetTitle(
            ' '.join((gv.APP_NAME, datetime.now().strftime("[ %m/%d/%Y, %H:%M:%S ]"))))
        if gv.iEmgStop:
            return
        timeStr = time.time()
        self.mapPanel.periodic(timeStr)
        self.attackPanel.periodic(timeStr)

#--railWayHubFrame-------------------------------------------------------------
    def OnClose(self, event):
        self.Destroy()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        mainFrame = railWayHubFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
