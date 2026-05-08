import os

from ament_index_python.packages import get_package_share_directory
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

    axis_q62_num = LaunchConfiguration('axis_q62_num', default='0')
    axis_q62_throttle_rate = LaunchConfiguration('axis_q62_throttle_rate', default='10')

    hostname = LaunchConfiguration('hostname', default='192.168.131.10')
    video_width = LaunchConfiguration('video_width', default='1280')
    video_height = LaunchConfiguration('video_height', default='720')
    compressed = LaunchConfiguration('compressed', default='true')
    fps = LaunchConfiguration('fps', default='30').perform(context)
    out_dir = LaunchConfiguration('out_dir',
        default=['/opt/onav/saved_files/media/axis_q62'])
    mount_path = LaunchConfiguration('mount_path',
        default=['/opt/onav/saved_files/media/axis_q62'])
    topic = LaunchConfiguration('topic',
        default=['sensors/camera_', axis_q62_num, '/image_raw/compressed'])
    username = LaunchConfiguration('username', default='root')
    password = LaunchConfiguration('password', default='clearpath')

    declared_arguments = [
        DeclareLaunchArgument('namespace', default_value=namespace),
        DeclareLaunchArgument('axis_q62_num', default_value=axis_q62_num),
        DeclareLaunchArgument('axis_q62_throttle_rate', default_value=axis_q62_throttle_rate),
        DeclareLaunchArgument('hostname', default_value=hostname),
        DeclareLaunchArgument('video_width', default_value=video_width),
        DeclareLaunchArgument('video_height', default_value=video_height),
        DeclareLaunchArgument('compressed', default_value=compressed),
        DeclareLaunchArgument('fps', default_value=fps),
        DeclareLaunchArgument('out_dir', default_value=out_dir),
        DeclareLaunchArgument('mount_path', default_value=mount_path),
        DeclareLaunchArgument('topic', default_value=topic),
        DeclareLaunchArgument('username', default_value=username),
        DeclareLaunchArgument('password', default_value=password),
    ]

    ptz_config = os.path.join(get_package_share_directory('axis_camera'),
        'config',
        'axis_q62.yaml'
        )

    teleop_config = os.path.join(get_package_share_directory('axis_camera'),
        'config',
        'teleop_ps4.yaml'
    )

    axis_q62 = Node(
        namespace=[namespace_prefix, '/sensors/camera_', axis_q62_num],
        package='axis_camera',
        executable='axis_camera_node',
        name='axis_camera',
        output='screen',
        parameters=[
            ptz_config,
            teleop_config,
            {
                'hostname': hostname,
                'http_port': 80,
                'username': username,
                'password': password,
                'width': video_width,
                'height': video_height,
                'fps': int(fps),
                'tf_prefix': ['camera_', axis_q62_num],
                'camera_info_url': '',
                'use_encrypted_password': True,
                'ptz': True,
                'ptz_teleop': True,
                'ir': True,
                'defog': True,
                'wiper': True,
                'camera': 0,
            }
        ],
        remappings=[
            ('joint_states', [namespace_prefix, '/platform/joint_states']),
            ('joy', [namespace_prefix, '/joy_teleop/joy']),
        ]
    )

    axis_q62_extras = GroupAction(
        actions = [
            PushRosNamespace([namespace_prefix, '/sensors/camera_', axis_q62_num]),
            Node(
                package='topic_tools',
                executable='throttle',
                name='throttle',
                output='screen',
                arguments=["messages", [namespace_prefix, '/sensors/camera_', axis_q62_num, '/image_raw/compressed'], axis_q62_throttle_rate, [namespace_prefix, '/sensors/camera_', axis_q62_num, '/image_raw_throttle/compressed']],
                additional_env={'ROS_SUPER_CLIENT':'True'}
            ),
            Node(
                package='image_transport',
                executable='republish',
                name='republish_raw',
                output='screen',
                arguments=['compressed', 'raw'],
                parameters=[{
                    'in_transport': 'compressed',
                    'out_transport': 'raw',
                }],
                remappings=[
                    ('in/compressed', 'image_raw_throttle/compressed'),  # Previously you could remap 'in' and all transport topics would be remaped. This is no longer the case.
                    ('out', 'image_raw_out'),
                ]
            ),
            Node(
                output='screen',
                package='onav_network_camera',
                executable='q62_recording_node',
                name='q62_recording_node',
                namespace='',
                parameters=[{
                    "camera_name": ["camera_", axis_q62_num],
                    "media_directory": "/opt/onav/saved_files/media/axis_q62",
                    "camera_ip": hostname,
                }]
            ),
        ]
    )

    return declared_arguments + [  # noqa: RUF005
        axis_q62,
        axis_q62_extras
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
