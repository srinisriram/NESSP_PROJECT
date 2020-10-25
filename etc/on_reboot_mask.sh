#!/bin/bash

source `which virtualenvwrapper.sh`
workon openvino
source ~/openvino/bin/setupvars.sh
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT
rm -rf Mask.log
cd ~/NESSP_PROJECT/Mask_Detector
python3 mask_detector.py &>> /home/pi/Mask.log
echo "script exiting..." &>> /home/pi/Mask.log
echo "sending crash report via email..." &>> /home/pi/Mask.log
python3 ~/NESSP_PROJECT/etc/crash_report.py -l /home/pi/Mask.log -m True
#echo "rebooting..." &>> /home/pi/Mask.log
#sudo reboot
