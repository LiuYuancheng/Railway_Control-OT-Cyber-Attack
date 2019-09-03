#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:         M2PLC221.py
#
# Purpose:     This module is used to connect the Schneider M2xx PLC. The related
#              PLC setting link(function code):
#              https://www.schneider-electric.com/en/faqs/FA308725/
#              https://www.schneider-electric.com/en/faqs/FA295250/
#              https://www.schneider-electric.com/en/faqs/FA249614/
#               
# Author:      Yuancheng Liu
#
# Created:     2019/09/02
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------
import socket
import sys

PLC_PORT = 502
# M221 PLC memory address list.
MEM_ADDR = {'M0':   '0000',
            'M1':   '0001',
            'M2':   '0002',
            'M3':   '0003',
            'M4':   '0004',
            'M5':   '0005',
            'M6':   '0006',
            'M10':  '000a',
            'M20':  '0014',
            'M30':  '001e',
            'M40':  '0028',
            'M50':  '0032',
            'M60':  '003c'
           }


TID = '0000'
PROTOCOL_ID = '0000'
UID = '01'
BIT_COUNT = '0001'
BYTE_COUNT = '01'
LENGTH = '0008'
M_FC = '0f' # memory access function code.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class M221(object):
    def __init__(self, ip, debug=False):
        self.ip = ip
        self.plcAgent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.plcAgent.connect((self.ip, PLC_PORT))
        except:
            print("PLC connection fail.")

    def setMemory(self, mTag, val):
        """ Set the plc memory address. mTag: (str)memory tag, val:(int) 0/1
        """
        modbus_payload = "".join(
            (TID, PROTOCOL_ID, LENGTH, UID, M_FC, mTag, BIT_COUNT, BYTE_COUNT, str(val)))
        self.plcAgent.send(modbus_payload.decode('hex'))
        response = self.plcAgent.recv(1024).encode('hex')
        print(response)

    def disConnect(self):
        """ Disconnect from PLC."""
        print("M221:    Disconnect from PLC.")
        self.plcAgent.close()