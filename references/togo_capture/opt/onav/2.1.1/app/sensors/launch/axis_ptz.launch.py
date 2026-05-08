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
from launch_ros.actions import Node, PushRosNamespace, SetRemap
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    ros2_namespace = LaunchConfiguration('ros2_namespace',
                        default=EnvironmentVariable('ROS2_TOPIC_NAMESPACE', default_value='')).perform(context)
    ros2_namespace_prefix = '' if ros2_namespace == '' else '/' + ros2_namespace

    axis_ptz_num = LaunchConfiguration('axis_ptz_num',
        default=EnvironmentVariable('AXIS_PTZ_NUM', default_value='0'))
    axis_ptz_throttle_rate = LaunchConfiguration('axis_ptz_throttle_rate',
        default=EnvironmentVariable('AXIS_PTZ_THROTTLE_RATE', default_value='10'))

    hostname = LaunchConfiguration('hostname',
        default=EnvironmentVariable('AXIS_PTZ_IP', default_value='192.168.131.10'))
    video_width = LaunchConfiguration('video_width',
        default=EnvironmentVariable('AXIS_PTZ_WIDTH', default_value='1280'))
    video_height = LaunchConfiguration('video_height',
        default=EnvironmentVariable('AXIS_PTZ_HEIGHT', default_value='720'))
    compressed = LaunchConfiguration('compressed', default='true')
    fps = LaunchConfiguration('fps',
        default=EnvironmentVariable('AXIS_PTZ_FPS', default_value='30')).perform(context)
    out_dir = LaunchConfiguration('out_dir',
        default=['/opt/onav/saved_files/media/axis_ptz_', axis_ptz_num])
    mount_path = LaunchConfiguration('mount_path',
        default=['/opt/onav/saved_files/media/axis_ptz_', axis_ptz_num])
    topic = LaunchConfiguration('topic',
        default=[ros2_namespace_prefix, '/sensors/camera_', axis_ptz_num, '/image_raw/compressed'])
    username = LaunchConfiguration('username', default='root')
    password = LaunchConfiguration('password', default='clearpath')

    declared_arguments = [
        DeclareLaunchArgument('ros2_namespace', default_value=ros2_namespace),
        DeclareLaunchArgument('axis_ptz_num', default_value=axis_ptz_num),
        DeclareLaunchArgument('axis_ptz_throttle_rate', default_value=axis_ptz_throttle_rate),
        DeclareLaunchArgument('hostname', default_value=hostname),
        DeclareLaunchArgument('video_width', default_value=video_width),
        DeclareLaunchArgument('video_height', default_value=video_height),
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
                PushRosNamespace([ros2_namespace_prefix, '/sensors/camera_', axis_ptz_num]),
                SetRemap(src=['/sensors/camera_', axis_ptz_num, '/joy'], dst='/joy_teleop/joy'),
                IncludeLaunchDescription(
                    AnyLaunchDescriptionSource([
                        FindPackageShare("axis_camera"), '/launch', '/axis_camera.launch'
                    ]),
                    launch_arguments={
                        'camera_name': ['camera_', axis_ptz_num],
                        'hostname': hostname,
                        'username': username,
                        'password': password,
                        'fps': fps,
                        'enable_ptz': 'true',
                        'enable_ptz_teleop': 'true',
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
                    arguments=['messages', [ros2_namespace_prefix, '/sensors/camera_', axis_ptz_num, '/image_raw/compressed'], axis_ptz_throttle_rate, [ros2_namespace_prefix, '/sensors/camera_', axis_ptz_num, '/image_raw_throttle/compressed']]
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
                        'camera_frame': ['camera_', axis_ptz_num, '_camera_link'],
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
