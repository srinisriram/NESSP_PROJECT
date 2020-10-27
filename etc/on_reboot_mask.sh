#!/bin/bash

echo "Initializing Environment..." &>/home/pi/Mask.log
# shellcheck disable=SC1090
# shellcheck disable=SC2046
# shellcheck disable=SC2230
source $(which virtualenvwrapper.sh)
workon openvino
# shellcheck disable=SC1090
source ~/openvino/openvino/bin/setupvars.sh
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT
echo "Testing Audio..." &>>Mask.log
aplay /home/pi/test_audio.wav
# shellcheck disable=SC2164
cd ~/NESSP_PROJECT/Mask_Detector
# shellcheck disable=SC2129
echo "Running the Script..." &>>/home/pi/Mask.log
python3 mask_detector.py &>>/home/pi/Mask.log
echo "Script Exiting..." &>>/home/pi/Mask.log
echo "Sending Crash Report via Email..." &>>/home/pi/Mask.log
python3 ~/NESSP_PROJECT/etc/crash_report.py -l /home/pi/Mask.log -m True
echo "Crash Report Sent..." &>>/home/pi/Mask.log
#echo "rebooting..." &>> /home/pi/Mask.log
#sudo reboot
