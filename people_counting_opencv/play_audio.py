# This file implements logic to play a speech audio.
from constants import SPEECH_FILENAME
import subprocess
import os
from logger import Logger


class PlayAudio:
    """
    This class implements the logic to play audio files.
    """

    @classmethod
    def play_audio_file(cls):
        """
        This method implements logic to play audio file.
        :return:
        """
        play_audio_successful = False
        try:
            speech_file_path = os.path.join(os.path.dirname(__file__), SPEECH_FILENAME)
            Logger.logger().info("Trying to open {}.".format(speech_file_path))
            return_code = subprocess.call(["afplay", speech_file_path])
            play_audio_successful = True
        except KeyboardInterrupt:
            Logger.logger().info('\nInterrupted by user')
        except Exception as e:
            Logger.logger().info(type(e).__name__ + ': ' + str(e))
        else:
            Logger.logger().info("Played {} with return code {}.".format(SPEECH_FILENAME, return_code))
        finally:
            return play_audio_successful
