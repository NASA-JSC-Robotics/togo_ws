from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan_node',
            remappings=[
                ('cloud_in', '/husky/sensors/seyond/points'),
                ('scan', '/husky/sensors/seyond/scan')
            ],
            parameters=[{
#                'target_frame': 'camera_0_rgb_camera_frame',              # Center of your camera frame
                'use_sim_time': True,
                'transform_tolerance': 0.01,
                'min_height': 0.,                        # Min Z point to consider (meters)
                'max_height': 20.5,                         # Max Z point to consider (meters)
                'angle_min': -1.5708,                       # -90 degrees
                'angle_max': 1.5708,                        # 90 degrees
                'angle_increment': 0.0087,                  # Resolution of scan
                'range_min': 0.5,                          # Min range (meters)
                'range_max': 30.0,                           # Max range (meters)
                'use_inf': True
            }],
        )
    ])
