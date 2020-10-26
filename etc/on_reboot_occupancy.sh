#!/bin/bash

echo "Initializing Environment..." &> Occupation.log
source `which virtualenvwrapper.sh`
workon openvino
source ~/openvino/bin/setupvars.sh
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT
echo "Testing Audio..." &>> Occupation.log
aplay test_audio.wav
cd ~/NESSP_PROJECT/Occupancy_Tracker
echo "Running the Script..." &>> Occupation.log
python3 human_detector.py -i 192.168.86.73 &>> /home/pi/Occupation.log
echo "Script Exiting..." &>> /home/pi/Occupation.log
echo "Sending Crash Report Via Email..." &>> /home/pi/Occupation.log
python3 ~/NESSP_PROJECT/etc/crash_report.py -l /home/pi/Occupation.log -o True
echo "Crash Report Sent..." &>> Occupation.log
#echo "rebooting..." &>> /home/pi/Occupation.log
#sudo reboot
