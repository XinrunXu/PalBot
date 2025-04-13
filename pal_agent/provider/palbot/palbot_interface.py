import time
import cv2
import os
from typing import List, Tuple
from copy import deepcopy

import numpy as np

# from cradle.gameio import IOEnvironment

from pal_agent.config.config import Config
from pal_agent.log.logger import Logger
from pal_agent.utils.image_utils import blurry_detection
from pal_agent import constants
from pal_agent.utils.string_utils import dict_to_call_params
from pal_agent.provider.palbot.client import Client
from pal_agent.memory.local_memory import LocalMemory
# from pal_agent.gameio.game_manager import GameManager


# Configuration
# robot_ip = '192.168.15.89' # Robot IP
# robot_ip = '192.168.230.103'
robot_ip = '127.0.0.1' # My laptop IP
robot_port = 9080

config = Config()
# io_env = IOEnvironment()
logger = Logger()

test_using_trace = False

trace_path = f'res/robot/samples/operate_printer_0716'

class PalbotInterface:

    def __init__(self):
        self.client = Client(robot_ip, robot_port)
        self.work_dir = config.work_dir
        self.trace_frame_id = 1
        self.memory = LocalMemory()


class PalbotInterface:

    def __init__(self):
        self.client = Client(robot_ip, robot_port)
        self.work_dir = config.work_dir
        self.trace_frame_id = 1
        self.memory = LocalMemory()


    def capture_screen(self, save = True) -> Tuple[str, str]:
        """
        Request frame from robot camera after action execution.
        """
        tid = time.time()
        logger.info('Request frame from robot camera after action execution.')

        # If using predefined trace for testing
        if test_using_trace is True:
            image_path = f'{trace_path}/{self.trace_frame_id}.jpg'
            rgb_image = cv2.imread(image_path)
            self.trace_frame_id += 1

            # Save the RGB image
            rgb_image_filename = os.path.join(self.work_dir, f'{str(tid)}_rgb.jpg')
            cv2.imwrite(rgb_image_filename, rgb_image)
            return rgb_image_filename

        # Get RGB and Depth image by calling robot API
        target_image_mode = 'RGB'
        frame_id, rgb_image, colored_depth_image, depth_frame = self.client.get_video_frame(target_image_mode)

        if save is True:
            # Determine whether the image is blurry. If so, keep requesting new frames until receiving a clear frame
            max_num_rerequesting = 5
            num = 0
            while blurry_detection(rgb_image) is True and num < max_num_rerequesting:
                time.sleep(0.5) # wait a short time for robot to be stable
                frame_id, rgb_image, colored_depth_image, depth_frame = self.client.get_video_frame(target_image_mode)
                num += 1

        # Save sharpened RGB and Depth image in working directory
        rgb_image_filename = os.path.join(self.work_dir, f'{frame_id}_rgb.jpg')
        cv2.imwrite(rgb_image_filename, rgb_image)

        if colored_depth_image is not None:
            depth_image_filename = os.path.join(self.work_dir, f'{frame_id}_depth.jpg')
            cv2.imwrite(depth_image_filename, colored_depth_image)

            # Save depth_frame in working directory
            downloaded_depth_frame_path = os.path.join(self.work_dir, f'{frame_id}_downloaded_depth_frame.npy')
            with open(downloaded_depth_frame_path, 'wb') as f:
                f.write(depth_frame.content)
            print("Save downloaded_depth_frame in working directory.")

        # Return the path of RGB image
        return rgb_image_filename, frame_id



    def retrieve_skill_library(self):
        """
        Retrieve skill library from robot.
        """
        return self.client.get_skills()


    def capture_screen_during_action(self):
        """
        Request frame from robot camera during action execution.
        """

        tid = time.time()

        # Get RGB and Depth image by calling robot API
        target_image_mode = 'RGB'
        rgb_image, colored_depth_image, frame_id, depth_frame = self.client.get_video_frame(target_image_mode, tid, save = False)

        # Return RGB and depth image
        return rgb_image, colored_depth_image


    def audio_log(self, messages, is_skill = False):
        """
        Log via audio what the robot is doing.
        """
        # @TODO Change to proper API in robot server
        log_command = "speak"

        if isinstance(messages, str):
            messages = [messages]
        elif not isinstance(messages, list):
            raise ValueError("Messages should be a list or a string.")

        if is_skill is True:

            skill, parameter_values = self.weak_skill_steps_parse(messages)

            concatenated_parameters = dict_to_call_params(parameter_values)

            parameter_values = concatenated_parameters

            if parameter_values is not None:
                message = (skill + ", " + parameter_values).replace("'", " ").replace('"', " ").replace("(", " ").replace(")", " ").replace("_", " ").replace('=', ",")
            else:
                message = skill.replace("'", " ").replace('"', " ").replace("(", " ").replace(")", " ").replace("_", " ").replace('=', ",")

            parameters = {"text": message}
            self.client.post_action(log_command, parameters = parameters)
        else:
            for message in messages:
                parameters = {"text": message}
                self.client.post_action(log_command, parameters = parameters)


    def weak_skill_steps_parse(self, skill_steps):

        # @TODO Hack fix
        if isinstance(skill_steps, list):
            skill = skill_steps[0]
        else:
            skill = skill_steps

        if skill == '':
            return '', None

        # @HERE Fix parsing of skill and parameters
        tokens = skill.split('(')
        skill = tokens[0]
        parameters = tokens[1].split(')')[0]#.strip('"')
        if parameters == '':
            parameters = None

        if '=' in parameters:
            tokens = parameters.split('=')
            parameters = {tokens[0]: tokens[1].strip('"')}

        print("skill = ", skill)
        print("parameters = ", parameters)

        # @HACK hack again
        def is_convertible_to_float(s):
            try:
                float(s)
                return True
            except:
                return False
        if is_convertible_to_float(parameters):
            parameters = float(parameters)

        return skill, parameters


    def execute_nop_skill(self):
        time.sleep(2)


    def execute_actions(self, skill, parameters = None, confirming=True):

        exec_info = {
            constants.EXECUTED_SKILLS: [],
            constants.LAST_SKILL: '',
            constants.LAST_PARAMETERS: None,
            constants.ERRORS : False,
            constants.ERRORS_INFO: ""
        }

        if skill is None or len(skill) == 0 or skill == '' or skill[0] == '':
            logger.warning(f"No actions to execute! Executing nop.")
            self.execute_nop_skill()

            exec_info[constants.ERRORS] = False
            return exec_info

        params = deepcopy(self.memory.working_area)
        # cur_timestamp = params[constants.CUR_SCREENSHOT_TIMESTAMP] # !!!
        cur_timestamp = None

        skill, parameters = self.weak_skill_steps_parse(skill)
        message = ""
        if confirming:
            execution_flag = input("Please verify if this action could be executed. (Yes or No)")
            if execution_flag.lower() == "y" or execution_flag.lower() == "yes":
                success, message = self.client.post_action(skill, parameters, cur_timestamp)
            else:
                execution_modification = input("Do you want to input a new command? (Yes or No)")
                if execution_modification.lower() == "y" or execution_modification.lower() == "yes":
                    skill = input("Please input a new skill name: ")
                    parameters = input("Please input the new skill parameters: ")
                    success, message = self.client.post_action(skill, parameters, cur_timestamp)
                else:
                    success, message = False, "Action not executed as it was not correct in user's opinion."
        else:
            success, message = self.client.post_action(skill, parameters, cur_timestamp)

        exec_info[constants.EXECUTED_SKILLS].append(skill)
        exec_info[constants.LAST_SKILL] = skill

        parameters_str = dict_to_call_params(parameters)
        exec_info[constants.LAST_PARAMETERS] = parameters_str

        if success is False:
            exec_info[constants.ERRORS] = True
            exec_info[constants.ERRORS_INFO] = message

        return exec_info
