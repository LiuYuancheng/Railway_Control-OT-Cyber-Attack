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
        
        self.SetSizer(self._buidUISizer())
        self.statusbar = self.CreateStatusBar()
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms

#--UIFrame---------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI Sizer. """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        gs = wx.FlexGridSizer(9, 2, 5, 5)

        gs.Add(wx.StaticText(self, label=' Frequency : '), flag=flagsR, border=2)
        freText = wx.TextCtrl(self, -1, "0")
        self.fieldlList.append(freText)
        gs.Add(freText, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Voltage : '), flag=flagsR, border=2)
        volText = wx.TextCtrl(self, -1, "0")
        self.fieldlList.append(volText)
        gs.Add(volText, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Frequency LED : '), flag=flagsR, border=2)
        freLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        self.fieldlList.append(freLedCB)
        gs.Add(freLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Voltage LED : '), flag=flagsR, border=2)
        volLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        self.fieldlList.append(volLedCB)
        gs.Add(volLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Motor LED : '), flag=flagsR, border=2)
        motLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        self.fieldlList.append(motLedCB)
        gs.Add(motLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Pump LED : '), flag=flagsR, border=2)
        pumLedCB= wx.ComboBox(self, -1, choices=['green', 'amber', 'red'])
        self.fieldlList.append(pumLedCB)
        gs.Add(pumLedCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Smoke : '), flag=flagsR, border=2)
        smokeCB= wx.ComboBox(self, -1, choices=['on', 'off'])
        self.fieldlList.append(smokeCB)
        gs.Add(smokeCB, flag=flagsR, border=2)

        gs.Add(wx.StaticText(self, label=' Siren : '), flag=flagsR, border=2)
        sirenCB= wx.ComboBox(self, -1, choices=['on', 'off'])
        self.fieldlList.append(sirenCB)
        gs.Add(sirenCB, flag=flagsR, border=2)
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
        msgStr = ','.join([item.GetValue() for item in self.fieldlList])
        self.statusbar.SetStatusText(msgStr)
        if self.serComm:
            print('Send message [%s] to cmd ' %msgStr)
            self.serComm.write(msgStr.encode('utf-8'))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        iMainFrame = UIFrame(None, -1, "Serial Comm tester")
        iMainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()

