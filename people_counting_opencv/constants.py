# This file defines the constants used in this package.
MAX_OCCUPANCY = 100
SPEECH_FILENAME = 'speech.wav'
ENTER_EXCEL_SHEET_NAME = 'enter_file.xlsx'
EXIT_EXCEL_SHEET_NAME = 'exit_file.xlsx'
SERVER_PORT = 10000
MAX_NUMBER_OF_RCV_BYTES = 1024
prototxt = "models/MobileNetSSD_deploy.prototxt"
model = "models/MobileNetSSD_deploy.caffemodel"
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
          "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
          "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
          "sofa", "train", "tvmonitor"]
MAX_TRACKER_LIST_SIZE = 10