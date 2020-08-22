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
from constants import prototxt, model, CLASSES
import time
from send_receive_messages import SendReceiveMessages


class FaceTracker:
    """
    This class implements the logic to track a human face.
    """
    run_program = True

    net = None
    vs = None
    ct = None
    trackers = []
    trackable_objects = {}
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
    def perform_job(cls):
        t1 = threading.Thread(target=cls.thread_for_capturing_face)
        # starting thread 1
        t1.start()

    @classmethod
    def __load_model(cls):
        cls.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        cls.net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

    @classmethod
    def __start_video_capture(cls):
        print("[INFO] starting video stream...")
        cls.vs = cv2.VideoCapture(0)
        time.sleep(2.0)

    @classmethod
    def __load_centroid_tracker(cls):
        cls.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)

    @classmethod
    def __populate_a_frame_and_blob(cls):
        cls.ret, cls.frame = cls.vs.read()
        cls.frame = cv2.resize(cls.frame, (240, 240), interpolation=cv2.INTER_AREA)
        cls.rgb = cv2.cvtColor(cls.frame, cv2.COLOR_BGR2RGB)
        (cls.H, cls.W) = cls.frame.shape[:2]
        cls.blob = cv2.dnn.blobFromImage(cls.frame, 0.007843, (cls.W, cls.H), 127.5)

    @classmethod
    def __draw_a_line_to_differentiate_if_the_person_is_entering_or_exiting(cls):
        cv2.line(cls.frame, (0, cls.H // 2), (cls.W, cls.H // 2), (0, 255, 255), 2)
        cv2.imshow("Frame", cls.frame)
        cv2.waitKey(1)

    @classmethod
    def __load_the_blob_into_caffe_model(cls):
        cls.net.setInput(cls.blob)
        cls.detections = cls.net.forward()

    @classmethod
    def __populate_a_tracker_object_and_add_it_to_trackers_list(cls, current_index):
        box = cls.detections[0, 0, current_index, 3:7] * np.array([cls.W, cls.H, cls.W, cls.H])
        (startX, startY, endX, endY) = box.astype("int")
        cv2.rectangle(cls.frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        tracker = dlib.correlation_tracker()
        rect = dlib.rectangle(startX, startY, endX, endY)
        tracker.start_track(cls.rgb, rect)
        tracker.update(cls.rgb)
        cls.trackers.append(tracker)

    @classmethod
    def __detect_a_human(cls):
        cls.status = "Detecting"
        for current_index in np.arange(0, cls.detections.shape[2]):
            confidence = cls.detections[0, 0, current_index, 2]
            if confidence > 0.5:
                idx = int(cls.detections[0, 0, current_index, 1])
                if CLASSES[idx] != "person":
                    continue
                cls.__populate_a_tracker_object_and_add_it_to_trackers_list(current_index)

    @classmethod
    def __perform_tracking(cls):
        cls.status = "Tracking"
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
        tz_ny = pytz.timezone('America/New_York')
        datetime_ny = datetime.now(tz_ny)
        curr_time = datetime_ny.strftime("%H:%M %p")
        date = datetime_ny.strftime("%m") + "/" + datetime_ny.strftime("%d") + "/" + datetime_ny.strftime("%y")
        enter_exit_dict["Time"].append(curr_time)
        enter_exit_dict["Date"].append(date)

    @classmethod
    def __perform_centroid_tracking(cls):
        # Pass in the list of 10 items of the 4 tuple values to the centroid tracker.
        objects = cls.ct.update(cls.rects)
        move_dict = {}
        for (objectID, centroid) in objects.items():
            if objectID in move_dict:
                move_dict[objectID].append(centroid[1])
            else:
                move_dict[objectID] = [centroid[1]]
            # print("[MOVE DICTIONARY]: ", move_dict)
            to = cls.trackable_objects.get(objectID, None)
            if to is None:
                to = TrackableObject(objectID, centroid)
            else:
                to.centroids.append(centroid)
                if not to.counted:
                    for keyName in move_dict:
                        keyVals = move_dict[keyName]
                        if "Counted" in keyVals:
                            pass
                        elif (keyVals[0] < cls.W // 2) and (keyVals[-1] > cls.W // 2):
                            cls.totalUp += 1
                            cls.totalPeople += 1
                            SendReceiveMessages.decrement_face_detected_locally()
                            cls.__update_time(cls.enter_dict)
                        elif (keyVals[0] > cls.W // 2) and (keyVals[-1] < cls.W // 2):
                            cls.totalPeople -= 1
                            cls.totalDown += 1
                            SendReceiveMessages.increment_face_detected_locally()
                            cls.__update_time(cls.exit_dict)

                        # FINISH CODE BEFORE THIS
                        values = move_dict[keyName]
                        values.append("Counted")
                        move_dict[keyName] = values
                        to.counted = True

            cls.trackable_objects[objectID] = to
            text = "ID {}".format(objectID)
            cv2.putText(cls.frame, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(cls.frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    @classmethod
    def thread_for_capturing_face(cls):
        print("[INFO] Running thread_for_capturing_face...")
        cls.__load_model()
        cls.__start_video_capture()
        cls.__load_centroid_tracker()

        while cls.run_program:
            cls.__populate_a_frame_and_blob()
            cls.__load_the_blob_into_caffe_model()
            status = "Waiting"
            cls.rects = []
            if cls.totalFrames % 10 == 0:
                cls.__detect_a_human()
            else:
                cls.__perform_tracking()
                cls.trackers = []
                cls.__perform_centroid_tracking()
                cls.__draw_a_line_to_differentiate_if_the_person_is_entering_or_exiting()
            cls.totalFrames += 1
