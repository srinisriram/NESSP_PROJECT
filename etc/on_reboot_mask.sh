#!/bin/bash

echo "Initializing Environment..." &> /home/pi/Mask.log
source `which virtualenvwrapper.sh`
workon openvino
source ~/openvino/bin/setupvars.sh
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT
cd ~/NESSP_PROJECT/Mask_Detector
echo "Running the Script..." &>> /home/pi/Mask.log
python3 mask_detector.py &>> /home/pi/Mask.log
echo "Script Exiting..." &>> /home/pi/Mask.log
echo "Sending Crash Report via Email..." &>> /home/pi/Mask.log
python3 ~/NESSP_PROJECT/etc/crash_report.py -l /home/pi/Mask.log -m True
echo "Crash Report Sent..." &>> /home/pi/Mask.log
#echo "rebooting..." &>> /home/pi/Mask.log
#sudo reboot
