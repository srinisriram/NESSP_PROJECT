# Import necessary packages
import os

import cv2
from detect import detect
from tensorflow.keras.models import load_model
from vars import prototxt_path, face_model_path, mask_model_path, video_cam_index, label, min_mask_confidence
from play_audioMask import PlayAudio

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# Load all the models, and start the camera stream
faceModel = cv2.dnn.readNet(prototxt_path, face_model_path)
# faceModel.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
maskModel = load_model(mask_model_path)

stream = cv2.VideoCapture(video_cam_index)

while True:
    # Read frame from the stream
    ret, frame = stream.read()

    # Run the detect function on the frame
    (locations, predictions) = detect(frame, faceModel, maskModel)

    # Go through each face detection.
    for (box, pred) in zip(locations, predictions):
        # Extract the prediction and bounding box coords
        (startX, startY, endX, endY) = box
        (mask, withoutMask) = pred

        # Determine the class label and make actions accordingly
        if mask > withoutMask:
            confidence = round(mask)
            confidence *= 100
            if confidence > min_mask_confidence:
                label = 'Mask ' + str(confidence)
                color = (0, 255, 0)
        else:
            confidence = round(withoutMask)
            confidence *= 100
            if confidence > min_mask_confidence:
                label = 'No Mask ' + str(confidence)
                PlayAudio.play_audio_file()
                color = (0, 0, 255)

        # Place label and Bounding Box
        cv2.putText(frame, label, (startX, startY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

    # show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # break from loop if key pressed is q
    if key == ord("q"):
        break

# Cleanup
stream.release()
cv2.destroyAllWindows()
