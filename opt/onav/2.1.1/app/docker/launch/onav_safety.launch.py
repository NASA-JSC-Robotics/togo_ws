from clearpath_config.clearpath_config import ClearpathConfig
from clearpath_config.common.utils.yaml import read_yaml
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

DEFAULT_ROBOT_CONFIG_PATH = '/etc/clearpath/robot.yaml'
DEFAULT_OUTDOORNAV_CONFIG_PATH = '/opt/onav/config/outdoornav.yaml'


def launch_setup(context, *args, **kwargs):

    # Read YAML
    robot_config_path = LaunchConfiguration('robot_config_path',
                                            default=DEFAULT_ROBOT_CONFIG_PATH).perform(context)
    robot_config = read_yaml(robot_config_path)
    onav_config_path = LaunchConfiguration('onav_config_path',
                                            default=DEFAULT_OUTDOORNAV_CONFIG_PATH).perform(context)
    onav_config = read_yaml(onav_config_path)

    # Parse YAML into config
    namespace = robot_config['system']['ros2']['namespace']
    model = robot_config['serial_number'].split("-")[0]

    try:
        enable_watchdogs = onav_config['safety']['watchdogs']['enabled']
    except (KeyError, TypeError):
        enable_watchdogs = True

    safety_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            '/opt/onav/app/autonomy/launch/safety.launch.py'
        ]),
        launch_arguments={
            'namespace': namespace,
            'platform_model': model,
            'enable_watchdogs': str(enable_watchdogs),
        }.items()
    )

    return [safety_nodes]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
