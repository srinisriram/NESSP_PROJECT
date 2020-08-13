import time
import cv2
import imutils
import numpy as np
import math
import simpleaudio as sa

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
		   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
		   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
		   "sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

net = cv2.dnn.readNetFromCaffe(prototxt="models/MobileNetSSD_deploy.prototxt.txt", caffeModel="models/MobileNetSSD_deploy.caffemodel")
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)


vs = cv2.VideoCapture(0)
def thread_for_detecting_humans():
	global CLASSES
	global COLORS
	global net
	global vs
	while True:
		ret, frame = vs.read()

		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

		net.setInput(blob)
		detections = net.forward()

		for i in np.arange(0, detections.shape[2]):
			confidence = detections[0, 0, i, 2]

			if confidence > 0.5:
				idx = int(detections[0, 0, i, 1])
				label = round(idx)

				if label == 15:
					print("Human Detected")

		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF



if __name__ == "__main__":
	thread_for_detecting_humans()
