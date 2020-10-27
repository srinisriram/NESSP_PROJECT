#!/bin/bash

echo "Initializing Environment..." &>Occupation.log
# shellcheck disable=SC1090
# shellcheck disable=SC2046
source $(which virtualenvwrapper.sh)
workon openvino
# shellcheck disable=SC1090
source ~/openvino/openvino/bin/setupvars.sh
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT
#echo "Testing Audio..." &>> Occupation.log
#aplay test_audio.wav
# shellcheck disable=SC2164
cd ~/NESSP_PROJECT/Occupancy_Tracker
echo "Running the Script..." &>>Occupation.log
# shellcheck disable=SC2129
python3 human_detector.py -i 192.168.86.73 &>>/home/pi/Occupation.log
echo "Script Exiting..." &>>/home/pi/Occupation.log
echo "Sending Crash Report Via Email..." &>>/home/pi/Occupation.log
python3 ~/NESSP_PROJECT/etc/crash_report.py -l /home/pi/Occupation.log -o True
echo "Crash Report Sent..." &>>Occupation.log
#echo "rebooting..." &>> /home/pi/Occupation.log
#sudo reboot
