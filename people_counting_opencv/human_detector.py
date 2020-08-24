# This file implements the algorithm for tracking human face.
# !/usr/bin/env python3
import os
import time
from datetime import datetime
import argparse
import dlib
import imutils
import numpy as np
import cv2
import logging
from imutils.video import FPS
from imutils.video import VideoStream
from human_validator import HumanValidator
from human_tracker_handler import HumanTrackerHandler
from centroid_object_creator import CentroidObjectCreator
from send_receive_messages import SendReceiveMessages
import threading

# import the necessary packages
from constants import PROTO_TEXT_FILE, MODEL_NAME, FRAME_WIDTH_IN_PIXELS, OPEN_DISPLAY, VIDEO_DEV_ID, \
    USE_PI_CAMERA, SERVER_PORT
from logger import Logger


class HumanDetector:
    run_program = True

    send_receive_message_instance = None
    input_video_file_path = None
    preferable_target = None

    def __init__(self):
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

        # Load Model
        self.load_model()
        # Initialize the camera.
        self.initialize_camera()

        # start the frames per second throughput estimator
        self.fps = FPS().start()
        self.centroid_object_creator = CentroidObjectCreator()

    @classmethod
    def perform_job(cls, send_receive_message_instance, video_file_path=None,
                    preferable_target=cv2.dnn.DNN_TARGET_MYRIAD):
        """
        This method performs the job expected out from this class.
        :param video_file_path: path.
        :param send_receive_message_instance: instance
        :return:
        """
        HumanDetector.send_receive_message_instance = send_receive_message_instance
        HumanDetector.input_video_file_path = video_file_path
        HumanDetector.preferable_target = preferable_target

        t1 = threading.Thread(target=HumanDetector().thread_for_face_tracker)
        # starting thread 1
        t1.start()

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
        self.net.setPreferableTarget(HumanDetector.preferable_target)

    def initialize_camera(self):
        """
        Initialize the video stream and allow the camera sensor to warmup.
        """
        if HumanDetector.input_video_file_path:
            Logger.logger().info("setting the video file path ={} as input to the video capture.".format(
                HumanDetector.input_video_file_path))
            self.video_stream = cv2.VideoCapture(HumanDetector.input_video_file_path)
        elif USE_PI_CAMERA:
            Logger.logger().info("Setting video capture device to PI CAMERA.")
            self.video_stream = VideoStream(0).start()
        else:
            Logger.logger().info("Setting video capture device to {}.".format(VIDEO_DEV_ID))
            self.video_stream = VideoStream(src=VIDEO_DEV_ID).start()
        time.sleep(2.0)

    def grab_next_frame(self):
        """
        1. Grab the next frame from the stream.
        2. store the current timestamp, and store the new date.
        """
        if HumanDetector.input_video_file_path:
            if self.video_stream.isOpened():
                _, self.frame = self.video_stream.read()
        else:
            self.frame = self.video_stream.read()
        if self.frame is None:
            return

        self.current_time_stamp = datetime.now()
        # resize the frame
        self.frame = imutils.resize(self.frame, width=FRAME_WIDTH_IN_PIXELS)
        self.rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

    def set_frame_dimensions(self):
        """
        If the frame dimensions are empty, set them.
        """
        # if the frame dimensions are empty, set them
        if not self.W or not self.H:
            (self.H, self.W) = self.frame.shape[:2]
            self.meter_per_pixel = 1 / self.W

    def loop_over_streams(self):
        while HumanDetector.run_program:
            self.grab_next_frame()
            # check if the frame is None, if so, break out of the loop
            if self.frame is None:
                break
            self.set_frame_dimensions()

            objects = self.centroid_object_creator.create_centroid_tracker_object(self.H, self.W, self.rgb, self.net,
                                                                                  self.frame)
            for speed_tracked_object, objectID, centroid in HumanTrackerHandler.yield_a_human_tracker_object(objects):
                HumanTrackerHandler.update_column_index_movement(self.frame, speed_tracked_object, objectID, centroid,
                                                                 self.current_time_stamp)
                if speed_tracked_object.direction is not None:
                    Logger.logger().debug("Computed direction = {} for objectID = {}, "
                                          .format(speed_tracked_object.direction,
                                                  objectID))
                HumanValidator.validate_column_movement(speed_tracked_object, self.current_time_stamp, self.frame,
                                                        objectID, HumanDetector.send_receive_message_instance)

            HumanTrackerHandler.compute_direction_for_dangling_object_ids(HumanDetector.send_receive_message_instance)

            # if the *display* flag is set, then display the current frame
            # to the screen and record if a user presses a key
            if OPEN_DISPLAY:
                cv2.imshow("Human_detector_frame", self.frame)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key is pressed, break from the loop
                if key == ord("q"):
                    break

            # Update the FPS counter
            self.fps.update()

    def clean_up(self):
        # stop the timer and display FPS information
        self.fps.stop()
        Logger.logger().info("elapsed time: {:.2f}".format(self.fps.elapsed()))
        Logger.logger().info("approx. FPS: {:.2f}".format(self.fps.fps()))

        # Close the log file.
        HumanValidator.close_log_file()

        # close any open windows
        cv2.destroyAllWindows()

        # clean up
        Logger.logger().info("cleaning up...")
        if HumanDetector.input_video_file_path:
            self.video_stream.release()
        else:
            self.video_stream.stop()

    def thread_for_face_tracker(self):
        while HumanDetector.run_program:
            try:
                self.loop_over_streams()
            except ValueError:
                self.clean_up()
                time.sleep(10)
        self.clean_up()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--peer_ip_address", type=str, help="Provide the IP address of the remote raspberry PI.")
    parser.add_argument("-p", "--peer_port", type=int, help="Provide the server port of the remote raspberry PI.",
                        default=SERVER_PORT)
    parser.add_argument('-d', '--debug', type=bool, help='Enable debug logging.', default=False)
    args = parser.parse_args()
    if args.debug:
        Logger.set_log_level(logging.DEBUG)
    send_rcv_inst = SendReceiveMessages()
    send_rcv_inst.perform_job()
    HumanDetector.perform_job(send_receive_message_instance=send_rcv_inst,
                              preferable_target=cv2.dnn.DNN_TARGET_CPU)
