from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # declare launch arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the hardware robot",
        )
    )

    # initialize arguments
    ns = LaunchConfiguration("ns")

    # helper function to make controller nodes
    def MakeControllerNode(controller_name, active=True, condition=None, controller_ros_args=None):
        arguments = [
            "--controller-manager",
            "controller_manager",
            "--controller-manager-timeout",
            "300",
            "--namespace",
            ns,
            controller_name,
        ]
        if not active:
            arguments.append("--inactive")
        if controller_ros_args is not None:
            for controller_ros_arg in controller_ros_args:
                arguments.append("--controller-ros-args")
                arguments.append(f"{controller_ros_arg}")

        return Node(
            package="controller_manager",
            executable="spawner",
            name=controller_name,
            arguments=arguments,
            output="screen",
            condition=condition,
        )

    # list of controller nodes to spawn
    nodes = []

    # add controllers (based on the corresponding config YAML file)
    nodes.append(MakeControllerNode("platform_velocity_controller"))

    return LaunchDescription(declared_arguments + nodes)
