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
    namespace = LaunchConfiguration('namespace', default='').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    enable_localization = LaunchConfiguration('enable_localization')

    declared_arguments = [
        DeclareLaunchArgument('namespace', default_value=namespace),
        DeclareLaunchArgument('enable_localization', default_value=enable_localization),
    ]

    localization = GroupAction(
        condition=IfCondition(
            PythonExpression([
                '\'',
                enable_localization,
                '\''
            ])
        ),
        actions=[
            PushRosNamespace(namespace_prefix),
            Node(
                name='localization',
                namespace='',
                package='onav_localization',
                executable='localization_node',
                output='screen',
                remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='map_odom_publisher',
                output='screen',
                arguments=["0", "0", "0", "0", "0", "0", "1", "map", "odom"],
                remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
            )
        ]
    )

    return [*declared_arguments, localization]


def generate_launch_description():

    return LaunchDescription(
        [OpaqueFunction(function=launch_setup)]
    )
