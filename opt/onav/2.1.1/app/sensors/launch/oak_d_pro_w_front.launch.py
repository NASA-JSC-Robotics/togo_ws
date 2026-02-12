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

    oak_d_pro_w_front_name = LaunchConfiguration('oak_d_pro_w_front_name',
        default=EnvironmentVariable('OAK_D_PRO_W_FRONT_NAME', default_value='oak_d_pro_w_front'))
    oak_d_pro_w_front_num = LaunchConfiguration('oak_d_pro_w_front_num',
        default=EnvironmentVariable('OAK_D_PRO_W_FRONT_NUM', default_value='0'))
    oak_d_pro_w_front_ip = LaunchConfiguration('oak_d_pro_w_front_ip',
        default=EnvironmentVariable('OAK_D_PRO_W_FRONT_IP', default_value='192.168.131.10'))

    declared_arguments = [
        DeclareLaunchArgument('ros2_namespace', default_value=ros2_namespace),
        DeclareLaunchArgument('oak_d_pro_w_front_name', default_value=oak_d_pro_w_front_name),
        DeclareLaunchArgument('oak_d_pro_w_front_num', default_value=oak_d_pro_w_front_num),
        DeclareLaunchArgument('oak_d_pro_w_front_ip', default_value=oak_d_pro_w_front_ip),
    ]

    oak_d_pro_w_front = GroupAction(
        actions = [
            Node(
                namespace=ros2_namespace,
                package='onav_oakd_camera',
                executable='onav_oakd_camera_node',
                name=oak_d_pro_w_front_name,
                output='screen',
                respawn=True,
                respawn_delay=20,
                parameters=[{
                    'ip': oak_d_pro_w_front_ip,
                    'name': oak_d_pro_w_front_name,
                    'save_directory': '/opt/onav/saved_files/media/',
                    'host_name': 'cpr-rooftop:1180',
                }],
                remappings=[
                    ('/tf', 'tf'), ('/tf_static', 'tf_static'),
                    ('/diagnostics', 'diagnostics'),
                    # ('', ['sensors/camera_', oak_d_pro_w_front_num, '/camera_info']),
                    ([oak_d_pro_w_front_name, '/image_color_raw'], ['sensors/camera_', oak_d_pro_w_front_num, '/color/image']),
                    ([oak_d_pro_w_front_name, '/imu_data'], ['sensors/camera_', oak_d_pro_w_front_num, '/imu/data_raw']),
                    ([oak_d_pro_w_front_name, '/pointcloud'], ['sensors/camera_', oak_d_pro_w_front_num, '/pointcloud'])
                ]
            )
        ]
    )


    return declared_arguments + [
        oak_d_pro_w_front
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
