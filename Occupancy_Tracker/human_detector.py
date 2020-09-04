# This file implements the algorithm for tracking human face.
# !/usr/bin/env python3
import argparse
import logging
import os
import threading
import time
from datetime import datetime

import cv2
import imutils
from Occupancy_Tracker.centroid_object_creator import CentroidObjectCreator
# import the necessary packages
from Occupancy_Tracker.constants import PROTO_TEXT_FILE, MODEL_NAME, FRAME_WIDTH_IN_PIXELS, VIDEO_DEV_ID, \
    SERVER_PORT, TIMEOUT_FOR_TRACKER
from Occupancy_Tracker.human_tracker_handler import HumanTrackerHandler
from Occupancy_Tracker.human_validator import HumanValidator
from Occupancy_Tracker.logger import Logger
from Occupancy_Tracker.send_receive_messages import SendReceiveMessages
from imutils.video import FPS
from imutils.video import VideoStream
from Occupancy_Tracker.singleton_template import Singleton


class HumanDetector(metaclass=Singleton):
    def __init__(self, find_humans_from_video_file_name=None,
                 use_pi_camera=True, open_display=True):
        # initialize the frame dimensions (we'll set them as soon as we read
        # the first frame from the video)
        self.H = None
        self.W = None
        self.video_stream = None
        self.net = None
        self.current_time_stamp = None
        self.frame = None
        self.rgb = None
        self.meter_per_pixel = None
        self.args = None
        self.find_humans_from_video_file_name = find_humans_from_video_file_name
        self.use_pi_camera = use_pi_camera
        self.open_display = open_display
        self.perform_human_detection = True

        SendReceiveMessages().perform_job()

        # Load Model
        self.load_model()
        # Initialize the camera.
        self.initialize_camera()

        # start the frames per second throughput estimator
        self.fps = FPS().start()
        self.centroid_object_creator = CentroidObjectCreator()

    @classmethod
    def perform_job(cls):
        """
        This method performs the job expected out from this class.
        :return:
        """
        t1 = threading.Thread(target=HumanDetector().thread_for_face_tracker)
        # starting thread 1
        t1.start()
        return t1.join()

    def get_human_centroid_dict(self):
        """
        This is used for unit test purpose only.
        :return:
        """
        return HumanTrackerHandler.human_tracking_dict

    def load_model(self):
        """
        Load our serialized model from disk
        """
        Logger.logger().info("Loading model name:{}, proto_text:{}.".format(MODEL_NAME, PROTO_TEXT_FILE))
        self.net = cv2.dnn.readNetFromCaffe(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            PROTO_TEXT_FILE),
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                MODEL_NAME))

        if self.use_pi_camera:
            # Set the target to the MOVIDIUS NCS stick connected via USB
            # Prerequisite: https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html
            Logger.logger().info("Setting MOVIDIUS NCS stick connected via USB as the target to run the model.")
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        else:
            Logger.logger().info("Setting target to CPU.")
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def initialize_camera(self):
        """
        Initialize the video stream and allow the camera sensor to warmup.
        """
        if self.find_humans_from_video_file_name:
            self.find_humans_from_video_file_name = \
                os.path.join(os.path.dirname(__file__),
                             self.find_humans_from_video_file_name)
            Logger.logger().info("Reading the input video file {}.".format(self.find_humans_from_video_file_name))

            self.video_stream = cv2.VideoCapture(self.find_humans_from_video_file_name)
            if not self.video_stream:
                Logger.logger().error("cv2.VideoCapture() returned None.")
                raise ValueError
            # self.video_stream.set(cv2.CAP_PROP_FPS, int(10))
        elif self.use_pi_camera:
            Logger.logger().info("Warming up Raspberry PI camera connected via the PCB slot.")
            self.video_stream = VideoStream(usePiCamera=True).start()
        else:
            Logger.logger().debug("Setting video capture device to {}.".format(VIDEO_DEV_ID))
            self.video_stream = VideoStream(src=VIDEO_DEV_ID).start()
        time.sleep(2.0)

    def grab_next_frame(self):
        """
        1. Grab the next frame from the stream.
        2. store the current timestamp, and store the new date.
        """
        if self.find_humans_from_video_file_name:
            if self.video_stream.isOpened():
                ret, self.frame = self.video_stream.read()
            else:
                Logger.logger().info("Unable to open video stream...")
                raise ValueError
        else:
            self.frame = self.video_stream.read()
        if self.frame is None:
            return

        self.current_time_stamp = datetime.now()
        # resize the frame
        self.frame = imutils.resize(self.frame, width=FRAME_WIDTH_IN_PIXELS)
        # width = FRAME_WIDTH_IN_PIXELS
        # height = self.frame.shape[0] # keep original height
        # dim = (width, height)
        # self.frame = cv2.resize(self.frame, dim, interpolation = cv2.INTER_AREA)
        self.rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

    def set_frame_dimensions(self):
        """
        If the frame dimensions are empty, set them.
        """
        # if the frame dimensions are empty, set them
        if not self.W or not self.H:
            (self.H, self.W) = self.frame.shape[:2]

    def loop_over_streams(self):
        while self.perform_human_detection:
            self.grab_next_frame()
            # check if the frame is None, if so, break out of the loop
            if self.frame is None:
                if self.find_humans_from_video_file_name:
                    for _ in range(TIMEOUT_FOR_TRACKER+1):
                        HumanTrackerHandler.compute_direction_for_dangling_object_ids(keep_dict_items=True)
                        time.sleep(1)
                    self.perform_human_detection = False
                    break
                else:
                    HumanTrackerHandler.compute_direction_for_dangling_object_ids()
                    continue
            self.set_frame_dimensions()

            objects = self.centroid_object_creator.create_centroid_tracker_object(self.H, self.W, self.rgb, self.net,
                                                                                  self.frame)
            for speed_tracked_object, objectID, centroid in HumanTrackerHandler.yield_a_human_tracker_object(objects):
                HumanTrackerHandler.record_movement(speed_tracked_object)
                HumanValidator.validate_column_movement(speed_tracked_object, self.current_time_stamp, self.frame,
                                                        objectID)
            if self.find_humans_from_video_file_name:
                HumanTrackerHandler.compute_direction_for_dangling_object_ids(keep_dict_items=True)
            else:
                HumanTrackerHandler.compute_direction_for_dangling_object_ids()

            # if the *display* flag is set, then display the current frame
            # to the screen and record if a user presses a key
            if self.open_display:
                cv2.imshow("Human_detector_frame", self.frame)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key is pressed, break from the loop
                if key == ord("q"):
                    break

            # Update the FPS counter
            self.fps.update()

    def clean_up(self):
        self.perform_human_detection = False
        SendReceiveMessages().cleanup()
        # stop the timer and display FPS information
        self.fps.stop()
        Logger.logger().debug("elapsed time: {:.2f}".format(self.fps.elapsed()))
        Logger.logger().debug("approx. FPS: {:.2f}".format(self.fps.fps()))

        # Close the log file.
        HumanValidator.close_log_file()

        # close any open windows
        cv2.destroyAllWindows()

        # clean up
        Logger.logger().debug("cleaning up...")
        if self.find_humans_from_video_file_name:
            self.video_stream.release()
        else:
            self.video_stream.stop()
        time.sleep(2)

    def thread_for_face_tracker(self):
        return_value = True
        while self.perform_human_detection:
            try:
                self.loop_over_streams()
            except Exception as e:
                Logger.logger().error("Caught an exception while looping over streams {}, rebooting....".format(
                    type(e).__name__ + ': ' + str(e)))
                return_value = False
                os.system("sudo reboot")
        return return_value


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--peer_ip_address", type=str, help="Provide the IP address of the remote raspberry PI.")
    parser.add_argument("-p", "--peer_port", type=int, help="Provide the server port of the remote raspberry PI.",
                        default=SERVER_PORT)
    parser.add_argument('-d', '--debug', type=bool, help='Enable debug logging.', default=False)
    args = parser.parse_args()
    if args.debug:
        Logger.set_log_level(logging.DEBUG)
    HumanDetector().perform_job()