import os
import time
from typing import Dict, Any

from pal_agent.config.config import Config
from pal_agent.log.logger import Logger
from pal_agent import constants
from pal_agent.provider.palbot.palbot_interface import PalbotInterface
from pal_agent.provider.base_provider import BaseProvider
from pal_agent.environment.skill_registry import SkillRegistry
from pal_agent.memory.local_memory import LocalMemory
from pal_agent.provider.video.video_recorder import VideoRecordProvider

config = Config()
logger = Logger()


class Executor(BaseProvider):

    def __init__(self, *args,
                 env_manager: Any,
                 use_unpause_game: bool = False,
                 robot_interface: PalbotInterface = None,
                 **kwargs):

        super(Executor, self).__init__()
        self.gm = env_manager
        self.video_recorder = VideoRecordProvider(os.path.join(config.work_dir, 'video.mp4'))
        self.memory = LocalMemory(memory_path=config.work_dir, max_recent_steps=config.max_recent_steps)
        self.robot_interface = robot_interface
        pass


    @BaseProvider.write
    def __call__(self,
                 *args,
                 **kwargs) -> Dict[str, Any]:

        # > Pre-processing
        params = self.memory.recent_history.copy()

        # skill_steps = params.get(constants.SKILL_STEPS, [])
        # som_map = params.get(constants.SOM_MAP, {})
        # pre_screen_classification = params.get("pre_screen_classification", "")
        # screen_classification = params.get("screen_classification", "")
        skill_steps = pre_action = params.get("pre_action", "")[-1]

        # if config.is_game is True:

        #     self.gm.unpause_game()

        #     # @TODO: Rename GENERAL_GAME_INTERFACE
        #     if (pre_screen_classification.lower() == constants.GENERAL_GAME_INTERFACE and
        #             (screen_classification.lower() == constants.MAP_INTERFACE or
        #             screen_classification.lower() == constants.SATCHEL_INTERFACE) and pre_action):
        #         exec_info = self.gm.execute_actions([pre_action])

        # else:
        #     skill_steps = SkillRegistry.pre_process_skill_steps(skill_steps, som_map)

        skill_steps = SkillRegistry.pre_process_skill_steps(skill_steps, None)


        # >> Calling SKILL EXECUTION
        logger.info(f'>>> Calling SKILL EXECUTION')
        logger.info(f'Skill Steps: {skill_steps}')

        # Execute actions
        start_frame_id = self.video_recorder.get_current_frame_id()

        # if "towards" in pre_action:
        #     print()

        if config.is_robot is True:
            self.gm.audio_log(messages=skill_steps, is_skill=True)
            time.sleep(.1)
            # exec_info = self.robot_interface.execute_actions(skill_steps)
            exec_info = self.gm.execute_actions(skill_steps)

        else:
            exec_info = self.gm.execute_actions(skill_steps)

        # # > Post-processing
        logger.info(f'>>> Post skill execution sensing...')

        # Sense here to avoid changes in state after action execution completes
        mouse_x, mouse_y = -1, -1

        # cur_screenshot_timestamp = None
        # if config.is_robot == True:
        #     cur_screenshot_path, cur_screenshot_timestamp = self.robot_interface.capture_screen(save = True)
        # elif config.is_game == True:
        #     mouse_x, mouse_y = self.gm.get_mouse_position()
        #     cur_screenshot_path = self.gm.capture_screen()
        # else:
        #     mouse_x, mouse_y = self.gm.get_mouse_position()
        #     # First, check if interaction left the target environment
        #     if not self.gm.check_active_window():
        #         logger.warning(f"Target environment window is no longer active!")
        #         cur_screenshot_path = self.gm.get_out_screen()
        #     else:
        #         cur_screenshot_path = self.gm.capture_screen()

        end_frame_id = self.video_recorder.get_current_frame_id()

        logger.info(f'>>> Sensing done.')

        # if config.is_game == True:
        #     pause_flag = self.gm.pause_game(screen_classification.lower())
        #     logger.info(f'Pause flag: {pause_flag}')
        #     if not pause_flag:
        #         self.gm.pause_game(screen_type=None)

        # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.
        pre_action = exec_info[constants.LAST_SKILL] #+ '(' + exec_info[constants.LAST_PARAMETERS] + ')'  # @HERE
        # pre_screen_classification = screen_classification

        self.memory.add_recent_history_kv(constants.ACTION, pre_action)
        if exec_info[constants.ERRORS]:
            self.memory.add_recent_history_kv(constants.ACTION_ERROR, exec_info[constants.ERRORS_INFO])
        else:
            self.memory.add_recent_history_kv(constants.ACTION_ERROR,'')

        response = {
            f"{constants.START_FRAME_ID}": start_frame_id,
            f"{constants.END_FRAME_ID}": end_frame_id,
            # f"{constants.CUR_SCREENSHOT_PATH}": cur_screenshot_path,
            # f"{constants.CUR_SCREENSHOT_TIMESTAMP}": cur_screenshot_timestamp,
            # f"{constants.MOUSE_POSITION}" : (mouse_x, mouse_y),
            f"{constants.PRE_ACTION}": pre_action,
            f"{constants.EXEC_INFO}": exec_info,
            # "pre_screen_classification": pre_screen_classification,
        }

        self.memory.update_info_history(response)

        del params

        return response
