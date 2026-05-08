import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml


def launch_setup(context, *args, **kwargs):

    stdout_linebuf_envvar = SetEnvironmentVariable(
        'RCUTILS_LOGGING_BUFFERED_STREAM', '1'
    )

    namespace = LaunchConfiguration('namespace', default='').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    platform_model = LaunchConfiguration('platform_model')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')
    use_respawn = LaunchConfiguration('use_respawn')
    log_level = LaunchConfiguration('log_level')
    enable_navigation = LaunchConfiguration('enable_navigation')

    lifecycle_nodes = [
        'controller_server',
        'smoother_server',
        'planner_server',
        'behavior_server',
        'velocity_smoother',
        'onav_navigator',
        'collision_monitor'
    ]

    # Map fully qualified names to relative ones so the node's namespace can be prepended.
    # In case of the transforms (tf), currently, there doesn't seem to be a better alternative
    # https://github.com/ros/geometry2/issues/32
    # https://github.com/ros/robot_state_publisher/pull/30
    # TODO(orduno) Substitute with `PushNodeRemapping`
    #              https://github.com/ros2/launch_ros/issues/56
    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    # Create our own temporary YAML files that include substitutions
    param_substitutions = {'autostart': autostart}

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key=namespace,
            param_rewrites=param_substitutions,
            convert_types=True,
        ),
        allow_substs=True,
    )

    declared_arguments = [
        DeclareLaunchArgument('namespace', default_value='', description='Top-level namespace'),
        DeclareLaunchArgument('platform_model', default_value=platform_model),
        DeclareLaunchArgument('params_file', default_value=os.path.join('/opt/onav/app/autonomy/params/', str(platform_model), '/navigation/nav2_params.yaml'),
                              description='Full path to the ROS2 parameters file to use for all launched nodes'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Automatically startup the nav2 stack'),
        DeclareLaunchArgument('use_respawn', default_value='true',
                              description='Whether to respawn if a node crashes. Applied when composition is disabled.'),
        DeclareLaunchArgument('log_level', default_value='info', description='log level'),
        DeclareLaunchArgument('enable_navigation', default_value=enable_navigation),
    ]

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    nav2_nodes = GroupAction(
        condition=IfCondition(
            PythonExpression([
                '\'',
                enable_navigation,
                '\''
            ])
        ),
        actions=[
            Node(
                package='nav2_controller',
                executable='controller_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
                remappings=[*remappings,
                            ('cmd_vel', 'cmd_vel_nav'),
                            ('/points/nonground', f'{namespace_prefix}/sensors/lidar3d_0/nonground_filtered'),
                            ('/points', f'{namespace_prefix}/sensors/lidar3d_0/pointcloud'),
                            ('/autonomy/context_grid', f'{namespace_prefix}/autonomy/context_grid'),
                ],
            ),
            Node(
                package='nav2_smoother',
                executable='smoother_server',
                name='smoother_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
                remappings=[*remappings,
                  ('/autonomy/context_grid', f'{namespace_prefix}/autonomy/context_grid'),
                ],
            ),
            Node(
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
                remappings=[*remappings,
                  ('/autonomy/context_grid', f'{namespace_prefix}/autonomy/context_grid'),
                ],
            ),
            Node(
                package='nav2_behaviors',
                executable='behavior_server',
                name='behavior_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
                remappings=[*remappings, ('cmd_vel', 'cmd_vel_nav')],
            ),
            Node(
                package='onav_navigation',
                executable='onav_navigator_node',
                name='onav_navigator',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
                remappings=remappings,
            ),
            Node(
                package='nav2_velocity_smoother',
                executable='velocity_smoother',
                name='velocity_smoother',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
                remappings=[*remappings, ('cmd_vel', 'cmd_vel_nav')],
            ),
            Node(
                package='nav2_collision_monitor',
                executable='collision_monitor',
                name='collision_monitor',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
                remappings=[*remappings,
                            ('/points/nonground', f'{namespace_prefix}/sensors/lidar3d_0/nonground_filtered'),
                            ('/points', f'{namespace_prefix}/sensors/lidar3d_0/pointcloud'),
                ],
            ),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_navigation',
                output='screen',
                respawn=use_respawn,
                respawn_delay=5.0,
                arguments=['--ros-args', '--log-level', log_level],
                parameters=[{'autostart': autostart}, {'node_names': lifecycle_nodes}],
            ),
        ],
    )

    set_collision_avoidance_node = Node(
        namespace=namespace,
        package='onav_navigation',
        executable='set_collision_avoidance_node.py',
        name='set_collision_avoidance',
        output='screen',
    )

    return declared_arguments + [  # noqa: RUF005
        PushRosNamespace(namespace_prefix),
        nav2_nodes
        # set_collision_avoidance_node,
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
