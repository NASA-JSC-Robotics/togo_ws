import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace', default='').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    task_executor_node = Node(
        package='onav_tasks',
        executable='task_executor_node',
        name='task_executor',
        output='screen',
        respawn=True,
        respawn_delay=5.0
    )
    
    return [
        PushRosNamespace(namespace_prefix),
        task_executor_node
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
