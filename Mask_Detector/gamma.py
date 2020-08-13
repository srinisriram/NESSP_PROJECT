import glob
import numpy as np
import cv2
import os

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

files = []
ImagesPath = "/Users/srinivassriram/Desktop/train-face-recognition/abhi/without_mask/*.jpg"
for file in glob.glob(ImagesPath):
    files.append(str(file))

k = 0
i = 0

while i < len(files):
    frame = cv2.imread(files[k])
    frame = cv2.resize(frame, (640, 480))
    frame = adjust_gamma(frame, gamma=3)

    cv2.waitKey(1)
    print(files[k])

    cv2.imwrite("GammaPic1.5"+str(k)+".jpg", frame)
    print("saving")
    k = k + 1
    i = i + 1


os.system("mv *.jpg gamma/without_mask")
