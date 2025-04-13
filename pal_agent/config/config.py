import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from pal_agent.utils.singleton import Singleton
from pal_agent import constants
from pal_agent.utils.file_utils import assemble_project_path, get_project_root
from pal_agent.utils.json_utils import load_json
from pal_agent.utils.dict_utils import kget

load_dotenv(verbose=True)

class Config(metaclass = Singleton):
    """
    Configuration class for the PAL Agent.
    """

    work_dir = './runs'
    env_short_name = 'palbot'

    DEFAULT_POST_ACTION_WAIT_TIME = 3

    def __init__(self):

        # Skill retrieval defaults
        self.skill_configs = {
            constants.SKILL_CONFIG_FROM_DEFAULT: True,
            constants.SKILL_CONFIG_RETRIEVAL: False,
            constants.SKILL_CONFIG_MAX_COUNT: 20,
            constants.SKILL_CONFIG_MODE: constants.SKILL_LIB_MODE_FULL, # FULL, BASIC, or NONE
            constants.SKILL_CONFIG_NAMES_DENY: [],
            constants.SKILL_CONFIG_NAMES_ALLOW: [],
            constants.SKILL_CONFIG_NAMES_BASIC: [],
            constants.SKILL_CONFIG_NAMES_OTHERS: None,
            constants.SKILL_CONFIG_LOCAL_PATH: None,
            constants.SKILL_CONFIG_REGISTERED_SKILLS: None,
        }


        # Memory parameters
        self.max_recent_steps = 5

        # Video
        self.video_fps = 8
        self.frames_per_slice = 1000

        self._set_dirs()

    def load_env_config(self, env_config_path):

        path = assemble_project_path(env_config_path)
        self.env_config = load_json(path)

        print(f'Env Config: {self.env_config}')

        self.env_name = kget(self.env_config, constants.ENVIRONMENT_NAME, default='')
        self.is_robot = kget(self.env_config, constants.ENVIRONMENT_IS_ROBOT)
        self.is_game = False

        self.skill_registry_name = kget(self.env_config, constants.SKILL_REGISTRY_KEY)
        self.skill_local_path = './res/skills/'
        self.skill_configs[constants.SKILL_CONFIG_LOCAL_PATH] = self.skill_local_path

        default_skill_configs = self.skill_configs.copy()

        skill_config = kget(self.env_config, constants.SKILL_CONFIGS, default=None)

        if skill_config is not None:
            for key in default_skill_configs.keys():
                skill_config[key] = kget(skill_config, key, default=default_skill_configs[key])
        else:
            skill_config = default_skill_configs

        self.skill_configs = skill_config


    def _set_dirs(self):

        """Setup directories needed for one system run."""
        self.root_dir = get_project_root()

        self.work_dir = assemble_project_path(os.path.join(self.work_dir, str(time.time())))
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)
