from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import SetEnvironmentVariable
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    ## This is config for Seyond lidar
    rviz_config=get_package_share_directory('togo_deploy')+'/rviz/rviz2.rviz'
    yaml_config=get_package_share_directory('togo_deploy')+'/config/seyond_config.yaml'

    # set log color
    rc_utils = SetEnvironmentVariable(name='RCUTILS_COLORIZED_OUTPUT', value='1')

    config_arg = DeclareLaunchArgument(
        'config_path',
        default_value=yaml_config,
        description='config path'
    )
    

    seyond_node = Node(
        package="seyond",
        executable="seyond_node",
        parameters=[
            {'config_path': LaunchConfiguration('config_path')},
        ],
    )
    # Node(namespace='rviz2', package='rviz2', executable='rviz2', arguments=['-d',rviz_config])

    ## This is config section for oakd front camera
    yaml_front_oakd_config=get_package_share_directory('togo_deploy')+'/config/front_oakd_config.yaml'
    front_depthai_oakd_node = ComposableNode(
        package='depthai_ros_driver',
        name='front_oakd',
        plugin='depthai_ros_driver::Camera',
        parameters=[yaml_front_oakd_config],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    front_depthai_pcl_node = ComposableNode(
        package='depth_image_proc',
        plugin='depth_image_proc::PointCloudXyzNode',
        name='front_point_cloud_xyz_node',
        remappings=[
            ('image_rect', '/front_oakd/stereo/image_raw'),
            ('camera_info', '/front_oakd/stereo/camera_info'),
            ('points', '/front_oakd/points'),
        ],
    )

    front_image_processing_container = ComposableNodeContainer(
        name='front_image_processing_container',
        package='rclcpp_components',
        namespace="",
        executable='component_container',
        composable_node_descriptions=[
          front_depthai_oakd_node,
          front_depthai_pcl_node,
        ],
        output='screen'
    )

    ## This is config section for oakd rear camera
    yaml_rear_oakd_config=get_package_share_directory('togo_deploy')+'/config/rear_oakd_config.yaml'
    rear_depthai_oakd_node = ComposableNode(
        package='depthai_ros_driver',
        name='rear_oakd',
        plugin='depthai_ros_driver::Camera',
        parameters=[yaml_rear_oakd_config],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    rear_depthai_pcl_node = ComposableNode(
        package='depth_image_proc',
        plugin='depth_image_proc::PointCloudXyzNode',
        name='rear_point_cloud_xyz_node',
        remappings=[
            ('image_rect', '/rear_oakd/stereo/image_raw'),
            ('camera_info', '/rear_oakd/stereo/camera_info'),
            ('points', '/rear_oakd/points'),
        ],
    )

    rear_image_processing_container = ComposableNodeContainer(
        name='rear_image_processing_container',
        package='rclcpp_components',
        namespace="",
        executable='component_container',
        composable_node_descriptions=[
          rear_depthai_oakd_node,
          rear_depthai_pcl_node,
        ],
        output='screen'
    )

    ## This is config section for INS sensor
    yaml_ins_config=get_package_share_directory('togo_deploy')+'/config/ins_config.yaml'
    fixposition_node = Node(
        package='fixposition_driver_ros2',
        executable='fixposition_driver_ros2_exec',
        name='fixposition_driver',
        output='screen',
        parameters=[yaml_ins_config],
    )

    return LaunchDescription(
        [
            rc_utils,
            config_arg,
            # seyond_node,
            # front_image_processing_container,
            # rear_image_processing_container,
            fixposition_node,
        ]
    )
