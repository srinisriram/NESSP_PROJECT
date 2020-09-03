from Occupancy_Tracker.constants import SEND_EMAIL, ENTER_LOG_FILE_NAME, EXIT_LOG_FILE_NAME, Direction
import cv2
import os
from threading import Thread
from pathlib import Path
from imutils.io import TempFile
from Occupancy_Tracker.email_sender import EmailSender
from datetime import datetime
from Occupancy_Tracker.logger import Logger
from Occupancy_Tracker.send_receive_messages import SendReceiveMessages


class HumanValidator:
    enter_log_file = None
    exit_log_file = None

    @classmethod
    def close_log_file(cls):
        # check if the log file object exists, if it does, then close it
        if not cls.enter_log_file:
            cls.enter_log_file.close()

        if not cls.exit_log_file:
            cls.exit_log_file.close()

    @classmethod
    def initialize_log_file(cls):
        if not cls.enter_log_file:
            cls.enter_log_file = open(os.path.join(Path(__file__).parent, ENTER_LOG_FILE_NAME), mode="a")
        # set the file pointer to end of the file
        if cls.enter_log_file.seek(0, os.SEEK_END) == 0:
            cls.enter_log_file.write("Year,Month,Day,Time (in MPH),Speed\n")
        if not cls.exit_log_file:
            cls.exit_log_file = open(os.path.join(Path(__file__).parent, EXIT_LOG_FILE_NAME), mode="a")
        # set the file pointer to end of the file
        if cls.exit_log_file.seek(0, os.SEEK_END) == 0:
            cls.exit_log_file.write("Year,Month,Day,Time (in MPH),Speed\n")

    @classmethod
    def validate_column_movement(cls, trackable_object, time_stamp, frame, objectID):
        # Initialize log file.
        if not cls.enter_log_file or not cls.exit_log_file:
            cls.initialize_log_file()

        # check if the object has not been logged
        if not trackable_object.logged and trackable_object.estimated and trackable_object.direction:
            Logger.logger().info("For objectID={}, direction ={}".format(
                objectID,
                repr(trackable_object.direction)))

            # set the current year, month, day, and time
            year = time_stamp.strftime("%Y")
            month = time_stamp.strftime("%m")
            day = time_stamp.strftime("%d")
            time = time_stamp.strftime("%H:%M:%S")

            if SEND_EMAIL and frame is not None:
                # initialize the image id, and the temporary file
                imageID = time_stamp.strftime("%H%M%S%f")
                tempFile = TempFile()

                # write the date and speed on the image.
                cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
                # write the speed: first get the size of the text
                size, base = cv2.getTextSize("%s " % repr(trackable_object.direction), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                             3)
                # then center it horizontally on the image
                cntr_x = int((frame.shape[1] - size[0]) / 2)
                cv2.putText(frame, "%s " % repr(trackable_object.direction),
                            (cntr_x, int(frame.shape[0] * 0.2)), cv2.FONT_HERSHEY_SIMPLEX, 2.00, (0, 255, 0), 3)
                cv2.imwrite(tempFile.path, frame)

                # log the event in the log file
                info = "{},{},{},{},{},{}\n".format(year, month,
                                                    day, time, repr(trackable_object.direction), imageID)
            else:
                # log the event in the log file
                info = "{},{},{},{},{}\n".format(year, month,
                                                 day, time, repr(trackable_object.direction))
            if trackable_object.direction == Direction.ENTER:
                cls.enter_log_file.write(info)
                SendReceiveMessages().increment_face_detected_locally()
            elif trackable_object.direction == Direction.EXIT:
                cls.exit_log_file.write(info)
                SendReceiveMessages().decrement_face_detected_locally()

            # set the object has logged
            trackable_object.logged = True

            # create a thread to send the image via email.
            # and start it
            t = Thread(target=EmailSender.send_email)
            t.start()
