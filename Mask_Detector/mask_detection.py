from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os
#import simpleaudio as sa
import threading

def most_frequent(List):
		counter = 0
		num = List[0]
		for i in List:
				curr_frequency = List.count(i)
				if (curr_frequency > counter):
						counter = curr_frequency
						num = i
		return num


def gamma(image, gamma=1.0):
		invGamma = 1.0 / gamma
		table = np.array([((i / 255.0) ** invGamma) * 255
				for i in np.arange(0, 256)]).astype("uint8")
		return cv2.LUT(image, table)

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--detector", type=str,default = "face_detection_model",
	help="path to OpenCV's deep learning face detector")
ap.add_argument("-m", "--embedding-model", type=str, default="face_embedding_model/openface_nn4.small2.v1.t7",
	help="path to OpenCV's deep learning face embedding model")
ap.add_argument("-r", "--recognizer", type=str, default="recognizer.pickle",
	help="path to model trained to recognize faces")
ap.add_argument("-l", "--le", type=str,default="labels.pickle",
	help="path to label encoder")
ap.add_argument("-c", "--confidence", type=float, default=0.6,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

print("[INFO] Loading Models...")
protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"])
modelPath = os.path.sep.join([args["detector"],
	"res10_300x300_ssd_iter_140000.caffemodel"])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
detector.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

embedder = cv2.dnn.readNetFromTorch(args["embedding_model"])
embedder.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

recognizer = pickle.loads(open(args["recognizer"], "rb").read())
le = pickle.loads(open(args["le"], "rb").read())

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

filename = 'mask.wav'
#wave_obj = sa.WaveObject.from_wave_file(filename)
arr = []

fail_safe = []
no_mask = False
with_mask = False
def thread_for_maskDetection():
	global detector
	global embedder
	global recognizer
	global le
	global vs
	global no_mask
	global with_mask
	while True:
		frame = vs.read()
		frame = gamma(frame, gamma=1)

		frame = imutils.resize(frame, width=600)
		(h, w) = frame.shape[:2]

		imageBlob = cv2.dnn.blobFromImage(
			cv2.resize(frame, (300, 300)), 1.0, (300, 300),
			(104.0, 177.0, 123.0), swapRB=False, crop=False)

		detector.setInput(imageBlob)
		detections = detector.forward()

		for i in range(0, detections.shape[2]):
			confidence = detections[0, 0, i, 2]

			if confidence > args["confidence"]:
				#face_detected = True
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")

				face = frame[startY:endY, startX:endX]
				(fH, fW) = face.shape[:2]

				if fW < 20 or fH < 20:
					continue

				faceBlob = cv2.dnn.blobFromImage(cv2.resize(face,
					(96, 96)), 1.0 / 255, (96, 96), (0, 0, 0),
					swapRB=True, crop=False)
				embedder.setInput(faceBlob)
				vec = embedder.forward()

				preds = recognizer.predict_proba(vec)[0]
				j = np.argmax(preds)
				proba = preds[j]
				name = le.classes_[j]
				fail_safe.append(name)

				if len(fail_safe) == 5:
					most_freq = most_frequent(fail_safe)
					print(most_freq)
					if most_freq == "with_mask":
						with_mask = True
						no_mask = False
						fail_safe.clear()
					elif most_freq == "without_mask":
						no_mask = True
						with_mask = False
						fail_safe.clear()
					elif most_freq == "":
						no_mask = False
						with_mask = False

			#elif confidence < args["confidence"]:
				#face_detected = False
			print("{}, {}".format(no_mask, with_mask))

		cv2.imshow("Mask Detection", frame)
		key = cv2.waitKey(1) & 0xFF


CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                   "sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

net = cv2.dnn.readNetFromCaffe(prototxt="models/MobileNetSSD_deploy.prototxt.txt", caffeModel="models/MobileNetSSD_deploy.caffemodel")
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

human_detected = False

def thread_for_detecting_humans():
        global CLASSES
        global COLORS
        global net
        global vs
        global human_detected
        while True:
                frame = vs.read()

                (h, w) = frame.shape[:2]
                blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

                net.setInput(blob)
                detections = net.forward()

                for i in np.arange(0, detections.shape[2]):
                        confidence = detections[0, 0, i, 2]

                        if confidence > 0.7:
                                idx = int(detections[0, 0, i, 1])
                                label = round(idx)

                                if label == 15:
                                        human_detected = True
                                else:
                                        human_detected = False
                cv2.imshow("Human Detection", frame)
                key = cv2.waitKey(1) & 0xFF




def thread_for_playing_sound():
	while True:
		global no_mask
		global human_detected
		global face_detected

		"""
		if human_detected == True and face_detected == False:
			print("Please look up for mask detection")
		if human_detected == True and face_detected == True and no_mask == True:
			print("Please wear a mask to enter")
		if human_detected == True and face_detected == True and no_mask == False:
			print("Your good to go!")
		"""


if __name__ == "__main__":
	t1 = threading.Thread(target=thread_for_maskDetection)
	t2 = threading.Thread(target=thread_for_detecting_humans)
	t3 = threading.Thread(target=thread_for_playing_sound)

	t1.start()
	t2.start()
	t3.start()

	t1.join()
	t2.join()
	t3.join()


