from pal_agent.provider.llm.openai_provider import OpenAIProvider
from pal_agent.utils import Singleton

class LLMFactory(metaclass=Singleton):

    def __init__(self):
        self._builders = {}


    def create(self, llm_provider_config_path, **kwargs):

        llm_provider = None
        embed_provider = None

        key = llm_provider_config_path

        llm_provider = OpenAIProvider()
        llm_provider.init_provider(llm_provider_config_path)
        embed_provider = llm_provider


        if not llm_provider or not embed_provider:
            raise ValueError(key)

        return llm_provider, embed_provider
