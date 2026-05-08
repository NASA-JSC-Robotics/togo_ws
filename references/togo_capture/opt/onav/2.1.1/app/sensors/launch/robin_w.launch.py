from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer, PushRosNamespace
from launch_ros.descriptions import ComposableNode


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    robin_w_num = LaunchConfiguration('robin_w_num', default='0')
    robin_w_name = LaunchConfiguration('robin_w_name', default='seyond')
    robin_w_frame_id = LaunchConfiguration('robin_w_frame_id', default=['lidar3d_', robin_w_num, '_laser'])
    robin_w_ip = LaunchConfiguration('robin_w_ip', default='192.168.131.25')

    declared_arguments = [
        DeclareLaunchArgument('namespace', default_value=namespace),
        DeclareLaunchArgument('robin_w_num', default_value=robin_w_num),
        DeclareLaunchArgument('robin_w_name', default_value=robin_w_name),
        DeclareLaunchArgument('robin_w_frame_id', default_value=robin_w_frame_id),
        DeclareLaunchArgument('robin_w_ip', default_value=robin_w_ip),
    ]
    ground_filter_params_file = '/opt/onav/app/sensors/config/ground_segmentation_params.yaml'

    return declared_arguments + [   # noqa: RUF005
        GroupAction(
            actions = [
                PushRosNamespace(namespace_prefix),
                ComposableNodeContainer(
                    name='robinw_container',
                    namespace='',
                    package='rclcpp_components',
                    executable='component_container',
                    output='screen',
                    composable_node_descriptions=[
                        ComposableNode(
                            package='seyond',
                            plugin='seyond::SeyondDriverComponent',
                            name='robinw_driver',
                            parameters=[
                                {'lidar_name': robin_w_name},
                                {'lidar_ip': robin_w_ip},
                                {'frame_id': robin_w_frame_id},
                                {'min_range': 0.25},
                                {'log_level': 'error'}
                            ],
                            remappings=[
                                ('iv_packets', ['sensors/lidar3d_', robin_w_num, '/packets']),
                                ('iv_points', ['sensors/lidar3d_', robin_w_num, '/pointcloud']),
                            ],
                            extra_arguments=[{'use_intra_process_comms': True}],
                        ),
                        ComposableNode(
                            package="pcl_ros",
                            plugin='pcl_ros::VoxelGrid',
                            name='robinw_voxel_filter',
                            parameters=[{
                                'leaf_size': 0.05,
                                'filter_field_name': 'x',
                                'filter_limit_min': 0.1,
                                'filter_limit_max': 30.0,
                            }],
                            extra_arguments=[{'use_intra_process_comms': True}],
                            remappings=[
                                ('input', ['sensors/lidar3d_', robin_w_num, '/pointcloud']),
                                ('output', ['sensors/lidar3d_', robin_w_num, '/pointcloud_voxel']),
                            ]
                        ),
                        ComposableNode(
                            package="pcl_ros",
                            plugin='pcl_ros::RadiusOutlierRemoval',
                            name='robinw_nonground_noise_filter',
                            parameters=[{
                                'min_neighbors': 5,
                                'radius_search': 0.15,
                            }],
                            extra_arguments=[{'use_intra_process_comms': True}],
                            remappings=[
                                ('input', ['sensors/lidar3d_', robin_w_num, '/nonground']),
                                ('output', ['sensors/lidar3d_', robin_w_num, '/nonground_filtered']),
                            ]
                        ),
                        ComposableNode(
                            package='patchworkpp',
                            plugin='patchworkpp_ros::GroundSegmentationServer',
                            name='robinw_segmentation',
                            remappings=[
                                ("pointcloud_topic", ['sensors/lidar3d_', robin_w_num, '/pointcloud']),
                                ("/patchworkpp/cloud", ['sensors/lidar3d_', robin_w_num, '/cloud']),
                                ("/patchworkpp/ground", ['sensors/lidar3d_', robin_w_num, '/ground']),
                                ("/patchworkpp/nonground", ['sensors/lidar3d_', robin_w_num, '/nonground'])
                            ],
                            parameters=[ground_filter_params_file],
                            extra_arguments=[{'use_intra_process_comms': True}]
                        )
                    ]
                )
            ]
        )
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
