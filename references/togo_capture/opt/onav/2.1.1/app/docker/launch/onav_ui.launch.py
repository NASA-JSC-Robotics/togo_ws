from clearpath_config.clearpath_config import ClearpathConfig
from clearpath_config.common.utils.yaml import read_yaml
from launch import LaunchDescription
from launch.actions import (
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare

DEFAULT_ROBOT_CONFIG_PATH = '/etc/clearpath/robot.yaml'
DEFAULT_OUTDOORNAV_CONFIG_PATH = '/opt/onav/config/outdoornav.yaml'


def launch_setup(context, *args, **kwargs):

    # Read YAML
    robot_config_path = LaunchConfiguration('robot_config_path',
                                            default=DEFAULT_ROBOT_CONFIG_PATH).perform(context)
    robot_config = read_yaml(robot_config_path)
    onav_config_path = LaunchConfiguration('robot_config_path',
                                            default=DEFAULT_OUTDOORNAV_CONFIG_PATH).perform(context)
    onav_config = read_yaml(onav_config_path)

    # Parse YAML into config
    namespace = robot_config['system']['ros2']['namespace']

    try:
        enable_web_video_server = onav_config['outdoornav']['ui']['enable_rtsp']
    except (KeyError, TypeError):
        enable_web_video_server = True

    return [  # noqa: RUF005
        GroupAction(
            condition = IfCondition(
                PythonExpression([
                    '\'',
                    str(enable_web_video_server),
                    '\''
                ])
            ),
            actions = [
                Node(
                    namespace=namespace,
                    package='web_video_server',
                    executable='web_video_server',
                    name='web_video_server_1',
                    output='screen',
                    respawn=True
                ),
                # TODO: only if $(env ENABLE_SECONDARY_WEB_VIDEO_SERVER false)
                # Node(
                #     package='web_video_server',
                #     executable='web_video_server',
                #     name='web_video_server_2',
                #     output='screen',
                #     parameters=[{
                #         'port': 8081
                #     }]
                # )
            ]
        ),
        GroupAction(
            actions = [
                PushRosNamespace(namespace),
                IncludeLaunchDescription(
                    AnyLaunchDescriptionSource([
                        FindPackageShare("rosbridge_server"), '/launch', '/rosbridge_websocket_launch.xml'
                    ]),
                    launch_arguments={
                        'port': '9091',
                    }.items()
                )
            ]
        ),
        GroupAction(
            actions = [
                PushRosNamespace(namespace),
                IncludeLaunchDescription(
                    AnyLaunchDescriptionSource([
                        FindPackageShare("foxglove_bridge"), '/launch', '/foxglove_bridge_launch.xml'
                    ]),
                    launch_arguments={
                        'port': '8780',
                        'include_hidden': 'true',
                    }.items()
                )
            ]
        ),
        Node(
            namespace=namespace,
            package='topic_tools',
            executable='throttle',
            name='odom_throttle',
            output='screen',
            arguments=['messages', 'localization/odom', '4.0', 'localization/odom_throttle']
        )
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
