# This file implements the code for detecting and counting humans.
import argparse
from constants import SERVER_PORT
from face_tracker import FaceTracker
from send_receive_messages import SendReceiveMessages
import time


class OccupancyDetector:
    """
    This class implements the logic for detecting and counting humans.
    """
    @classmethod
    def perform_job(cls, peer_ip_address, peer_port):
        """
        This method invokes two classes to perform their respective jobs.
        :param peer_ip_address: str (peer IP address)
        :param peer_port: int (peer Port)
        :return:
        """
        FaceTracker.perform_job()
        SendReceiveMessages.perform_job(peer_ip_address, peer_port)
        try:
            while True:
                time.sleep(1)
        except Exception as e:
            FaceTracker.run_program = False
            SendReceiveMessages.run_program = False
            print(type(e).__name__ + ': ' + str(e))
        finally:
            print("Exiting....")


if __name__ == "__main__":
    # thread_for_capturing_face()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--peer_ip_address", type=str, help="Provide the IP address of the remote raspberry PI.")
    parser.add_argument("-p", "--peer_port", type=int, help="Provide the server port of the remote raspberry PI.",
                        default=SERVER_PORT)
    args = parser.parse_args()
    OccupancyDetector.perform_job(args.peer_ip_address, args.peer_port)

    # all threads completely executed
    print("Done!")
