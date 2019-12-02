#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:         controlPanel.py
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

import tkinter as tk
import socket

class controlPanel(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)   
        #reference to the master widget, which is the tk window                 
        self.master = master
        #with that, we want to then run init_window, which doesn't yet exist
        self.initWindow()

    #Creation of init_window
    def initWindow(self):
        self.master.title("OT-plantform attack control panel")
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)
        # creating a button instance
        startBt = tk.Button(self, text=" Active Attack ",command=self.startAtk)
        # placing the button on my window
        startBt.place(x=10, y=10)

        stopBt = tk.Button(self, text=" Stop Attack ",command=self.startAtk)
        # placing the button on my window
        stopBt.place(x=110, y=10)

        cntBt = tk.Button(self, text=" Connect Sev ",command=self.startAtk)
        cntBt.place(x=200, y=10)

        text = tk.Text(self, height=7, width = 35)
        text.place(x=10, y=40)
        text.insert(tk.INSERT, "Init finished\n")
        text.insert(tk.INSERT, "Try to connect to attack server\n")

    def startAtk(self):
        exit()

# root window created. Here, that would be the only window, but
# you can later have windows within windows.
root = tk.Tk()

root.geometry("300x200")

#creation of an instance
app = controlPanel(root)

#mainloop 
root.mainloop()  