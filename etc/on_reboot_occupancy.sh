#!/bin/bash

source `which virtualenvwrapper.sh`
workon openvino
source ~/openvino/bin/setupvars.sh
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT
echo "Testing Audio..."
aplay test_audio.wav
rm -rf Occupation.log
cd ~/NESSP_PROJECT/Occupancy_Tracker
python3 human_detector.py -i 192.168.86.73 &>> /home/pi/Occupation.log
echo "script exiting..." &>> /home/pi/Occupation.log
echo "sending crash report via email..." &>> /home/pi/Occupation.log
python3 ~/NESSP_PROJECT/etc/crash_report.py -l /home/pi/Occupation.log -o True
#echo "rebooting..." &>> /home/pi/Occupation.log
#sudo reboot
