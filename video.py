import time
import os
import json
from picamera2 import  MappedArray, Picamera2
import subprocess
from crontab import CronTab
from datetime import datetime
import cv2
#libcamera-vid -t 0 --width 1920 --height 1080 --codec h264 --inline --listen -o tcp://0.0.0.0:8888
#libcamera-jpeg -o test.jpg -t 2000 --width 640 --height 480 --shutter 20000 --gain 1
def create_cron(period):
    
    cron = CronTab(user='RPI6MM')
    # Parcourir toutes les tâches dans la crontab
    for job in cron:
        if job.command == '/home/RPI6MM/user_space/script.sh >> /home/RPI6MM/user_space/sortie.txt 2>&1':
            # Supprimer la tâche correspondante
            cron.remove(job)
    
    job = cron.new(command="/home/RPI6MM/user_space/script.sh >> /home/RPI6MM/user_space/sortie.txt 2>&1")
    job.minute.every(period)
    cron.write()

    """
    cron_job = f"*/{period} * * * * /home/RPI6MM/user_space/script.sh >> /home/RPI6MM/user_space/sortie.txt 2>&1"
    cron_file = "/etc/cron.d/my_cron"

    # Supprimer le fichier cron existant s'il existe
    if os.path.exists(cron_file):
        os.remove(cron_file)

    command = f"echo '{cron_job}' | sudo tee {cron_file}"
    os.system(command)

    print("Cron table created successfully.")
    """

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


def update_config_vid(on,width,height,duration):    
    #loading the json file
    with open('config_vid.json', 'r') as file:
        config = json.load(file)

    #updating data
    config['on'] = on
    config['width']=width
    config['height']=height
    config['duration']=duration
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
    output_file = os.path.join(os.path.expanduser("~"),"user_space", "static", filename)

    picam2.pre_callback = apply_timestamp
    picam2.start_and_record_video(output_file, duration=duration)

def take_picture(width, height,duration,shutter,gain):

    #Image output path and file name
    timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
    filename = 'picture_{}.jpg'.format(timestamp)
    output_file = os.path.join(os.path.expanduser("~"),"user_space", "static", filename)

    command = f"libcamera-jpeg -o {output_file} -t {duration} --width {width} --height {height} --shutter {shutter} --gain {gain}"
    subprocess.run(command, shell=True)

"""function that returns the dates of the files given as arguments"""
def date(file, file1):
    date1=datetime(int(file[6:10]), int(file[11:13]), int(file[14:16]), int(file[17:19]), int(file[20:22]))
    date2=datetime(int(file1[6:10]), int(file1[11:13]), int(file1[14:16]), int(file1[17:19]), int(file1[20:22]))
    return date1, date2

"""function that returns the last photo taken"""
def last_picture():
    #Path to the folder to be listed
    folder = '/home/RPI6MM/user_space/static'

    #Lists all the files in the folder
    files = os.listdir(folder)
    i=0
    
    #test if no photo was taken
    if len(files)==1:
        return False
    
    #Removes the photo home.png from the list of photos to compare
    for file in files:
        if file == 'home.png' :
            del files[i]
            break
        i+=1
    
    #comparison of picture dates
    recent_file = files[0]
    for i in range(len(files)-1):
        date1,date2=date(files[i],recent_file)
        
        if date1 < date2:
            path_file = os.path.join(folder, recent_file)
        else :
            path_file = os.path.join(folder, files[i])
            recent_file=files[i]

    return path_file
