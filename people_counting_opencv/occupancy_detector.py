# This file implements the code for detecting and counting humans.
import argparse
from constants import SERVER_PORT
# from face_tracker import FaceTracker
from human_detector import HumanDetector
from send_receive_messages import SendReceiveMessages
import time
import logging
from logger import Logger


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
        Logger.logger().debug("Invoking OccupancyDetector:perform_job")
        send_receive_message_instance = SendReceiveMessages()
        send_receive_message_instance.perform_job(peer_ip_address, peer_port)
        # FaceTracker.perform_job(send_receive_message_instance)
        HumanDetector.perform_job(send_receive_message_instance)

        try:
            while True:
                time.sleep(1)
        except Exception as e:
            # FaceTracker.run_program = False
            HumanDetector.run_program = False
            SendReceiveMessages.run_program = False
            Logger.logger().info(type(e).__name__ + ': ' + str(e))
        finally:
            Logger.logger().info("Exiting....")


if __name__ == "__main__":
    # thread_for_capturing_face()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--peer_ip_address", type=str, help="Provide the IP address of the remote raspberry PI.")
    parser.add_argument("-p", "--peer_port", type=int, help="Provide the server port of the remote raspberry PI.",
                        default=SERVER_PORT)
    parser.add_argument('-d', '--debug', type=bool, help='Enable debug logging.', default=False)
    args = parser.parse_args()
    if args.debug:
        Logger.set_log_level(logging.DEBUG)
    OccupancyDetector.perform_job(args.peer_ip_address, args.peer_port)

    # all threads completely executed
    Logger.logger().info("Done!")
