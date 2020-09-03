# This file implements the logic to send / receive TCP/IP messages from/to peer IP address.

import socket
import threading
import time
from Occupancy_Tracker.constants import MAX_OCCUPANCY, SERVER_PORT, MAX_NUMBER_OF_RCV_BYTES
from Occupancy_Tracker.logger import Logger
from Occupancy_Tracker.play_audio import PlayAudio
from Occupancy_Tracker.singleton_template import Singleton


class SendReceiveMessages(metaclass=Singleton):
    """
    This class is used for sending and receiving messages over TCP/IP socket from/to peer Ip address.
    """
    run_program = True

    def cleanup(self):
        """
        This method terminates all threads.
        :return:
        """
        SendReceiveMessages.run_program = False
        if self.thread_for_receiving_face_detected_by_peer:
            self.thread_for_receiving_face_detected_by_peer.join()
        if self.thread_for_transmitting_face_detected_locally:
            self.thread_for_transmitting_face_detected_locally.join()
        if self.thread__for_comparing_local_face_detected_and_global_face_detected:
            self.thread__for_comparing_local_face_detected_and_global_face_detected.join()

    def perform_job(self, peer_ip_address='', peer_port=SERVER_PORT + 1, local_ip_address='', local_port=SERVER_PORT):
        """
        This method performs Send receive face detection count between two raspberry PI's.
        :param local_port: int
        :param local_ip_address: str
        :param peer_port: peer port.
        :param peer_ip_address: Peer IP address.
        :return:
        """
        self.thread_for_receiving_face_detected_by_peer = threading.Thread(
            target=self.method_for_receiving_face_detected_by_peer,
            args=(local_ip_address, local_port))
        self.thread_for_transmitting_face_detected_locally = threading.Thread(
            target=self.method_for_transmitting_face_detected_locally,
            args=(peer_ip_address, peer_port))
        self.thread__for_comparing_local_face_detected_and_global_face_detected = threading.Thread(
            target=self.method_for_comparing_local_face_detected_and_global_face_detected)
        # starting thread 1
        self.thread_for_receiving_face_detected_by_peer.start()
        # starting thread 2
        self.thread_for_transmitting_face_detected_locally.start()
        # starting thread 3
        self.thread__for_comparing_local_face_detected_and_global_face_detected.start()

    def __init__(self):
        self.__total_faces_detected_locally = 0
        self.__total_faces_detected_by_peer = 0
        self.thread_for_receiving_face_detected_by_peer = None
        self.thread_for_transmitting_face_detected_locally = None
        self.thread__for_comparing_local_face_detected_and_global_face_detected = None

    def method_for_receiving_face_detected_by_peer(self, local_ip_address='', local_port=SERVER_PORT):
        """
        This method is used for receiving the face count detected by peer.
        :return:
        """
        Logger.logger().info("Running method_for_receiving_face_detected_by_peer...")
        # Initialize a TCP server socket using SOCK_STREAM
        # Bind the socket to the port
        server_address = (local_ip_address, local_port)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            Logger.logger().info('Server method_for_receiving_face_detected_by_peer: starting up on {} port {}'.format(
                *server_address))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(server_address)
            s.listen(1)
            s.setblocking(flag=False)
            s.settimeout(value=5.0)
            Logger.logger().info('Server {} method_for_receiving_face_detected_by_peer: Waiting for a '
                                 'connection'.format(server_address))
            conn, addr = s.accept()
            with conn:
                Logger.logger().info('Server {}: received connection from peer {}.'.format(server_address, addr))
                while SendReceiveMessages.run_program:
                    Logger.logger().info("Run program is set to True.")
                    data = conn.recv(MAX_NUMBER_OF_RCV_BYTES)
                    if data:
                        Logger.logger().debug('Server {}: received {} from peer {}.'.format(server_address, data, addr))
                        data = data.decode('utf-8')
                        self.__total_faces_detected_by_peer = int(data)
                        Logger.logger().debug("Server {}: total_faces_detected_by_peer = {}".format(
                            server_address, self.__total_faces_detected_by_peer))
                    else:
                        Logger.logger().debug("server method_for_receiving_face_detected_by_peer: data is Null")

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
        Logger.logger().info("Client Running Thread method_for_transmitting_face_detected_locally...")
        # Create a TCP/IP socket
        # Connect the socket to the port where the server is listening
        peer_server_address = (peer_ip_address, peer_port)
        successfully_connected_to_peer = False
        while SendReceiveMessages.run_program and not successfully_connected_to_peer:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.connect(peer_server_address)
                    successfully_connected_to_peer = True
                    self.__send_face_detected_count_via_socket(s, peer_server_address)
            except Exception as e:
                print(type(e).__name__ + ': ' + str(e))
                time.sleep(1)

    def __send_face_detected_count_via_socket(self, sock, peer_server_address):
        """
        This method sends the face detected count via the connected socket.
        :param sock: socket id.
        :param peer_server_address: str
        :return:
        """
        curr_count = 0
        while SendReceiveMessages.run_program:
            try:
                if self.__total_faces_detected_locally != curr_count:
                    # Send the count
                    Logger.logger().debug(
                        "Client method_for_transmitting_face_detected_locally: Sending total_"
                        "faces_detected_locally={} to peer ip={}, "
                        "port={}.".format(
                            self.__total_faces_detected_locally,
                            *peer_server_address))
                    sock.sendall(str(self.__total_faces_detected_locally).encode())
                    curr_count = self.__total_faces_detected_locally
                    time.sleep(1)
            except:
                Logger.logger().info('Client method_for_transmitting_face_detected_locally: Exception: '
                                     'closing client socket')
                sock.close()

    def method_for_comparing_local_face_detected_and_global_face_detected(self):
        """
        This method is used to compare the face detected locally vs the face detected by peer and take
        corresponding action.
        :return:
        """
        Logger.logger().info("Running thread method_for_comparing_local_face_detected_and_global_face_detected...")
        while SendReceiveMessages.run_program:
            total_faces_detected = self.__total_faces_detected_locally + self.__total_faces_detected_by_peer
            Logger.logger().info("[INFO D 1]: {}".format(total_faces_detected))
            Logger.logger().info("[INFO L 2]: {}".format(self.__total_faces_detected_locally))
            Logger.logger().info("[INFO P 3]: {}".format(self.__total_faces_detected_by_peer))
            Logger.logger().info(
                "method_for_comparing_local_face_detected_and_global_face_detected: Compute total faces "
                "detected by both cameras: {}".format(total_faces_detected))
            if total_faces_detected >= MAX_OCCUPANCY:
                Logger.logger().info("Please wait because the occupancy is greater than {}".format(MAX_OCCUPANCY))
                PlayAudio.play_audio_file()
            time.sleep(5)
