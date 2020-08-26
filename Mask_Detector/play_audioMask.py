# This file implements logic to play a speech audio.
from constants import sound_file
import subprocess
import os



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
            speech_file_path = os.path.join(os.path.dirname(__file__), sound_file)
            print("Trying to open {}.".format(speech_file_path))
            return_code = subprocess.call(["aplay", speech_file_path])
            play_audio_successful = True
        except KeyboardInterrupt:
            print('\nInterrupted by user')
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))
        else:
            print("Played {} with return code {}.".format(sound_file, return_code))
        finally:
            return play_audio_successful

