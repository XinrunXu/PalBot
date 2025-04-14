import matplotlib.pyplot as plt
import numpy as np
import pyrealsense2 as rs
import open3d as o3d
from enum import Enum
import cv2

from pal_agent.utils.singleton import Singleton

class RealSenseCamera(metaclass=Singleton):

    def __init__(self, width=640, height=480, mode = rs.rs400_visual_preset.high_accuracy):
        self.width = width
        self.height = height
        # Configure depth and color streams
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.rgb8, 30)
        self.config.enable_stream(rs.stream.infrared, 1, self.width, self.height, rs.format.y8, 30)
        self.config.enable_stream(rs.stream.infrared, 2, self.width, self.height, rs.format.y8, 30)

        # Start RealSense pipeline
        self.pipeline = rs.pipeline()
        self.align = rs.align(rs.stream.color)
        self.profile = self.pipeline.start(self.config)

        device = self.pipeline.get_active_profile().get_device()
        depth_sensor = device.first_depth_sensor()
        if depth_sensor.supports(rs.option.visual_preset):
            depth_sensor.set_option(rs.option.visual_preset, mode.value)

    def get_aligned_frames(self):
        # Wait for a coherent pair of frames: aligned depth and color
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        color_frame = np.asanyarray(aligned_frames.get_color_frame().get_data())
        depth_frame = np.float32(np.asanyarray(aligned_frames.get_depth_frame().get_data())) / 1000.
        ir_l_image = np.asanyarray(aligned_frames.get_infrared_frame(1).get_data())
        ir_r_image = np.asanyarray(aligned_frames.get_infrared_frame(2).get_data())
        return color_frame, depth_frame, ir_l_image, ir_r_image

    def get_frames(self):
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        color_frame = np.asanyarray(frames.get_color_frame().get_data())
        depth_frame = np.float32(np.asanyarray(frames.get_depth_frame().get_data())) / 1000.
        return color_frame, depth_frame

    def get_camera_intrinsics(self):
        # depth_intrin = self.profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
        color_intrin = self.profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        return color_intrin

    def get_camera_intrinsics_matrix(self):
        color_intrin = self.get_camera_intrinsics()
        # Construct the intrinsics matrix
        intrinsics_matrix = np.array([[color_intrin.fx, 0, color_intrin.ppx],
                                      [0, color_intrin.fy, color_intrin.ppy],
                                      [0, 0, 1]])
        return intrinsics_matrix

    def show_frames(self):
        color_frame, depth_frame = self.get_frames()
        # Plot the depth and color images
        plt.subplot(1, 2, 1)
        plt.imshow(depth_frame, cmap='gray')
        plt.title('Depth Image')
        plt.subplot(1, 2, 2)
        plt.imshow(color_frame)
        plt.title('Color Image')
        plt.show()
        # save the color and depth images as png files
        # cv2.imwrite('color.png', color_frame)
        # cv2.imwrite('depth.png', depth_frame)

    def _show_frames(self):
        depth_frame, color_frame = self.get_frames()
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Plot the depth and color images
        plt.subplot(1, 2, 1)
        plt.imshow(depth_image, cmap='gray')
        plt.title('Depth Image')
        plt.subplot(1, 2, 2)
        plt.imshow(color_image)
        plt.title('Color Image')
        plt.show()

    def close(self):
        self.pipeline.stop()

def main():

    camera = RealSenseCamera()
    # camera.show_frames()
    color_frame, depth_frame, ir_l_image, ir_r_image = camera.get_aligned_frames()
    print(f"Color frame shape: {color_frame.shape}")
    print(f"Depth frame shape: {depth_frame.shape}")
    camera_intrinsics = camera.get_camera_intrinsics()
    print(f"Camera Intrinsics: {camera_intrinsics}")
    intrinsics_matrix = camera.get_camera_intrinsics_matrix()
    print(f"Intrinsics Matrix: {intrinsics_matrix}")

    import time
    color_img_path = "runs/" + time.strftime("%Y%m%d-%H%M%S") + "_color.jpg"
    cv2.imwrite(color_img_path, color_frame)

    camera.close()

if __name__ == "__main__":
    main()
