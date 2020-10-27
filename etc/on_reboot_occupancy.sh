#!/bin/bash

echo "Initializing Environment..." &>/home/pi/Occupation.log
# shellcheck disable=SC1090
# shellcheck disable=SC2046
# shellcheck disable=SC2230
# shellcheck disable=SC2129
source $(which virtualenvwrapper.sh) &>>/home/pi/Occupation.log
workon openvino &>>/home/pi/Occupation.log
# shellcheck disable=SC1090
source ~/openvino/openvino/bin/setupvars.sh &>>/home/pi/Occupation.log
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT &>>/home/pi/Occupation.log
#echo "Testing Audio..." &>> Occupation.log
#aplay test_audio.wav
# shellcheck disable=SC2164
cd ~/NESSP_PROJECT/Occupancy_Tracker
# shellcheck disable=SC2129
echo "Running the Script..." &>>/home/pi/Occupation.log
# shellcheck disable=SC2129
python3 human_detector.py -i 192.168.86.73 &>>/home/pi/Occupation.log
echo "Script Exiting..." &>>/home/pi/Occupation.log
echo "Sending Crash Report Via Email..." &>>/home/pi/Occupation.log
python3 ~/NESSP_PROJECT/etc/crash_report.py -l /home/pi/Occupation.log -o True &>>/home/pi/Occupation.log
echo "Crash Report Sent..." &>>/home/pi/Occupation.log
#echo "rebooting..." &>> /home/pi/Occupation.log
#sudo reboot
