import inspect
import base64
from typing import List, Any

from pal_agent import constants
from pal_agent.utils.singleton import Singleton
from pal_agent.environment.skill_registry import SkillRegistry
from pal_agent.environment.skill import Skill

skill_configs = {
    constants.SKILL_CONFIG_FROM_DEFAULT: True,
    constants.SKILL_CONFIG_RETRIEVAL: False,
    constants.SKILL_CONFIG_MAX_COUNT: 20,
    constants.SKILL_CONFIG_MODE: constants.SKILL_LIB_MODE_FULL,
    constants.SKILL_CONFIG_NAMES_DENY: [],
    constants.SKILL_CONFIG_NAMES_ALLOW: [],
    constants.SKILL_CONFIG_NAMES_BASIC: [],
    constants.SKILL_CONFIG_NAMES_OTHERS: None,
    constants.SKILL_CONFIG_LOCAL_PATH: None,
    constants.SKILL_CONFIG_REGISTERED_SKILLS: None,
}

SKILLS = {}
def register_skill(name):
    def decorator(skill):

        skill_name = name
        skill_function = skill
        skill_code = inspect.getsource(skill)

        # Remove unnecessary annotation in skill library
        if f"@register_skill(\"{name}\")\n" in skill_code:
            skill_code = skill_code.replace(f"@register_skill(\"{name}\")\n", "")

        skill_code_base64 = base64.b64encode(skill_code.encode('utf-8')).decode('utf-8')

        skill_ins = Skill(skill_name,
                       skill_function,
                       "" , # skill_embedding
                       skill_code,
                       skill_code_base64)
        SKILLS[skill_name] = skill_ins

        return skill_ins

    return decorator


class RobotSkillRegistry(SkillRegistry, metaclass=Singleton):

    def __init__(self,
                 *args,
                 skill_configs: dict[str, Any]  = skill_configs,
                 embedding_provider=None,
                 **kwargs):

        if skill_configs[constants.SKILL_CONFIG_REGISTERED_SKILLS] is None:
            skill_configs[constants.SKILL_CONFIG_REGISTERED_SKILLS] = SKILLS

        super(RobotSkillRegistry, self).__init__(skill_configs=skill_configs,
                                                  embedding_provider=embedding_provider)
