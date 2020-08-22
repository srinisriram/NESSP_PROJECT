# This file is used to test the playing audio functionality.

import unittest
from play_audio import PlayAudio


class TestPlayAudio(unittest.TestCase):
    """
    This class unit tests Play Audio class.
    """
    def test_play_audio(self):
        self.assertEqual(PlayAudio.play_audio_file(), True)


if __name__ == '__main__':
    unittest.main()
