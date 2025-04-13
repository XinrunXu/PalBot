from copy import deepcopy
from dotenv import load_dotenv

load_dotenv()

from pal_agent import constants
from pal_agent.log.logger import Logger
from pal_agent.config.config import Config
from pal_agent.utils.file_utils import read_resource_file
from pal_agent.utils.json_utils import parse_semi_formatted_text
from pal_agent.environment.skill_registry_factory import SkillRegistryFactory
from pal_agent.provider.llm.llm_factory import LLMFactory
from pal_agent.provider.palbot.palbot_interface import PalbotInterface
from pal_agent.gameio.game_manager import GameManager
from pal_agent.module.executor import Executor
from pal_agent.memory.local_memory import LocalMemory

config = Config()
logger = Logger()

class PipelineRunner:

    def __init__(self,
                llm_provider_config_path: str = None,
                embed_provider_config_path: str = None,
                task_description: str = None):

        self.llm_provider_config_path = llm_provider_config_path
        self.embed_provider_config_path = embed_provider_config_path
        self.task_description = task_description

        self.success_flag = False

        self.pipeline_info = {}

        self.count = 0

        self.set_internal_params()

    def set_internal_params(self):

        self.pipeline_info[constants.PREVIOUS_ACTION_CALL] = "This is the 1st turn of the pipeline. So the previous action call is none."
        self.pipeline_info[constants.PREVIOUS_ACTION_CODE] = "This is the 1st turn of the pipeline. So the previous action code is none."
        self.pipeline_info[constants.EXECUTING_ACTION_ERROR] = "This is the 1st turn of the pipeline. So the executing action error is none."
        self.pipeline_info[constants.KEY_REASON_OF_LAST_ACTION] = "This is the 1st turn of the pipeline. So the key reason of last action is none."
        self.pipeline_info[constants.SUCCESS_DETECTION] = "This is the 1st turn of the pipeline. So the success detection is false."
        self.pipeline_info[constants.PREVIOUS_ACTION] = "This is the 1st turn of the pipeline. So the previous action is none."
        self.pipeline_info[constants.PREVIOUS_ACTION_RESULT] = "This is the 1st turn of the pipeline. So the previous action result is none."
        self.pipeline_info[constants.TASK_DESCRIPTION] = self.task_description
        self.pipeline_info[constants.SUBTASK_DESCRIPTION] = "This is the 1st turn of the pipeline. So the sub task description is not reasoning yet."
        self.pipeline_info[constants.SUBTASK_REASONING] = "This is the 1st turn of the pipeline. So the sub task reasoning is not reasoning yet."
        self.pipeline_info[constants.HISTORY_SUMMARY] = "This is the 1st turn of the pipeline. So the history summary is none."

        lf = LLMFactory()
        self.llm_provider, self.embedding_provider = lf.create(self.llm_provider_config_path)

        # Init memory
        self.memory = LocalMemory(memory_path=config.work_dir,
                                  max_recent_steps=config.max_recent_steps)
        # self.memory.load(config.memory_load_path) # !!! zan shi bu hui yong dao yi qian de memory

        srf = SkillRegistryFactory()
        srf.register_builder(config.env_short_name, config.skill_registry_name)
        self.skill_registry = srf.create(config.env_short_name, skill_configs=config.skill_configs, embedding_provider=self.embedding_provider)
        logger.info(f"Skill registry: {self.skill_registry}")

        self.gm = GameManager(env_name=config.env_name,
                              embedding_provider=self.embedding_provider,
                              llm_provider=self.llm_provider,
                              skill_registry=self.skill_registry,
                             )

        skills = self.gm.retrieve_skills(query_task=self.task_description,
                                    skill_num=config.skill_configs[constants.SKILL_CONFIG_MAX_COUNT],
                                    screen_type=constants.GENERAL_GAME_INTERFACE)

        self.skill_library = self.gm.get_skill_information(skills, False)
        self.pipeline_info[constants.SKILL_LIBRARY] = self.skill_library
        logger.info(f"Skill library retrieved: {self.skill_library}")

        self.palbot_interface = PalbotInterface()
        self.gm.audio_log("Hello, I am PALBOT. How can I assist you today?") #!!! audio log
        # self.palbot_interface.audio_log(self.task_description)

        # self.skill_library = self.palbot_interface.retrieve_skill_library()
        # self.pipeline_info[constants.SKILL_LIBRARY] = self.skill_library
        # transformed_skill_library = self.skill_registry.transform_skill_library_format(self.skill_library)

        # Init skill execute provider
        self.skill_execute = Executor(env_manager=self.gm, robot_interface=self.palbot_interface)


    def run(self):

        logger.info(f">>> Task description: {self.task_description}")
        logger.info(f">>> Agent Loop {self.count}")

        while not self.success_flag:
            try:

                self.run_information_gathering()

                self.run_self_reflection()
                if self.success_flag:
                    logger.info("Task completed successfully.")
                    break

                self.run_task_inference()

                self.run_action_planning()

                self.execute_action()

                self.memory.save()

                self.count += 1
                logger.info(f"---------------- Count Turn: {self.count} ----------------")

                if self.count > constants.MAX_TURN_COUNT:
                    logger.info("Max turn count reached. Exiting.")
                    break

            except KeyboardInterrupt:
                logger.info("Pipeline interrupted by user.")
                break

        self.pipeline_shutdown()


    def pipeline_shutdown(self):
        logger.info(">>> Bye Bye <<<")


    def run_information_gathering(self):

        logger.info("Running information gathering...")

        # Information gathering preprocess
        image_introduction = [
            {
            constants.IMAGE_INTRO: "This is the end image from the last action performed.",
            constants.IMAGE_PATH: constants.PICTURE_TEST_FILE_PATH_3,
            constants.ASSISTANT: ""
            }]

        self.pipeline_info[constants.IMAGE_INTRODUCTION] = image_introduction

        information_gathering_prompt_template = read_resource_file(constants.INFORMATION_GATHERING_PROMPT_FILE_PATH)
        information_gathering_prompt = self.llm_provider.assemble_prompt(template_str=information_gathering_prompt_template, params=self.pipeline_info)

        logger.info(f"Information Gathering Prompt: {information_gathering_prompt}")

        # Information gathering llm process

        response, _ = self.llm_provider.create_completion(messages=information_gathering_prompt)
        processed_response = parse_semi_formatted_text(response)
        logger.info(f"Information Gathering Response: {processed_response}")

        # Information gathering postprocess
        if processed_response:
            self.pipeline_info[constants.IMAGE_DESCRIPTION] = processed_response.get(constants.IMAGE_DESCRIPTION)
            self.pipeline_info[constants.TARGET_NAME] = processed_response.get(constants.TARGET_NAME)
            self.pipeline_info[constants.REASONING_FOR_TARGET] = processed_response.get(constants.REASONING_FOR_TARGET)
        else:
            logger.warning("No valid response from information gathering.")
            logger.debug("Response: ", response, " processed_response:", processed_response)

    def run_self_reflection(self):
        logger.info("Running self reflection...")

        # Self reflection preprocess
        image_introduction = [
            {
            constants.IMAGE_INTRO: "This is the image before the last action performed.",
            constants.IMAGE_PATH: constants.PICTURE_TEST_FILE_PATH_3,
            constants.ASSISTANT: ""
            },{
            constants.IMAGE_INTRO: "This is the image after the last action performed.",
            constants.IMAGE_PATH: constants.PICTURE_TEST_FILE_PATH_1,
            constants.ASSISTANT: ""
            }
        ]

        self.pipeline_info[constants.IMAGE_INTRODUCTION] = image_introduction

        self_reflection_prompt_template = read_resource_file(constants.SELF_REFLECTION_PROMPT_FILE_PATH)
        self_reflection_prompt = self.llm_provider.assemble_prompt(template_str=self_reflection_prompt_template, params=self.pipeline_info)

        logger.info(f"Self Reflection Prompt: {self_reflection_prompt}")

        # Self reflection llm process
        response, _ = self.llm_provider.create_completion(messages=self_reflection_prompt)
        processed_response = parse_semi_formatted_text(response)
        logger.info(f"Self Reflection Response: {processed_response}")

        # Self reflection postprocess
        if processed_response:
            self.pipeline_info[constants.SELF_REFLECTION_REASONING] = processed_response.get(constants.SELF_REFLECTION_REASONING)
            self.pipeline_info[constants.SUCCESS_DETECTION] = processed_response.get(constants.SUCCESS_DETECTION)
        else:
            logger.warning("No valid response from self reflection.")
            logger.debug("Response: ", response, " processed_response:", processed_response)

        # Check if the task is successful
        if self.pipeline_info[constants.SUCCESS_DETECTION] == "SUCCESSFUL":
            self.success_flag = True
            logger.info("Task completed successfully.")


    def run_task_inference(self):
        logger.info("Running task inference...")

        # Task inference preprocess
        image_introduction = [
            {
            constants.IMAGE_INTRO: "This is the image before the last action performed.",
            constants.IMAGE_PATH: constants.PICTURE_TEST_FILE_PATH_3,
            constants.ASSISTANT: ""
            },
            {
            constants.IMAGE_INTRO: "This is the image after the last action performed.",
            constants.IMAGE_PATH: constants.PICTURE_TEST_FILE_PATH_1,
            constants.ASSISTANT: ""
            }
        ]

        self.pipeline_info[constants.IMAGE_INTRODUCTION] = image_introduction

        self_reflection_prompt_template = read_resource_file(constants.TASK_INFERENCE_PROMPT_FILE_PATH)
        self_reflection_prompt = self.llm_provider.assemble_prompt(template_str=self_reflection_prompt_template, params=self.pipeline_info)

        logger.info(f"Task Inference Prompt: {self_reflection_prompt}")

        # Task inference llm process
        response, _ = self.llm_provider.create_completion(messages=self_reflection_prompt)
        processed_response = parse_semi_formatted_text(response)
        logger.info(f"Task Inference Response: {processed_response}")

        # Task inference postprocess
        if processed_response:
            self.pipeline_info[constants.HISTORY_SUMMARY] = processed_response.get(constants.HISTORY_SUMMARY)
            self.pipeline_info[constants.SUBTASK_REASONING] = processed_response.get(constants.SUBTASK_REASONING)
            self.pipeline_info[constants.SUBTASK_DESCRIPTION] = processed_response.get(constants.SUBTASK_DESCRIPTION)
        else:
            logger.warning("No valid response from task inference.")
            logger.debug("Response: ", response, " processed_response:", processed_response)


    def run_action_planning(self):
        logger.info("Running action planning...")

        # Action planning preprocess
        image_introduction = [
            {
            constants.IMAGE_INTRO: "This is the image before the last action performed.",
            constants.IMAGE_PATH: constants.PICTURE_TEST_FILE_PATH_3,
            constants.ASSISTANT: ""
            },
            {
            constants.IMAGE_INTRO: "This is the image after the last action performed.",
            constants.IMAGE_PATH: constants.PICTURE_TEST_FILE_PATH_1,
            constants.ASSISTANT: ""
            }
        ]
        self.pipeline_info[constants.IMAGE_INTRODUCTION] = image_introduction

        action_planning_prompt_template = read_resource_file(constants.ACTION_PLANNING_PROMPT_FILE_PATH)
        action_planning_prompt = self.llm_provider.assemble_prompt(template_str=action_planning_prompt_template, params=self.pipeline_info)

        logger.info(f"Action Planning Prompt: {action_planning_prompt}")

        # Action planning llm process
        response, _ = self.llm_provider.create_completion(messages=action_planning_prompt)
        processed_response = parse_semi_formatted_text(response)
        logger.info(f"Action Planning Response: {processed_response}")

        # Action planning postprocess
        if processed_response:
            self.pipeline_info[constants.DECISION_MAKING_REASONING] = processed_response.get(constants.DECISION_MAKING_REASONING)
            self.pipeline_info[constants.ACTIONS] = processed_response.get(constants.ACTIONS)

            self.memory.add_recent_history_kv(key=constants.ACTION, info=self.pipeline_info[constants.ACTIONS])
            self.memory.add_recent_history_kv(key=constants.SKILL_STEPS, info=str(self.pipeline_info[constants.ACTIONS]))

            self.pipeline_info[constants.KEY_REASON_OF_LAST_ACTION] = processed_response.get(constants.KEY_REASON_OF_LAST_ACTION)
        else:
            logger.warning("No valid response from action planning.")
            logger.debug("Response: ", response, " processed_response:", processed_response)


    def execute_action(self):

        self.skill_execute()


if __name__ == "__main__":

    config.load_env_config('./conf/env_config_palbot.json')

    # Example usage
    llm_provider_config_path = "./conf/openai_config.json"
    embed_provider_config_path = "./conf/openai_config.json"
    task_description = "This is a test task description: NEVER SAY TASK is SUCCESSFUL."
    pipeline_runner = PipelineRunner(
                        llm_provider_config_path=llm_provider_config_path,
                        embed_provider_config_path=embed_provider_config_path,
                        task_description=task_description)


    pipeline_runner.run()  # Start the pipeline
    print("Pipeline finished running.")