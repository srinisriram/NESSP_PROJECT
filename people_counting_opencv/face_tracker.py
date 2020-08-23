# This file implements the algorithm for tracking human face.
import cv2
import dlib
import numpy as np
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
import pandas as pd
from datetime import datetime
import pytz
import threading
from constants import prototxt, model, CLASSES, MAX_TRACKER_LIST_SIZE, VIDEO_DEV_ID
import time
from collections import defaultdict
import os
from logger import Logger

from send_receive_messages import SendReceiveMessages


class FaceTracker:
    """
    This class implements the logic to track a human face.
    """
    run_program = True

    send_receive_message_instance = None
    __input_video_file_path = None
    __preferable_target = None
    net = None
    vs = None
    ct = None
    trackers = []
    ret = None
    frame = None
    rgb = None
    H = None
    W = None
    blob = None
    detections = None
    rects = []

    status = None

    totalFrames = 0
    totalDown = 0
    totalUp = 0
    totalPeople = 0

    move_dict = {}
    arr = []
    emailSent = False
    enter_dict = {"Date": [], "Time": []}
    exit_dict = {"Date": [], "Time": []}

    @classmethod
    def perform_job(cls, send_receive_message_instance):
        """
        This method performs the job expected out from this class.
        :param send_receive_message_instance:
        :return:
        """
        cls.send_receive_message_instance = send_receive_message_instance
        t1 = threading.Thread(target=cls.thread_for_capturing_face)
        # starting thread 1
        t1.start()

    @classmethod
    def __load_model(cls):
        """
        This method loads the model and prototext and sets the target as Movidius NCS stick
        connected to Raspberry PI for the inference engine.
        :return:
        """
        prototxt_path = os.path.join(os.path.dirname(__file__), prototxt)
        model_path = os.path.join(os.path.dirname(__file__), model)
        cls.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
        if cls.__preferable_target == cv2.dnn.DNN_TARGET_MYRIAD:
            Logger.logger().info("Setting the inference engine to be Movidius NCS stick on Raspberry PI.")
            cls.net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
        else:
            Logger.logger().info("Setting the inference engine target to {}.".format(cls.__preferable_target))
            cls.net.setPreferableTarget(cls.__preferable_target)
    @classmethod
    def __start_video_capture(cls):
        """
        This method starts the video capture on video0.
        :return:
        """
        Logger.logger().info("starting video stream...")
        if cls.__input_video_file_path:
            Logger.logger().info("setting the video file path ={} as input to the video capture.".format(
                cls.__input_video_file_path))
            cls.vs = cv2.VideoCapture(cls.__input_video_file_path)
        else:
            Logger.logger().info("Setting video capture device to {}.".format(VIDEO_DEV_ID))
            cls.vs = cv2.VideoCapture(1)
        time.sleep(2.0)

    @classmethod
    def __load_centroid_tracker(cls):
        """
        This method instantiates centroid tracker class.
        :return:
        """
        cls.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)

    @classmethod
    def __populate_a_frame_and_blob(cls):
        """
        This method reads a video frame and populates a blob from the frame.
        It also populates the other frame parameters used later in other methods.
        :return:
        """
        if cls.__input_video_file_path:
            cls.frame = cls.vs.read()
        else:
            cls.ret, cls.frame = cls.vs.read()

        cls.frame = cv2.resize(cls.frame, (240, 240), interpolation=cv2.INTER_AREA)
        cls.rgb = cv2.cvtColor(cls.frame, cv2.COLOR_BGR2RGB)
        (cls.H, cls.W) = cls.frame.shape[:2]
        cls.blob = cv2.dnn.blobFromImage(cls.frame, 0.007843, (cls.W, cls.H), 127.5)

    @classmethod
    def __draw_a_line_to_differentiate_if_the_person_is_entering_or_exiting(cls):
        """
        This method draws a line on the frame to differentiate if a person is entering or exiting the door.
        :return:
        """
        cv2.line(cls.frame, (0, cls.H // 2), (cls.W, cls.H // 2), (0, 255, 255), 2)
        cv2.waitKey(1)

    @classmethod
    def __load_the_blob_into_caffe_model(cls):
        """
        This method loads the video frame blob into the caffe model and sets the detections to forward.
        :return:
        """
        cls.net.setInput(cls.blob)
        cls.detections = cls.net.forward()

    @classmethod
    def __populate_a_tracker_object_and_add_it_to_trackers_list(cls, current_index):
        """
        This method does the following:
        1. It uses the current index to fetch the box from the detections/
        2. It draws a rectangular frame from the box.
        3. It instantiates a correlation tracker instance.
        4. It uses the correlation tracker instance to start tracking.
        5. It updates tracker with the rgb values.
        6. It appends the tracker to a tracker list.
        :param current_index:
        :return:
        """
        box = cls.detections[0, 0, current_index, 3:7] * np.array([cls.W, cls.H, cls.W, cls.H])
        (startX, startY, endX, endY) = box.astype("int")
        cv2.rectangle(cls.frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        tracker = dlib.correlation_tracker()
        rect = dlib.rectangle(startX, startY, endX, endY)
        tracker.start_track(cls.rgb, rect)
        tracker.update(cls.rgb)
        cls.trackers.append(tracker)

    @classmethod
    def __is_person(cls, current_index):
        is_person = False
        confidence = cls.detections[0, 0, current_index, 2]
        if confidence > 0.5:
            idx = int(cls.detections[0, 0, current_index, 1])
            if CLASSES[idx] != "person":
                is_person = True
        return is_person

    @classmethod
    def __populate_tracker_position_tuple_into_rects_list(cls):
        """
        This method populates tracker position into rects list.
        :return:
        """
        cls.rects = []
        # loop over the trackers
        for tracker in cls.trackers:
            pos = tracker.get_position()
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())
            cls.rects.append((startX, startY, endX, endY))

    @classmethod
    def __update_time(cls, enter_exit_dict):
        """
        This method updats time and date into the passed in dictionary.
        :param enter_exit_dict: dict
        :return:
        """
        tz_ny = pytz.timezone('America/New_York')
        datetime_ny = datetime.now(tz_ny)
        curr_time = datetime_ny.strftime("%H:%M %p")
        date = datetime_ny.strftime("%m") + "/" + datetime_ny.strftime("%d") + "/" + datetime_ny.strftime("%y")
        enter_exit_dict["Time"].append(curr_time)
        enter_exit_dict["Date"].append(date)

    @classmethod
    def __populate_move_dict(cls, objects):
        """
        This method populates move_dict with objectId as the key and the list of centroids as the values.
        :param objects: dict
        :return: dict
        """
        move_dict = defaultdict(list)
        for (objectID, centroid) in objects.items():
            move_dict[objectID].append(centroid[1])
        return move_dict

    @classmethod
    def __populate_trackable_object_dict(cls, objects):
        """
        This method populates trackable object dict.
        It creates a trackable object instance when the objectID is not found in the dict.
        It appends to the centroids list when it found a trackable object for that object id.
        :param objects: dict
        :return: dict
        """
        trackable_object_dict = {}
        for (objectID, centroid) in objects.items():
            if objectID not in trackable_object_dict:
                trackable_object_dict[objectID] = TrackableObject(objectID, centroid)
            else:
                trackable_object_dict[objectID].centroids.append(centroid)
        return trackable_object_dict

    @classmethod
    def __perform_centroid_tracking(cls):
        # Pass in the list of rects of the 4 tuple values to the centroid tracker.
        objects = cls.ct.update(cls.rects)
        move_dict = cls.__populate_move_dict(objects)
        for keyName in move_dict:
            keyVals = move_dict[keyName]
            if "Counted" in keyVals:
                pass
            elif (keyVals[0] < cls.W // 2) and (keyVals[-1] > cls.W // 2):
                Logger.logger().info("Detected a human leave the boundary line. Decrementing the local face count.")
                cls.send_receive_message_instance.decrement_face_detected_locally()
                cls.__update_time(cls.enter_dict)
            elif (keyVals[0] > cls.W // 2) and (keyVals[-1] < cls.W // 2):
                Logger.logger().info("Detected a human cross the boundary line. Incrementing the local face count.")
                cls.send_receive_message_instance.increment_face_detected_locally()
                cls.__update_time(cls.exit_dict)
            move_dict[keyName].append("Counted")

        for (objectID, centroid) in objects.items():
            text = "ID {}".format(objectID)
            cv2.putText(cls.frame, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(cls.frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    @classmethod
    def thread_for_capturing_face(cls, input_video_file_path=None, preferable_target=cv2.dnn.DNN_TARGET_MYRIAD):
        if input_video_file_path:
            cls.__input_video_file_path = input_video_file_path
        cls.__preferable_target = preferable_target
        Logger.logger().debug("[INFO] Running thread_for_capturing_face...")
        cls.__load_model()
        Logger.logger().debug("1. Successfully loaded caffe model and set the preferred target.")
        cls.__start_video_capture()
        Logger.logger().debug("2. Successfully started video capture.")
        cls.__load_centroid_tracker()
        Logger.logger().debug("3. Successfully instantiated the centroid tracker.")

        while cls.run_program:
            cls.__populate_a_frame_and_blob()
            Logger.logger().debug("4. Successfully populated a video frame and blob.")
            cls.__load_the_blob_into_caffe_model()
            Logger.logger().debug("5. successfully loaded the blob into the caffe model and set the forward detections.")
            cls.rects = []

            Logger.logger().debug("6. Draw a line to differentiate if the person is entering or exiting.")
            cls.__draw_a_line_to_differentiate_if_the_person_is_entering_or_exiting()

            for current_index in np.arange(0, cls.detections.shape[2]):
                Logger.logger().debug("7. Going to perform human detection and populate tracker object.")
                if cls.__is_person(current_index):
                    Logger.logger().info("8. Found a person, successfully populated tracker object into tracker list.")
                    cls.__populate_a_tracker_object_and_add_it_to_trackers_list(current_index)
            if len(cls.trackers) == MAX_TRACKER_LIST_SIZE:
                Logger.logger().info("9. Going to populate tracker position tuple into rects list.")
                cls.__populate_tracker_position_tuple_into_rects_list()
                # Remember to clear the trackers list.
                cls.trackers = []
                Logger.logger().info("10. Perform centroid tracking.")
                cls.__perform_centroid_tracking()
            cv2.imshow("Frame", cls.frame)


if __name__ == '__main__':
    FaceTracker.perform_job(send_receive_message_instance=SendReceiveMessages())
