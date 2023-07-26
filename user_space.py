from video import take_video, update_config_vid, update_config_pic, create_cron, last_picture
from flask import Flask, redirect, url_for, request, render_template, send_from_directory, make_response
import os
import time
from picamera2 import Picamera2
import json
from flask_socketio import SocketIO, emit
from crontab import CronTab

app = Flask(__name__)
socketio = SocketIO(app)
PIC_FOLDER = os.path.join('static','picture_shutter')
app.config['UPLOAD_FOLDER'] = PIC_FOLDER
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
        #test if parameters have been chosen
        if 'param' in request.form :
            width = int(request.form['width'])
            height = int(request.form['height'])
            duration = int(request.form['duration'])
            period = int(request.form['period'])
            update_config_vid(width,height,duration,period)  #update file json
            #test if we want a continuous stream
            if duration == 0:
                return redirect(url_for('video'))
            
            #take a video
            take_video(duration, width, height)
    
        #test if you want to return to the home page
        elif 'return' in request.form :
            return redirect(url_for('choice'))
    return render_template('param.html')

@app.route('/Video', methods=['POST', 'GET'])
def video():

    
    #loading the json file
    with open('config_vid.json', 'r') as file:
        config = json.load(file)

    #updating data
    width=config['width']
    height=config['height']
    period=config['period']

    create_cron(period,'capture_image.sh')

    return render_template('video.html',width=width, height=height)



@socketio.on('stop_stream')
"""the stream is stopped, we also stop taking periodic photos"""
def stop_stream(data):
    cron = CronTab(user='<name_camera>')
    for job in cron:
        if job.command == '/home/<name_camera>/user_space/capture_image.sh >> /home/<name_camera>/user_space/sortie.txt 2>&1':
            cron.remove(job)
            cron.write()
    if data.get('stop') :
        emit('redirect')


@app.route('/Picture', methods=['POST', 'GET'])
def picture():
    photo_recent = last_picture()
    if photo_recent != False:
        picture = os.path.join(app.config['UPLOAD_FOLDER'], photo_recent[-29:])
    else:
        picture=None

    if request.method == 'POST':
        if 'param' in request.form:
            width = int(request.form['width'])
            height = int(request.form['height'])
            duration = int(request.form['duration'])
            shutter = int(request.form['shutter'])
            gain = int(request.form['gain'])
            period = int(request.form['period'])
            update_config_pic(True,width,height,duration,shutter,gain)
            create_cron(period,'script.sh')

        elif 'change' in request.form:
            update_config_pic(False,False,False,False,False,False)
            return redirect(url_for('choice'))
    return render_template('picture.html', user_space=picture)
    


if __name__ == '__main__':
   socketio.run(app,host='0.0.0.0', port=5000)
