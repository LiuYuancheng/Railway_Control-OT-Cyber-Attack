#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        action.py [python2.7/python3]
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

import socket
import subprocess
import time
SEV_IP = ('0.0.0.0', 5006)  # UDP server ip
BUFFER_SZ = 1024
# opened file link



# 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SEV_IP)

while True:
    data, address = sock.recvfrom(BUFFER_SZ)
    if not data: break
    if isinstance(data, bytes):
        print("income message")
        atkStr = 'explorer "C:\Users\Administrator\Documents\doc"'
        print(str(subprocess.Popen(atkStr, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
        time.sleep(1)
        atkStr = '"C:\Users\Administrator\Documents\doc\operation manual.docm"'
        print(str(subprocess.Popen(atkStr, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)))          # UPD receive buffer size
        
    else:
        print('Data format invalid: %s' % str(data))
