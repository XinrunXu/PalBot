# Hardware parameters
ROBOT_DEVICE_NAME = '/dev/ttyUSB1'
ROBOT_DEVICE_PORT = "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FT763GYX-if00-port0"
ROBOT_FREQ = 8
ROBOT_VELOCITY = 80
ROBOT_WHEEL_PORT = "/dev/ttyACM0"
WHEEL_LINEAR_SPEED = 200
WHEEL_ANGULAR_SPEED = 30

# Audio parameters
AUDIO_TEST_FILE_PATH = "./res/file/openai-fm-verse-medieval-knight.wav"
SPEAKER_NAME = 'UACDemoV1.0'
MICROPHONE_NAME = 'SF-558'
TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "sage"
TTS_INSTRUCTIONS =  """Affect/personality: A cheerful guide \n\nTone: Friendly, clear, and reassuring, creating a calm atmosphere and making the listener feel confident and comfortable.\n\nPronunciation: Clear, articulate, and steady, ensuring each instruction is easily understood while maintaining a natural, conversational flow.\n\nPause: Brief, purposeful pauses after key instructions (e.g., \"cross the street\" and \"turn right\") to allow time for the listener to process the information and follow along.\n\nEmotion: Warm and supportive, conveying empathy and care, ensuring the listener feels guided and safe throughout the journey."""
ASR_MODEL = "gpt-4o-mini-transcribe"

PICTURE_TEST_FILE_PATH_1 = './res/file/animal1.jpeg'
PICTURE_TEST_FILE_PATH_2 = './res/file/animal2.jpeg'
PICTURE_TEST_FILE_PATH_3 = './res/file/bottle.jpg'

OPENAI_TEMPRATURE = 1.0
OPENAI_SEED = 42
OPENAI_MAX_TOKENS = 1024
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_CHAT_MODEL = "gpt-4o-2024-05-13"

MAX_TURN_COUNT = 50

INFORMATION_GATHERING_PROMPT_FILE_PATH = './res/prompts/information_gathering.prompt'
SELF_REFLECTION_PROMPT_FILE_PATH = './res/prompts/self_reflection.prompt'
TASK_INFERENCE_PROMPT_FILE_PATH = './res/prompts/task_inference.prompt'
ACTION_PLANNING_PROMPT_FILE_PATH = './res/prompts/action_planning.prompt'

IMAGE_INTRODUCTION = 'image_introduction'
IMAGE_INTRO = 'image_intro'
IMAGE_PATH = 'image_path'
ASSISTANT = 'assistant'
IMAGE_RESOLUTION = 'image_resolution'
IMAGE_RESIZE = 'image_resize'
TASK_DESCRIPTION = 'task_description'
SUBTASK_DESCRIPTION = 'sub_ask_description'
PREVIOUS_ACTION_CALL = 'previous_action_call'
PREVIOUS_ACTION_CODE = 'previous_action_code'
PREVIOUS_ACTION_RESULT = 'previous_action_result'
EXECUTING_ACTION_ERROR = 'executing_action_error'
PREVIOUS_ACTION = 'previous_action'
KEY_REASON_OF_LAST_ACTION = 'key_reason_of_last_action'
SUCCESS_DETECTION = 'success_detection'
SKILL_LIBRARY = 'skill_library'
SELF_REFLECTION_REASONING = 'self_reflection_reasoning'
SUBTASK_DESCRIPTION = 'subtask_description'
SUBTASK_REASONING = 'subtask_reasoning'
IMAGE_DESCRIPTION = 'image_description'
TARGET_NAME = 'target_name'
REASONING_FOR_TARGET = 'reasoning_for_target'
HISTORY_SUMMARY = 'history_summary'
DECISION_MAKING_REASONING = 'decision_making_reasoning'
ACTIONS = 'actions'
ACTION = 'action'
TASK_GUIDANCE = 'task_guidance'
DIALOGUE = 'dialogue'
LAST_TASK_GUIDANCE = 'last_task_guidance'
SKILL_STEPS = 'skill_steps'
ACTION_ERROR = 'action_error'
PRE_ACTION = 'pre_action'

# Video capture keys
START_FRAME_ID = 'start_frame_id'
END_FRAME_ID = 'end_frame_id'

# Skill-related config keys
SKILL_CONFIGS = "skill_configs"
SKILL_CONFIG_FROM_DEFAULT = "skill_from_default"
SKILL_CONFIG_RETRIEVAL = "skill_retrieval"
SKILL_CONFIG_MAX_COUNT = "skill_num"
SKILL_CONFIG_MODE = "skill_mode"
SKILL_CONFIG_NAMES_DENY = "skill_names_deny"
SKILL_CONFIG_NAMES_ALLOW = "skill_names_allow"
SKILL_CONFIG_NAMES_BASIC = "skill_names_basic"
SKILL_CONFIG_NAMES_OTHERS = "skill_names_others"
SKILL_CONFIG_LOCAL_PATH = "skill_local_path"
SKILL_CONFIG_REGISTERED_SKILLS = 'skills_registered'

# Skill-related keys
SKILL_CODE_HASH_KEY = "skill_code_base64"
SKILL_FULL_LIB_FILE = "skill_lib.json"
SKILL_BASIC_LIB_FILE = "skill_lib_basic.json"
SKILL_LIB_MODE_BASIC = 'Basic'
SKILL_LIB_MODE_FULL = 'Full'
SKILL_LIB_MODE_NONE = None

# Env-specific skill list configs
SKILL_CONFIG_NAMES_MOVEMENT = "skill_names_movement"
SKILL_CONFIG_NAMES_MAP = "skill_names_map"
SKILL_CONFIG_NAMES_TRADE = "skill_names_trade"
SKILL_REGISTRY_KEY = 'skill_registry_name'

COLOURS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
}

ACTION_GUIDANCE = 'action_guidance'
ENVIRONMENT_NAME = 'env_name'
USER_NAME = 'user_name'
ENVIRONMENT_IS_ROBOT = 'is_robot'
GENERAL_GAME_INTERFACE = 'general game interface without any menu'

# Local memory
AUGMENTED_IMAGES_MEM_BUCKET = 'augmented_image'
IMAGES_MEM_BUCKET = 'image'
SKIIL_LIB_MEM_BUCKET = 'skill_library'
SUMMARIZATION_MEM_BUCKET = 'summarization'

# Keys in exec_info
EXEC_INFO = 'exec_info'
EXECUTED_SKILLS = 'executed_skills'
LAST_SKILL = 'last_skill'
LAST_PARAMETERS = 'last_parameters'
ERRORS = 'errors'
ERRORS_INFO = 'errors_info'

CUR_SCREENSHOT_TIMESTAMP = 'cur_screenshot_timestamp'
INVALID_BBOX = 'invalid_bbox'