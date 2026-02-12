from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    GroupAction,
    OpaqueFunction,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node, PushRosNamespace
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    hokuyo_num = LaunchConfiguration('hokuyo_num', default='0')
    hokuyo_ip = LaunchConfiguration('hokuyo_ip', default='192.168.131.20')
    hokuyo_frame_id = LaunchConfiguration('hokuyo_frame_id', default=['lidar2d_', hokuyo_num, '_laser'])

    declared_arguments = [
        DeclareLaunchArgument('ros2_namespace', default_value=namespace),
        DeclareLaunchArgument('hokuyo_num', default_value=hokuyo_num),
        DeclareLaunchArgument('hokuyo_ip', default_value=hokuyo_ip),
        DeclareLaunchArgument('hokuyo_frame_id', default_value=hokuyo_frame_id),
    ]

    lifecycle_node = LifecycleNode(
        package='urg_node2',
        executable='urg_node2_node',
        name=LaunchConfiguration('node_name'),
        remappings=[
            ('scan', ['sensors/lidar2d_', hokuyo_num, '/scan']),
            ('/diagnostics', 'diagnostics')
        ],
        parameters=[{
                    'ip_address': hokuyo_ip,
                    'ip_port': 10940,
                    'frame_id': hokuyo_frame_id,
                    'publish_intensity': True,
                    'angle_min': -1.5,
                    'angle_max': 1.5
                    }],
        namespace='',
        output='screen',
    )

    urg_node2_node_configure_event_handler = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=lifecycle_node,
            on_start=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(lifecycle_node),
                        transition_id=Transition.TRANSITION_CONFIGURE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_start')),
    )

    urg_node2_node_activate_event_handler = RegisterEventHandler(
        event_handler=OnStateTransition(
            target_lifecycle_node=lifecycle_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(lifecycle_node),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_start')),
    )

    filter_params = {'filter1': {'name': 'intensity', 'type': 'laser_filters/LaserScanIntensityFilter',
                                 'params': {'lower_threshold': 0.0, 'upper_threshold': 15000.0, 'disp_histogram': 1}}}

    filter_node = Node(
        namespace=namespace_prefix,
        package="laser_filters",
        executable="scan_to_scan_filter_chain",
        parameters=[filter_params],
        remappings=[
            ('scan', ['sensors/lidar2d_', hokuyo_num, '/scan']),
            ('scan_filtered', ['sensors/lidar2d_', hokuyo_num, '/scan_filtered'])
        ]
    )

    return declared_arguments + [  # noqa: RUF005
        GroupAction(actions = [
            PushRosNamespace([namespace_prefix]),
            DeclareLaunchArgument('auto_start', default_value='true'),
            DeclareLaunchArgument('node_name', default_value='urg_node2'),
            lifecycle_node,
            urg_node2_node_configure_event_handler,
            urg_node2_node_activate_event_handler,
            TimerAction(period=30.0, actions=[filter_node])
        ])
    ]


def generate_launch_description():

    return LaunchDescription(
        [OpaqueFunction(function=launch_setup)]
    )
