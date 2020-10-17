# Import necessary packages
import threading
import time

import cv2
from detect import detect
from play_audioMask import PlayAudio
from tensorflow.keras.models import load_model
from vars import prototxt_path, face_model_path, mask_model_path, min_mask_confidence

# Load all the models, and start the camera stream
faceModel = cv2.dnn.readNet(prototxt_path, face_model_path)
# faceModel.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
maskModel = load_model(mask_model_path)
stream = cv2.VideoCapture(0)

AudioPlay = False
playAudio = False


def thread_for_when_to_play_audio():
    """
    This function is used for playing the alarm if a person is not wearing a mask.
    :return:
    """
    global playAudio
    while True:
        if playAudio:
            play_audio()


def play_audio():
    """
    This function is used for playing the alarm if a person is not wearing a mask.
    :return:
    """
    global AudioPlay
    global playAudio
    SoundThread = threading.Thread(target=PlayAudio.play_audio_file)
    print("[INFO]: Starting Sound Thread")
    if not AudioPlay:
        AudioPlay = True
        SoundThread.start()
        time.sleep(3)
        AudioPlay = False
        playAudio = False
        print("[INFO]: Stopping Sound Thread")


def thread_for_mask_detection():
    global faceModel
    global maskModel
    global stream
    global playAudio
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
                    playAudio = True
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


if __name__ == "__main__":
    t1 = threading.Thread(target=thread_for_when_to_play_audio)

    t1.start()

    thread_for_mask_detection()
