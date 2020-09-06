import unittest
# from face_tracker import FaceTracker
from Occupancy_Tracker.human_detector import HumanDetector
from Occupancy_Tracker.send_receive_messages import SendReceiveMessages
from Occupancy_Tracker.logger import Logger
import logging
import os
from Occupancy_Tracker.constants import TEST_VIDEO_FILE_PATH_1, TEST_VIDEO_FILE_PATH_2, Direction
import cv2
import time


class TestFaceTracker(unittest.TestCase):
    """
    This class will test the face tracker class.

    :key
    """
    def __cleanup(self):
        for file in os.listdir(os.getcwd()):
            if file.endswith('.jpg'):
                os.remove(file)

    def test_one_person_entering(self):
        """
        This method validates if occupancy detector can actually detect one person entering the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/one_person_entering.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 1)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 1)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_two_persons_exiting(self):
        """
        This method validates if occupancy detector can actually detect two persons exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/two_persons_exiting.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 2)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), -2)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_three_persons_entering(self):
        """
        This method validates if occupancy detector can actually detect three persons entering the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/3_persons_entering.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 3)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 3)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_four_persons_entering(self):
        """
        This method validates if occupancy detector can actually detect four persons entering the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/4_persons_entering.mov',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 4)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_four_persons_exiting(self):
        """
        This method validates if occupancy detector can actually detect four persons exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/4_persons_exiting.mov',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 5)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[3].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), -5)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_horizontal_line_4_Exiting(self):
        """
        This method validates if occupancy detector can actually detect three persons entering the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/horizontal_line_4_Exiting.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[3].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), -4)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_horizontal_line_4_Entering(self):
        """
        This method validates if occupancy detector can actually detect four persons entering horizontally the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/horizontal_line_4_Entering.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 4)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_vertical_line_Exiting(self):
        """
        This method validates if occupancy detector can actually detect four persons exiting vertically the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/vertical_line_Exiting.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[3].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), -4)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_grouped_exit(self):
        """
        This method validates if occupancy detector can actually detect four persons grouped together exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/grouped_Exit.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[3].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), -4)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_grouped_enter(self):
        """
        This method validates if occupancy detector can actually detect four persons grouped together entering the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/grouped_Enter.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 4)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_one_by_one_crossAdiMilan(self):
        """
        This method validates if occupancy detector can actually detect 1 person entering and teh other exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/one_by_one_cross_AdiMilan.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 2)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 0)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_one_by_one_crossAbhiSrini(self):
        """
        This method validates if occupancy detector can actually detect 1 person entering and teh other exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/one_by_one_cross_AbhiSrini.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 2)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 0)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_one_by_two_cross_EnterExit(self):
        """
        This method validates if occupancy detector can actually detect 1 person entering and the other 2 exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/one_by_two_cross_Enter_Exit.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 3)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), -1)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_one_by_three_cross_EnterExit(self):
        """
        This method validates if occupancy detector can actually detect 1 person exiting and the other 3 entering the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/three_by_one_cross_EnterExit.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 2)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_two_by_two_cross_EnterExit(self):
        """
        This method validates if occupancy detector can actually detect 1 person exiting and the other 3 entering the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/two_by_two_cross_EnterExit.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 4)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 0)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_horizontal_Exit(self):
        """
        This method validates if occupancy detector can actually detect 1 person entering and teh other exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/horizontal_line_Exit.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 3)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), -3)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_horizontal_Enter(self):
        """
        This method validates if occupancy detector can actually detect 1 person entering and teh other exiting the premises.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/TempleVideos/horizontal_line_Entering.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 3)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 3)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_1(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy1.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 9)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[2].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[4].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[5].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[6].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[7].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[8].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 3)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_3(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy3.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 5)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[4].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 5)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_5(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy5.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 9)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[4].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[5].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[6].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[7].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[8].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 7)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_6(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy6.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 12)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[4].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[5].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[6].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[7].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[8].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[9].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[10].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[11].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 2)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_7(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy7.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 2)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.EXIT)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 0)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_8(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy8.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 8)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[4].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[5].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[6].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[7].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 6)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_9(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy9.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 11)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[3].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[4].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[5].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[6].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[7].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[8].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[9].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[10].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 3)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_10(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy10.mp4',
            use_pi_camera=False, open_display=True)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 12)
        self.assertEqual(human_centroid_dict[0].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[2].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[3].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[4].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[5].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[6].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[7].direction, Direction.EXIT)
        self.assertEqual(human_centroid_dict[8].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[9].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[10].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[11].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 2)
        human_detector_inst.clean_up()
        self.__cleanup()

    def test_occupancy_11(self):
        """
        This method validates if occupancy detector can actually correctly calculate the number of people entering the premises on a typical temple day.
        :return:
        """
        human_detector_inst = HumanDetector(
            find_humans_from_video_file_name='videos/occupancy_test_videos/occupancy11.mp4',
            use_pi_camera=False, open_display=False)
        self.assertEqual(human_detector_inst.perform_job(), None)
        human_centroid_dict = human_detector_inst.get_human_centroid_dict()
        self.assertEqual(len(human_centroid_dict), 2)
        self.assertEqual(human_centroid_dict[0].direction, Direction.ENTER)
        self.assertEqual(human_centroid_dict[1].direction, Direction.ENTER)
        self.assertEqual(SendReceiveMessages().get_face_detected_count_locally(), 2)
        human_detector_inst.clean_up()
        self.__cleanup()


if __name__ == '__main__':
    unittest.main()
