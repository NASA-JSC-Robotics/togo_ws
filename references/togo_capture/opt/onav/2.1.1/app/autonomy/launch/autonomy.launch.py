import os

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

    platform_model = LaunchConfiguration('platform_model').perform(context)
    outdoornav_version = LaunchConfiguration('outdoornav_version')

    enable_autonomy_previewer = LaunchConfiguration('enable_control_selection')
    enable_control_selection = LaunchConfiguration('enable_control_selection')
    enable_logger = LaunchConfiguration('enable_logger')
    enable_mission_manager = LaunchConfiguration('enable_mission_manager')

    axis_q62_enable_driver = LaunchConfiguration('axis_q62_enable_driver', default=False)
    axis_q62_num = LaunchConfiguration('axis_q62_num').perform(context)

    declared_arguments = [
        DeclareLaunchArgument('platform_model', default_value=platform_model),
        DeclareLaunchArgument('outdoornav_version', default_value=outdoornav_version),
        DeclareLaunchArgument('enable_autonomy_previewer', default_value=enable_autonomy_previewer),
        DeclareLaunchArgument('enable_control_selection', default_value=enable_control_selection),
        DeclareLaunchArgument('enable_logger', default_value=enable_logger),
        DeclareLaunchArgument('enable_mission_manager', default_value=enable_mission_manager),
        DeclareLaunchArgument('axis_q62_enable_driver', default_value=axis_q62_enable_driver),
        DeclareLaunchArgument('axis_q62_num', default_value=axis_q62_num),
    ]

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    mission_manager = GroupAction(
        condition=IfCondition(
            PythonExpression([
                '\'',
                enable_mission_manager,
                '\''
            ])
        ),
        actions=[
            Node(
                package='onav_mission_manager',
                executable='mission_manager_node',
                name='mission_manager',
                output='screen',
                respawn=True,
                respawn_delay=5.0,
            )
        ]
    )

    log_topics_config = '/opt/onav/app/autonomy/params/' + str(platform_model) + '/autonomy/log_topics.yaml'
    log_analyzers_config = '/opt/onav/app/autonomy/params/' + str(platform_model) + '/autonomy/log_analyzers.yaml'
    logger = GroupAction(
        condition=IfCondition(
            PythonExpression([
                '\'',
                enable_logger,
                '\''
            ])
        ),
        actions=[
            Node(
                package='onav_logger',
                executable='log_manager.py',
                name='log_manager',
                output='screen',
                respawn=True,
                respawn_delay=5.0,
                parameters=[log_topics_config],
                remappings=[]
            ),
            Node(
                package='onav_logger',
                executable='log_analyzer.py',
                name='log_analyzer',
                output='screen',
                respawn=True,
                respawn_delay=5.0,
                parameters=[log_analyzers_config]
            )
        ]
    )

    autonomy_previewer = GroupAction(
        condition=IfCondition(
            PythonExpression([
                '\'',
                enable_autonomy_previewer,
                '\''
            ])
        ),
        actions=[
            Node(
                package='onav_network',
                executable='autonomy_previewer_node',
                name='autonomy_previewer',
                output='screen',
                respawn=True,
                respawn_delay=5.0,
            )
        ]
    )

    path_recorder_node = Node(
        package='onav_path_recorder',
        executable='path_recorder_node',
        name='path_recorder',
        output='screen',
    )

    configuration_node = Node(
        package='onav_configuration',
        executable='onav_configuration',
        name='onav_configuration',
        output='screen',
        parameters=[{
            'version': outdoornav_version
        }]
    )

    control_selection = GroupAction(
        condition=IfCondition(
            PythonExpression([
                '\'',
                enable_control_selection,
                '\''
            ])
        ),
        actions=[
            Node(
                package='onav_control_selection',
                executable='control_selection',
                name='control_selection',
                output='screen',
                parameters=[{
                    'platform_model': platform_model
                }]
            )
        ]
    )

    inspect_poi_group_action = GroupAction(
        condition = IfCondition(
            PythonExpression([
                '\'',
                axis_q62_enable_driver,
                '\''
            ])
        ),
        actions = [
            Node(
                package='onav_camera',
                executable='inspect_poi_node',
                name='inspect_poi',
                output='screen',
                parameters=[{
                    'platform_model': platform_model,
                    'camera_num': int(axis_q62_num),
                }],
                remappings=remappings
            )
        ]
    )

    return declared_arguments + [  # noqa: RUF005
        PushRosNamespace(namespace_prefix),
        mission_manager,
        logger,
        autonomy_previewer,
        # path_recorder_node,
        configuration_node,
        control_selection,
        # inspect_poi_group_action,
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
