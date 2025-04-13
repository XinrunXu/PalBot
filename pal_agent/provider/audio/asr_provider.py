import asyncio
import numpy as np
from typing import Optional
from openai import AsyncOpenAI

from pal_agent.utils.audio_utils import read_wav_file
from pal_agent import constants
from pal_agent.log.logger import Logger
from pal_agent.utils import Singleton

logger = Logger()

class AudioTranscriber(metaclass=Singleton):
    """Audio transcription using OpenAI's API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the transcriber.

        Args:
            api_key: Optional OpenAI API key. If None, will use environment variable.
        """
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info("Initialized OpenAI audio transcriber")

    async def transcribe_audio_async(self, audio_file_path: str) -> str:
        """
        Transcribe audio from a file path asynchronously.

        Args:
            audio_file_path: Path to audio file (WAV/MP3/etc.)

        Returns:
            Transcribed text
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model=constants.ASR_MODEL,
                    file=audio_file
                )
            return transcription.text
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            raise

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Synchronous wrapper for audio transcription.

        Args:
            audio_file_path: Path to audio file

        Returns:
            Transcribed text
        """
        return asyncio.run(self.transcribe_audio_async(audio_file_path))

    async def transcribe_pcm_data_async(self, pcm_data: bytes, sample_rate: int) -> str:
        """
        Transcribe raw PCM data asynchronously.

        Args:
            pcm_data: Raw PCM audio bytes
            sample_rate: Sample rate in Hz

        Returns:
            Transcribed text
        """
        try:
            # Convert PCM to numpy array and save as temporary WAV
            import tempfile
            import soundfile as sf

            audio_data = np.frombuffer(pcm_data, dtype=np.int16)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmpfile:
                sf.write(tmpfile.name, audio_data, sample_rate)
                return await self.transcribe_audio_async(tmpfile.name)

        except Exception as e:
            logger.error(f"Error transcribing PCM data: {e}")
            raise

    def transcribe_pcm_data(self, pcm_data: bytes, sample_rate: int) -> str:
        """
        Synchronous wrapper for PCM data transcription.

        Args:
            pcm_data: Raw PCM audio bytes
            sample_rate: Sample rate in Hz

        Returns:
            Transcribed text
        """
        return asyncio.run(self.transcribe_pcm_data_async(pcm_data, sample_rate))


if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv()

    # Example usage
    transcriber = AudioTranscriber()

    # Option 1: Transcribe from file
    audio_file = constants.AUDIO_TEST_FILE_PATH
    text = transcriber.transcribe_audio(audio_file)
    print("Transcription from file:", text)

    # Option 2: Transcribe PCM data
    pcm_data, sample_rate = read_wav_file(audio_file)
    text = transcriber.transcribe_pcm_data(pcm_data, sample_rate)
    print("Transcription from PCM data: \n", text)
