import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    togo_deploy_dir = get_package_share_directory('togo_deploy')
    
    husky_comm_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(togo_deploy_dir, 'launch', 'husky_comm.launch.py')
        )
    )

    control_hardware_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(togo_deploy_dir, 'launch', 'control_hardware.launch.py')
        )
    )

    togo_sensors_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(togo_deploy_dir, 'launch', 'togo_sensors.launch.py')
        )
    )

    tag_detector_node = Node(
        package='togo_apriltag',
        executable='apriltag_pos', 
        name='apriltag_detector',
        output='screen'
    )

    tag_follower_node = Node(
        package='togo_apriltag',
        executable='rotate_only', 
        name='tag_follower',
        output='screen'
    )

    ld = LaunchDescription()

    ld.add_action(husky_comm_launch)
    ld.add_action(control_hardware_launch)
    ld.add_action(togo_sensors_launch)
    ld.add_action(tag_detector_node)
    ld.add_action(tag_follower_node)

    return ld