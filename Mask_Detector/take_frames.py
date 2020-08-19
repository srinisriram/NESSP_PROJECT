import cv2
import time


vs = cv2.VideoCapture(0)

i=0

time.sleep(5)
while i < 200:
	ret, frame = vs.read()

	img = frame
	cv2.imshow("img",img)

	cv2.imwrite('WithMaskPics'+str(i)+'.jpg',img)
	i+=1
