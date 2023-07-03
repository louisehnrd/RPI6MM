#!/usr/bin/python

import json
from video import take_picture

def take_periodic_pic():
    #Load configuration from JSON file
    with open('/home/RPI6MM/user_space/config_pic.json','r') as config_file:
        config = json.load(config_file)
    config_file.close()

    if config['on']:
        width = config['width']
        height = config['height']
        duration = config['duration']
        shutter = config['shutter']
        gain = config['gain']

        take_picture(width, height,duration,shutter,gain)

        print(f"Pictures taken with settings : width={width}, height={height}, duration={duration}, shutter={shutter}, gain={gain}")
    else:
        print("Photo-taking is deactivated in the configuration.")

if __name__ == '__main__':
    take_periodic_pic() 
