#!/usr/bin/python
import socket
from platform import python_version

if '3.' in python_version():
    from http.server import BaseHTTPRequestHandler,HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

PORT_NUMBER = 9090#8080
SEV_IP = ('192.168.10.244', 5005)
BUFFER_SZ = 1024

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):	
	#Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write(b"405 file not found.")
        # init the server and send the attack active request.
        self.crtClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = 'A;1'
        self.crtClient.sendto(msg.encode('utf-8'), SEV_IP)
        print('Finished on response.')
        return

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port %s' %str(PORT_NUMBER))

    #Wait forever for incoming htto requests
    server.serve_forever()
    print("server end")

except KeyboardInterrupt:
    #print '^C received, shutting down the web server'
    server.socket.close()