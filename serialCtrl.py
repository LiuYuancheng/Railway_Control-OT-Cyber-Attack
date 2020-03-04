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
import serial
import glob
import wx
import M2PLC221 as m221
import S7PLC1200 as s71200

PERIODIC = 500      # update in every 500ms



#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class UIFrame(wx.Frame):
    """ URL/IP gps position finder main UI frame."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(250, 320))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        # Set the periodic call back
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.updateLock = False
        self.dataList = ['0', '0', 'off', 'off', 'red', 'red', 'off', 'on']
        self.fieldlList = []
        # init the serial communication:
        portList = []
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Serial Port comm connection error: Unsupported platform.')
        for port in ports:
            # Check whether the port can be open.
            try:
                s = serial.Serial(port)
                s.close()
                portList.append(port)
            except (OSError, serial.SerialException):
                pass
        print(('COM connection: the serial port can be used :%s' % str(portList)))

        self.serialPort = portList[-1]

        try:
            self.serComm = serial.Serial(self.serialPort, 115200, 8, 'N', 1, timeout=1)
        except:
            print("Serial connection: serial port open error.")
            return None
        # connect to the PLC
        self.se1 = m221.M221('192.168.10.72')
        self.se2 = s71200.S7PLC1200('192.168.10.73')
        self.se3 = m221.M221('192.168.10.71')



        self.SetSizer(self._buidUISizer())
        self.statusbar = self.CreateStatusBar()
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms

#--UIFrame---------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI Sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        gs = wx.FlexGridSizer(13, 2, 5, 5)

        gs.Add(wx.StaticText(self, label=' Frequency : '), flag=flagsR, border=2)
        freText = wx.TextCtrl(self, -1, "0.0")
        self.fieldlList.append(freText)
        gs.Add(freText, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Voltage : '), flag=flagsR, border=2)
        volText = wx.TextCtrl(self, -1, "0.0")
        self.fieldlList.append(volText)
        gs.Add(volText, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Frequency LED : '), flag=flagsR, border=2)
        freLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        freLedCB.SetSelection(0)
        self.fieldlList.append(freLedCB)
        gs.Add(freLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Voltage LED : '), flag=flagsR, border=2)
        volLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        volLedCB.SetSelection(0)
        self.fieldlList.append(volLedCB)
        gs.Add(volLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Motor LED : '), flag=flagsR, border=2)
        motLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        motLedCB.SetSelection(0)
        self.fieldlList.append(motLedCB)
        gs.Add(motLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Pump LED : '), flag=flagsR, border=2)
        pumLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        pumLedCB.SetSelection(0)
        self.fieldlList.append(pumLedCB)
        gs.Add(pumLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Smoke : '), flag=flagsR, border=2)
        smokeCB= wx.ComboBox(self, -1, choices=['slow','fast', 'off'])
        smokeCB.SetSelection(0)
        self.fieldlList.append(smokeCB)
        gs.Add(smokeCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Siren : '), flag=flagsR, border=2)
        sirenCB= wx.ComboBox(self, -1, choices=['on', 'off'])
        sirenCB.SetSelection(0)
        self.fieldlList.append(sirenCB)
        gs.Add(sirenCB, flag=flagsR, border=2)


        gs.Add(wx.StaticText(self, label=' Pump speed : '), flag=flagsR, border=2)
        self.pumpSP= wx.ComboBox(self, -1, choices=['off', 'low', 'high'])
        self.pumpSP.SetSelection(0)
        gs.Add(self.pumpSP, flag=flagsR, border=2)


        gs.Add(wx.StaticText(self, label=' Moto speed : '), flag=flagsR, border=2)
        self.MotoSP= wx.ComboBox(self, -1, choices=['off', 'low', 'high'])
        self.MotoSP.SetSelection(0)
        gs.Add(self.MotoSP, flag=flagsR, border=2)


        gs.Add(wx.StaticText(self, label=' All sensor control : '), flag=flagsR, border=2)
        self.senPower= wx.ComboBox(self, -1, choices=['on', 'off'])
        self.senPower.SetSelection(0)
        gs.Add(self.senPower, flag=flagsR, border=2)


        gs.Add(wx.StaticText(self, label=' All power control : '), flag=flagsR, border=2)
        self.AllPower= wx.ComboBox(self, -1, choices=['on', 'off'])
        self.AllPower.SetSelection(0)
        gs.Add(self.AllPower, flag=flagsR, border=2)
        gs.AddSpacer(5)



        self.sendBt = wx.Button(self, label='Set')
        self.sendBt.Bind(wx.EVT_BUTTON, self.onSend)
        gs.Add(self.sendBt, flag=flagsR, border=2)
        
        mSizer.Add(gs, flag=flagsR, border=2)
        return mSizer

#--UIFrame---------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        now = time.time()
        if (not self.updateLock) and now - self.lastPeriodicTime >= 2:
            print("main frame update at %s" % str(now))
            self.lastPeriodicTime = now

    def onSend(self, event):
        msgStr = ':'.join([item.GetValue() for item in self.fieldlList])#+'\r'
        self.statusbar.SetStatusText(msgStr)
        if self.serComm:
            print('Send message [%s] to cmd ' %msgStr)
            self.serComm.write(msgStr.encode('utf-8'))
        time.sleep(0.1)
        if self.pumpSP.GetSelection() == 0:
            self.se1.writeMem('M4', 0)
            self.se1.writeMem('M5', 0)
        elif self.pumpSP.GetSelection() == 1:
            self.se1.writeMem('M4', 0)
            self.se1.writeMem('M5', 1)
        elif self.pumpSP.GetSelection() == 2:
            self.se1.writeMem('M4', 1)
            self.se1.writeMem('M5', 0)
        time.sleep(0.1)
        if self.MotoSP.GetSelection() == 0:
            self.se2.writeMem('qx0.3', False)
            self.se2.writeMem('qx0.4', False)
        elif self.MotoSP.GetSelection() == 1:
            self.se2.writeMem('qx0.3', False)
            self.se2.writeMem('qx0.4', True)
        elif self.MotoSP.GetSelection() == 2:
            self.se2.writeMem('qx0.3', True)
            self.se2.writeMem('qx0.4', False)
        time.sleep(0.1)
        if self.senPower.GetSelection() == 0:
            self.se3.writeMem('M4', 1)
            self.se3.writeMem('M5', 1)
        elif self.senPower.GetSelection() == 1:
            self.se3.writeMem('M4', 0)
            self.se3.writeMem('M5', 0)
        time.sleep(0.1)
        if self.AllPower.GetSelection() == 0:
            self.se3.writeMem('M6', 0)
        elif self.AllPower.GetSelection() == 1:
            self.se3.writeMem('M6', 1)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        iMainFrame = UIFrame(None, -1, "Serial Comm tester")
        iMainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()

