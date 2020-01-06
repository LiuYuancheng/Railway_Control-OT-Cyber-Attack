#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        attackHost.py [python2.7/python3]
#
# Purpose:     This module is used to create a http server on port 8080 to handle
#              the control get request.(Send the attack active cmd to attckServ)
# Author:      Yuancheng Liu
#
# Created:     2019/12/05
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import time
import socket
import subprocess
from platform import python_version

if '3.' in python_version():
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Init the constants
TEST_MODE = True    # Test mode flag - True: test on local computer
PORT_NUMBER = 8000 if TEST_MODE else 8080 # http host port.
SEV_IP = ('127.0.0.1', 5005) if TEST_MODE else ('192.168.10.244', 5005) # attack server IP address.
BUFFER_SZ = 1024

# Init the global variable
updClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class myHandler(BaseHTTPRequestHandler):
     
    def do_GET(self):
        """ Handler for the GET requests."""
        global updClient
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message.
        self.wfile.write(b"405 file not found.")
        if self.path == '/BE3':
            # direct to the attack doc folder and open the attack document with macro.
            print('Start Black Energy 3 attack.')
            atkStr = 'explorer \"C:\\Users\\dcslyc\\Documents\"' if TEST_MODE else 'explorer \"C:\\Users\\Administrator\\Documents\\doc\"'
            print(str(subprocess.Popen(atkStr, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
            time.sleep(1)
            atkStr = '\"C:\\Users\\dcslyc\\Documents\\operation manual.docm"' if TEST_MODE else '\"C:\\Users\\Administrator\\Documents\\doc\\operation manual.docm"'
            print(str(subprocess.Popen(atkStr, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)))      
        elif self.path == '/STOP':
            print('Stop attack.')
            msg = 'A;0'  # attack active message.
            updClient.sendto(msg.encode('utf-8'), SEV_IP)
        elif self.path == '/':
            msg = 'A;1'  # attack active message.
            updClient.sendto(msg.encode('utf-8'), SEV_IP)
        print('Finished response the <GET> request.')
        return

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    try:
        server = HTTPServer(('0.0.0.0', PORT_NUMBER), myHandler)
        print('Started httpserver on port %s' % str(PORT_NUMBER))
        #Wait forever for incoming htto requests
        server.serve_forever()
        print("Server end.")
    except KeyboardInterrupt:
        server.socket.close()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
