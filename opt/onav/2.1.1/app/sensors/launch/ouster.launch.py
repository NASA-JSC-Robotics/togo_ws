from pathlib import Path

import launch
from launch import LaunchDescription
from launch.actions import EmitEvent, LogInfo, OpaqueFunction, RegisterEventHandler
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node, PushRosNamespace
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
import lifecycle_msgs.msg


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    ouster_num = LaunchConfiguration('ouster_num', default='0')
    ouster_ip = LaunchConfiguration('ouster_ip', default='192.168.131.20')
    ouster_udp_dest_ip = LaunchConfiguration('ouster_udp_dest_ip', default='192.168.131.1')

    ground_filter_params_file = '/opt/onav/app/sensors/config/ground_segmentation_params.yaml'

    os_driver = LifecycleNode(
        package='ouster_ros',
        executable='os_driver',
        name='ouster_driver',
        namespace=[namespace_prefix, '/sensors/lidar3d_', ouster_num],
        parameters=[
            {'sensor_hostname': ouster_ip},
            {'timestamp_mode': 'TIME_FROM_ROS_TIME'},
            {'lidar_frame': ['lidar3d_', ouster_num, '_laser']},
            {'imu_frame': ['lidar3d_', ouster_num, '_imu']},
            {'point_cloud_frame': ['lidar3d_', ouster_num, '_laser']},
            {'computer_ip': ouster_udp_dest_ip},
            {'sensor_frame': ['lidar3d_', ouster_num, '_sensor_link']},
            {'udp_dest': ouster_udp_dest_ip},
            {'organized': False}
        ],
        remappings=[
            ('/tf_static', [namespace_prefix, '/tf_static']),
            ('points', 'pointcloud'),
            ('imu', 'imu/data_raw'),
        ],
        output='screen',
    )

    sensor_configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(os_driver),
            transition_id=lifecycle_msgs.msg.Transition.TRANSITION_CONFIGURE,
        )
    )

    sensor_activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=os_driver, goal_state='inactive',
            entities=[
                LogInfo(msg="os_driver activating..."),
                EmitEvent(event=ChangeState(
                    lifecycle_node_matcher=matches_action(os_driver),
                    transition_id=lifecycle_msgs.msg.Transition.TRANSITION_ACTIVATE,
                )),
            ],
            handle_once=True
        )
    )

    sensor_finalized_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=os_driver, goal_state='finalized',
            entities=[
                LogInfo(
                    msg="Failed to communicate with the sensor in a timely manner."),
                EmitEvent(event=launch.events.Shutdown(
                    reason="Couldn't communicate with sensor"))
            ],
        )
    )

    voxel_filter = Node(
        package="pcl_ros",
        executable='filter_voxel_grid_node',
        name='ouster_voxel_filter',
        parameters=[{
            'leaf_size': 0.05,
            'filter_field_name': 'x',
            'filter_limit_min': 0.1,
            'filter_limit_max': 30.0,
        }],
        remappings=[
            ('input', ['sensors/lidar3d_', ouster_num, '/pointcloud']),
            ('output', ['sensors/lidar3d_', ouster_num, '/pointcloud_voxel']),
        ]
    )

    ground_segmentation_filter = Node(
        package='patchworkpp',
        executable='patchworkpp_node',
        name='ouster_segmentation',
        remappings=[
            ("pointcloud_topic", ['sensors/lidar3d_', ouster_num, '/pointcloud']),
            ("/patchworkpp/cloud", ['sensors/lidar3d_', ouster_num, '/cloud']),
            ("/patchworkpp/ground", ['sensors/lidar3d_', ouster_num, '/ground']),
            ("/patchworkpp/nonground", ['sensors/lidar3d_', ouster_num, '/nonground'])
        ],
        parameters=[ground_filter_params_file],
    )

    radius_outlier_filter = Node(
        package="pcl_ros",
        executable='filter_radius_outlier_removal_node',
        name='ouster_nonground_noise_filter',
        parameters=[{
            'min_neighbors': 5,
            'radius_search': 0.15,
        }],
        remappings=[
            ('input', ['sensors/lidar3d_', ouster_num, '/nonground']),
            ('output', ['sensors/lidar3d_', ouster_num, '/nonground_filtered']),
        ]
    )

    return [
        PushRosNamespace(namespace_prefix),
        os_driver,
        sensor_configure_event,
        sensor_activate_event,
        sensor_finalized_event,
        voxel_filter,
        ground_segmentation_filter,
        radius_outlier_filter
    ]


def generate_launch_description():

    return LaunchDescription(
        [OpaqueFunction(function=launch_setup)]
    )
