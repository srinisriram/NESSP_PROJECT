# This file defines the constants used in this package.

from enum import Enum

MAX_OCCUPANCY = 100
SPEECH_FILENAME = 'speech2.wav'
SERVER_PORT = 10000
MAX_NUMBER_OF_RCV_BYTES = 1024

# object detection model
MODEL_NAME = "models/MobileNetSSD_deploy.caffemodel"

# proto text file of the object detection model
PROTO_TEXT_FILE = "models/MobileNetSSD_deploy.prototxt"

# Frame width.
FRAME_WIDTH_IN_PIXELS = 400

# Maximum consecutive frames a given object is allowed to be
# marked as "disappeared" until we need to deregister the object from tracking.
MAX_NUM_OF_CONSECUTIVE_FRAMES_FOR_ACTION = 50

# Maximum distance between centroids to associate an object --
# if the distance is larger than this maximum distance we'll
# start to mark the object as "disappeared".
MAX_DISTANCE_FROM_THE_OBJECT = 100

# list holding the different speed estimation column index.
# For example, first timestamp is stored at column index 60 and so on...
COLUMN_SAMPLE_POINTS_LIST = [60, 120, 180, 240]

# Column traversal
COLUMN = 1

# minimum confidence
MIN_CONFIDENCE = 0.4

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
MAX_TRACKER_LIST_SIZE = 10

OPEN_DISPLAY = True

VIDEO_DEV_ID = 0

SEND_EMAIL = True

TIMEOUT_FOR_TRACKER = 2

DEMARCATION_LINE = 100

TEST_VIDEO_FILE_PATH_1 = 'videos/example_01.mp4'
TEST_VIDEO_FILE_PATH_2 = 'videos/example_02.mp4'

# Log file name
ENTER_LOG_FILE_NAME = "enter_file.csv"
EXIT_LOG_FILE_NAME = "exit_file.csv"

USE_PI_CAMERA = True


class Direction(Enum):
    ENTER = 1
    EXIT = 2
