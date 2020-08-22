import unittest
from face_tracker import FaceTracker
from send_receive_messages import SendReceiveMessages
from logger import Logger
import logging


class TestFaceTracker(unittest.TestCase):
    """
    This class will test the face tracker class.

    :key
    """

    def test_face_tracker(self):
        # Logger.set_log_level(logging.DEBUG)
        SendReceiveMessages.send_receive_message_instance = SendReceiveMessages()
        FaceTracker.thread_for_capturing_face()


if __name__ == '__main__':
    unittest.main()
