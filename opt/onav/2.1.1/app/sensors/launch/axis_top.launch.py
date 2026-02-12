from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    ros2_namespace = LaunchConfiguration('ros2_namespace',
                        default=EnvironmentVariable('ROS2_TOPIC_NAMESPACE', default_value='')).perform(context)
    ros2_namespace_prefix = '' if ros2_namespace == '' else '/' + ros2_namespace

    axis_top_num = LaunchConfiguration('axis_top_num',
        default=EnvironmentVariable('AXIS_TOP_NUM', default_value='0'))
    axis_top_teleop_throttle_rate = LaunchConfiguration('axis_top_teleop_throttle_rate',
        default=EnvironmentVariable('AXIS_TOP_TELEOP_THROTTLE_RATE', default_value='10'))

    hostname = LaunchConfiguration('hostname',
        default=EnvironmentVariable('AXIS_TOP_IP', default_value='192.168.131.10'))
    video_width = LaunchConfiguration('video_width',
        default=EnvironmentVariable('AXIS_TOP_WIDTH', default_value='1280'))
    video_height = LaunchConfiguration('video_height',
        default=EnvironmentVariable('AXIS_TOP_HEIGHT', default_value='1280'))
    compressed = LaunchConfiguration('compressed', default='true')
    fps = LaunchConfiguration('fps',
        default=EnvironmentVariable('AXIS_TOP_FPS', default_value='30')).perform(context)
    out_dir = LaunchConfiguration('out_dir',
        default=['/opt/onav/saved_files/media/axis_top_', axis_top_num])
    mount_path = LaunchConfiguration('mount_path',
        default=['/opt/onav/saved_files/media/axis_top_', axis_top_num])
    topic = LaunchConfiguration('topic',
        default=[ros2_namespace_prefix, '/sensors/camera_', axis_top_num, '/image_raw/compressed'])
    username = LaunchConfiguration('username', default='root')
    password = LaunchConfiguration('password', default='clearpath')

    declared_arguments = [
        DeclareLaunchArgument('ros2_namespace', default_value=ros2_namespace),
        DeclareLaunchArgument('axis_top_enable_driver', default_value=axis_top_enable_driver),
        DeclareLaunchArgument('axis_top_num', default_value=axis_top_num),
        DeclareLaunchArgument('axis_top_teleop_throttle_rate', default_value=axis_top_teleop_throttle_rate),
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

    return declared_arguments + [
        GroupAction(
            actions = [
                PushRosNamespace([ros2_namespace_prefix, '/sensors/camera_', axis_top_num]),
                IncludeLaunchDescription(
                    AnyLaunchDescriptionSource([
                        FindPackageShare("axis_camera"), '/launch', '/axis_camera.launch'
                    ]),
                    launch_arguments={
                        'camera_name': ['camera_', axis_top_num],
                        'hostname': hostname,
                        'username': username,
                        'password': password,
                        'encrypt_password': 'true',
                        'fps': fps,
                        'enable_theora': 'false',
                        'enable_ptz': 'false',
                        'enable_ptz_teleop': 'false',
                        'enable_defog': 'false',
                        'enable_ir': 'false',
                        'enable_wiper': 'false',
                        'frame_width': video_width,
                        'frame_height': video_height,
                        'camera': '0',
                    }.items()
                ),
                Node(
                    package='topic_tools',
                    executable='throttle',
                    name='throttle',
                    output='screen',
                    arguments=['messages', [ros2_namespace_prefix, '/sensors/camera_', axis_top_num, '/image_raw/compressed'], axis_top_teleop_throttle_rate, [ros2_namespace_prefix, '/sensors/camera_', axis_top_num, '/image_raw_throttle/compressed']]
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
                    package='video_recorder',
                    executable='video_recorder_node',
                    name='capture',
                    output='screen',
                    parameters=[{
                        'compressed': compressed,
                        'fps': float(fps),
                        'out_dir': out_dir,
                        'mount_path': mount_path,
                        'topic': topic,
                        'output_width': video_width,
                        'output_height': video_height,
                        'camera_frame': ['camera_', axis_top_num, '_camera_link'],
                        # Optionally specify an absolute maximum duration for video files generated by the node
                        #     Videos that exceed this duration will automatically be stopped
                        'max_duration': 0,
                    }]
                ),
            ]
        )
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
