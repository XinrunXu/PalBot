import requests
import base64
import time
import os
import json
import ast

import numpy as np
from requests_toolbelt.multipart.decoder import MultipartDecoder
from requests_toolbelt import MultipartEncoder
import cv2

from pal_agent.config.config import Config
from pal_agent.log.logger import Logger

config = Config()
logger = Logger()

# Default values
robot_ip = 'localhost'
robot_port = 9080

IMAGE_MODE_RGB = 'RGB'
IMAGE_MODE_RGBD = 'RGB-D'


class Client:

    def __init__(self, ip, port):
        self.robot_ip = ip # currently the ip of my laptop
        self.robot_port = port
        self.base_url =  f'http://{self.robot_ip}:{self.robot_port}'


    def get_video_frame(self, mode = IMAGE_MODE_RGB, full_resolution=False):

        # In this function, we call the "video_frame" API to get rgb and depth data from robot, then store the data in files.
        url = f'{self.base_url}/video_frame'
        print("GET", url)

        response = requests.get(url, params={'mode': mode, "full_resolution": full_resolution})
        # print("response = ", response.content)
        # Decode the response
        decoder = MultipartDecoder.from_response(response)

        # Extract the JSON part
        json_part = decoder.parts[0]
        json_data = json.loads(json_part.text)

        # Decode RGB image
        encoded_rgb_image = json_data['encoded_rgb_image']
        decoded_rgb_image = base64.b64decode(encoded_rgb_image)
        rgb_image_np = np.frombuffer(decoded_rgb_image, np.uint8) # Convert bytes to numpy array
        rgb_image = cv2.imdecode(rgb_image_np, cv2.IMREAD_COLOR)
        # rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
        if rgb_image is None:
            rgb_image = cv2.imdecode(rgb_image_np, cv2.IMREAD_UNCHANGED)

        # Get frame id
        frame_id = json_data['frame_id']

        if mode == IMAGE_MODE_RGBD:
            # Decode depth image
            encoded_depth_image = json_data['encoded_depth_image']
            decoded_depth_image = base64.b64decode(encoded_depth_image)
            depth_image = np.frombuffer(decoded_depth_image, np.uint8) # Convert bytes to numpy array
            depth_image = cv2.imdecode(depth_image, cv2.IMREAD_COLOR)

            # Extract the depth_frame part
            depth_frame = decoder.parts[1]

        if mode == IMAGE_MODE_RGBD:
            return frame_id, rgb_image, depth_image, depth_frame
        else:
            return frame_id, rgb_image, None, None


    def post_action(self, skill, parameters = None, frame_id = None):
        url = f'{self.base_url}/action'
        print("POST", url, skill, parameters)

        json_data = {
            'skill': skill,
            'parameters': parameters,
            'frame_id': frame_id,
        }

        # Create MultipartEncoder object
        downloaded_depth_frame_path = os.path.join(config.work_dir, f'{frame_id}_downloaded_depth_frame.npy')
        if os.path.exists(downloaded_depth_frame_path):
            m = MultipartEncoder(
                fields={
                    'json_data': ('json_data', json.dumps(json_data), 'application/json'),
                    'depth_frame': ('depth_frame', open(downloaded_depth_frame_path, 'rb'), 'application/octet-stream')
                }
            )
        else:
            m = MultipartEncoder(
                fields={
                    'json_data': ('json_data', json.dumps(json_data), 'application/json'),
                    'depth_frame': ('depth_frame', None, 'application/octet-stream')
                }
            )

        response = requests.post(url, data = m, headers={'Content-Type': m.content_type})

        # @ TODO Agent: Handle the case when response shows that robot execution fails
        if response.json()['success']:
            result = (True, 'Done')
            logger.info(f"Action execution `{skill}`is successful.")
        else:
            logger.info(f"Action execution `{skill}` failed. Reason: {response.json()['error_message']}")
            result = (False, response.json()['error_message'])
        return result


    def parse_skills(self, code_str):
        # Parse the code string into an AST
        try:
            parsed_code = ast.parse(code_str)
        except SyntaxError as e:
            print(f"Failed to parse the code. Reason: {e} : {code_str}")
            raise e

        functions = []

        # Traverse the AST to find function definitions
        for node in parsed_code.body:
            if isinstance(node, ast.FunctionDef):
                # Collect function details
                function_info = {
                    "name": node.name,
                    "arguments": [arg.arg for arg in node.args.args],
                    "body": [ast.dump(statement) for statement in node.body]
                }
                functions.append(function_info)

        return functions


    def get_skills(self):

        url = f'{self.base_url}/skills'
        print("GET", url)

        response = requests.get(url)
        skill_lib_raw = response.json()
        skill_lib = []
        for skill in skill_lib_raw:

            # @TODO: check if we need to specify the parameters in function_expression too
            parsed_skill = self.parse_skills(skill_lib_raw[skill]['skill_code'])
            if len(skill_lib_raw[skill]['skill_code'].split('"""')) > 1:
                desc = skill_lib_raw[skill]['skill_code'].split('"""')[1]
            else:
                desc = skill_lib_raw[skill]['skill_code'].split("'''")[1]

            entry = {
                'function_expression' : skill + '()',
                'description': desc,
                'parameters': {"name": parsed_skill[0]['arguments']}
            }

            skill_lib.append(entry)

        return skill_lib


if __name__ == '__main__':

    print('Testing robot client')

    client = Client(robot_ip, robot_port)

    previous_frame = None  # Variable to store the previous frame
    frame_counter = 0  # Counter for saved frames

    target_dir = '../cli_frames/' + str(time.time())
    os.makedirs(target_dir, exist_ok=True)

    # while True:
    #     _, frame, _, _ = client.get_video_frame(full_resolution=False)

    #     to_save = True

    #     if previous_frame is None:
    #         to_save = True

    #     if previous_frame is not None:
    #         # Check if the current frame is different from the previous frame
    #         difference = cv2.absdiff(frame, previous_frame)
    #         if np.sum(difference) > 0:  # If there's any difference
    #             to_save = True

    #     if to_save is True:
    #         ts = time.time()
    #         filename = f"{target_dir}/frame_{frame_counter}_{ts}.jpg"
    #         cv2.imwrite(filename, frame)

    #     frame_counter += 1

    #     previous_frame = frame.copy()  # Update previous frame

    #     cv2.imshow("Frame", frame)

    #     # Press 'q' to exit the display loop
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    #     time.sleep(0.05)

    # cv2.destroyAllWindows()

    # skills = client.get_skills()

    client.post_action('speak', parameters = 'Hello, I am a robot.')
    time.sleep(5)

    #client.post_action('left_shoulder_up')
    #time.sleep(5)
    #client.post_action('left_shoulder_down')

    print()
