from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    oak_d_pro_w_front_enable_driver = LaunchConfiguration('oak_d_pro_w_front_enable_driver', default='false')
    oak_d_pro_w_front_name = LaunchConfiguration('oak_d_pro_w_front_name', default='oak_d_pro_w_front')
    oak_d_pro_w_front_num = LaunchConfiguration('oak_d_pro_w_front_num', default='0')
    oak_d_pro_w_front_ip = LaunchConfiguration('oak_d_pro_w_front_ip', default='192.168.131.15')
    oak_d_pro_w_front_parent_link = LaunchConfiguration('oak_d_pro_w_front_parent_link', default='default_mount')
    oak_d_pro_w_front_x = LaunchConfiguration('oak_d_pro_w_front_x', default='0.0').perform(context),
    oak_d_pro_w_front_z = LaunchConfiguration('oak_d_pro_w_front_z', default='0.0').perform(context),
    oak_d_pro_w_front_r = LaunchConfiguration('oak_d_pro_w_front_r', default='0.0').perform(context),
    oak_d_pro_w_front_p = LaunchConfiguration('oak_d_pro_w_front_p', default='0.0').perform(context),
    oak_d_pro_w_front_y = LaunchConfiguration('oak_d_pro_w_front_y', default='0.0').perform(context),
    oak_d_pro_w_front_yaw = LaunchConfiguration('oak_d_pro_w_front_yaw', default='0.0').perform(context),
    oak_d_pro_w_rear_enable_driver = LaunchConfiguration('oak_d_pro_w_rear_enable_driver', default='false')
    oak_d_pro_w_rear_name = LaunchConfiguration('oak_d_pro_w_rear_name', default='oak_d_pro_w_rear')
    oak_d_pro_w_rear_num = LaunchConfiguration('oak_d_pro_w_rear_num', default='1')
    oak_d_pro_w_rear_ip = LaunchConfiguration('oak_d_pro_w_rear_ip', default='192.168.131.16')
    oak_d_pro_w_rear_parent_link = LaunchConfiguration('oak_d_pro_w_rear_parent_link', default='default_mount')
    oak_d_pro_w_rear_x = LaunchConfiguration('oak_d_pro_w_rear_x', default='0.0').perform(context),
    oak_d_pro_w_rear_y = LaunchConfiguration('oak_d_pro_w_rear_y', default='0.0').perform(context),
    oak_d_pro_w_rear_z = LaunchConfiguration('oak_d_pro_w_rear_z', default='0.0').perform(context),
    oak_d_pro_w_rear_r = LaunchConfiguration('oak_d_pro_w_rear_r', default='0.0').perform(context),
    oak_d_pro_w_rear_p = LaunchConfiguration('oak_d_pro_w_rear_p', default='0.0').perform(context),
    oak_d_pro_w_rear_yaw = LaunchConfiguration('oak_d_pro_w_rear_yaw', default='0.0').perform(context),

    declared_arguments = [
        DeclareLaunchArgument('namespace', default_value=namespace),
        DeclareLaunchArgument('oak_d_pro_w_front_enable_driver', default_value=oak_d_pro_w_front_enable_driver),
        DeclareLaunchArgument('oak_d_pro_w_front_name', default_value=oak_d_pro_w_front_name),
        DeclareLaunchArgument('oak_d_pro_w_front_num', default_value=oak_d_pro_w_front_num),
        DeclareLaunchArgument('oak_d_pro_w_front_ip', default_value=oak_d_pro_w_front_ip),
        DeclareLaunchArgument('oak_d_pro_w_front_parent_link', default_value=oak_d_pro_w_front_parent_link),
        DeclareLaunchArgument('oak_d_pro_w_front_x', default_value=oak_d_pro_w_front_x),
        DeclareLaunchArgument('oak_d_pro_w_front_y', default_value=oak_d_pro_w_front_y),
        DeclareLaunchArgument('oak_d_pro_w_front_z', default_value=oak_d_pro_w_front_z),
        DeclareLaunchArgument('oak_d_pro_w_front_r', default_value=oak_d_pro_w_front_r),
        DeclareLaunchArgument('oak_d_pro_w_front_p', default_value=oak_d_pro_w_front_p),
        DeclareLaunchArgument('oak_d_pro_w_front_yaw', default_value=oak_d_pro_w_front_yaw),
        DeclareLaunchArgument('oak_d_pro_w_rear_enable_driver', default_value=oak_d_pro_w_rear_enable_driver),
        DeclareLaunchArgument('oak_d_pro_w_rear_name', default_value=oak_d_pro_w_rear_name),
        DeclareLaunchArgument('oak_d_pro_w_rear_num', default_value=oak_d_pro_w_rear_num),
        DeclareLaunchArgument('oak_d_pro_w_rear_ip', default_value=oak_d_pro_w_rear_ip),
        DeclareLaunchArgument('oak_d_pro_w_rear_parent_link', default_value=oak_d_pro_w_rear_parent_link),
        DeclareLaunchArgument('oak_d_pro_w_rear_x', default_value=oak_d_pro_w_rear_x),
        DeclareLaunchArgument('oak_d_pro_w_rear_y', default_value=oak_d_pro_w_rear_y),
        DeclareLaunchArgument('oak_d_pro_w_rear_z', default_value=oak_d_pro_w_rear_z),
        DeclareLaunchArgument('oak_d_pro_w_rear_r', default_value=oak_d_pro_w_rear_r),
        DeclareLaunchArgument('oak_d_pro_w_rear_p', default_value=oak_d_pro_w_rear_p),
        DeclareLaunchArgument('oak_d_pro_w_rear_yaw', default_value=oak_d_pro_w_rear_yaw),
    ]

    oak_d_pro_w_front = GroupAction(
        condition = IfCondition(
            PythonExpression([
                '\'',
                oak_d_pro_w_front_enable_driver,
                '\''
            ])
        ),
        actions = [
            PushRosNamespace([namespace_prefix]),
            Node(
                package='onav_oakd_camera',
                executable='onav_oakd_camera_node',
                name='oak_d_pro_w_front',
                output='screen',
                respawn=True,
                respawn_delay=20,
                parameters=[{
                    'name': oak_d_pro_w_front_name,
                    'ip': oak_d_pro_w_front_ip,
                    'save_directory': '/opt/onav/saved_files/media/',
                    'host_name': 'cpr-rooftop:1180',
                }],
                remappings=[
                    ('/tf', 'tf'), ('/tf_static', 'tf_static'),
                    ('/diagnostics', 'diagnostics'),
                    # ('', ['sensors/', oak_d_pro_w_front_name, '/camera_info']),
                    ([oak_d_pro_w_front_name, '/image_color_raw'], ['sensors/camera_', oak_d_pro_w_front_num, '/color/image']),
                    ([oak_d_pro_w_front_name, '/imu_data'], ['sensors/camera_', oak_d_pro_w_front_num, '/imu/data_raw']),
                    ([oak_d_pro_w_front_name, '/pointcloud'], ['sensors/camera_', oak_d_pro_w_front_num, '/pointcloud']),
                ]
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='oakd_pro_w_front_tf_publisher',
                output='screen',
                arguments=[
                    oak_d_pro_w_front_x,
                    oak_d_pro_w_front_y,
                    oak_d_pro_w_front_z,
                    oak_d_pro_w_front_r,
                    oak_d_pro_w_front_p,
                    oak_d_pro_w_front_yaw,
                    oak_d_pro_w_front_parent_link,
                    [oak_d_pro_w_front_name, '_link']
                ],
                remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
            )
        ]
    )

    oak_d_pro_w_rear = GroupAction(
        condition = IfCondition(
            PythonExpression([
                '\'',
                oak_d_pro_w_rear_enable_driver,
                '\''
            ])
        ),
        actions = [
            PushRosNamespace([namespace_prefix]),
            Node(
                package='onav_oakd_camera',
                executable='onav_oakd_camera_node',
                name='oak_d_pro_w_rear',
                output='screen',
                respawn=True,
                respawn_delay=20,
                parameters=[{
                    'name': oak_d_pro_w_rear_name,
                    'ip': oak_d_pro_w_rear_ip,
                    'save_directory': '/opt/onav/saved_files/media/',
                    'host_name': 'cpr-rooftop:1180',
                }],
                remappings=[
                    ('/tf', 'tf'), ('/tf_static', 'tf_static'),
                    ('/diagnostics', 'diagnostics'),
                    # ('', ['sensors/', oak_d_pro_w_rear_name, '/camera_info']),
                    ([oak_d_pro_w_rear_name, '/image_color_raw'], ['sensors/camera_', oak_d_pro_w_rear_num, '/color/image']),
                    ([oak_d_pro_w_rear_name, '/imu_data'], ['sensors/camera_', oak_d_pro_w_rear_num, '/imu/data_raw']),
                    ([oak_d_pro_w_rear_name, '/pointcloud'], ['sensors/camera_', oak_d_pro_w_rear_num, '/pointcloud']),
                ]
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='oakd_pro_w_rear_tf_publisher',
                output='screen',
                arguments=[
                    oak_d_pro_w_rear_x,
                    oak_d_pro_w_rear_y,
                    oak_d_pro_w_rear_z,
                    oak_d_pro_w_rear_r,
                    oak_d_pro_w_rear_p,
                    oak_d_pro_w_rear_yaw,
                    oak_d_pro_w_rear_parent_link,
                    [oak_d_pro_w_rear_name, '_link']
                ],
                remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
            )
        ]
    )

    return declared_arguments + [  # noqa: RUF005
        oak_d_pro_w_front,
        oak_d_pro_w_rear,
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
