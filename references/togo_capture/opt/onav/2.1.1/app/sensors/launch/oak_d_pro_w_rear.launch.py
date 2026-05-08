from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    ros2_namespace = LaunchConfiguration('ros2_namespace',
                        default=EnvironmentVariable('ROS2_TOPIC_NAMESPACE', default_value='')).perform(context)
    ros2_namespace_prefix = '' if ros2_namespace == '' else '/' + ros2_namespace

    oak_d_pro_w_rear_name = LaunchConfiguration('oak_d_pro_w_rear_name',
        default=EnvironmentVariable('OAK_D_PRO_W_REAR_NAME', default_value='oak_d_pro_w_rear'))
    oak_d_pro_w_rear_num = LaunchConfiguration('oak_d_pro_w_rear_num',
        default=EnvironmentVariable('OAK_D_PRO_W_REAR_NUM', default_value='1'))
    oak_d_pro_w_rear_ip = LaunchConfiguration('oak_d_pro_w_rear_ip',
        default=EnvironmentVariable('OAK_D_PRO_W_REAR_IP', default_value='192.168.131.11'))

    declared_arguments = [
        DeclareLaunchArgument('ros2_namespace', default_value=ros2_namespace),
        DeclareLaunchArgument('oak_d_pro_w_rear_name', default_value=oak_d_pro_w_rear_name),
        DeclareLaunchArgument('oak_d_pro_w_rear_num', default_value=oak_d_pro_w_rear_num),
        DeclareLaunchArgument('oak_d_pro_w_rear_ip', default_value=oak_d_pro_w_rear_ip),
    ]

    oak_d_pro_w_rear = GroupAction(
        actions = [
            Node(
                namespace=ros2_namespace,
                package='onav_oakd_camera',
                executable='onav_oakd_camera_node',
                name=oak_d_pro_w_rear_name,
                output='screen',
                respawn=True,
                respawn_delay=20,                
                parameters=[{
                    'ip': oak_d_pro_w_rear_ip,
                    'name': oak_d_pro_w_rear_name,
                    'save_directory': '/opt/onav/saved_files/media/',
                    'host_name': 'cpr-rooftop:1180',
                }],
                remappings=[
                    ('/tf', 'tf'), ('/tf_static', 'tf_static'),
                    ('/diagnostics', 'diagnostics'),
                    # ('', ['sensors/camera_', oak_d_pro_w_front_num, '/camera_info']),
                    ([oak_d_pro_w_rear_name, '/image_color_raw'], ['sensors/camera_', oak_d_pro_w_rear_num, '/color/image']),
                    ([oak_d_pro_w_rear_name, '/imu_data'], ['sensors/camera_', oak_d_pro_w_rear_num, '/imu/data_raw']),
                    ([oak_d_pro_w_rear_name, '/pointcloud'], ['sensors/camera_', oak_d_pro_w_rear_num, '/pointcloud'])
                ]
            )
        ]
    )

    return declared_arguments + [
        oak_d_pro_w_rear
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
