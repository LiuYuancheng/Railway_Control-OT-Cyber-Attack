#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        udpCom.py
#
# Purpose:     This module will provide a UDP client and server communication API.
#
# Author:      Yuancheng Liu
#
# Created:     2019/01/15
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import socket

BUFFER_SZ = 4096    # TCP buffer size.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class udpClient(object):
    """ UDP client module."""
    def __init__(self, ipAddr):
        """ Create an ipv4 (AF_INET) socket object using the udp protocol (SOCK_DGRAM)
            init example: client = udpClient(('127.0.0.1', 502))
        """
        self.ipAddr = ipAddr
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#--udpClient-------------------------------------------------------------------
    def sendMsg(self, msg, resp=False, ipAddr=None):
        """ Convert the msg to bytes and send it to UDP server. 
            - resp: server response flag, method will wait server's response and 
                return the bytes format response if it is set to True. 
        """
        if not ipAddr is None: self.ipAddr = ipAddr  # reset ip address.
        if not isinstance(msg, bytes): msg = str(msg).encode('utf-8')
        self.client.sendto(msg, self.ipAddr)
        if resp:
            data, _ = self.client.recvfrom(BUFFER_SZ)
            return data
        return None

#--udpClient-------------------------------------------------------------------
    def disconnect(self):
        """ Send a empty logout message and close the socket."""
        self.sendMsg(msg='')
        self.client.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class udpServer(object):
    """ UDP server module."""
    def __init__(self, parent, port):
        """ Create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
            init example: server = udpServer(None, 5005)
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', port))
        self.terminate = False  # Server terminate flag.

#--udpServer-------------------------------------------------------------------
    def serverStart(self, handler=None):
        """ Start the UDP server to handle the incomming message."""
        while not self.terminate:
            data, address = self.server.recvfrom(BUFFER_SZ)
            print("Accepted connection from %s" % str(address))
            msg = handler(data) if not handler is None else data
            if not msg is None:  # don't response client if the handler feed back is None
                if not isinstance(msg, bytes): msg = str(msg).encode('utf-8')
                self.server.sendto(msg, address)
        self.server.close()

#--udpServer-------------------------------------------------------------------
    def serverStop(self):
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Test case program: udpComTest.py