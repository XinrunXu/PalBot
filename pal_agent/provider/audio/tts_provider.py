import asyncio
from typing import Optional, Tuple

from openai import AsyncOpenAI

from hardware.speaker import Speaker
from pal_agent import constants
from pal_agent.utils import Singleton
from pal_agent.log.logger import Logger
from pal_agent.utils.audio_utils import read_wav_file

logger = Logger()

class TextToSpeechProvider(metaclass=Singleton):

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the TTS provider with fixed GPT-4o-mini model.

        Args:
            api_key: Optional OpenAI API key. If None, will use environment variable.
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = constants.TTS_MODEL
        self.instructions = constants.TTS_INSTRUCTIONS
        self.voice = constants.TTS_VOICE

        logger.info(f"Initialized TTS provider with model: {self.model}")

    async def text_to_speech_async(
        self,
        text: str,
        response_format: str = "pcm",
        speed: float = 1.0,
    ) -> Tuple[bytes, int]:
        """
        Convert text to speech using GPT-4o-mini model.

        Args:
            text: Input text to synthesize
            voice: Voice to use (only 'verse' supported for this model)
            response_format: Output format (pcm, mp3, opus, aac, flac)
            speed: Speaking speed (0.25 to 4.0)
            instructions: Detailed voice instructions

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            # Fixed sample rate for this model's PCM output
            sample_rate = 24000

            async with self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format=response_format,
                speed=speed,
                instructions=self.instructions,
            ) as response:
                # For PCM format we get raw bytes
                if response_format == "pcm":
                    pcm_data = await response.read()
                    return pcm_data, sample_rate
                # For other formats save to temp file then read
                else:
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=f".{response_format}", delete=True) as tmpfile:
                        await response.stream_to_file(tmpfile.name)
                        return read_wav_file(tmpfile.name)

        except Exception as e:
            logger.error(f"Error in TTS conversion: {e}")
            raise

    def text_to_speech(
        self,
        text: str,
        response_format: str = "pcm",
        speed: float = 1.0
    ) -> Tuple[bytes, int]:
        """
        Synchronous wrapper for text-to-speech conversion.
        """
        return asyncio.run(
            self.text_to_speech_async(text, response_format, speed)
        )


if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv()

    # Example usage with fixed model
    tts = TextToSpeechProvider()

    text =  """Do you need any help? I think I could help you grab a cup of coffee to cheer you up!\n\nAre you fine? I am a bit worried about you. Do you mind letting me know what happened?"""

    pcm_data, sample_rate = tts.text_to_speech(text=text)

    # Play the audio
    speaker = Speaker()
    speaker.init()
    speaker.play_audio(pcm_data, sample_rate)
    speaker.stop()