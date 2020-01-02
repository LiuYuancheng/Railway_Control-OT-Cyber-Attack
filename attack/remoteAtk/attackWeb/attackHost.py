import socket
from flask import Flask, redirect, url_for, request, render_template

SEV_IP = ('127.0.0.1', 5005)
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
            #return render_template('login.html')
            msg = 'A;1'
            crtClient.sendto(msg.encode('utf-8'), SEV_IP)
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
   