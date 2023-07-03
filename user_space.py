from video import take_video, update_config_vid, update_config_pic, create_cron, last_picture
from flask import Flask, redirect, url_for, request, render_template, send_from_directory, make_response
import os
import time
from picamera2 import Picamera2
import json

app = Flask(__name__)
VID_FOLDER = os.path.join('static')
app.config['UPLOAD_FOLDER'] = VID_FOLDER
app.config["DEBUG"] = True

@app.route('/',methods=['POST','GET'])
def choice():
    if request.method == 'POST':
        valeur_select = request.form['action']
        if valeur_select == 'Picture':
            return redirect(url_for('picture'))
        else :
           return redirect(url_for('param'))
    return render_template('user_space.html')


@app.route('/Param', methods=['POST', 'GET'])
def param():
    if request.method == 'POST':
        width = int(request.form['width'])
        height = int(request.form['height'])
        duration = int(request.form['duration'])
        update_config_vid(False,width,height,duration)
        if duration == 0:
            print("je suis la")
            return redirect(url_for('video'))
        take_video(duration, width, height)
    return render_template('param.html')

@app.route('/Video', methods=['POST', 'GET'])
def video():
    if request.method == 'POST':
        #loading the json file
        with open('config_vid.json', 'r') as file:
            config = json.load(file)
        width=int(config['width'])
        height=int(config['height'])
        duration=int(config['duration'])
        #stream youtube
        #display stream youtube

        if 'stop' in request.form:
            #stop stream youtube
            return redirect(url_for('choice'))
    return render_template('video.html')

@app.route('/Picture', methods=['POST', 'GET'])
def picture():
    photo_recent = last_picture()
    if photo_recent != False:
        picture = os.path.join(app.config['UPLOAD_FOLDER'], photo_recent[-29:])
    else:
        picture = os.path.join(app.config['UPLOAD_FOLDER'], 'home.png')

    if request.method == 'POST':
        if 'param' in request.form:
            width = int(request.form['width'])
            height = int(request.form['height'])
            duration = int(request.form['duration'])
            shutter = int(request.form['shutter'])
            gain = int(request.form['gain'])
            period = int(request.form['period'])
            update_config_pic(True,width,height,duration,shutter,gain)
            create_cron(period)

        elif 'change' in request.form:
            update_config_pic(False,False,False,False,False,False)
            return redirect(url_for('choice'))
    return render_template('picture.html', user_space=picture)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
