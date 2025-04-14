import platform
import time
import sounddevice as sd
import numpy as np
from typing import Optional

from pal_agent.utils.audio_utils import read_wav_file
from pal_agent import constants
from pal_agent.utils import Singleton
from pal_agent.log.logger import Logger

logger = Logger()

class Speaker(metaclass=Singleton):
    """Class for bot speaker."""

    def __init__(self) -> None:
        """Initialize the Speaker class."""
        self.device_id: Optional[int] = None
        self.sample_rate: Optional[int] = None
        self._is_playing: bool = False

    def check_devices(self) -> int:
        """Check the available audio devices and return the device ID for the target device."""
        devices = sd.query_devices()

        # Target device name
        target_device_name = constants.SPEAKER_NAME

        for idx, device in enumerate(devices):
            if target_device_name in device['name'] and device['max_output_channels'] > 0:
                return idx

        available_devices = "\n".join([f"{idx}: {d['name']}" for idx, d in enumerate(devices)])
        raise ValueError(
            f"Device '{target_device_name}' not found or not an output device.\n"
            f"Available devices:\n{available_devices}"
        )

    def init(self) -> None:
        """Initialize the speaker for local playback using sounddevice."""
        self.device_id = self.check_devices()
        device_info = sd.query_devices(self.device_id, 'output')

        # Prefer common sample rates
        self.sample_rate = int(device_info['default_samplerate'])
        if self.sample_rate not in [44100, 48000, 96000]:
            self.sample_rate = 44100

        logger.info(f"Using output device {self.device_id}: {device_info['name']}")
        logger.info(f"Using sample rate: {self.sample_rate}")

        # Test the device with a simple tone
        # self._test_device()
        logger.info("Speaker initialized successfully.")

    def _test_device(self) -> None:
        """Test if the audio device can play sound."""
        try:
            duration = 1.0  # seconds
            frequency = 440  # Hz
            samples = int(duration * self.sample_rate)
            t = np.linspace(0, duration, samples, endpoint=False)
            test_tone = 0.3 * np.sin(2 * np.pi * frequency * t)

            logger.info("Testing audio device with a 440Hz tone...")
            sd.play(test_tone, samplerate=self.sample_rate, device=self.device_id)

            # sd.wait()
            logger.info("Device test successful.")
        except Exception as e:
            raise RuntimeError(f"Audio device test failed: {str(e)}")

    def is_initialized(self) -> bool:
        """Check if the speaker is initialized."""
        return self.device_id is not None and self.sample_rate is not None

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._is_playing

    def play_audio(self, pcm_data: bytes, audio_sample_rate: int) -> None:
        """Play audio data from a PCM byte stream."""
        if not self.is_initialized():
            raise RuntimeError("Speaker not initialized")

        try:
            self._is_playing = True

            # Convert PCM data to numpy array
            audio_data = np.frombuffer(pcm_data, dtype=np.int16)

            # Convert to float32 and normalize to [-1, 1] range
            audio_data = audio_data.astype(np.float32) / 32768.0

            # Ensure correct shape (samples, channels)
            if audio_data.ndim == 1:
                audio_data = np.reshape(audio_data, (-1, 1))

            # Resample if needed
            if audio_sample_rate != self.sample_rate:
                logger.info(f"Resampling from {audio_sample_rate}Hz to {self.sample_rate}Hz")
                from resampy import resample
                audio_data = resample(
                    audio_data,
                    audio_sample_rate,
                    self.sample_rate,
                    axis=0,
                    filter='kaiser_best'
                )

            logger.info(f"Starting playback (shape: {audio_data.shape}, dtype: {audio_data.dtype})")

            # Start playback with explicit device and sample rate
            sd.play(
                audio_data,
                samplerate=self.sample_rate,
                device=self.device_id,
                blocking=False
            )

            # Wait for playback to complete
            while sd.get_stream().active:
                time.sleep(0.05)

            sd.wait()  # Ensure all audio is played before proceeding

            self._is_playing = False

            return "True"

        except Exception as e:

            self.stop()
            logger.error(f"Error during playback: {str(e)}")
            self._is_playing = False
            return f"Error during playback: {str(e)}"


    def is_initialized(self) -> bool:
        """Check if the speaker is initialized."""
        return self.device_id is not None and self.sample_rate is not None


    def stop(self) -> None:
        """Stop all ongoing audio playback."""
        sd.stop()
        self._is_playing = False
        logger.info("Playback stopped")

if __name__ == '__main__':
    print('Testing Speaker')

    try:
        speaker = Speaker()
        speaker.init()

        # Test with a simple tone first
        # print("\nTesting with generated tone...")
        # duration = 2.0
        # freq = 440
        # samples = int(duration * speaker.sample_rate)
        # tone = 0.5 * np.sin(2 * np.pi * freq * np.linspace(0, duration, samples))
        # sd.play(tone, samplerate=speaker.sample_rate, device=speaker.device_id)
        # sd.wait()

        # Test with WAV file
        print("\nTesting with WAV file...")
        wav_file = constants.AUDIO_TEST_FILE_PATH
        pcm_data, sample_rate = read_wav_file(wav_file)

        print(f"Loaded WAV file: {len(pcm_data)} bytes, {sample_rate}Hz")
        speaker.play_audio(pcm_data, sample_rate)

        print("\nPlayback completed successfully")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        speaker.stop()