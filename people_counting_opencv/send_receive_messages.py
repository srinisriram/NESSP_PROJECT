# This file implements the logic to send / receive TCP/IP messages from/to peer IP address.

import socket
import time
from constants import MAX_OCCUPANCY, SERVER_PORT, MAX_NUMBER_OF_RCV_BYTES
from play_audio import PlayAudio
import threading


class SendReceiveMessages:
    """
    This class is used for sending and receiving messages over TCP/IP socket from/to peer Ip address.
    """
    run_program = True

    __instance = None

    def __new__(cls):
        if SendReceiveMessages.__instance is None:
            SendReceiveMessages.__instance = object.__new__(cls)
        return SendReceiveMessages.__instance

    @classmethod
    def perform_job(cls, peer_ip_address, peer_port):
        """
        This method performs Send receive face detection count between two raspberry PI's.
        :param peer_port: peer port.
        :param peer_ip_address: Peer IP address.
        :return:
        """
        self_instance = cls()
        t1 = threading.Thread(target=self_instance.method_for_receiving_face_detected_by_peer)
        t2 = threading.Thread(target=self_instance.method_for_transmitting_face_detected_locally,
                              args=(peer_ip_address, peer_port))
        t3 = threading.Thread(target=self_instance.method_for_comparing_local_face_detected_and_global_face_detected)
        # starting thread 1
        t1.start()
        # starting thread 1
        t2.start()
        # starting thread 1
        t3.start()

    def __init__(self):
        self.__total_faces_detected_locally = 0
        self.__total_faces_detected_by_peer = 0

    def method_for_receiving_face_detected_by_peer(self, local_ip_address='', local_port=SERVER_PORT):
        """
        This method is used for receiving the face count detected by peer.
        :return:
        """
        print("[INFO] Running Thread 2...")
        # Initialize a TCP server socket using SOCK_STREAM
        # Bind the socket to the port
        server_address = (local_ip_address, local_port)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print('Server Thread2: starting up on {} port {}'.format(*server_address))
            s.bind(server_address)
            s.listen(1)
            print('Server Thread2: Waiting for a connection')
            conn, addr = s.accept()
            with conn:
                print('Server Thread2: connection from', addr)
                while SendReceiveMessages.run_program:
                    data = conn.recv(MAX_NUMBER_OF_RCV_BYTES)
                    if data:
                        print('Server Thread2: received {} from peer {}.'.format(data, addr))
                        data = data.decode('utf-8')
                        self.__total_faces_detected_by_peer = int(data)
                        print("Server Thread2: total_faces_detected_by_peer = {}".format(
                            self.__total_faces_detected_by_peer))
                    else:
                        print("server Thread2: data is Null")

    def increment_face_detected_locally(self):
        """
        The caller SHALL invoke this API to increment the face count detected locally.
        :return:
        """
        self.__total_faces_detected_locally += 1

    def decrement_face_detected_locally(self):
        """
        The caller SHALL invoke this API to decrement the face count detected locally.
        :return:
        """
        self.__total_faces_detected_locally -= 1

    def get_face_detected_by_peer(self):
        """
        The caller SHALL use this API to probe the face count detected from peer.
        :return:
        """
        return self.__total_faces_detected_by_peer

    def get_face_detected_count_locally(self):
        return self.__total_faces_detected_locally

    def method_for_transmitting_face_detected_locally(self, peer_ip_address, peer_port=SERVER_PORT):
        """
        This method is used for transmitting the __total_faces_detected_locally count to peer.
        :param peer_ip_address: str
        :param peer_port: str
        :return:
        """
        print("Client [INFO] Running Thread 3...")
        # Create a TCP/IP socket
        # Connect the socket to the port where the server is listening
        server_address = (peer_ip_address, peer_port)

        curr_count = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            successfully_connected_to_peer = False
            while not successfully_connected_to_peer:
                try:
                    print('Client Thread3: connecting to {} port {}'.format(*server_address))
                    s.connect(server_address)
                    successfully_connected_to_peer = True
                except:
                    time.sleep(5)
            while SendReceiveMessages.run_program:
                try:
                    if self.__total_faces_detected_locally != curr_count:
                        # Send the count
                        print("Client Thread3: Sending total_faces_detected_locally={} to peer ip={}, port={}.".format(
                            self.__total_faces_detected_locally,
                            *server_address))
                        s.sendall(str(self.__total_faces_detected_locally).encode())
                        curr_count = self.__total_faces_detected_locally
                        time.sleep(1)
                except:
                    print('Client Thread3: Exception: closing client socket')
                    s.close()

    def method_for_comparing_local_face_detected_and_global_face_detected(self):
        """
        This method is used to compare the face detected locally vs the face detected by peer and take
        corresponding action.
        :return:
        """
        while SendReceiveMessages.run_program:
            total_faces_detected = self.__total_faces_detected_locally + self.__total_faces_detected_by_peer
            print("[INFO D 1]: ", total_faces_detected)
            print("[INFO L 2]: ", self.__total_faces_detected_locally)
            print("[INFO P 3]: ", self.__total_faces_detected_by_peer)
            print("Thead4: Compute total faces detected by both cameras: {}".format(total_faces_detected))
            if total_faces_detected > MAX_OCCUPANCY:
                print("Please wait because the occupancy is greater than {}".format(MAX_OCCUPANCY))
                PlayAudio.play_audio_file()
            time.sleep(5)
