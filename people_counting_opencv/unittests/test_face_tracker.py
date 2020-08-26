import unittest
# from face_tracker import FaceTracker
from human_detector import HumanDetector
from send_receive_messages import SendReceiveMessages
from logger import Logger
import logging
import os
from constants import TEST_VIDEO_FILE_PATH_1, TEST_VIDEO_FILE_PATH_2
import cv2


class TestFaceTracker(unittest.TestCase):
    """
    This class will test the face tracker class.

    :key
    """

    def test_face_tracker_example_video_file1(self):
        # Logger.set_log_level(logging.DEBUG)
        video_file_path = os.path.join('/'.join(os.path.dirname(__file__).split('/')[:-1]), TEST_VIDEO_FILE_PATH_1)
        Logger.logger().info("Trying to open {}.".format(video_file_path))
        HumanDetector.send_receive_message_instance = SendReceiveMessages()
        HumanDetector.send_receive_message_instance.perform_job()
        HumanDetector.input_video_file_path = video_file_path
        HumanDetector.preferable_target = cv2.dnn.DNN_TARGET_CPU
        # FaceTracker.thread_for_capturing_face(video_file_path, preferable_target=cv2.dnn.DNN_TARGET_CPU)
        HumanDetector().thread_for_face_tracker()

    def test_face_tracker_example_video_file2(self):
        # Logger.set_log_level(logging.DEBUG)
        video_file_path = os.path.join('/'.join(os.path.dirname(__file__).split('/')[:-1]), TEST_VIDEO_FILE_PATH_2)
        Logger.logger().info("Trying to open {}.".format(video_file_path))
        HumanDetector.send_receive_message_instance = SendReceiveMessages()
        HumanDetector.send_receive_message_instance.perform_job()
        HumanDetector.input_video_file_path = video_file_path
        HumanDetector.preferable_target = cv2.dnn.DNN_TARGET_CPU
        # FaceTracker.thread_for_capturing_face(video_file_path, preferable_target=cv2.dnn.DNN_TARGET_CPU)
        HumanDetector().thread_for_face_tracker()

    def test_face_tracker_locally_on_mac(self):
        # Logger.set_log_level(logging.DEBUG)
        video_file_path = os.path.join('/'.join(os.path.dirname(__file__).split('/')[:-1]), TEST_VIDEO_FILE_PATH_1)
        Logger.logger().info("Trying to open {}.".format(video_file_path))
        HumanDetector.send_receive_message_instance = SendReceiveMessages()
        HumanDetector.preferable_target = cv2.dnn.DNN_TARGET_CPU
        # FaceTracker.thread_for_capturing_face(video_file_path, preferable_target=cv2.dnn.DNN_TARGET_CPU)
        HumanDetector().thread_for_face_tracker()


if __name__ == '__main__':
    unittest.main()
