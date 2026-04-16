from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterFile, ParameterValue
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os


# TODO check if we actually need all of this or can do anything with these parameters


def generate_launch_description():
    # declare launch arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Start robot with simulated hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="If the robot is running in simulation, use the published clock",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "tf_prefix",
            default_value="",
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the hardware robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_description_package",
            default_value="togo_description",
            description="The package to find the robot description.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_description_file",
            default_value="togo.urdf.xacro",
            description="The name of the robot description file. "
            "Must be in the 'urdf' folder of the description package.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "extra_xacro_args",
            default_value="",
            description="Extra args to add for making a robot description. "
            "Should be in the format of 'arg1:=value1 arg2:=value2'",
        )
    )

    # initialize arguments
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    use_sim_time = LaunchConfiguration("use_sim_time")
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")
    robot_description_package = LaunchConfiguration("robot_description_package")
    robot_description_file = LaunchConfiguration("robot_description_file")
    extra_xacro_args = LaunchConfiguration("extra_xacro_args")

    # common launch args shared across different nodes
    common_launch_args = {
        "use_fake_hardware": use_fake_hardware,
        "tf_prefix": tf_prefix,
        "ns": ns,
        "robot_description_package": robot_description_package,
        "robot_description_file": robot_description_file,
        "is_sim": use_fake_hardware,
    }.items()

    # helper function to organize launch description objects with the same launch args and package names
    def AddLaunchDescriptions(package_name, launch_file_names, launch_args, if_condition="true"):
        launch_files_list = []
        for launch_file_name in launch_file_names:
            launch_files_list.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(
                            get_package_share_directory(package_name),
                            "launch",
                            launch_file_name,
                        )
                    ),
                    launch_arguments=launch_args,
                    condition=IfCondition(if_condition),
                )
            )

        return launch_files_list

    # list of launch files to start
    launch_file_names = []

    # add controller spawners
    launch_file_names.append("spawn_controllers.launch.py")

    # generate launch files
    launch_files = AddLaunchDescriptions(
        package_name="togo_deploy",
        launch_file_names=launch_file_names,
        launch_args=common_launch_args,
    )

    # helper function to get controllers files
    def GetControllersFile(file_name):
        return PathJoinSubstitution(
            [
                get_package_share_directory("togo_deploy"),
                "config",
                file_name,
            ]
        )

    # get controller config file
    controllers_a300 = GetControllersFile("controllers_a300.yaml")

    # launch description for Togo
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare(robot_description_package), "urdf", robot_description_file]),
            " ",
            "ns:=",
            ns,
            " ",
            "tf_prefix:=",
            tf_prefix,
            " ",
            "is_sim:=",
            use_fake_hardware,
            " ",
            extra_xacro_args,  # this should always be last
        ]
    )
    robot_description = {"robot_description": ParameterValue(value=robot_description_content, value_type=str)}

    # robot state publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace=ns,
        output="both",
        parameters=[
            robot_description,
            {"use_sim_time": use_sim_time},
        ],
    )

    # start controller manager node with all controller config files
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        namespace=ns,
        # allow_substs allows tf_prefix to be pulled in
        parameters=[
            ParameterFile(controllers_a300, allow_substs=True),
            {"use_sim_time": use_sim_time},
        ],
        output="both",
    )

    ns_action = GroupAction(actions=[PushRosNamespace(ns)] + launch_files + [robot_state_publisher_node, control_node])

    return LaunchDescription(declared_arguments + [ns_action])
