import time
import argparse
import numpy as np
from dynamixel_sdk import PortHandler, PacketHandler, GroupSyncWrite, COMM_SUCCESS
from dynamixel_sdk.robotis_def import DXL_LOBYTE, DXL_HIBYTE, DXL_LOWORD, DXL_HIWORD

from pal_agent.config.palbot_config import ROBOT_CONFIG_degree, convert_degree_to_rad
from pal_agent.config.config import Config
from pal_agent.log.logger import Logger
from pal_agent import constants
from pal_agent.utils.singleton import Singleton

config = Config()
logger = Logger()
ROBOT_CONFIG_rad = convert_degree_to_rad(ROBOT_CONFIG_degree)


class MultiDynamixelController(metaclass=Singleton):

    def __init__(self, device_name=constants.ROBOT_DEVICE_PORT, baudrate=57600):
        self.ids = [j.motor_id for j in ROBOT_CONFIG_rad]
        self.DEVICENAME = device_name
        self.BAUDRATE = baudrate
        self.PROTOCOL_VERSION = 2.0

        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_OPERATING_MODE = 11
        self.ADDR_GOAL_POSITION = 116
        self.LEN_GOAL_POSITION = 4
        self.OPERATING_MODE_POSITION = 3
        self.ADDR_PROFILE_VELOCITY = 112

        self.portHandler = PortHandler(self.DEVICENAME)
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)
        self.groupSyncWrite = GroupSyncWrite(
            self.portHandler, self.packetHandler, self.ADDR_GOAL_POSITION, self.LEN_GOAL_POSITION
        )


    def angle_to_position(self, angle_rad):
        return int((angle_rad / (2 * np.pi)) * 4095)


    def set_profile_velocity(self, dxl_id, velocity_value):
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, dxl_id, self.ADDR_PROFILE_VELOCITY, velocity_value
        )
        if dxl_comm_result != COMM_SUCCESS or dxl_error != 0:
            logger.warning(f"Failed to set velocity for ID {dxl_id}, error: {dxl_error}")


    def set_all_profile_velocities(self, velocity_value):
        for dxl_id in self.ids:
            self.set_profile_velocity(dxl_id, velocity_value)


    def initialize(self, velocity):
        if not self.portHandler.openPort():
            raise RuntimeError("Failed to open port")
        self.portHandler.setBaudRate(self.BAUDRATE)

        for dxl_id in self.ids:
            self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_TORQUE_ENABLE, 0)
            self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_OPERATING_MODE, self.OPERATING_MODE_POSITION)
        self.set_all_profile_velocities(velocity)
        for dxl_id in self.ids:
            self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_TORQUE_ENABLE, 1)

        logger.info(f"Dynamixel group initialized (velocity={velocity})")


    def send_angles(self, angles):
        assert len(angles) == len(self.ids), "Length of angles must match motor count."
        self.groupSyncWrite.clearParam()

        for dxl_id, angle in zip(self.ids, angles):
            goal_pos = self.angle_to_position(angle)
            param_goal_pos = [
                DXL_LOBYTE(DXL_LOWORD(goal_pos)),
                DXL_HIBYTE(DXL_LOWORD(goal_pos)),
                DXL_LOBYTE(DXL_HIWORD(goal_pos)),
                DXL_HIBYTE(DXL_HIWORD(goal_pos)),
            ]
            self.groupSyncWrite.addParam(dxl_id, bytes(param_goal_pos))

        dxl_comm_result = self.groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            logger.warning(f"SyncWrite failed: {dxl_comm_result}")


    def disable_torque(self):
        for dxl_id in self.ids:
            self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_TORQUE_ENABLE, 0)


    def close(self):
        self.portHandler.closePort()


    def replay_trajectory(self, name: str, freq: int = constants.ROBOT_FREQ, velocity: int = constants.ROBOT_VELOCITY):

        name = name.strip()

        root_path = config.skill_data_path
        data_path = f"{root_path}{name}.npy"
        trajectory = np.load(data_path)
        logger.info(f"Loaded trajectory: {data_path}")
        logger.info(f"Total steps: {len(trajectory)}, joints: {trajectory.shape[1]}")

        try:
            initial_positions = [j.initial_rad for j in ROBOT_CONFIG_rad]

            self.initialize(velocity=velocity)

            logger.info("[Init] Moving to initial joint positions...")
            self.send_angles(initial_positions)
            time.sleep(2)

            # from config.palbot_config import get_dual_arm_pos
            # right_arm_pose = [3.195, 3.341, 6.177, 4.737, 3.146]
            # full_pose_rad = get_dual_arm_pos(right_arm_pose)
            # controller.send_angles(full_pose_rad)
            # time.sleep(2)

            dt = 1.0 / freq

            for step_idx, angles in enumerate(trajectory):
                logger.info(f"[Replay] Step {step_idx+1}/{len(trajectory)} - Sending angles: {angles}")
                self.send_angles(angles)
                time.sleep(dt)

            exec_info = "True"
            return exec_info

        except Exception as e:

            exec_info = f"Error during replay: {e}"
            logger.error(exec_info)
            return exec_info


def main():

    controller = MultiDynamixelController()

    parser = argparse.ArgumentParser(description="Replay recorded trajectory with Dynamixel motors.")
    parser.add_argument("-n", "--name", type=str, required=True, help="Trajectory file name (no extension)")
    parser.add_argument("-f", "--freq", type=int, default=8, help="Playback frequency (Hz)")
    parser.add_argument("--velocity", type=int, default=80, help="Dynamixel profile velocity (0-1023)")
    args = parser.parse_args()

    controller.replay_trajectory(name=args.name, freq=args.freq, velocity=args.velocity)

    controller.disable_torque()
    controller.close()


if __name__ == "__main__":

    main()
