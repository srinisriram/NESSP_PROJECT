from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os
import threading
import simpleaudio as sa

camIndex = 1
minConfidence = 0.97

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--detector", type=str, default="face_detection_model",
                help="path to OpenCV's deep learning face detector")
ap.add_argument("-m", "--embedding-model", type=str, default="face_embedding_model/openface_nn4.small2.v1.t7",
                help="path to OpenCV's deep learning face embedding model")
ap.add_argument("-r", "--recognizer", type=str, default="recognizer.pickle",
                help="path to model trained to recognize faces")
ap.add_argument("-l", "--le", type=str, default="labels.pickle",
                help="path to label encoder")
ap.add_argument("-c", "--confidence", type=float, default=0.6,
                help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized face detector from disk
print("[INFO] loading face detector...")
protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"])
modelPath = os.path.sep.join([args["detector"],
                              "res10_300x300_ssd_iter_140000.caffemodel"])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
detector.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

# load our serialized face embedding model from disk and set the
# preferable target to MYRIAD
print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch(args["embedding_model"])
embedder.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

# load the actual face recognition model along with the label encoder
recognizer = pickle.loads(open(args["recognizer"], "rb").read())
le = pickle.loads(open(args["le"], "rb").read())

print("[INFO] starting video stream...")
vs = VideoStream(src=camIndex).start()
time.sleep(2.0)

filename1 = 'speech1.wav'
wave_obj1 = sa.WaveObject.from_wave_file(filename1)

human_detected = False
playSound = False
fail_safe = []

mask_play = False

totalFrames = 0


def thread_for_maskDetection():
    global human_detected
    global play_obj
    global play_obj1
    global vs
    global mask_play
    global totalFrames
    global playSound
    while True:
        # grab the frame from the threaded video stream
        frame = vs.read()
        frame = imutils.resize(frame, width=320)
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # frame = gamma(frame, gamma=0.5)

        # resize the frame to have a width of 600 pixels (while
        # maintaining the aspect ratio), and then grab the image
        # dimensions
        # frame = imutils.resize(frame, width=600)
        (h, w) = frame.shape[:2]

        # construct a blob from the image
        imageBlob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)

        # apply OpenCV's deep learning-based face detector to localize
        # faces in the input image
        detector.setInput(imageBlob)
        detections = detector.forward()

        # print("Human_Detected: {}".format(human_detected))
        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]
            # print(confidence)
            # filter out weak detections
            if confidence > args["confidence"]:
                # compute the (x, y)-coordinates of the bounding box for
                # the face
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # extract the face ROI
                face = frame[startY:endY, startX:endX]
                (fH, fW) = face.shape[:2]

                # ensure the face width and height are sufficiently large
                if fW < 20 or fH < 20:
                    continue

                # construct a blob for the face ROI, then pass the blob
                # through our face embedding model to obtain the 128-d
                # quantification of the face
                faceBlob = cv2.dnn.blobFromImage(cv2.resize(face,
                                                            (96, 96)), 1.0 / 255, (96, 96), (0, 0, 0),
                                                 swapRB=True, crop=False)
                embedder.setInput(faceBlob)
                vec = embedder.forward()

                # perform classification to recognize the face
                preds = recognizer.predict_proba(vec)[0]
                j = np.argmax(preds)
                proba = preds[j]
                name = le.classes_[j]
                print("Proba: ", proba)
                if proba > minConfidence and name == "without_mask":
                    playSound = True

                COLORS = [(0, 0, 255), (0, 255, 0)]
                # draw the bounding box of the face along with the
                # associated probability
                text = "{}: {:.2f}%".format(name, proba * 100)
                y = startY - 10 if startY - 10 > 10 else startY + 10
                n = 0
                if name == "with_mask":
                    n = 1
                cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[n], 2)
                cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLORS[n], 2)

        totalFrames += 1
        cv2.imshow("Mask Detection", frame)
        cv2.waitKey(1)


def thread_for_playing_sound():
    global playSound
    while True:
        if playSound:
            play_obj1 = wave_obj1.play()
            play_obj1.wait_done()
            playSound = False
        else:
            pass


if __name__ == "__main__":
    t1 = threading.Thread(target=thread_for_maskDetection)
    t2 = threading.Thread(target=thread_for_playing_sound)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
