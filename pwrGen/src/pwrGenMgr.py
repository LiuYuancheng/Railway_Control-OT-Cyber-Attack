#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        pwrGenMgr.py
#
# Purpose:     power generator auto control manager
#              
# Author:       Yuancheng Liu
#
# Created:     2020/02/17
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#--------------------------------------------------------------------------
import time
import threading
PERIOD = 1  # update frequency

class pwrGenMgr(threading.Thread):
    """ TCP server thread.""" 
    def __init__(self, parent, threadID, name):
        threading.Thread.__init__(self)
        self.parent = parent
        self.loadPins = [0]*5   # load connect to the generator.
        self.loadCount = sum(self.loadPins)
        self.motorSp = 50        # motor speed 0:low, 1:medium, 2:high
        self.pumpSp = 1         # pump speed 0:low, 1 medium, 2:high
        self.respT = 3          # time interval to response back to normal.
        self.terminate = False

    def setLoad(self, idxList, ValList):
        for item in zip(idxList, ValList):
            idx, val = item
            self.loadPins[idx] = val
        # simulate the frequency imediatly change.
        val = sum(self.loadPins)
        
        # Set pump speed
        if  val == 0:
            self.pumpSp = 0
        elif val == 3:
            self.pumpSp = 2
        elif val < 3:
            self.pumpSp = 1
        else:
            self.pumpSp = 3

        # set moto speed
        if val > self.loadCount:
            self.motorSp -= 3
        elif val < self.loadCount:
            self.motorSp += 3
        self.loadCount = val


    def getMotorSp(self):
        return self.motorSp
    
    def getPumpSp(self):
        return self.pumpSp

    def run(self):
        while not self.terminate:
            time.sleep(PERIOD)
            if self.motorSp < 50:
                self.motorSp += 1
            elif self.motorSp > 50:
                self.motorSp -= 1
            print(" M and P speed: %s" %str( (self.motorSp, self.pumpSp) ))

    def stop(self):
        self.terminate = True