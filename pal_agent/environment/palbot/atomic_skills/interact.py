from pal_agent.log.logger import Logger
from pal_agent.config.config import Config
from pal_agent.environment.palbot.skill_registry import register_skill
from hardware.audio_manager import AudioManager
from hardware.driver.multi_dynamixel_controller import MultiDynamixelController
from pal_agent.provider.audio.asr_provider import AudioTranscriber
from pal_agent.provider.audio.tts_provider import TextToSpeechProvider

audio_manager = AudioManager()
audio_manager.init()
tts_processor = TextToSpeechProvider()
asr_transcriber = AudioTranscriber()
multi_dynamixel_controller = MultiDynamixelController()


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


@register_skill("cheer_up")
def cheer_up():
    """
    The robot performs a cheer up gesture.
    """
    logger.info("Performing cheer up gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="cheer_up")

    return exec_info


@register_skill("dance")
def dance():
    """
    The robot performs a dance gesture.
    """
    logger.info("Performing dance gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="dance")

    return exec_info


@register_skill("fight")
def fight():
    """
    The robot performs a fight gesture.
    """
    logger.info("Performing fight gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="fight")

    return exec_info


@register_skill("hug")
def hug():
    """
    The robot performs a hug gesture.
    """
    logger.info("Performing hug gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="hug")

    return exec_info


@register_skill("love_you_gesture")
def love_you_gesture():
    """
    The robot performs a love you gesture.
    """
    logger.info("Performing love you gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="love_you_gesture")

    return exec_info


@register_skill("nod")
def nod():
    """
    The robot performs a nod gesture.
    """
    logger.info("Performing nod gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="nod")

    return exec_info


@register_skill("shake_head_to_deny")
def shake_head_to_deny():
    """
    The robot performs a shake head to deny gesture.
    """
    logger.info("Performing shake head to deny gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="shake_head_to_deny")

    return exec_info


@register_skill("shake_right_hand")
def shake_right_hand():
    """
    The robot performs a shake right hand gesture.
    """
    logger.info("Performing shake right hand gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="shake_right_hand")

    return exec_info


@register_skill("wave_left_hand")
def wave_left_hand():
    """
    The robot performs a wave left hand gesture.
    """
    logger.info("Performing wave left hand gesture.")
    exec_info = multi_dynamixel_controller.replay_trajectory(name="wave_left_hand")

    return exec_info


__all__ = [
    "speak",
    "cheer_up",
    "dance",
    "fight",
    "hug",
    "love_you_gesture",
    "nod",
    "shake_head_to_deny",
    "shake_right_hand",
    "wave_left_hand"
]
