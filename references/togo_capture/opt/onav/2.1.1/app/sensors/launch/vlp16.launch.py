import os

import ament_index_python.packages
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    GroupAction,
    OpaqueFunction,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    vlp_lidar_num = LaunchConfiguration('vlp_lidar_num',
        default=EnvironmentVariable('VLP_LIDAR_NUM', default_value='0'))
    vlp_ip = LaunchConfiguration('vlp_ip',
        default=EnvironmentVariable('VLP_IP', default_value='192.168.131.20')).perform(context)
    vlp_frame = LaunchConfiguration('vlp_frame',
        default=EnvironmentVariable('VLP_FRAME', default_value='velodyne'))
    vlp_min_range = LaunchConfiguration('vlp_min_range',
        default=EnvironmentVariable('VLP_MIN_RANGE', default_value='0.6'))

    declared_arguments = [
        DeclareLaunchArgument('vlp_lidar_num', default_value=vlp_lidar_num),
        DeclareLaunchArgument('vlp_ip', default_value=vlp_ip),
        DeclareLaunchArgument('vlp_frame', default_value=vlp_frame),
        DeclareLaunchArgument('vlp_min_range', default_value=vlp_min_range),
    ]

    velodyne_driver_node = Node(
        package='velodyne_driver',
        executable='velodyne_driver_node',
        output='screen',
        parameters=[{
            'model': 'VLP16',
            'device_ip': str(vlp_ip),
            'frame_id': vlp_frame}]
    )

    convert_share_dir = ament_index_python.packages.get_package_share_directory('velodyne_pointcloud')
    calibration_file_path = os.path.join(convert_share_dir, 'params', 'VLP16db.yaml')
    velodyne_transform_node = Node(
        package='velodyne_pointcloud',
        executable='velodyne_transform_node',
        output='screen',
        parameters=[{
            'model': 'VLP16',
            'calibration': calibration_file_path,
            'min_range': vlp_min_range,
            'max_range': 130.0,
            'fixed_frame': vlp_frame,
            'target_frame': vlp_frame,
            'organize_cloud': False}],
        remappings=[('/velodyne_points', ['/sensors/lidar_', vlp_lidar_num, '/pointcloud'])]
    )

    return declared_arguments + [
        GroupAction(
            actions = [
                velodyne_driver_node,
                velodyne_transform_node,
                RegisterEventHandler(
                    event_handler=OnProcessExit(target_action=velodyne_driver_node,
                                        on_exit=[EmitEvent(event=Shutdown())],
                )),
            ]
        )
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
