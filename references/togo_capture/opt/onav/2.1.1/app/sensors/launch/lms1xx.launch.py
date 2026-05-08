from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace


def launch_setup(context, *args, **kwargs):
    ros2_namespace = LaunchConfiguration('ros2_namespace',
                        default=EnvironmentVariable('ROS2_TOPIC_NAMESPACE', default_value='')).perform(context)
    ros2_namespace_prefix = '' if ros2_namespace == '' else '/' + ros2_namespace

    lms1xx_num = LaunchConfiguration('lms1xx_num',
        default=EnvironmentVariable('LMS1XX_NUM', default_value='0'))
    lms1xx_ip = LaunchConfiguration('lms1xx_ip',
        default=EnvironmentVariable('LMS1XX_IP', default_value='192.168.131.20'))
    lms1xx_frame = LaunchConfiguration('lms1xx_frame',
        default=EnvironmentVariable('LMS1XX_FRAME', default_value='front_laser'))

    declared_arguments = [
        DeclareLaunchArgument('ros2_namespace', default_value=ros2_namespace),
        DeclareLaunchArgument('lms1xx_enable_driver', default_value=lms1xx_enable_driver),
        DeclareLaunchArgument('lms1xx_num', default_value=lms1xx_num),
        DeclareLaunchArgument('lms1xx_ip', default_value=lms1xx_ip),
        DeclareLaunchArgument('lms1xx_frame', default_value=lms1xx_frame),
    ]

    return declared_arguments + [
        GroupAction(
            actions = [
                PushRosNamespace(ros2_namespace_prefix),
                Node(
                    package='lms1xx',
                    executable='lms1xx',
                    name='front_lms1xx',
                    output='screen',
                    parameters=[{
                        'host': lms1xx_ip,
                        'frame_id': lms1xx_frame,
                    }],
                    remappings=[
                        ([ros2_namespace_prefix, '/scan'], [ros2_namespace_prefix, '/sensors/lidar_', lms1xx_num, '/scan'])
                    ]
                ),
            ]
        )
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
