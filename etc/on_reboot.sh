#!/bin/bash

source `which virtualenvwrapper.sh`
workon openvino
source openvino/openvino/bin/setupvars.sh
export PYTHONPATH=$PYTHONPATH:/home/pi/NESSP_PROJECT
cd NESSP_PROJECT/Occupancy_Tracker
python3 human_detector.py -i 192.168.86.73
