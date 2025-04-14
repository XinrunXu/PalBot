import time
import math
import serial

from pal_agent import constants
from pal_agent.log.logger import Logger
from pal_agent.utils.singleton import Singleton

logger = Logger()


class WheelController(metaclass=Singleton):

    def __init__(self,
                 port = constants.ROBOT_WHEEL_PORT,
                 linear_speed=constants.WHEEL_LINEAR_SPEED,
                 angular_speed_degree=constants.WHEEL_ANGULAR_SPEED,
                 baudrate=115200):

        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=0.5)

        self.linear_speed = linear_speed  # mm/s
        self.angular_speed = math.radians(angular_speed_degree) # rad/s


    def close(self):
        self.ser.close()


    def _make_command(self, x_vel, y_vel, z_vel):
        def to_bytes(val, factor=1):
            val = int(val * factor)
            return val.to_bytes(2, byteorder='big', signed=True)

        data = bytearray()
        data.append(0x7B)
        data += b'\x00\x00'
        data += to_bytes(x_vel)
        data += to_bytes(y_vel)
        data += to_bytes(z_vel, 1000)
        bcc = 0
        for byte in data:
            bcc ^= byte
        data.append(bcc)
        data.append(0x7D)
        return data


    def _send_command(self, x_vel, y_vel, z_vel, duration):
        cmd = self._make_command(x_vel, y_vel, z_vel)
        self.ser.write(cmd)
        time.sleep(duration)
        stop_cmd = self._make_command(0, 0, 0)
        self.ser.write(stop_cmd)


    def move(self, x: float, y: float, z: float):

        """
        move command
        :param x: x-axis distance in cm
        :param y: y-axis distance in cm
        :param z: z-axis angle in degrees
        """

        # a hueristic strategy, because the robot is not very accurate, usually short
        # distance command is 0.8 of the real distance
        x = x / 0.8
        y = y / 0.5

        # transform cm to mm and degrees to radians
        x_mm = x * 10
        y_mm = y * 10
        z_rad = math.radians(z)

        # calculate time to move
        t_x = abs(x_mm) / self.linear_speed if x_mm != 0 else 0
        t_y = abs(y_mm) / self.linear_speed if y_mm != 0 else 0
        t_z = abs(z_rad) / self.angular_speed if z_rad != 0 else 0

        # uniformly set the duration to the maximum of the three
        duration = max(t_x, t_y, t_z)

        # calculate the velocities
        vx = self.linear_speed * (1 if x_mm >= 0 else -1) if t_x > 0 else 0
        vy = self.linear_speed * (1 if y_mm >= 0 else -1) if t_y > 0 else 0
        vz = self.angular_speed * (1 if z_rad >= 0 else -1) if t_z > 0 else 0

        try:

            # logger.info(f"Moving: x = {x_mm}cm, y = {y_mm} cm, z = {z_rad} rad")
            self._send_command(vx, vy, vz, duration)

            return "True"

        except Exception as e:

            logger.error(f"Error during movement: {str(e)}")
            return f"Error during movement: {str(e)}"


if __name__ == "__main__":

    controller = WheelController()

    try:
        # controller.move(x=0, y=0, z=90) # turn left 90 degrees
        # time.sleep(1)
        controller.move(x=10, y=0, z=0) # move forward 10 cm

    finally:
        controller.close()