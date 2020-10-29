# Import necessary packages
import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array


def detect(img, faceModel, maskModel):
    # Generate a blob
    (h, w) = img.shape[:2]
    blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300),
                                 (104.0, 177.0, 123.0))

    # Set up the face detector and pass the blob through the face detector
    faceModel.setInput(blob)
    detections = faceModel.forward()

    # Create empty lists, num_of_faces, locations, and predictions
    num_of_faces = []
    locations = []
    predictions = []

    # Go through each detection
    for x in range(0, detections.shape[2]):
        # extract the confidence from each detection
        conf = detections[0, 0, x, 2]

        if conf > 0.4:
            # Compute the bounding box coords if the confidence of the face detection is greater than 0.5
            box = detections[0, 0, x, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Make sure that the coords do not exceed maximum frame capacity
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            # Extract the face, and preprocess it so that the mask_model can make inferences
            face = img[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)

            # Add the face to the number of faces list defined above, and add the coordinates of the face to the locations list defined above.
            num_of_faces.append(face)
            locations.append((startX, startY, endX, endY))

    # Check if at least one face was detected
    if len(num_of_faces) > 0:
        # Use the model to predict on the whole batch of faces that are there.
        faces = np.array(num_of_faces, dtype="float32")
        predictions = maskModel.predict(faces, batch_size=32)

    # Return the locations and predictions as a tuple to the main function.
    return locations, predictions
