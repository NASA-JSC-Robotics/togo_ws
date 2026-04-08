from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # declare launch arguments
    declared_arguments = []
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

    # initialize arguments
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")

    # common launch args passed to each of the launch files
    common_launch_args = {
        "tf_prefix": tf_prefix,
        "ns": ns,
    }.items()

    # helper function to organize launch description objects with the same launch args and package names
    def MakeLaunchDescription(launch_file, launch_args, condition=IfCondition("true")):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file),
            launch_arguments=launch_args,
            condition=condition,
        )

    # helper function to make controller nodes
    def MakeControllerNode(controller_name):
        return Node(
            package="controller_manager",
            executable="spawner",
            name=controller_name,
            arguments=[
                "--controller-manager",
                "controller_manager",
                "--controller-manager-timeout",
                "300",
                "--namespace",
                ns,
                controller_name,
            ],
            output="screen",
        )

    # create joint state broadcaster
    joint_state_broadcaster = MakeControllerNode("joint_state_broadcaster")

    # controller spawner launch files for each subsystem
    pkg_togo_deploy = get_package_share_directory("togo_deploy")
    launch_file_a300_spawner = PathJoinSubstitution(
        [
            pkg_togo_deploy,
            "launch",
            "spawn_controllers",
            "spawn_controllers_a300.launch.py",
        ]
    )

    # list of spawners
    spawner_launches = []

    # add controller spawners
    spawner_launches.append(MakeLaunchDescription(launch_file_a300_spawner, common_launch_args))

    return LaunchDescription(declared_arguments + spawner_launches + [joint_state_broadcaster])
