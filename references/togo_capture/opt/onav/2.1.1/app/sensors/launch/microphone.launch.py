#!/usr/bin/env python3

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
                PushRosNamespace([namespace_prefix, '/sensors/microphone_0']),
                Node(
                    package='audio_recorder',
                    executable='audio_recorder_node',
                    output='screen',
                    namespace='',
                    respawn=True,
                    parameters=[
                        {'bitrate': 44100},
                        {'card_id': 0},
                        {'channels': 1},
                        {'device_id': 0},
                        {'format': 'S16_LE'},
                        # {'mic_frame': mic_frame},
                        # {'mount_dir': '/opt/onav/saved_files/microphone'},
                        {'out_dir': '/opt/onav/saved_files/media/microphone'},
                        {'record_metadata': True},
                    ]
                )
            ]
        )
    ]


def generate_launch_description():

    return LaunchDescription(
        [OpaqueFunction(function=launch_setup)]
    )
