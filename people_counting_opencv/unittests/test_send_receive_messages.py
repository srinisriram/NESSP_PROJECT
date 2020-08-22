# This file tests the send_receive_messages.py functionality.
import unittest
import threading
from send_receive_messages import SendReceiveMessages
import time


class TestSendReceiveMessages(unittest.TestCase):
    """
    This class is used to test send receive messages functionality.
    """

    def create_a_socket_instance(self, send_recv_msg_instance, local_ip_address,
                                 local_port, peer_ip_address, peer_port):
        """
        This method initiates a send recv socket instance.
        :param local_port: local port.
        :param local_ip_address: ip address of local.
        :param send_recv_msg_instance: an instance of SendRecvMessage class.
        :param peer_ip_address: ip address of peer.
        :param peer_port: port of the peer.
        :return:
        """
        t1 = threading.Thread(target=send_recv_msg_instance.method_for_receiving_face_detected_by_peer,
                              args=(local_ip_address, local_port))
        t2 = threading.Thread(target=send_recv_msg_instance.method_for_transmitting_face_detected_locally,
                              args=(peer_ip_address, peer_port))
        t3 = threading.Thread(
            target=send_recv_msg_instance.method_for_comparing_local_face_detected_and_global_face_detected)
        # starting thread 1
        t1.start()
        # starting thread 2
        t2.start()
        # starting thread 3
        t3.start()
        # wait until thread 1 is completely executed
        t1.join()
        # wait until thread 2 is completely executed
        t2.join()
        # wait until thread 3 is completely executed
        t3.join()

    def test_send_recv_messages_between_two_sockets(self):
        """
        This method tests the send recv functionality between two instances of
        raspberry pi talking to each other.
        :return:
        """
        raspberry_pi_instance_1 = SendReceiveMessages()
        raspberry_pi_1 = threading.Thread(target=self.create_a_socket_instance,
                                          args=(raspberry_pi_instance_1, '', 10001, '', 10002))
        raspberry_pi_instance_2 = SendReceiveMessages()
        raspberry_pi_2 = threading.Thread(target=self.create_a_socket_instance,
                                          args=(raspberry_pi_instance_2, '', 10002, '', 10001))
        raspberry_pi_1.start()
        raspberry_pi_2.start()
        time.sleep(5)
        for index in range(100):
            print("Incrementing face detected locally for 1st raspberry PI.")
            raspberry_pi_instance_1.increment_face_detected_locally()
            time.sleep(1)
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
        raspberry_pi_instance_1.run_program = False
        raspberry_pi_instance_2.run_program = False
        raspberry_pi_1.join()
        raspberry_pi_2.join()


if __name__ == '__main__':
    unittest.main()
