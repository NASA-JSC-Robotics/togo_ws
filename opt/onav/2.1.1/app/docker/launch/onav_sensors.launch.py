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
    outdoornav_sensors_config = onav_config['sensors']

    launch_sensors = []

    ###############
    # INS sensors #
    ###############
    xvn_config_num = 0; xvn_config = None
    ins_sensors_listdict = robot_config.get('sensors', {}).get('ins')
    if ins_sensors_listdict:
        for ins_idx in range(len(ins_sensors_listdict)):
            if ins_sensors_listdict[ins_idx]['model'] == 'fixposition':
                xvn_config_num = ins_idx
                xvn_config = ins_sensors_listdict[xvn_config_num]['ros_parameters']['fixposition_driver']

        # XVN #
        try:
            xvn_launch = outdoornav_sensors_config['xvn']['enabled']
        except (KeyError, TypeError):
            xvn_launch = False
        if xvn_launch:
            if xvn_config is not None:
                xvn = IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        '/opt/onav/app/sensors/launch/xvn.launch.py'
                    ]),
                    launch_arguments={
                        'namespace': namespace,
                        'xvn_ip': xvn_config['ip'],
                        'xvn_rate': str(xvn_config['rate'])
                    }.items()
                )
                launch_sensors.append(xvn)
            else:
                print(f'[ERROR] [launch] \'xvn\' config missing from {DEFAULT_ROBOT_CONFIG_PATH}')
                raise SystemExit('')
    else:
        print(f'[WARN] [launch] No ins sensors defined in {DEFAULT_ROBOT_CONFIG_PATH}')

    ###################
    # Lidar2D sensors #
    ###################
    hokuyo_config_num = 0; hokuyo_config = None
    lms1xx_config_num = 0; lms1xx_config = None
    lidar2d_sensors_listdict = robot_config.get('sensors', {}).get('lidar2d')

    if lidar2d_sensors_listdict:
        for lidar2d_idx in range(len(lidar2d_sensors_listdict)):
            if lidar2d_sensors_listdict[lidar2d_idx]['model'] == 'hokuyo_ust':
                hokuyo_config_num = lidar2d_idx
                hokuyo_config = lidar2d_sensors_listdict[hokuyo_config_num]['ros_parameters']['urg_node']
            elif lidar2d_sensors_listdict[lidar2d_idx]['model'] == 'sick_lms1xx':
                lms1xx_config_num = lidar2d_idx
                lms1xx_config = lidar2d_sensors_listdict[lms1xx_config_num]['ros_parameters']['lms1xx']

        # Hokuyo #
        try:
            hokuyo_launch = outdoornav_sensors_config['hokuyo']['enabled']
        except (KeyError, TypeError):
            hokuyo_launch = False
        if hokuyo_launch:
            if hokuyo_config is not None:
                hokuyo = IncludeLaunchDescription(
                            PythonLaunchDescriptionSource([
                                '/opt/onav/app/sensors/launch/hokuyo.launch.py'
                            ]),
                            launch_arguments={
                                'namespace': namespace,
                                'hokuyo_num': str(hokuyo_config_num),
                                'hokuyo_ip': hokuyo_config['ip_address'],
                            }.items()
                )
                launch_sensors.append(hokuyo)
            else:
                print(f'[ERROR] [launch] \'hokuyo\' config missing from {DEFAULT_ROBOT_CONFIG_PATH}')
                raise SystemExit('')

        # LMS1XX #
        try:
            lms1xx_launch = outdoornav_sensors_config['lms1xx']['enabled']
        except (KeyError, TypeError):
            lms1xx_launch = False
        if lms1xx_launch:
            if lms1xx_config is not None:
                lms1xx = IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        '/opt/onav/app/sensors/launch/lms1xx.launch.py'
                    ]),
                    launch_arguments={
                        'namespace': namespace,
                        'lms1xx_frame_id': lms1xx_config['frame_id'],
                        'lms1xx_lidar_ip': lms1xx_config['host'],
                    }.items()
                )
                launch_sensors.append(lms1xx)
            else:
                print(f'[ERROR] [launch] \'lms1xx\' config missing from {DEFAULT_ROBOT_CONFIG_PATH}')
                raise SystemExit('')
    else:
        print(f'[WARN] [launch] No lidar2d sensors defined in {DEFAULT_ROBOT_CONFIG_PATH}')

    ###################
    # Lidar3D sensors #
    ###################
    robin_w_config_num = 0; robin_w_config = None
    ouster_config_num = 0; ouster_config = None
    lidar3d_sensors_listdict = robot_config.get('sensors', {}).get('lidar3d')

    if lidar3d_sensors_listdict:
        for lidar3d_idx in range(len(lidar3d_sensors_listdict)):
            if lidar3d_sensors_listdict[lidar3d_idx]['model'] == 'seyond_lidar':
                robin_w_config_num = lidar3d_idx
                robin_w_config = lidar3d_sensors_listdict[robin_w_config_num]['ros_parameters']['seyond_node']
            elif lidar3d_sensors_listdict[lidar3d_idx]['model'] == 'ouster_os1':
                ouster_config_num = lidar3d_idx
                ouster_config = lidar3d_sensors_listdict[ouster_config_num]['ros_parameters']['ouster_driver']

        # Robin W #
        try:
            robin_w_launch = outdoornav_sensors_config['robin_w']['enabled']
        except (KeyError, TypeError):
            robin_w_launch = False
        if robin_w_launch:
            if robin_w_config is not None:
                robin_w = IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        '/opt/onav/app/sensors/launch/robin_w.launch.py'
                    ]),
                    launch_arguments={
                        'namespace': namespace,
                        # 'robin_w_frame_id': robin_w_config['frame_id'],
                        'robin_w_num': str(robin_w_config_num),
                        'robin_w_ip': robin_w_config['ip_address'],
                    }.items(),
                )
                launch_sensors.append(robin_w)
            else:
                print(f'[ERROR] [launch] \'seyond_lidar\' config missing from {DEFAULT_ROBOT_CONFIG_PATH}')
                raise SystemExit('')

        # Ouster #
        try:
            ouster_launch = outdoornav_sensors_config['ouster']['enabled']
        except (KeyError, TypeError):
            ouster_launch = False
        if ouster_launch:
            if ouster_config is not None:
                ouster = IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        '/opt/onav/app/sensors/launch/ouster.launch.py'
                    ]),
                    launch_arguments={
                        'namespace': namespace,
                        'ouster_num': str(ouster_config_num),
                        'ouster_ip': ouster_config['sensor_hostname'],
                        'ouster_udp_dest_ip': ouster_config['udp_dest'],
                    }.items()
                )
                launch_sensors.append(ouster)
            else:
                print(f'[ERROR] [launch] \'ouster_os1\' config missing from {DEFAULT_ROBOT_CONFIG_PATH}')
                raise SystemExit('')
    else:
        print(f'[WARN] [launch] No lidar3d sensors defined in {DEFAULT_ROBOT_CONFIG_PATH}')

    ###########
    # Cameras #
    ###########
    oakd_front_config_num = 0; oakd_front_config = None
    oakd_rear_config_num = 0; oakd_rear_config = None
    axis_q62_config_num = 0; axis_q62_config = None
    camera_listdict = robot_config.get('sensors', {}).get('camera')

    if camera_listdict:
        camera_idx = 0
        while camera_idx <= len(camera_listdict) - 1:
            if camera_listdict[camera_idx]['model'] == 'luxonis_oakd':
                # assume that both oak d cameras are entered one after the other
                oakd_front_config_num = camera_idx
                oakd_front_config = camera_listdict[oakd_front_config_num]['ros_parameters']['oakd']
                if camera_idx + 1 <= len(camera_listdict) - 1:
                    camera_idx += 1
                else:
                    break
                oakd_rear_config_num = camera_idx
                oakd_rear_config = camera_listdict[oakd_rear_config_num]['ros_parameters']['oakd']
            elif camera_listdict[camera_idx]['model'] == 'axis_camera':
                axis_q62_config_num = camera_idx
                axis_q62_config = camera_listdict[axis_q62_config_num]['ros_parameters']['axis_camera']

            camera_idx += 1

        # Axis Q62 #
        try:
            axis_q62_launch = outdoornav_sensors_config['axis_q62']['enabled']
        except (KeyError, TypeError):
            axis_q62_launch = False
        if axis_q62_launch:
            if axis_q62_config is not None:
                axis_q62 = IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        '/opt/onav/app/sensors/launch/axis_q62.launch.py'
                    ]),
                    launch_arguments={
                        'namespace': namespace,
                        'axis_q62_num': str(axis_q62_config_num),
                        'hostname': axis_q62_config['hostname'],
                    }.items()
                )
                launch_sensors.append(axis_q62)
            else:
                print(f'[ERROR] [launch] \'axis_q62\' config missing from {DEFAULT_ROBOT_CONFIG_PATH}')
                raise SystemExit('')

                # axis_ptz = IncludeLaunchDescription(
                #     PythonLaunchDescriptionSource([
                #         '/opt/onav/app/sensors/launch/axis_ptz.launch.py'
                #     ]),
                #     launch_arguments={
                #         'namespace': namespace,
                #     }.items()
                # )

                # axis_top = IncludeLaunchDescription(
                #     PythonLaunchDescriptionSource([
                #         '/opt/onav/app/sensors/launch/axis_top.launch.py'
                #     ]),
                #     launch_arguments={
                #         'namespace': namespace,
                #     }.items()
                # )

                # flir_boson = IncludeLaunchDescription(
                #     PythonLaunchDescriptionSource([
                #         '/opt/onav/app/sensors/launch/flir_boson.launch.py'
                #     ]),
                #     launch_arguments={
                #         'namespace': namespace,
                #     }.items()
                # )

        # # Oak D Pro W PoE #
        oakd_front_args = {}; oakd_rear_args = {}
        oak_d_launch_args = {
            'namespace': namespace
        }
        try:
            oakd_front_launch = outdoornav_sensors_config['oakd_front']['enabled']
        except (KeyError, TypeError):
            oakd_front_launch = False
        try:
            oakd_rear_launch = outdoornav_sensors_config['oakd_rear']['enabled']
        except (KeyError, TypeError):
            oakd_rear_launch = False
        if (oakd_front_launch and oakd_front_config is not None) or \
           (oakd_rear_launch and oakd_rear_config is not None):
            if oakd_front_launch:
                oakd_front_args = {
                    'oak_d_pro_w_front_enable_driver': str(oakd_front_launch),
                    'oak_d_pro_w_front_num': str(oakd_front_config_num),
                    'oak_d_pro_w_front_ip': oakd_front_config['camera']['i_ip'],
                    'oak_d_pro_w_front_parent_link': camera_listdict[oakd_front_config_num]['parent'],
                    'oak_d_pro_w_front_x': str(camera_listdict[oakd_front_config_num]['xyz'][0]),
                    'oak_d_pro_w_front_y': str(camera_listdict[oakd_front_config_num]['xyz'][1]),
                    'oak_d_pro_w_front_z': str(camera_listdict[oakd_front_config_num]['xyz'][2]),
                    'oak_d_pro_w_front_r': str(camera_listdict[oakd_front_config_num]['rpy'][0]),
                    'oak_d_pro_w_front_p': str(camera_listdict[oakd_front_config_num]['rpy'][1]),
                    'oak_d_pro_w_front_yaw': str(camera_listdict[oakd_front_config_num]['rpy'][2]),
                }
            if oakd_rear_launch:
                oakd_rear_args = {
                    'oak_d_pro_w_rear_enable_driver': str(oakd_rear_launch),
                    'oak_d_pro_w_rear_num': str(oakd_rear_config_num),
                    'oak_d_pro_w_rear_ip': oakd_rear_config['camera']['i_ip'],
                    'oak_d_pro_w_rear_parent_link': camera_listdict[oakd_rear_config_num]['parent'],
                    'oak_d_pro_w_rear_x': str(camera_listdict[oakd_rear_config_num]['xyz'][0]),
                    'oak_d_pro_w_rear_y': str(camera_listdict[oakd_rear_config_num]['xyz'][1]),
                    'oak_d_pro_w_rear_z': str(camera_listdict[oakd_rear_config_num]['xyz'][2]),
                    'oak_d_pro_w_rear_r': str(camera_listdict[oakd_rear_config_num]['rpy'][0]),
                    'oak_d_pro_w_rear_p': str(camera_listdict[oakd_rear_config_num]['rpy'][1]),
                    'oak_d_pro_w_rear_yaw': str(camera_listdict[oakd_rear_config_num]['rpy'][2]),
                }
            oak_d_launch_args.update(oakd_front_args)
            oak_d_launch_args.update(oakd_rear_args)
            oak_d_pro_w = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    '/opt/onav/app/sensors/launch/oak_d_pro_w.launch.py'
                ]),
                launch_arguments=oak_d_launch_args.items()
            )
            launch_sensors.append(oak_d_pro_w)
        else:
            if oakd_front_config is None or oakd_rear_config is None:
                print(f'[ERROR] [launch] \'oak_d\' config missing from {DEFAULT_ROBOT_CONFIG_PATH}')
                raise SystemExit('')
    else:
        print(f'[WARN] [launch] No camera sensors defined in {DEFAULT_ROBOT_CONFIG_PATH}')

    #############################
    # Sensors not in robot.yaml #
    #############################
    # Flir Boson #
    try:
        flir_boson_launch = outdoornav_sensors_config['flir_boson']['enabled']
    except (KeyError, TypeError):
        flir_boson_launch = False
    if flir_boson_launch:
        flir_boson = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                '/opt/onav/app/sensors/launch/flir_boson.launch.py'
            ]),
            launch_arguments={
                'namespace': namespace,
            }.items()
        )
        launch_sensors.append(flir_boson)

    # Shotgun Microphone #
    try:
        microphone_launch = outdoornav_sensors_config['microphone']['enabled']
    except (KeyError, TypeError):
        microphone_launch = False
    if microphone_launch:
        microphone = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                '/opt/onav/app/sensors/launch/microphone.launch.py'
            ]),
            launch_arguments={
                'namespace': namespace,
            }.items()
        )
        launch_sensors.append(microphone)

    return launch_sensors


def generate_launch_description():
    return LaunchDescription([OpaqueFunction(function=launch_setup)])
