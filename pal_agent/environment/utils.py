from typing import Dict


from pal_agent.environment.skill import Skill

def serialize_skills(skills: Dict[str, Skill]) -> Dict[str, Dict]:
    serialized_skills = {name: skill.to_dict() for name, skill in skills.items()}
    return serialized_skills


def deserialize_skills(serialized_skills: Dict[str, Dict]) -> Dict[str, Skill]:
    return {name: Skill.from_dict(skill) for name, skill in serialized_skills.items()}
