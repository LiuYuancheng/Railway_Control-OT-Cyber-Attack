#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        attackHost.py [python2.7]
#
# Purpose:     This module is used to create a http server on port 8080 to handle
#              the get request.
# Author:      Yuancheng Liu
#
# Created:     2019/12/05
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import socket
from platform import python_version

if '3.' in python_version():
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

PORT_NUMBER = 8080                  # http host port.
SEV_IP = ('192.168.10.244', 5005)   # attack server IP address.
BUFFER_SZ = 1024

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """ Handler for the GET requests."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write(b"405 file not found.")
        # init the server and send the attack active request.
        self.crtClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = 'A;1'  # attack active on message.
        self.crtClient.sendto(msg.encode('utf-8'), SEV_IP)
        print('Finished response the <GET> request.')
        return

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    try:
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print('Started httpserver on port %s' % str(PORT_NUMBER))
        #Wait forever for incoming htto requests
        server.serve_forever()
        print("Server end.")
    except KeyboardInterrupt:
        #print '^C received, shutting down the web server'
        server.socket.close()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
