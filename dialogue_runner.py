from dotenv import load_dotenv
load_dotenv()

from pal_agent.log.logger import Logger
from pal_agent.config.config import Config
from pal_agent.environment.palbot.skill_registry import register_skill
from hardware.audio_manager import AudioManager
from hardware.multi_dynamixel_controller import MultiDynamixelController
from pal_agent.provider.audio.asr_provider import AudioTranscriber
from pal_agent.provider.audio.tts_provider import TextToSpeechProvider
from hardware.wheel_controller import WheelController
from pal_agent.provider.llm.llm_factory import LLMFactory
from pal_agent.environment.skill_registry_factory import SkillRegistryFactory
from pal_agent.config.config import Config
from pal_agent.log.logger import Logger
from pal_agent.gameio.game_manager import GameManager
from pal_agent import constants
from pal_agent.provider.palbot.palbot_interface import PalbotInterface
from pal_agent.module.executor import Executor
from pal_agent.memory.local_memory import LocalMemory
from pal_agent.utils.file_utils import read_resource_file
from pal_agent.utils.json_utils import parse_semi_formatted_text

config = Config()
logger = Logger()


class DialogueRunner:

    def __init__(self,
                llm_provider_config_path: str = None,
                embed_provider_config_path: str = None):

        self.llm_provider_config_path = llm_provider_config_path
        self.embed_provider_config_path = embed_provider_config_path

        self.success_flag = False

        self.pipeline_info = {}
        self.count = 0

        self.audio_manager = AudioManager()
        self.audio_manager.init()
        self.tts_processor = TextToSpeechProvider()
        self.asr_transcriber = AudioTranscriber()
        # self.multi_dynamixel_controller = MultiDynamixelController() # !!!
        # self.wheel_controller = WheelController() # !!!

        lf = LLMFactory()
        self.llm_provider, self.embedding_provider = lf.create(self.llm_provider_config_path)

        self.memory = LocalMemory(memory_path=config.work_dir,
                                  max_recent_steps=config.max_recent_steps)

        srf = SkillRegistryFactory()
        srf.register_builder(config.env_short_name, config.skill_registry_name)
        self.skill_registry = srf.create(config.env_short_name, skill_configs=config.skill_configs, embedding_provider=self.embedding_provider)
        logger.info(f"Skill registry: {self.skill_registry}")

        self.gm = GameManager(env_name=config.env_name,
                              embedding_provider=self.embedding_provider,
                              llm_provider=self.llm_provider,
                              skill_registry=self.skill_registry,
                             )

        skills = self.gm.retrieve_skills(query_task= "",
                                    skill_num=config.skill_configs[constants.SKILL_CONFIG_MAX_COUNT],
                                    screen_type=constants.GENERAL_GAME_INTERFACE)

        self.skill_library = self.gm.get_skill_information(skills, False)

        self.pipeline_info[constants.SKILL_LIBRARY] = self.skill_library
        logger.info(f"Skill library retrieved: {self.skill_library}")

        hello_audio = "Hello! I am PALBOT. How can I help you today?"

        self.palbot_interface = PalbotInterface()
        self.gm.audio_log(hello_audio)
        self.pipeline_info["palbot_last_reply"] = hello_audio

        self.skill_execute = Executor(env_manager=self.gm, robot_interface=self.palbot_interface)


    def run(self):
        logger.info("Starting dialogue runner...")

        while not self.success_flag:

            action_info = ["listen()"]
            self.memory.add_recent_history_kv(key=constants.PRE_ACTION, info=action_info)
            response = self.skill_execute()

            exec_info = response.get(constants.EXEC_INFO)
            user_reply = exec_info.get(constants.LAST_SKILL)
            user_reply = user_reply.split("#")[1].strip()
            logger.info(f"User reply: {user_reply}")

            self.pipeline_info["user_last_reply"] = user_reply

            self.generate_palbot_reply(self)
            palbot_reply = self.pipeline_info.get("palbot_reply")

            self.gm.audio_log(palbot_reply)

    def generate_palbot_reply(self, user_reply):
        logger.info(f"Generating PALBOT reply for: {user_reply}")

        image_introduction = [
            {
            constants.IMAGE_INTRO: "Don't pay attention to the image, just focus on my words.",
            constants.IMAGE_PATH: constants.IMAGE_TEST_FILE_PATH,
            constants.ASSISTANT: ""
            }]

        self.pipeline_info[constants.IMAGE_INTRODUCTION] = image_introduction

        # Generate a response using the LLM
        dialogue_prompt_template = read_resource_file(constants.DIALOGUE_PROMPT_FILE_PATH)
        dialogue_prompt = self.llm_provider.assemble_prompt(template_str=dialogue_prompt_template, params=self.pipeline_info)

        logger.info(f"Dialogue prompt: {dialogue_prompt}")

        response, _ = self.llm_provider.create_completion(messages=dialogue_prompt)
        processed_response = parse_semi_formatted_text(response)
        logger.info(f"Dialogue response: {processed_response}")

        if processed_response:

            self.pipeline_info["previous_conversations_summary"] = processed_response.get("previous_conversations_summary")
            self.pipeline_info["palbot_reply"] = processed_response.get("palbot_reply")

        else:
            logger.warning("No response generated.")
            self.pipeline_info["palbot_reply"] = "I'm sorry, I didn't understand that."



if __name__ == "__main__":

    config.load_env_config('./conf/env_config_palbot.json')

    llm_provider_config_path = "./conf/openai_config.json"
    embed_provider_config_path = "./conf/openai_config.json"

    dialogue_runner = DialogueRunner(
        llm_provider_config_path=llm_provider_config_path,
        embed_provider_config_path=embed_provider_config_path
    )

    dialogue_runner.run()

