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
M_RD = '01' # read internal bits %M




VALUES = {'0': '00', '1': '01'}
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class M221(object):
    def __init__(self, ip, debug=False):
        self.ip = ip
        self.plcAgent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.plcAgent.connect((self.ip, 502))

    def redMem(self):
        """ Set the plc memory address. mTag: (str)memory tag, val:(int) 0/1
        """
        modbus_payload = TID + PROTOCOL_ID + '0006' + UID + M_RD+"0000003d"
        print(modbus_payload)
        bdata = bytes.fromhex(modbus_payload)
        self.plcAgent.send(bdata)
        #response = self.plcAgent.recv(1024).dencode('hex')
        response = self.plcAgent.recv(1024).hex()
        #response = self.plcAgent.recv(1024).hex()
        print(response)
        return str(response)


    def writeMem(self, mTag, val):
        """ Set the plc memory address. mTag: (str)memory tag, val:(int) 0/1
        """
        modbus_payload = TID + PROTOCOL_ID + LENGTH + UID + M_FC + MEM_ADDR[mTag] + BIT_COUNT + BYTE_COUNT + VALUES[str(val)]
        print(modbus_payload)
        # print modbus_payload
        #self.plcAgent.send(modbus_payload.decode('hex'))
        #modbus_payload = "".join(
        #    (TID, PROTOCOL_ID, LENGTH, UID, M_FC, mTag, BIT_COUNT, BYTE_COUNT, str(val)))
        #self.plcAgent.send(modbus_payload.decode('hex'))
        bdata = bytes.fromhex(modbus_payload)
        self.plcAgent.send(bdata)

        #response = self.plcAgent.recv(1024).dencode('hex')
        response = self.plcAgent.recv(1024).hex()
        print(response)

    def disconnect(self):
        """ Disconnect from PLC."""
        print("M221:    Disconnect from PLC.")
        self.plcAgent.close()

#-----------------------------------------------------------------------------
def testCase():
    plc = M221('192.168.10.71')
    plc.redMem()
    #plc.writeMem('M10', 0)





    plc.disconnect()
	
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase()
