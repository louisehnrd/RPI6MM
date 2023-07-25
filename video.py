import time
import os
import json
from picamera2 import  MappedArray, Picamera2
import subprocess
from crontab import CronTab
from datetime import datetime
import cv2

def create_cron(period,name_script):
    
    cron = CronTab(user='RPI6MM')
    # Parcourir toutes les tâches dans la crontab
    for job in cron:
        if job.command == '/home/<name_camera>/user_space/script.sh >> /home/RPI6MM/user_space/sortie.txt 2>&1':
            # Supprimer la tâche correspondante
            cron.remove(job)
    
    job = cron.new(command=f"/home/<name_camera>/user_space/{name_script} >> /home/RPI6MM/user_space/sortie.txt 2>&1")
    job.minute.every(period)
    cron.write()

def update_config_pic(on,width,height,duration,shutter,gain):
    #loading the json file
    with open('config_pic.json', 'r') as file:
        config = json.load(file)

    #updating data
    config['on'] = on
    config['width']=width
    config['height']=height
    config['duration']=duration
    config['shutter']=shutter
    config['gain']=gain

    print(config)
        
    #write to the json config file
    with open("config_pic.json", "w") as json_file:
        json.dump(config, json_file)        
    json_file.close()


def update_config_vid(width,height,duration,period):    
    #loading the json file
    with open('config_vid.json', 'r') as file:
        config = json.load(file)

    #updating data
    config['width']=width
    config['height']=height
    config['duration']=duration
    config['period'] = period
    print(config)
        
    #write to the json config file
    with open("config_vid.json", "w") as json_file:
        json.dump(config, json_file)        
    json_file.close()

def apply_timestamp(request):
    colour = (0, 255, 0)
    origin = (0, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1
    thickness = 2
    timestamp = time.strftime("%Y-%m-%d %X")
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)

def take_video(duration, width, height):
    
    picam2 = Picamera2()
    capture_config = picam2.create_video_configuration({"size": (width,height)})
    picam2.align_configuration(capture_config)
    picam2.configure(capture_config)

    #Image output path and file name
    timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
    filename = 'video_{}.h264'.format(timestamp)
    output_file = os.path.join(os.path.expanduser("~"),"user_space", "static", "video",filename)

    picam2.pre_callback = apply_timestamp
    picam2.start_and_record_video(output_file, duration=duration)

def take_picture(width, height,duration,shutter,gain):

    #Image output path and file name
    timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
    filename = 'picture_{}.jpg'.format(timestamp)
    output_file = os.path.join(os.path.expanduser("~"),"user_space", "static","picture_shutter", filename)

    command = f"libcamera-jpeg -o {output_file} -t {duration} --width {width} --height {height} --shutter {shutter} --gain {gain}"
    subprocess.run(command, shell=True)

"""function that returns the dates of the files given as arguments"""
def date(file, file1):
    date1=datetime(int(file[8:12]), int(file[13:15]), int(file[16:18]), int(file[19:21]), int(file[22:24]))
    date2=datetime(int(file1[8:12]), int(file1[13:15]), int(file1[16:18]), int(file1[19:21]), int(file1[22:24]))
    return date1, date2

"""function that returns the last photo taken"""
def last_picture():
    #Path to the folder to be listed
    folder = '/home/<name_camera>/user_space/static/picture_shutter'

    #Lists all the files in the folder
    files = os.listdir(folder)
    i=0
    
    #test if no photo was taken
    if len(files)==0:
        return False
    
    #comparison of picture dates
    recent_file = files[0]
    for i in range(len(files)-1):
        date1,date2=date(files[i],recent_file)
        
        if date1 < date2:
            path_file = os.path.join(folder, recent_file)
        else :
            path_file = os.path.join(folder, files[i])
            recent_file=files[i]

    print(path_file)
    return path_file
