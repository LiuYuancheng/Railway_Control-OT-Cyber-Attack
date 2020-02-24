#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        uiRun.py
#
# Purpose:     This module is used to create the main wx frame.
#
# Author:      Yuancheng Liu
#
# Created:     2019/01/10
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import os, sys
import time
import wx
import wx.gizmos as gizmos

import pwrGenGobal as gv
import pwrGenPanel as pl
import pwrGenMgr as gm
PERIODIC = 100      # update in every 500ms

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class UIFrame(wx.Frame):
    """ URL/IP gps position finder main UI frame."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(600, 240))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        self.loadCbList = []
        self.ledList = []
        self.SetSizer(self._buidUISizer())

        gv.iGnMgr = gm.pwrGenMgr(self, 0, "Gen mgr")
        gv.iGnMgr.start()
        gv.iGnMgr.setLoad([],[])


        self.parmList = [50, 22, 50, 50, gv.iGnMgr.getMotorSp(), gv.iGnMgr.getPumpSp(), 0, 0]
        self.setLEDVal(0, self.parmList[0]*100)
        self.setLEDVal(1, self.parmList[1]*10)
        self.setLEDVal(2, gv.iGnMgr.getMotorSp())
        self.setLEDVal(3, gv.iGnMgr.getPumpSp())

        # Set the periodic call back
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.updateLock = False
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms
        
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('COM Msg to Arduino: %s ' % str(self.parmList))
        self.Bind(wx.EVT_CLOSE, self.onClose)

        print("Program init finished.")


#--UIFrame---------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI Sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        sizerAll= wx.BoxSizer(wx.VERTICAL)
        sizerAll.AddSpacer(5)
        # LED area
        uSizer = wx.BoxSizer(wx.HORIZONTAL)
        lbList = ('Frequency : ', 'Voltage : ', 'MotoSpeed : ', 'PumpSpeed : ')
        for i in range(4):
            uSizer.Add(wx.StaticText(self, label=lbList[i]), flag=flagsR, border=2)
            led = gizmos.LEDNumberCtrl(self, -1, size = (60, 25), style=gizmos.LED_ALIGN_CENTER)
            self.ledList.append(led)
            uSizer.AddSpacer(5)
            uSizer.Add(led, flag=flagsR, border=2)
            uSizer.AddSpacer(10)

        sizerAll.Add(uSizer, flag=flagsR, border=2)
        sizerAll.AddSpacer(5)

        sizerAll.Add(wx.StaticLine(self, wx.ID_ANY, size=(600, -1),
                    style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Col 0 : output load sizer:
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, label="Load setting: "), flag=flagsR, border=2)
        vbox.AddSpacer(5)
        loadLb = ('Airport', 'Train track A', 'Train track B', 'City Pwr', 'Industrial Pwr')
        for i in range(5):
            cb = wx.CheckBox(self, label = 'Load[%s]: %s' %(str(i),loadLb[i])) 
            cb.Bind(wx.EVT_CHECKBOX, self.onCheck)
            vbox.Add(cb, flag=flagsR, border=2)
            vbox.AddSpacer(5)
        mSizer.Add(vbox, flag=flagsR, border=2)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 140),
                            style=wx.LI_VERTICAL), flag=flagsR, border=2)

        # Col 1: moto
        mSizer.AddSpacer(5)
        gv.iMotoImgPnl = pl.PanelMoto(self)
        mSizer.Add(gv.iMotoImgPnl, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 140),
                                 style=wx.LI_VERTICAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5)

        gv.iPumpImgPnl = pl.PanelPump(self)
        mSizer.Add(gv.iPumpImgPnl, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 140),
                            style=wx.LI_VERTICAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5)

        

 
        sizerAll.Add(mSizer, flag=flagsR, border=2)

        return sizerAll


    def onCheck(self, evnt):
        cb = evnt.GetEventObject()
        idx = int(cb.GetLabel().split('[')[-1][0])
        val = 1 if cb.GetValue() else 0
        gv.iGnMgr.setLoad([idx],[val])


#--UIFrame---------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        now = time.time()
        if (not self.updateLock) and now - self.lastPeriodicTime >= gv.iUpdateRate:
            #print("main frame update at %s" % str(now))
            self.lastPeriodicTime = now
            gv.iMotoImgPnl.updateDisplay()
            gv.iPumpImgPnl.updateDisplay()
            self.setLEDVal(2, gv.iGnMgr.getMotorSp())
            self.setLEDVal(3, gv.iGnMgr.getPumpSp())

    def setLEDVal(self, idx, val):
        self.ledList[idx].SetValue(str(val))

#--<telloFrame>----------------------------------------------------------------
    def onClose(self, event):
        """ Stop all the thread and close the UI."""
        gv.iGnMgr.stop()
        self.timer.Stop()
        self.Destroy()




#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        gv.iMainFrame = UIFrame(None, -1, gv.APP_NAME)
        gv.iMainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
