import unittest

from mask_detection import MaskDetector

class TestMaskDetector(unittest.TestCase):
    def test_mask_detector(self):
        MaskDetector.perform_job()