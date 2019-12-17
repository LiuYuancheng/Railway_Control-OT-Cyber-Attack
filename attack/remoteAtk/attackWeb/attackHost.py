from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['submit_button'] == 'startAtt1':
            #return render_template('login.html')
            return redirect(url_for('index'))
        elif request.form['submit_button'] == 'startAtt2':
            #return render_template('login.html')
            return redirect(url_for('index'))
        elif request.form['submit_button'] == 'stopAtt1':
            #return render_template('login.html')
            return redirect(url_for('index'))
        elif request.form['submit_button'] == 'stopAtt2':
            #return render_template('login.html')
            return redirect(url_for('index'))
    elif request.method == 'GET':
        return redirect('/index') 

if __name__ == '__main__':
   app.run(host= "0.0.0.0", debug=True, threaded=True)