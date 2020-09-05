import os
import pickle
import threading
import time

import cv2
import imutils
import numpy as np
from Mask_Detector.play_audioMask import PlayAudio
from Mask_Detector.constants import prototxt_path, model_path, embedder_path, recognizer_path, labels_path, COLORS, \
    LABELS, frame_width_in_pixels, MIN_CONFIDENCE, OPEN_DISPLAY, USE_VIDEO, MIN_CONFIDENCE_MASK
from imutils.video import VideoStream


class MaskDetector:
    run_program = True
    input_video_file_path = None
    preferable_target = cv2.dnn.DNN_TARGET_CPU

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
        self.AudioPlay = False
        self.debug = False

        self.load_caffe_model()
        self.load_pytorch_model()
        self.load_pickle_recognizer()

        self.initialize_camera()

    @classmethod
    def perform_job(cls, preferableTarget=cv2.dnn.DNN_TARGET_CPU):
        """
        This method performs the job expected from this class.
        :key
        """
        # Set preferable target.
        MaskDetector.preferable_target = preferableTarget
        # Set input video file path (if applicable)
        MaskDetector.input_video_file_path = MaskDetector.input_video_file_path
        # Create a thread that uses the thread_for_mask_detection function and start it.
        t1 = threading.Thread(target=MaskDetector().thread_for_mask_detection)
        t1.start()

    def load_caffe_model(self):
        """
        This function will load the caffe model that we will use for detecting a face, and then set the preferable target to the correct target.
        :key

        """
        print("Loading caffe model used for detecting a face.")

        # Use cv2.dnn function to read the caffe model used for detecting faces and set preferable target.
        self.detector = cv2.dnn.readNetFromCaffe(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            prototxt_path),
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                model_path))

        self.detector.setPreferableTarget(MaskDetector.preferable_target)

    def load_pytorch_model(self):
        """
        This function will load the pytorch model that is used for extracting the facial embeddings, and then we set the correct preferable target.

        :key
        """
        print("Loading pytorch embedding model used for extracting the facial embeddings.")

        # Load pytorch model used for extracting embeddings and set preferable target.
        self.embedder = cv2.dnn.readNetFromTorch(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            embedder_path))

        self.embedder.setPreferableTarget(MaskDetector.preferable_target)

    def load_pickle_recognizer(self):
        """
        This function will load our 2 pickle files. One file contains our SVM Machine trained in scikit-learn to classify the embeddings (recognizer.pickle).
        Another file contains the Label Encoder that will encode the output that our SVM model provides as a label, with or without mask.

        :key
        """
        print("Loading pickle files that are used to determine the class of the embeddings.")

        # Load pickle files.
        self.recognizer = pickle.loads(open(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            recognizer_path), "rb").read())

        self.le = pickle.loads(open(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            labels_path), "rb").read())

    def initialize_camera(self):
        """
        This function will initialize the camera or video stream by figuring out whether to stream the camera capture or from a video file.
        :key
        """
        if MaskDetector.input_video_file_path is None:
            print("[INFO] starting video stream...")
            self.vs = VideoStream(src=0).start()
            time.sleep(2.0)
        else:
            self.vs = cv2.VideoCapture(MaskDetector.input_video_file_path)

    def grab_next_frame(self):
        """
        This function extracts the next frame from the video stream.

        :return:
        """
        if MaskDetector.input_video_file_path is None:
            self.frame = self.vs.read()
        else:
            _, self.frame = self.vs.read()
            # self.frame = cv2.rotate(self.frame, cv2.ROTATE_180)

        if self.frame is None:
            return
        self.frame = imutils.resize(self.frame, width=frame_width_in_pixels)

    def set_dimensions_for_frame(self):
        """
        This function will set the frame dimensions, which we will use later on.
        :key
        """
        if not self.h or not self.w:
            #Set frame dimensions.
            (self.h, self.w) = self.frame.shape[:2]

    def create_frame_blob(self):
        """
        This function will create a blob for our face detector to detect a face.
        :key
        """
        self.image_blob = cv2.dnn.blobFromImage(
            cv2.resize(self.frame, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)

    def extract_face_detections(self):
        """
        This function will extract each face detection that our face detection model provides.
        :return:
        """
        self.detector.setInput(self.image_blob)
        self.detections = self.detector.forward()

    def extract_confidence_from_face_detections(self, i):
        """
        This function will extract the confidence(probability) of the face detection so that we can filter out weak detections.
        :param i:
        :return:
        """

        self.confidence = self.detections[0, 0, i, 2]

    def create_face_box(self, i):
        """
        This function will define coordinates of the face.
        :param i:
        :return:
        """
        self.box = self.detections[0, 0, i, 3:7] * np.array([self.w, self.h, self.w, self.h])
        (self.startX, self.startY, self.endX, self.endY) = self.box.astype("int")

    def extract_face_roi(self):
        """
        This function will use the coordinates defined earlier and create a ROI that we will use for embeddings.
        :return:
        """
        self.face = self.frame[self.startY:self.endY, self.startX:self.endX]
        (self.f_h, self.f_w) = self.face.shape[:2]

    def create_embeddings_blob(self):
        """
        This function will create another blob out of the face ROI that we will use for extracting the embeddings.
        :return:
        """
        self.face_blob = cv2.dnn.blobFromImage(cv2.resize(self.face,
                                                          (96, 96)), 1.0 / 255, (96, 96), (0, 0, 0),
                                               swapRB=True, crop=False)

    def extract_embeddings_detections(self):
        """
        This function extracts the embeddings from the face detections.
        :return:
        """
        self.embedder.setInput(self.face_blob)
        self.vec = self.embedder.forward()

    def perform_classification(self):
        """
        This function will now use the pickle files to do the following:
            1. Extract the class prediction of the embeddings.
            2. Get the probability of the prediction.
            3. Get the label of the prediction.

        :return:
        """
        self.predictions = self.recognizer.predict_proba(self.vec)[0]
        self.j = np.argmax(self.predictions)
        self.probability = self.predictions[self.j]
        self.name = self.le.classes_[self.j]

    def create_frame_icons(self):
        """
        This function will create the icons that will be displayed on the frame.

        :return:
        """
        self.text = "{}: {:.2f}%".format(self.name, self.probability * 100)
        self.y = self.startY - 10 if self.startY - 10 > 10 else self.startY + 10
        self.colorIndex = LABELS.index(self.name)

    def play_audio(self):
        """
        This function is used for playing the alarm if a person is not wearing a mask.
        :return:
        """
        SoundThread = threading.Thread(target=PlayAudio.play_audio_file)
        print("[INFO]: Starting Sound Thread")
        if not self.AudioPlay:
            self.AudioPlay = True
            SoundThread.start()
            time.sleep(3)
            self.AudioPlay = False
            print("[INFO]: Stopping Sound Thread")

    def loop_over_frames(self):
        """
        This is the main function that will loop through the frames and use the functions defined above to detect for face mask.
        :return:
        """
        while MaskDetector.run_program:
            self.grab_next_frame()
            self.set_dimensions_for_frame()
            self.create_frame_blob()
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
                    if self.debug:
                        print("Label {} + Probability = {}".format(self.name, self.probability))
                        print("Confidence of face detection", self.confidence)
                    if self.name == "without_mask" and self.probability >= MIN_CONFIDENCE_MASK:
                        print("Person is not wearing a mask.")
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
        """
        Clean up the cv2 video capture.
        :return:
        """
        cv2.destroyAllWindows()
        self.vs.release()

    def thread_for_mask_detection(self):
        """
        Callable function that will run the mask detector and can be invoked in a thread.
        :return:
        """
        while MaskDetector.run_program:
            try:
                self.loop_over_frames()
            except ValueError:
                self.clean_up()
                time.sleep(10)
        self.clean_up()


if __name__ == "__main__":
    Mask_Detector = MaskDetector()
    Mask_Detector.thread_for_mask_detection()
