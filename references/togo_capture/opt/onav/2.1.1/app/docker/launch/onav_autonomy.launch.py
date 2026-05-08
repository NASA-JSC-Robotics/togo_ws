from clearpath_config.common.utils.yaml import read_yaml
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
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

    outdoornav_sensors_config = onav_config['sensors']

    ################
    # Localization #
    ################
    try:
        outdoornav_localization_config = onav_config['localization']
        enable_localization = outdoornav_localization_config['enabled']
    except (KeyError, TypeError):
        enable_localization = True
    localization_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            '/opt/onav/app/autonomy/launch/localization.launch.py'
        ]),
        launch_arguments={
            'namespace': namespace,
            'enable_localization': str(enable_localization),
        }.items()
    )

    ##############
    # Navigation #
    ##############
    try:
        outdoornav_navigation_config = onav_config['navigation']
        enable_navigation = outdoornav_navigation_config['enabled']
    except (KeyError, TypeError):
        enable_navigation = True
    try:
        outdoornav_navigation_config = onav_config['navigation']
        params_file = outdoornav_navigation_config['param_file']
    except (KeyError, TypeError):
        params_file = '/opt/onav/app/autonomy/params/' + str(model) + '/navigation/nav2_params.yaml'

    navigation_nodes = TimerAction(
        period=30.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    '/opt/onav/app/autonomy/launch/navigation.launch.py'
                ]),
                launch_arguments={
                    'namespace': namespace,
                    'platform_model': model,
                    'enable_navigation': str(enable_navigation),
                    'params_file': params_file,
                }.items()
            )
        ]
    )

    ############
    # Autonomy #
    ############
    try:
        enable_axis_q62 = outdoornav_sensors_config['axis_q62']['enabled']
    except (KeyError, TypeError):
        enable_axis_q62 = False

    try:
        outdoornav_autonomy_config = onav_config['autonomy']
        enable_control_selection = outdoornav_autonomy_config['control_selection']['enabled']
    except (KeyError, TypeError):
        enable_control_selection = True
    try:
        outdoornav_autonomy_config = onav_config['autonomy']
        enable_autonomy_previewer = outdoornav_autonomy_config['path_previewer']['enabled']
    except (KeyError, TypeError):
        enable_autonomy_previewer = True
    try:
        outdoornav_autonomy_config = onav_config['autonomy']
        enable_logger = outdoornav_autonomy_config['logger']['enabled']
    except (KeyError, TypeError):
        enable_logger = True
    try:
        outdoornav_autonomy_config = onav_config['autonomy']
        enable_mission_manager = outdoornav_autonomy_config['mission_manager']['enabled']
    except (KeyError, TypeError):
        enable_mission_manager = True

    if enable_axis_q62:
        axis_q62_config_num = 0; camera_config = None
        camera_listdict = robot_config['sensors']['camera']
        for camera_idx in range(len(camera_listdict)):
            camera_config = camera_listdict[camera_idx]['ros_parameters']
            if camera_listdict[camera_idx]['model'] == 'axis_camera' and \
                camera_config['axis_camera']['device_type'] == 'q62':
                axis_q62_config_num = camera_idx
    else:
        axis_q62_config_num = 0

    autonomy_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            '/opt/onav/app/autonomy/launch/autonomy.launch.py'
        ]),
        launch_arguments={
            'namespace': namespace,
            'platform_model': model,
            'outdoornav_version': onav_config['version'],
            'enable_control_selection': str(enable_control_selection),
            'enable_autonomy_previewer': str(enable_autonomy_previewer),
            'enable_logger': str(enable_logger),
            'enable_mission_manager': str(enable_mission_manager),
            'axis_q62_enable_driver': str(enable_axis_q62),
            'axis_q62_num': str(axis_q62_config_num),
        }.items()
    )

    #########
    # Tasks #
    #########
    task_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            '/opt/onav/app/autonomy/launch/tasks.launch.py'
        ]),
        launch_arguments={
            'namespace': namespace,
        }.items()
    )

    ###########
    # Docking #
    ###########
    docking_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            '/opt/onav/app/autonomy/launch/docking.launch.py'
        ])
    )

    return [  # noqa: RUF005
        localization_nodes,
        navigation_nodes,
        autonomy_nodes,
        docking_node,
        task_nodes,
    ]


def generate_launch_description():

    return LaunchDescription(
       [OpaqueFunction(function=launch_setup)]
    )
