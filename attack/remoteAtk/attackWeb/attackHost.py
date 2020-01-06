#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        attackHost.py [python2.7/python3]
#
# Purpose:     This module is used to create a flask http server on port 5000 
#              to control the PLC-railway system attack.
# Author:      Yuancheng Liu
#
# Created:     2020/01/03
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import socket
import requests
from flask import Flask, redirect, url_for, request, render_template

TEST_MODE = True # Test mode flag - True: test on local computer

SEV_IP = ('127.0.0.1', 5005) if TEST_MODE else ('192.168.10.244', 5005)
ACT_IP = ('127.0.0.1', 8000) if TEST_MODE else('192.168.10.251', 8080)
BUFFER_SZ = 1024

# Init the UDP send server
crtClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Init the flask web server program.
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['submit_button'] == 'startAtt1':
            urlStr = "http://"+ACT_IP[0]+":"+str(ACT_IP[1])+"/BE3"
            requests.get(url = urlStr) 
            return redirect(url_for('index'))
        elif request.form['submit_button'] == 'startAtt2':
            #return render_template('login.html')
            msg = 'A;2'
            crtClient.sendto(msg.encode('utf-8'), SEV_IP)
            return redirect(url_for('index'))
        elif request.form['submit_button'] == 'stopAtt1':
            #return render_template('login.html')
            msg = 'A;0'
            crtClient.sendto(msg.encode('utf-8'), SEV_IP)
            return redirect(url_for('index'))
        elif request.form['submit_button'] == 'stopAtt2':
            #return render_template('login.html')
            msg = 'A;0'
            crtClient.sendto(msg.encode('utf-8'), SEV_IP)
            return redirect(url_for('index'))
    elif request.method == 'GET':
        return redirect('/index') 

if __name__ == '__main__':
    app.run(host= "0.0.0.0", debug=False, threaded=True)
   