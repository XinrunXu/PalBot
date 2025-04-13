from pal_agent.log.logger import Logger
from pal_agent.config.config import Config
from pal_agent.environment.palbot.skill_registry import register_skill
from hardware.audio_manager import AudioManager
from pal_agent.provider.audio.asr_provider import AudioTranscriber
from pal_agent.provider.audio.tts_provider import TextToSpeechProvider

audio_manager = AudioManager()
audio_manager.init()
tts_processor = TextToSpeechProvider()
asr_transcriber = AudioTranscriber()


config = Config()
logger = Logger()

@register_skill("speak")
def speak(text: str):
    """
    The robot speaks the given text.

    Parameters:
    - text: The text to be spoken by the robot.
    """

    pcm_data, sample_rate = tts_processor.text_to_speech(text)
    audio_manager.get_speaker().play_audio(pcm_data, sample_rate)

    return True

# todo: add skills names as functiion, and replay the motors posi inside the function

__all__ = [
    "speak",
]
