#!/bin/bash
set -o nounset  # Detects uninitialized variables on the script and exits with error
#set -o errexit  # Exits script on error

BASEDIRECTORY=/home/RPI6MM/<name_camera>/static/picture

now=$(date)
YEAR=$(date +"%Y");
MONTH=$(date +"%m");
DAY=$(date +"%d");
HORA=$(date +"%H");
MIN=$(date +"%M");
SEC=$(date +"%S");

VIDSOURCE="rtsp://<address_IP_camera>:5554/"
ffmpeg  -i "$VIDSOURCE" -vframes 1 "$BASEDIRECTORY/$YEAR-$MONTH-$DAY-$HORA-$MIN-$SEC.jpg"
