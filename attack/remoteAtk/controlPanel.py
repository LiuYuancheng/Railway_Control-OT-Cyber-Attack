#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:         controlPanel.py [python2.7/python3]
#
# Purpose:     This module will create attack control panel to start and stop
#              the man in the middle attack.
#               
# Author:      Yuancheng Liu
#
# Created:     2019/12/02
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

try:
    # for Python2
    import Tkinter as tk
    import ScrolledText as tkst
except ImportError:
    # for Python3
    import tkinter as tk
    import tkinter.scrolledtext as tkst
import socket

SEV_IP = ('127.0.0.1', 5005)
BUFFER_SZ = 1024

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class controlPanel(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)   
        #reference to the master widget, which is the tk window                 
        self.master = master
        # Create the UDP client
        self.crtClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.initWindow()

#-----------------------------------------------------------------------------
    def initWindow(self):
        self.master.title("OT-plantform attack control panel")
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)
        # place weidgts:
        self.startBt = tk.Button(self, text=" Active Attack ",command=self.startAtk)
        self.startBt.place(x=10, y=10)
        self.stopBt = tk.Button(self, text=" Stop Attack ",command=self.onStopAtk)
        self.stopBt.place(x=120, y=10)
        self.cntBt = tk.Button(self, text=" Connect Sev ",command=self.onConnect)
        self.cntBt.place(x=220, y=10)
        self.text = tkst.ScrolledText(self, height=7, width = 35)
        self.text.place(x=10, y=40)
        self.text.insert(tk.INSERT, "Init finished\n")
        
#-----------------------------------------------------------------------------
    def startAtk(self):
        self.text.insert(tk.INSERT, "Start Attack\n")
        msg = 'A;1'
        self.crtClient.sendto(msg.encode('utf-8'), SEV_IP)

#-----------------------------------------------------------------------------
    def onStopAtk(self):
        self.text.insert(tk.INSERT, "Stop Attack. \n")
        msg = 'A;0'
        self.crtClient.sendto(msg.encode('utf-8'), SEV_IP)

#-----------------------------------------------------------------------------
    def onConnect(self):
        """ Try to connect to the server.
        """
        self.text.insert(tk.INSERT, "Try to connect to attack server\n")
        msg = 'C;1'
        self.crtClient.sendto(msg.encode('utf-8'), SEV_IP)
        data, _ = self.crtClient.recvfrom(BUFFER_SZ)
        msg = data.decode(encoding="utf-8")
        self.text.insert(tk.INSERT, "Server response: %s\n" %str(msg))

# root window created. Here, that would be the only window, but
# you can later have windows within windows.
root = tk.Tk()
root.geometry("320x200")
#creation of an instance
app = controlPanel(root)
#mainloop 
root.mainloop()  
