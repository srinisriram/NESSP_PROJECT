# USAGE
# python recognize_video.py --detector face_detection_model \
#	--embedding-model face_embedding_model/openface_nn4.small2.v1.t7 \
#	--recognizer output/recognizer.pickle \
#	--le output/le.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os
import threading
import simpleaudio as sa

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
		# build a lookup table mapping the pixel values [0, 255] to
		# their adjusted gamma values
		invGamma = 1.0 / gamma
		table = np.array([((i / 255.0) ** invGamma) * 255
				for i in np.arange(0, 256)]).astype("uint8")
		# apply gamma correction using the lookup table
		return cv2.LUT(image, table)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--detector", required=True,
	help="path to OpenCV's deep learning face detector")
ap.add_argument("-m", "--embedding-model", required=True,
	help="path to OpenCV's deep learning face embedding model")
ap.add_argument("-r", "--recognizer", required=True,
	help="path to model trained to recognize faces")
ap.add_argument("-l", "--le", required=True,
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

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                   "sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

net = cv2.dnn.readNetFromCaffe(prototxt="models/MobileNetSSD_deploy.prototxt.txt", caffeModel="models/MobileNetSSD_deploy.caffemodel")
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

filename = 'mask.wav'
wave_obj = sa.WaveObject.from_wave_file(filename)

filename = 'look.wav'
wave_obj1 = sa.WaveObject.from_wave_file(filename)
arr = []

noMask = False
humanPresent = False

fail_safe = []

# start the FPS throughput estimator
fps = FPS().start()

def thread_for_detecting_humans():
	global CLASSES
	global COLORS
	global net
	global vs
	global humanPresent
	while True:
		frame = vs.read()

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
					humanPresent = True
				else:
					humanPresent = False
		print(humanPresent)
		cv2.imshow("Human Detection", frame)
		cv2.waitKey(1)

# loop over frames from the video file stream
def thread_for_maskDetection():
	global noMask
	while True:
		# grab the frame from the threaded video stream
		frame = vs.read()
		frame = gamma(frame, gamma=1)

		# resize the frame to have a width of 600 pixels (while
		# maintaining the aspect ratio), and then grab the image
		# dimensions
		frame = imutils.resize(frame, width=600)
		(h, w) = frame.shape[:2]

		# construct a blob from the image
		imageBlob = cv2.dnn.blobFromImage(
			cv2.resize(frame, (300, 300)), 1.0, (300, 300),
			(104.0, 177.0, 123.0), swapRB=False, crop=False)

		# apply OpenCV's deep learning-based face detector to localize
		# faces in the input image
		detector.setInput(imageBlob)
		detections = detector.forward()

		# loop over the detections
		for i in range(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with
			# the prediction
			confidence = detections[0, 0, i, 2]

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
				fail_safe.append(name)

				if len(fail_safe) == 5:
					most_freq = most_frequent(fail_safe)
					if most_freq == "with_mask":
							print("Your good to go!")
							noMask = False
							fail_safe.clear()
					elif most_freq == "without_mask":
							print("Please wear a mask to enter")
							noMask = True
							fail_safe.clear()

				COLORS = [(0, 0, 255), (0, 255, 0)]
				# draw the bounding box of the face along with the
				# associated probability
				text = "{}: {:.2f}%".format(name, proba * 100)
				y = startY - 10 if startY - 10 > 10 else startY + 10
				n = 0
				if name == "with_mask":
						n = 1
				cv2.rectangle(frame, (startX, startY), (endX, endY),
									COLORS[n], 2)
				cv2.putText(frame, text, (startX, y),
						cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLORS[n], 2)

		# update the FPS counter
		fps.update()
		cv2.imshow("Mask Detection", frame)
		cv2.waitKey(1)

def thread_for_playing_sound():
	print("[INFO]: Running thread for playing sound.")
	global humanPresent
	global noMask
	while True:
		#print(humanPresent)
		#print(noMask)
		if humanPresent:
			if noMask:
				play_obj = wave_obj.play()
				play_obj.wait_done()
			else:
				play_obj = wave_obj1.play()
				play_obj.wait_done()
			play_obj = wave_obj1.play()
			play_obj.wait_done()
		
		
if __name__ == "__main__":
	# initialize the video stream, then allow the camera sensor to warm up
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	# vs = VideoStream(usePiCamera=True).start()
	time.sleep(2.0)
	
	t1 = threading.Thread(target=thread_for_maskDetection)
	t2 = threading.Thread(target=thread_for_detecting_humans)
	t3 = threading.Thread(target=thread_for_playing_sound)
	
	t1.start()
	t2.start()
	t3.start()
