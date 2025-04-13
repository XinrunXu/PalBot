import platform
import time
import threading
import numpy as np
import sounddevice as sd
from collections import deque

from pal_agent import constants
from pal_agent.log.logger import Logger
from pal_agent.utils import Singleton

logger = Logger()

class Microphone(metaclass=Singleton):
    def __init__(self) -> None:
        self.max_buffer_size = 1300  # 30秒音频缓冲
        self.buffer = deque(maxlen=self.max_buffer_size)
        self.buffer_lock = threading.Lock()
        self.audio_thread = None
        self.audio_thread_running = False
        self.sample_rate = 44100  # 明确指定采样率
        self.device_id = None
        self.channels = 1
        self.dtype = 'int16'
        self.blocksize = 1024

    def check_devices(self) -> int:
        devices = sd.query_devices()
        target_device = constants.MICROPHONE_NAME

        for idx, device in enumerate(devices):
            if target_device in device['name'] and device['max_input_channels'] > 0:
                return idx
        raise ValueError(f"Input device '{target_device}' not found")

    def init(self) -> None:
        self.device_id = self.check_devices()
        device_info = sd.query_devices(self.device_id, 'input')

        # 使用设备支持的最佳采样率
        self.sample_rate = int(device_info['default_samplerate'])
        if self.sample_rate not in [44100, 48000]:
            self.sample_rate = 44100

        logger.info(f"Using device {self.device_id}: {device_info['name']}")
        logger.info(f"Sample rate: {self.sample_rate}, Channels: {self.channels}")

        self.audio_thread_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def is_initialized(self) -> bool:
        return self.device_id is not None

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            logger.info(f"Audio callback status: {status}")

        # 移除噪声门限检查，直接保存所有数据
        with self.buffer_lock:
            self.buffer.append(indata.copy())

    def audio_loop(self):
        logger.info("Starting audio stream...")
        with sd.InputStream(
            device=self.device_id,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self.audio_callback,
            blocksize=self.blocksize
        ):
            while self.audio_thread_running:
                time.sleep(0.1)

    def record_audio(self, duration: float = 5.0) -> tuple[np.ndarray, int]:
        start_time = time.time()
        self.buffer.clear()  # 开始前清空缓冲区

        # 精确等待所需时长
        while (time.time() - start_time) < duration:
            time.sleep(0.05)  # 适度休眠减少CPU占用

        with self.buffer_lock:
            if not self.buffer:
                logger.warning("No audio data collected")
                return None, self.sample_rate

            audio_data = np.concatenate(self.buffer, axis=0)
            actual_duration = len(audio_data) / self.sample_rate
            logger.info(f"实际采集时长: {actual_duration:.2f}秒")

            # 如果采集时长不足，补零
            if actual_duration < duration:
                logger.warning(f"Only {actual_duration:.2f} seconds of audio collected, padding with silence")
                silence_len = int((duration - actual_duration) * self.sample_rate)
                silence = np.zeros((silence_len, 1), dtype=np.int16)
                audio_data = np.concatenate([audio_data, silence])

            return audio_data, self.sample_rate

    def stop(self):
        self.audio_thread_running = False
        if self.audio_thread:
            self.audio_thread.join()
        logger.info('Microphone stopped')



if __name__ == '__main__':
    mic = Microphone()
    mic.init()

    # 录制5秒音频
    audio_data, sr = mic.record_audio(5.0)

    from hardware.speaker import Speaker
    speaker = Speaker()
    speaker.init()
    speaker.play_audio(audio_data, sr)

    # if audio_data is not None:
    #     # 保存为WAV文件
    #     sd.play(audio_data, sr)
    #     sd.wait()

    #     import soundfile as sf
    #     time_str = time.strftime("%Y%m%d-%H%M%S")
    #     record_file = 'tmp/recorded_audio_' + time_str + '.wav'
    #     sf.write(record_file, audio_data, sr)
    #     print("音频已保存为: ", record_file)

    mic.stop()