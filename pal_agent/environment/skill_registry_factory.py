import importlib

from pal_agent.utils import Singleton
from pal_agent.environment.palbot.atomic_skills import *  # !!!

class SkillRegistryFactory(metaclass=Singleton):

    def __init__(self):

        self._builders = {}


    def register_builder(self, key, builder_str):

        print(f"Registering builder for key: {key} with class: {builder_str}")

        try:

            # Split the module and class name
            module_name, class_name = builder_str.rsplit('.', 1)

            print(f"Module name: {module_name}, Class name: {class_name}")

            # Dynamically import the module
            module = importlib.import_module(module_name)

            print(f"Module imported: {module}")

            # Get the class from the module
            builder_class = getattr(module, class_name)

            print(f"Builder class: {builder_class}")

            self._builders[key] = builder_class

        except (ImportError, AttributeError) as e:
            raise ValueError(f"Class '{class_name}' not found in module '{module_name}'") from e


    # A SkillRegistry takes a skill_config and an embedding provider
    def create(self, key, **kwargs):

        builder = self._builders.get(key)

        if not builder:
            raise ValueError(key)

        return builder(**kwargs)
