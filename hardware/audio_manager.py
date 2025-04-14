from hardware.microphone import Microphone
from hardware.speaker import Speaker
from pal_agent.utils import Singleton


class AudioManager(metaclass=Singleton):

    _microphone : Microphone = None
    _speaker : Speaker = None

    def __init__(self):
        # Initialize Microphone and Speaker only once (singleton-like behavior)
        if AudioManager._microphone is None:
            AudioManager._microphone = Microphone()

        if AudioManager._speaker is None:
            AudioManager._speaker = Speaker()


    @classmethod
    def init(self):
        if not self._microphone.is_initialized():
            self._microphone.init()

        if not self._speaker.is_initialized():
            self._speaker.init()


    @classmethod
    def stop(self):
        self._microphone.stop()
        self._speaker.stop()


    @classmethod
    def get_microphone(self):
        if self._microphone is None:
            raise RuntimeError("AudioManager Microphone not initialized. Call AudioManager init() first.")
        return self._microphone


    @classmethod
    def get_speaker(self):
        if self._speaker is None:
            raise RuntimeError("AudioManager Speaker not initialized. Call AudioManager init() first.")
        return self._speaker


if __name__ == "__main__":

    # Test Code
    audio_manager = AudioManager()
    audio_manager.init()

    # from pal_agent.utils.audio_utils import read_wav_file
    # from pal_agent import constants
    # pcm_data, sample_rate = read_wav_file(constants.AUDIO_TEST_FILE_PATH)

    microphone = audio_manager.get_microphone()
    audiodata, sample_rate = microphone.record_audio(5)

    speaker = audio_manager.get_speaker()
    speaker.play_audio(audiodata, sample_rate)

    audio_manager.stop()
