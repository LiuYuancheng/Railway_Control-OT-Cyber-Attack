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
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import wx
import wx.grid
from wx.adv import Animation, AnimationCtrl
import time
import math
import random
import railwayGlobal as gv 
import railwayAgent as agent

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
class PanelAttackSimu(wx.Panel):
    """ Load different kinds off attack simulation stuation in the system."""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.infoWindow = None  # popup information window.
        self.attCount = -1      # count number to ctrl the time delay to start attack.        
        self.SetSizer(self.buidUISizer())

#--PanelAttackSimu-------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(
            self, label="Active Attack Simulation:"), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(210, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Set the attack selection part.
        self.attRb1 = wx.RadioButton(self, -1, 'Ransomware in the HMI.', style=wx.RB_GROUP)
        vsizer.Add(self.attRb1, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.attRb2 = wx.RadioButton(self, -1, 'Man in the middle from IOT device.')
        vsizer.Add(self.attRb2, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.attRb3 = wx.RadioButton(self, -1, 'Trojan in the technician PC.')
        vsizer.Add(self.attRb3, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.attRb4 = wx.RadioButton(self, -1, 'Black energy attack.')
        vsizer.Add(self.attRb4, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Set the attack state.
        self.idLb = wx.StaticText(self, label="Normal".center(20))
        self.idLb.SetBackgroundColour(wx.Colour('GREEN'))
        vsizer.Add(self.idLb, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.processDisplay = wx.Gauge(
            self, range=10, size=(150, 15), style=wx.GA_HORIZONTAL)
        vsizer.Add(self.processDisplay, flag=flagsR, border=2)
        vsizer.AddSpacer(10)
        # Attack simulation start/clear.
        hsizer0 = wx.BoxSizer(wx.HORIZONTAL)
        self.simuSBt = wx.Button(self, label='Start Attack', style=wx.BU_LEFT)
        self.simuSBt.Bind(wx.EVT_BUTTON, self.setAttck)
        hsizer0.Add(self.simuSBt, flag=flagsR, border=2)
        hsizer0.AddSpacer(5)
        self.simuCBt = wx.Button(self, label='Clear Attack', style=wx.BU_LEFT)
        self.simuCBt.Bind(wx.EVT_BUTTON, self.setAttck)
        hsizer0.Add(self.simuCBt, flag=flagsR, border=2)
        vsizer.Add(hsizer0, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        return vsizer

#--PanelAttackSimu-------------------------------------------------------------
    def periodic(self, now):
        """ periodic call back to show the current attack state. """
        if self.attCount == 1:
            self.idLb.SetLabel("Prepare to start attack")
            self.idLb.SetBackgroundColour(wx.Colour('YELLOW'))
            self.Refresh(False)
            self.attCount += 1
        elif 1 < self.attCount < 10:
            self.processDisplay.SetValue(self.attCount)
            self.attCount += 1
        elif self.attCount == 10:
            self.idLb.SetLabel("System under attack")
            self.idLb.SetBackgroundColour(wx.Colour('RED'))
            self.Refresh(False)
            if self.attRb1.GetValue():
                self.infoWindow = RansomwareFrame(gv.iMainFrame)
            elif self.attRb2.GetValue():
                gv.iSensorAttack = True
            elif self.attRb3.GetValue():
                self.infoWindow = TrojanAttFrame(gv.iMainFrame)
            self.attCount += 1
        elif self.attCount == 0:
            # Clear all the attack state.
            self.idLb.SetLabel("Normal".center(20))
            self.idLb.SetBackgroundColour(wx.Colour('GREEN'))
            self.Refresh(False)
            self.processDisplay.SetValue(self.attCount)
            self.attCount = -1
            gv.iSensorAttack = False

#--PanelAttackSimu-------------------------------------------------------------
    def setAttck(self, event):
        """ Start or clear the attack.
        """
        obj = event.GetEventObject()
        self.attCount = 1 if 'Start' in obj.GetLabel() else 0

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelCameraView(wx.Panel):
    """ Panel play a gif image to simulation the camera view when train pass."""
    def __init__(self, parent, idx, size=(280, 200), style=wx.TRANSPARENT_WINDOW):
        """ Panel to simulate the camera view."""
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.animCtrl = AnimationCtrl(self, -1, Animation(gv.TPSGIP_PATH))
        self.animCtrl.Stop() # stop the gif play first.
        sizer.Add(self.animCtrl)
        self.SetSizerAndFit(sizer)
        self.Show()

#--PanelCameraView-------------------------------------------------------------
    def setPlay(self, plagFlag):
        """ Set the gif play or stop"""
        if plagFlag:
            self.animCtrl.Play()
        else:
            self.animCtrl.Stop()

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
        # Buid the UI.
        hsizer = self.buidUISizer()
        self.SetSizer(hsizer)
        # Init all the data.
        self.initData()

#-----------------------------------------------------------------------------
    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        for _ in range(3):
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
    """ PLC panel UI to show PLC input feedback state and the relay connected 
        to the related output pin.
    """
    def __init__(self, parent, name, ipAddr):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        # Init self paremeters
        self.plcName = name
        self.ipAddr = ipAddr
        self.connected = {'0': 'Unconnected', '1': 'Connected'}
        self.gpioInList = [0]*8 # PLC GPIO input stuation list.
        self.gpioInLbList = []  # GPIO input device <id> label list.
        self.gpioOuList = [0]*8 # PLC GPIO output situation list.
        self.gpioOuLbList = []  # GPIO output device <id> label list.
        # Init the UI.
        self.SetSizer(self.buidUISizer())
        #self.Layout() # must call the layout if the panel size is set to fix.

#--PanelPLC--------------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        mSizer = wx.BoxSizer(wx.VERTICAL) # main sizer
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer.AddSpacer(5)
        # Row idx = 0 : set the basic PLC informaiton.
        self.nameLb = wx.StaticText(
            self, label="PLC Name: ".ljust(15)+self.plcName)
        mSizer.Add(self.nameLb, flag=flagsR, border=2)
        self.ipaddrLb = wx.StaticText(
            self, label="PLC IPaddr: ".ljust(15)+self.ipAddr)
        mSizer.Add(self.ipaddrLb, flag=flagsR, border=2)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.StaticText(self, label="Connection:".ljust(15)),
                  flag=flagsR, border=2)
        self.connLb = wx.StaticText(self, label=self.connected['0'])
        hbox0.Add(self.connLb, flag=flagsR, border=2)
        mSizer.Add(hbox0, flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        # Row idx = 1: set the GPIO and feed back of the PLC. 
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
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
            self.gpioInLbList.append(inputLb)
            # Col idx =1: PLC output labels.
            hsizer.AddSpacer(15)
            hsizer.Add(wx.StaticText(self, label=str(
                "%Q0."+str(i)+':').center(10)), flag=flagsR, border=2)
            # Col idx =2: PLC output ON/OFF contorl buttons.
            hsizer.AddSpacer(5)
            outputBt = wx.Button(self, label='OFF', size=(50, 17), name=self.plcName+':'+str(i))
            outputBt.Bind(wx.EVT_BUTTON, self.relayOn)
            self.gpioOuLbList.append(outputBt)
            hsizer.Add(outputBt, flag=flagsR, border=2)
            mSizer.Add(hsizer, flag=flagsR, border=2)
            mSizer.AddSpacer(3)
        return mSizer

#--PanelPLC--------------------------------------------------------------------
    def relayOn(self, event): 
        """ Turn on the related ralay based on the user's action and update the 
            button's display situation.
        """
        obj = event.GetEventObject()
        print("PLC panel:   Button idx %s" % str(obj.GetName()))
        plcIdx = int(obj.GetName().split('[')[0][-1])
        outIdx = int(obj.GetName().split(':')[-1])
        # toggle output state.
        self.gpioOuList[outIdx] = 1 - self.gpioOuList[outIdx]
        self.updateOutput(outIdx, self.gpioOuList[outIdx])
        # Update the element on the map.
        tag = str((plcIdx+1)*100+outIdx)
        for element in gv.iPowCtrlPanel.powerLabel:
            if tag in element:
                gv.iMapMgr.setSignalPwr(element, self.gpioOuList[outIdx])
                break

#--PanelPLC--------------------------------------------------------------------
    def setConnection(self, state):
        """ Update the connection state on the UI. 0 - disconnect 1- connected
        """
        self.connLb.SetLabel(self.connected[str(state)])
        self.connLb.SetBackgroundColour(
            wx.Colour('GREEN') if state else wx.Colour(120, 120, 120))
        self.Refresh(False)

#--PanelPLC--------------------------------------------------------------------
    def updateInput(self, idx, status): 
        """ Update the input state for each PLC input indicator."""
        if idx >= 8 or not status in [0,1]: 
            print("PLC panel:   the input parameter is not valid") 
            return
        elif self.gpioInList[idx] != status:
            self.gpioInList[idx] = status
            # Change the indicator status.
            self.gpioInLbList[idx].SetBackgroundColour(
                wx.Colour('GREEN') if status else wx.Colour(120, 120, 120))
            self.Refresh(False) # needed after the status update.

#--PanelPLC--------------------------------------------------------------------
    def updateOutput(self, idx, status):
        """ Update the output state for each PLC output button."""
        if idx >= 8 or not status in [0,1]: 
            print("PLC panel:   the output parameter is not valid") 
            return
        elif self.gpioOuList[idx] != status:
            self.gpioOuList[idx] = status
            [lbtext, color] = ['ON', wx.Colour('Green')] if status else [
            'OFF', wx.Colour(200, 200, 200)]
            self.gpioOuLbList[idx].SetLabel(lbtext)
            self.gpioOuLbList[idx].SetBackgroundColour(color)
            self.Refresh(False) # needed after the status update.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPointAtt(wx.Panel):
    """ The panel to set different cyber attack on the components in the system.
        Such as the sensor, signal and connection wires. 
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.SetSizer(self.buidUISizer())

#--PanelPointAtt---------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(
            self, label="Active component attack:"), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(165, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.idLb = wx.StaticText(self, label="Attack point ID: [001] ")
        vsizer.Add(self.idLb, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticText(self, label="Active attack type:"),
                   flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.simuCb1 = wx.CheckBox(self, -1, '1. Ransomware')
        vsizer.Add(self.simuCb1, flag=flagsR, border=2)
        #self.simuCb1.Disable()
        vsizer.AddSpacer(5)
        self.simuCb2 = wx.CheckBox(self, -1, '2. ManInMiddle')
        vsizer.Add(self.simuCb2, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.simuCb3 = wx.CheckBox(self, -1, '3. TrojarAttack')
        vsizer.Add(self.simuCb3, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.simuCb4 = wx.CheckBox(self, -1, '4. EternalBlue')
        vsizer.Add(self.simuCb4, flag=flagsR, border=2)
        #self.simuCb4.Disable()
        vsizer.AddSpacer(5)
        self.attackCtrl = wx.ComboBox(
            self, -1, choices=['Overwrite input', 'Overwrite output'], style=wx.CB_READONLY)
        self.attackCtrl.SetSelection(0)
        vsizer.Add(self.attackCtrl, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(self, label="Overwrite data:"),
                   flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        self.tc1 = wx.TextCtrl(self, -1, "", size=(40, -1),
                               style=wx.TE_PROCESS_ENTER)
        self.tc1.SetValue("1")
        hsizer.Add(self.tc1, flag=flagsR, border=2)
        
        vsizer.Add(hsizer, flag=flagsR, border=2)
        vsizer.AddSpacer(10)
        hsizer0 = wx.BoxSizer(wx.HORIZONTAL)
        self.simuBt1 = wx.Button(self, label='Set Attack', style=wx.BU_LEFT, size=(60,25))
        self.simuBt1.Bind(wx.EVT_BUTTON, self.setAttck)
        hsizer0.Add(self.simuBt1, flag=flagsR, border=2)
        hsizer0.AddSpacer(5)
        self.simuBt2 = wx.Button(self, label='Clear', style=wx.BU_LEFT, size=(60,25))
        self.simuBt2.Bind(wx.EVT_BUTTON, self.setAttck)
        hsizer0.Add(self.simuBt2, flag=flagsR, border=2)
        vsizer.Add(hsizer0, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        return vsizer

#--PanelPointAtt---------------------------------------------------------------
    def loatAttPtState(self, id):
        """ Load the attack point's ID. """
        self.idLb.SetLabel("Attack point ID: [%s] " %str(id).zfill(3))

#--PanelPointAtt---------------------------------------------------------------
    def setAttck(self, event):
        buttonLb = event.GetEventObject().GetLabel()
        if buttonLb == 'Set Attack':
            gv.iMapPanel.setHackedPt(0)
            gv.iMapPanel.updateDisplay()
            hackedV = self.tc1.GetValue()
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(
                    idx=1, state='Man in mid', origalV=0, changedV=hackedV)
        else:
            gv.iMapPanel.setHackedPt(-2)
            gv.iMapPanel.updateDisplay()
            if gv.iDetailPanel:
                gv.iDetailPanel.updateState(
                    idx=1, state='Normal', origalV=0, changedV=0)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelSysCtrl(wx.Panel):
    """ The whole system situation control panel."""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.powerLabel = (
            "S100 - Powerplant Lights", 
            "S101 - Airport Lights",
            "S102 - Industrial Lightbox",
            "S200 - Station Lights",
            "S201 - Auto Level Crossing",
            "S202 - Residential Lightbox",
            "S300 - Turnout Toggle",
            "S301 - Track A Fork Power",
            "S302 - Track B Fork Power",
            "S303 - City LightBox")
        self.powerCBList = [] # Output control checkbox.
        self.SetSizer(self.buidUISizer())

#--PanelSysCtrl----------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(self, label="System Power Control"),
                   flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)                       
        for labelStr in self.powerLabel:
            vsizer.AddSpacer(5)
            pwtBt = wx.CheckBox(self, -1, labelStr)
            pwtBt.Bind(wx.EVT_CHECKBOX, self.onChecked)
            pwtBt.SetValue(True)
            vsizer.Add(pwtBt, flag=flagsR, border=2)
            self.powerCBList.append(pwtBt)
        vsizer.AddSpacer(10)
        return vsizer

#--PanelSysCtrl----------------------------------------------------------------
    def onChecked(self, event):
        """ Passed the user clicked check box label and value to map manager.
        """
        cb = event.GetEventObject()
        # Set the signal state. 
        gv.iMapMgr.setSignalPwr(cb.GetLabel(), cb.GetValue())

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelTrainCtrl(wx.Panel):
    """ Train parameter contorl panel."""
    def __init__(self, parent, trainName):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.tName = trainName
        self.statDict = {
            '0': ('Running',    'GREEN',    80),
            '1': ('SlowDown',   'YELLOW',   40),
            '2': ('Accelerate', '#03AC15',  90),
            '3': ('Turning',    '#93CB8B',  60),
            '4': ('Waiting',    'ORANGE',   0),
            '5': ('Stopped',    'RED',      0)
        } # 'idx' :('speed Name', label color, speed num)
        self.SetSizer(self.buidUISizer())
        self.setState(0, 0)

#--PanelTrainCtrl--------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        # Set the panel title.
        self.ctrlAct = wx.CheckBox(self, -1, self.tName+" Control")
        self.ctrlAct.SetValue(True)
        vsizer.Add(self.ctrlAct, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Row idx = 0: train state display.
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.StaticText(self, label="Train status:"),
                  flag=flagsR, border=2)
        hbox0.AddSpacer(5)
        self.stateLb = wx.StaticText(self, label="Running".center(16))
        hbox0.Add(self.stateLb, flag=flagsR, border=2)
        vsizer.Add(hbox0, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        self.rwLabel = wx.StaticText(
            self, label="RailWay Pos: "+self.tName[-1])
        vsizer.Add(self.rwLabel, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Row idx = 1: Train speed contorl
        vsizer.Add(wx.StaticText(
            self, label="Train Throttle and Speed:"), flag=flagsR, border=2)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.throttleBar = wx.Gauge(
            self, range=10, size=(100, 17), style=wx.GA_HORIZONTAL)
        hbox1.Add(self.throttleBar, flag=flagsR, border=2)
        hbox1.AddSpacer(5)
        self.speedLb = wx.StaticText(self, label="[ 80km/h ]")
        hbox1.Add(self.speedLb, flag=flagsR, border=2)
        vsizer.Add(hbox1, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Row idx = 2: Train direction contorl
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(self, label="Direction :"),
                  flag=flagsR, border=2)
        self.dirCtrl = wx.ComboBox(
            self, -1, choices=['anticlockwise', 'clockwise'], style=wx.CB_READONLY)
        self.dirCtrl.SetSelection(0)
        hbox2.Add(self.dirCtrl, flag=flagsR, border=2)
        vsizer.Add(hbox2, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Row idx =3 : Train max speed control
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(
            self, label="Speed Ctrl [*10km]"), flag=flagsR, border=2)
        self.speedCtrl = wx.SpinCtrl(
            self, -1, '8', size=(50, -1), min=1, max=10)
        hbox3.Add(self.speedCtrl, flag=flagsR, border=2)
        hbox3.AddSpacer(5)
        vsizer.Add(hbox3, flag=flagsR, border=2)
        vsizer.AddSpacer(5)
        # Row idx = 4: Station wait time control
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(
            self, label="Station waitT [sec]:"), flag=flagsR, border=2)
        self.wTimeCtrl = wx.SpinCtrl(
            self, -1, '3', size=(50, -1), min=1, max=20)
        hbox4.Add(self.wTimeCtrl, flag=flagsR, border=2)
        vsizer.Add(hbox4, flag=flagsR, border=2)
        # Row idx = 5: Load setting, recover and emergency stop buttons.
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        # load setting button.
        hbox5.AddSpacer(5)
        bmp0 = wx.Bitmap(gv.LDSET_PATH, wx.BITMAP_TYPE_ANY)
        self.loadbtn1 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0,
                                        size=(bmp0.GetWidth()+10, bmp0.GetHeight()+10))
        hbox5.Add(self.loadbtn1, flag=flagsR, border=2)
        # recover button.
        hbox5.AddSpacer(5)
        bmp1 = wx.Bitmap(gv.RECOV_PATH, wx.BITMAP_TYPE_ANY)
        self.recbtn1 = wx.BitmapButton(self, id=wx.NewId(), bitmap=bmp1,
                                       size=(bmp1.GetWidth()+10, bmp1.GetHeight()+10))
        self.recbtn1.Bind(wx.EVT_BUTTON, self.emgHandle)
        hbox5.Add(self.recbtn1, flag=flagsR, border=2)
        # emergency stop button.
        hbox5.AddSpacer(5)
        bmp = wx.Bitmap(gv.EMGST_PATH, wx.BITMAP_TYPE_ANY)
        self.stopbtn1 = wx.BitmapButton(self, id=wx.NewId(), bitmap=bmp,
                                        size=(bmp.GetWidth()+10, bmp.GetHeight()+10))
        self.stopbtn1.Bind(wx.EVT_BUTTON, self.emgHandle)
        hbox5.Add(self.stopbtn1, flag=flagsR, border=2)
        hbox5.AddSpacer(5)
        vsizer.Add(hbox5, flag=flagsR, border=2)
        return vsizer

#--PanelTrainCtrl--------------------------------------------------------------
    def emgHandle(self, event):
        """ Set/recover the train to/from emergency stop situaton."""
        if not gv.iMapMgr: return
        obj = event.GetEventObject()
        (stop, speed) = (False, 0) if obj.GetId() == self.recbtn1.GetId() else (True, 5)
        gv.iMapMgr.setEmgStop(self.tName, stop)
        self.setState(speed, 0)  # recover

#--PanelTrainCtrl--------------------------------------------------------------
    def setState(self, idx, rwIdx): 
        """ Set the train running state. idx: speed idx in <self.statDict>."""
        state = self.statDict[str(idx)]
        self.stateLb.SetLabel(str(state[0]).center(16))
        self.stateLb.SetBackgroundColour(wx.Colour(state[1]))
        railWay = "[ Track A ]" if rwIdx == 0 else "[ Track B ]"
        self.rwLabel.SetLabel("RailWay Pos: " + railWay)
        self.speedLb.SetLabel("[ %dkm/h ]" % state[2])
        self.throttleBar.SetValue(state[2]//10)
        self.Refresh(False)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelDetailInfo(wx.Panel):
    """ The panel show the components' detail infomation."""
    def __init__(self, parent, idx, size=(140, 150)):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.idx = idx 
        self.hackState = ""
        self.origalV = self.changedV = 0
        self.SetSizer(self.buidUISizer())

#--PanelDetailInfo-------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.idLb = wx.StaticText(
            self, label="Attack point ID: [%s] " % str(self.idx).zfill(3))
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

#--PanelDetailInfo-------------------------------------------------------------
    def updateState(self, idx=None, state=None, origalV=None, changedV=None):
        """ Update the state when the user changed the setting
        """
        if not idx is None and self.idx != idx:
            self.idx = idx
            self.idLb.SetLabel(
                "Attack point ID: [%s] " % str(self.idx).zfill(3))
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
            self.orignLb.SetLabel("Orignal input: %s" % str(origalV))
        if not changedV is None and self.changedV != changedV:
            self.changedV = changedV
            self.hackLb.SetLabel("Hacked input: %s" % str(changedV))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class RansomwareFrame(wx.Frame):
    """ Popup frame to show the ransomeware attack simulation situation."""
    def __init__(self, parent):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, -1, 'Ransomware',
                          style=wx.MINIMIZE_BOX)
        self.SetBackgroundColour(wx.Colour('BLACK'))
        screenSZ = wx.GetDisplaySize()
        wx.StaticBitmap(self, -1, wx.Image(gv.RAJPG_PATH, wx.BITMAP_TYPE_JPEG).ConvertToBitmap(),
                        pos=(screenSZ[0]//2-350, screenSZ[0]//2-300))
        self.Maximize()
        self.encryptSetFile()
        self.Show()

#--RansomwareFrame-------------------------------------------------------------
    def encryptSetFile(self): 
        """Simulation the file attack by ransomeware."""
        fIn = open("encryptKey.txt")
        fOut = open("railwayPlcConfig.txt", "w")
        for line in fIn:
            fOut.write(line)
        fIn.close()
        fOut.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class TrojanAttFrame(wx.Frame):
    """ Popup frame to show a transparent window to block the desktop to simulate
        the trojan attack.
    """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="TrojanAttFrame",style=wx.MINIMIZE_BOX)
        self.SetBackgroundColour(wx.Colour('BLACK'))
        self.alphaValue = 255   # transparent control
        self.alphaIncrement = -4
        self.count = 500        # count to control when to stop the attack.   
        # Build the main UI.
        self.SetSizerAndFit(self.buidUISizer())

        self.changeAlpha_timer = wx.Timer(self)
        self.changeAlpha_timer.Start(100)       # 10 changes per second
        self.Bind(wx.EVT_TIMER, self.changeAlpha)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        # Set the frame cover full desktop.
        self.Maximize()
        self.ShowFullScreen(True)
        self.Show()

#--TrojanAttFrame--------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ctrl = AnimationCtrl(self, -1, Animation(gv.TAGIF_PATH))
        self.ctrl.Play()
        sizer.Add(self.ctrl, flag=wx.ALIGN_CENTER_VERTICAL |
                  wx.ALIGN_CENTER_HORIZONTAL, border=2)
        self.stTxt = wx.StaticText(
            self, -1, "Your computer has been took over by YC's Trojan, we will release control in 10 sec")
        self.stTxt.SetBackgroundColour(wx.Colour('GREEN'))
        self.stTxt.SetFont(wx.Font(30, wx.SWISS, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.stTxt, flag=wx.ALIGN_CENTER, border=2)
        return sizer

 #--TrojanAttFrame--------------------------------------------------------------
    def changeAlpha(self, evt):
        """ The term "alpha" means variable transparency this function we 
            follow the examle in =: 
            https://wiki.wxpython.org/Transparent%20Frames
              as opposed to a "mask" which is binary transparency.
              alpha == 255 :  fully opaque
              alpha ==   0 :  fully transparent (mouse is ineffective!)
            Only top-level controls can be transparent; no other controls can.
            This is because they are implemented by the OS, not wx.
        """
        self.alphaValue += self.alphaIncrement
        if (self.alphaValue) <= 0 or (self.alphaValue >= 255):
            # Reverse the increment direction.
            self.alphaIncrement = -self.alphaIncrement
            if self.alphaValue <= 0:
                self.alphaValue = 0
            if self.alphaValue > 255:
                self.alphaValue = 255
        # Show the release time text.
        self.count -=1
        if self.count%100 == 0:
            self.stTxt.SetLabel("Your computer has been took over by the Trojan, we will release control in "+str(self.count//100).zfill(2)+" sec")
        if self.count == 0:
            self.onCloseWindow(None)
        self.SetTransparent(self.alphaValue)

#--TrojanAttFrame--------------------------------------------------------------
    def onCloseWindow(self, evt):
        """ Stop the timeer and close the window."""
        self.changeAlpha_timer.Stop()
        del self.changeAlpha_timer       # avoid a memory leak
        self.Destroy()
