from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace', default='').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    platform_model = LaunchConfiguration('platform_model')
    enable_watchdogs = LaunchConfiguration('enable_watchdogs')

    declared_arguments = [
        DeclareLaunchArgument('namespace', default_value=namespace),
        DeclareLaunchArgument('platform_model', default_value=platform_model),
        DeclareLaunchArgument('enable_watchdogs', default_value=enable_watchdogs),
    ]

    watchdogs = GroupAction(
        condition=IfCondition(
            PythonExpression([
                '\'',
                enable_watchdogs,
                '\''
            ])
        ),
        actions=[
            PushRosNamespace([namespace_prefix, '/safety']),
            Node(
                package='onav_safety',
                executable='watchdogs_node.py',
                name='watchdogs',
                output='screen',
                parameters=[{
                    'platform_model': platform_model,
                }]
            ),
        ]
    )

    return declared_arguments + [  # noqa: RUF005
        watchdogs
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
