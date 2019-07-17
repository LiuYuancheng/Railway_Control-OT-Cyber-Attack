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

        if str(obj.GetName()) == 'PLC0 [m221]:0':
            if lbtext == 'ON':
                gv.iMapPanel.lightOn = 2
                gv.iMapPanel.updateDisplay()
            else:
                gv.iMapPanel.lightOn = 1
                gv.iMapPanel.updateDisplay()
        else:
            gv.iMapPanel.lightOn = 0


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

        self.idLb = wx.StaticText(self, label="Attack point ID: [001] ")
        vsizer.Add(self.idLb, flag=flagsR, border=2)
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

    def loatAttPtState(self, id):
        """ Load the attack point's state. 
        """
        self.idLb.SetLabel("Attack point ID: [%s] " %str(id).zfill(3))

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