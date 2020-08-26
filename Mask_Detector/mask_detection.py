import os
import pickle
import threading
import time

import cv2
import imutils
import numpy as np
from play_audioMask import PlayAudio
from constants import prototxt_path, model_path, embedder_path, recognizer_path, labels_path, COLORS, \
    LABELS, frame_width_in_pixels, MIN_CONFIDENCE, OPEN_DISPLAY
from imutils.video import VideoStream


class MaskDetector:
    run_program = True
    input_video_file_path = None
    preferable_target = None

    def __init__(self):
        self.frame = None
        self.h = None
        self.w = None
        self.vs = None
        self.image_blob = None
        self.confidence = None
        self.detections = None
        self.box = None
        self.face = None
        self.f_h = None
        self.f_w = None
        self.startX = None
        self.startY = None
        self.endX = None
        self.endY = None
        self.face_blob = None
        self.vec = None
        self.predictions = None
        self.probability = None
        self.name = None
        self.text = None
        self.y = None
        self.colorIndex = None
        self.detector = None
        self.embedder = None
        self.recognizer = None
        self.le = None
        self.box = None
        self.j = None

        self.load_caffe_model()
        self.load_pytorch_model()
        self.load_pickle_recognizer()

        self.initialize_camera()

    @classmethod
    def perform_job(cls, preferableTarget=cv2.dnn.DNN_TARGET_MYRIAD):
        MaskDetector.preferable_target = preferableTarget
        t1 = threading.Thread(target=MaskDetector().thread_for_mask_detection)
        t1.start()

    def load_caffe_model(self):
        print("Loading caffe model used for detecting a face.")
        self.detector = cv2.dnn.readNetFromCaffe(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            prototxt_path),
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                model_path))

        self.detector.setPreferableTarget(MaskDetector.preferable_target)

    def load_pytorch_model(self):
        print("Loading pytorch embedding model used for extracting the facial embeddings.")
        self.embedder = cv2.dnn.readNetFromTorch(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            embedder_path))

        self.embedder.setPreferableTarget(MaskDetector.preferable_target)

    def load_pickle_recognizer(self):
        print("Loading pickle files that are used to determine the class of the embeddings.")

        self.recognizer = pickle.loads(open(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            recognizer_path), "rb").read())

        self.le = pickle.loads(open(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            labels_path), "rb").read())

    def initialize_camera(self):
        print("Starting video stream.")

        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)

    def grab_next_frame(self):
        self.frame = self.vs.read()

        if self.frame is None:
            return

        self.frame = cv2.rotate(self.frame, cv2.ROTATE_180)
        self.frame = imutils.resize(self.frame, width=frame_width_in_pixels)

    def set_dimensions_for_face_blob(self):
        if not self.h or not self.w:
            (self.h, self.w) = self.frame.shape[:2]

    def create_face_blob(self):
        self.image_blob = cv2.dnn.blobFromImage(
            cv2.resize(self.frame, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)

    def extract_face_detections(self):
        self.detector.setInput(self.image_blob)
        self.detections = self.detector.forward()

    def extract_confidence_from_face_detections(self, i):
        self.confidence = self.detections[0, 0, i, 2]

    def create_face_box(self, i):
        self.box = self.detections[0, 0, i, 3:7] * np.array([self.w, self.h, self.w, self.h])
        (self.startX, self.startY, self.endX, self.endY) = self.box.astype("int")

    def extract_face_roi(self):
        self.face = self.frame[self.startY:self.endY, self.startX:self.endX]
        (self.f_h, self.f_w) = self.face.shape[:2]

    def create_embeddings_blob(self):
        self.face_blob = cv2.dnn.blobFromImage(cv2.resize(self.face,
                                                          (96, 96)), 1.0 / 255, (96, 96), (0, 0, 0),
                                               swapRB=True, crop=False)

    def extract_embeddings_detections(self):
        self.embedder.setInput(self.face_blob)
        self.vec = self.embedder.forward()

    def perform_classification(self):
        self.predictions = self.recognizer.predict_proba(self.vec)[0]
        self.j = np.argmax(self.predictions)
        self.probability = self.predictions[self.j]
        self.name = self.le.classes_[self.j]

    def create_frame_icons(self):
        """

        :return:
        """
        self.text = "{}: {:.2f}%".format(self.name, self.probability * 100)
        self.y = self.startY - 10 if self.startY - 10 > 10 else self.startY + 10
        self.colorIndex = LABELS.index(self.name)

    def play_audio(self):
        PlayAudio.play_audio_file()


    def loop_over_frames(self):
        while MaskDetector.run_program:
            self.grab_next_frame()
            self.set_dimensions_for_face_blob()
            self.create_face_blob()
            self.extract_face_detections()

            for i in range(0, self.detections.shape[2]):
                self.extract_confidence_from_face_detections(i)
                if self.confidence > MIN_CONFIDENCE:
                    self.create_face_box(i)
                    self.extract_face_roi()
                    if self.f_w < 20 or self.f_h < 20:
                        continue
                    self.create_embeddings_blob()
                    self.extract_embeddings_detections()
                    self.perform_classification()
                    if self.name == "without_mask" and self.probability > 0.99:
                        self.play_audio()
                    self.create_frame_icons()
                    cv2.rectangle(self.frame, (self.startX, self.startY), (self.endX, self.endY),
                                  COLORS[self.colorIndex], 2)
                    cv2.putText(self.frame, self.text, (self.startX, self.y), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                                COLORS[self.colorIndex], 2)

            if OPEN_DISPLAY:
                cv2.imshow("mask_detector_frame", self.frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    break

    def clean_up(self):
        cv2.destroyAllWindows()
        self.vs.release()

    def thread_for_mask_detection(self):
        while MaskDetector.run_program:
            try:
                self.loop_over_frames()
            except ValueError:
                self.clean_up()
                time.sleep(10)
        self.clean_up()


if __name__ == "__main__":
    MaskDetector.perform_job(preferableTarget=cv2.dnn.DNN_TARGET_MYRIAD)
