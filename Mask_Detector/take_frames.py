import cv2
import time


vs = cv2.VideoCapture(0)

i=0

time.sleep(5)
while i < 100:
	ret, frame = vs.read()

	img = frame
	cv2.imshow("img",img)
	cv2.waitKey(1)

	cv2.imwrite('WithMask1Pics'+str(i)+'.jpg',img)
	i+=1
