# This file tests the send_receive_messages.py functionality.
import unittest
import threading
from send_receive_messages import SendReceiveMessages
import time
from logger import Logger
import logging


class TestSendReceiveMessages(unittest.TestCase):
    """
    This class is used to test send receive messages functionality.
    """
    def test_send_recv_messages_between_two_sockets(self):
        """
        This method tests the send recv functionality between two instances of
        raspberry pi talking to each other.
        :return:
        """
        Logger.set_log_level(logging.DEBUG)

        raspberry_pi_instance_1 = SendReceiveMessages()
        raspberry_pi_instance_1.perform_job('', 10002, '', 10001)
        raspberry_pi_instance_2 = SendReceiveMessages()
        raspberry_pi_instance_2.perform_job('', 10001, '', 10002)
        time.sleep(10)
        for index in range(2):
            print("Incrementing face detected locally for 1st raspberry PI.")
            raspberry_pi_instance_1.increment_face_detected_locally()
            time.sleep(5)
            print("Checking if peer raspberry PI 2 received the newly incremented face count.")
            self.assertEqual(raspberry_pi_instance_2.get_face_detected_by_peer(),
                             raspberry_pi_instance_1.get_face_detected_count_locally())
            time.sleep(1)
            print("Incrementing face detected locally for 2nd raspberry PI.")
            raspberry_pi_instance_2.increment_face_detected_locally()
            print("Checking if peer raspberry PI 1 received the newly incremented face count.")
            time.sleep(1)
            self.assertEqual(raspberry_pi_instance_1.get_face_detected_by_peer(),
                             raspberry_pi_instance_2.get_face_detected_count_locally())
        time.sleep(5)
        print("cleaning up...")
        raspberry_pi_instance_1.cleanup()
        raspberry_pi_instance_2.cleanup()


if __name__ == '__main__':
    unittest.main()
