from Mask_Detector.mask_detection import MaskDetector
import unittest
import cv2
import numpy as np


class TestMaskDetector(unittest.TestCase):
    """
    This wil test the mask detection program.
    :key

    """

    def test_mask_detection(self):
        Mask_Detector = MaskDetector()
        Mask_Detector.perform_job(preferableTarget=cv2.dnn.DNN_TARGET_CPU,
                                  input_video_file_path='/Users/srinivassriram/PycharmProjects/NESSP_PROJECT'
                                                        '/Mask_Detector/videos'
                                                        '/intersection.mp4')
        no_mask_count = Mask_Detector.get_no_mask_count()
        print("Number of people who are not wearing a mask:".format(no_mask_count))




if __name__ == '__main__':
    unittest.main()
