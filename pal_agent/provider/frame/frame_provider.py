import time
import os
import cv2


from pal_agent.log.logger import Logger
from pal_agent.config.config import Config
from pal_agent.provider.base_provider import BaseProvider
from hardware.camera import RealSenseCamera

config = Config()
logger = Logger()

class FrameProvider(BaseProvider):
    def __init__(self):
        super(FrameProvider).__init__()

        self.camera = RealSenseCamera()
        self.rgb_frame = None

        self.screen_region = [0, 0, 640, 480]
        self.frame_path_dir = os.path.join(config.work_dir, 'frames')
        os.makedirs(self.frame_path_dir, exist_ok=True)

        self.frame_count = 0

    def get_current_frame_path(self):

        self.rgb_frame, _, _, _ = self.camera.get_aligned_frames()

        # change the frame to BGR format
        self.rgb_frame = cv2.cvtColor(self.rgb_frame, cv2.COLOR_RGB2BGR)

        rgb_frame_img_path = os.path.join(self.frame_path_dir, f'rgb_frame_{time.strftime("%Y%m%d-%H%M%S")}.jpg')
        cv2.imwrite(rgb_frame_img_path, self.rgb_frame)

        self.frame_count += 1
        logger.info(f"Frame {self.frame_count} captured and saved at {rgb_frame_img_path}")

        return rgb_frame_img_path

    def get_current_frame_cont(self):
        return self.frame_count

    def get_current_frame(self):
        return self.rgb_frame

if __name__ == "__main__":

    frame_provider = FrameProvider()
    frame_path = frame_provider.get_current_frame_path()
    print(f"Frame saved at: {frame_path}")
    frame_count = frame_provider.get_current_frame_cont()
    print(f"Total frames captured: {frame_count}")
    