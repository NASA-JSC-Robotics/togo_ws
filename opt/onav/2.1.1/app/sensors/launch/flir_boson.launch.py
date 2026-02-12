from launch import LaunchDescription
from launch.actions import (
    GroupAction,
    OpaqueFunction,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    return [
        GroupAction(
            actions=[
                PushRosNamespace([namespace_prefix]),
                Node(
                    output='screen',
                    package='boson_ros2',
                    executable='boson_node',
                    name='flir_boson',
                    namespace='',
                    respawn=True,
                    respawn_delay=10,
                    parameters=[{
                        "camera_name": "flir_boson",
                        "use_vaapi": False,
                        "throttled_frequency": 5.0,
                        "overlays.rotate": 90,
                        "overlays.max_temp.enabled": True,
                        "processing.color_palette": "ironbow"
                    }]
                )
            ])]


def generate_launch_description():

    return LaunchDescription(
        [OpaqueFunction(function=launch_setup)]
    )
