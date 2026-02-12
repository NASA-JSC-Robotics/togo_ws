from launch import LaunchDescription
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace', default='').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    params_file = '/opt/onav/app/autonomy/params/a300/docking/docking_params.yaml'

    docking_node = Node(
        package='onav_docking',
        executable='docking_node',
        output='screen',
        parameters=[params_file],
        respawn=True,
        respawn_delay=5.0,
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
    )

    return [
        PushRosNamespace(namespace_prefix),
        docking_node
    ]


def generate_launch_description():
    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
