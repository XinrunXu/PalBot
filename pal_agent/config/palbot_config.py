
from dataclasses import dataclass
from typing import List, Tuple
import math
from dataclasses import fields
from typing import Any


@dataclass
class JointConfigDegree:
    name: str
    motor_id: int
    sign: int
    initial_degree: float
    limit_degree: Tuple[float, float]

# 45, 90, 135, 180, 225, 270, 315
# lets say move up and move right as positive directions for right arms
ROBOT_CONFIG_degree: List[JointConfigDegree] = [
    JointConfigDegree("r_shoulder_pitch", 0,  1, 250.0, ( 200.0, 400.0)),
    JointConfigDegree("r_shoulder_roll",  1,  1, 225.0, (  80.0, 280.0)),
    JointConfigDegree("r_elbow_yaw",      2,  1, 225.0, (  30.0, 330.0)),
    JointConfigDegree("r_elbow_roll",     3,  1, 270.0, (  80.0, 280.0)),
    JointConfigDegree("r_wrist_roll",     4,  1, 180.0, (  30.0, 330.0)),
    JointConfigDegree("r_gripper",        5,  1, 225.0, ( 135.0, 225.0)), # open
##################################################################################
    JointConfigDegree("l_shoulder_pitch", 6, -1, 110.0, (-100.0, 160.0)),
    JointConfigDegree("l_shoulder_roll",  7,  1, 135.0, (  90.0,  270.0)),
    JointConfigDegree("l_elbow_yaw",      8,  1, 135.0, (  30.0, 330.0)),
    JointConfigDegree("l_elbow_roll",     9,  1,  90.0, (  90.0,  270.0)),
    JointConfigDegree("l_wrist_roll",    10,  1, 180.0, (  30.0, 330.0)),
    JointConfigDegree("l_gripper",       11,  1, 225.0, ( 135.0, 225.0)),
##############################################  head  #############################
    JointConfigDegree("head_yaw",        12,  1, 180.0, (  30.0, 330.0)),
    JointConfigDegree("head_pitch",      13, -1, 180.0, ( 90.0, 270.0)), # looking up as positive
]


@dataclass
class JointConfigRad:
    name: str
    motor_id: int
    sign: int
    initial_rad: float
    limit_rad: Tuple[float, float]


def convert_degree_to_rad(config_deg: List[JointConfigDegree]) -> List[JointConfigRad]:
    return [
        JointConfigRad(
            name=joint.name,
            motor_id=joint.motor_id,
            sign=joint.sign,
            initial_rad=math.radians(joint.initial_degree),
            limit_rad=(
                math.radians(joint.limit_degree[0]),
                math.radians(joint.limit_degree[1])
            )
        )
        for joint in config_deg
    ]


def pretty_print_joint_config(config_list: List[Any]) -> None:
    if not config_list:
        print("ROBOT_CONFIG: List[] = []")
        return

    cls = config_list[0].__class__
    field_names = [f.name for f in fields(cls)]
    field_widths = [len(name) for name in field_names]

    # calculate the max width for each field
    for joint in config_list:
        for i, f in enumerate(fields(joint)):
            val = getattr(joint, f.name)
            if isinstance(val, float):
                val_str = f"{val:.2f}"
            elif isinstance(val, tuple):
                val_str = f"({val[0]:.2f}, {val[1]:.2f})"
            elif isinstance(val, str):
                val_str = f"\"{val}\""
            else:
                val_str = str(val)
            field_widths[i] = max(field_widths[i], len(val_str))

    print(f"ROBOT_CONFIG: List[{cls.__name__}] = [")
    for joint in config_list:
        values = []
        for i, f in enumerate(fields(joint)):
            val = getattr(joint, f.name)
            if isinstance(val, float):
                val_str = f"{val:.2f}"
            elif isinstance(val, tuple):
                val_str = f"({val[0]:.2f}, {val[1]:.2f})"
            elif isinstance(val, str):
                val_str = f"\"{val}\""
            else:
                val_str = str(val)
            values.append(val_str.ljust(field_widths[i]))

        print(f"    {cls.__name__}({', '.join(values)}),")
    print("]")



def main():
    # from . import ROBOT_CONFIG

    names = [j.name for j in ROBOT_CONFIG_degree]
    initial_degrees = [j.initial_degree for j in ROBOT_CONFIG_degree]


    ROBOT_CONFIG_rad = convert_degree_to_rad(ROBOT_CONFIG_degree)
    pretty_print_joint_config(ROBOT_CONFIG_rad)


    ids = [j.motor_id for j in ROBOT_CONFIG_rad]
    initials = [j.initial_rad for j in ROBOT_CONFIG_rad]


def construct_full_pose(
    right_arm_pose: List[float],  # len=5
    r_gripper: float,
    head_yaw: float,
    head_pitch: float,
) -> List[float]:
    assert len(right_arm_pose) == 5, "right_arm_pose should be len=5"
    full_pose = right_arm_pose.copy()
    full_pose.append(r_gripper)
    for i in range(5):
        right_angle = right_arm_pose[i]
        mirrored = 180.0 - right_angle
        left_angle = mirrored
        full_pose.append(left_angle)
    full_pose.append(r_gripper)
    full_pose.append(head_yaw)
    full_pose.append(head_pitch)
    return full_pose


def get_dual_arm_pos(right_arm_pose):
    r_gripper = 225.0
    head_yaw = 180.0
    head_pitch = 180.0

    full_pose_deg = construct_full_pose(right_arm_pose, r_gripper, head_yaw, head_pitch)
    full_pose_rad = [math.radians(angle) for angle in full_pose_deg]
    return full_pose_rad


if __name__ == "__main__":
    main()

    full_pose_rad = get_dual_arm_pos(right_arm_pose = [3.132, 3.214, 3.263, 3.26 , 3.146])