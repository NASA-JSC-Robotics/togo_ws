from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    namespace_prefix = '' if namespace == '' else '/' + namespace

    xvn_ip = LaunchConfiguration('xvn_ip', default='192.168.131.35')
    xvn_port = LaunchConfiguration('xvn_port', default='21001').perform(context)
    xvn_rate = LaunchConfiguration('xvn_rate', default='200')
    xvn_reconnect_delay = LaunchConfiguration('xvn_reconnect_delay', default='5')
    xvn_gnss1_num = LaunchConfiguration('xvn_gnss1_num', default='0')
    xvn_gnss2_num = LaunchConfiguration('xvn_gnss2_num', default='1')
    xvn_imu_num = LaunchConfiguration('xvn_imu_num', default='0')

    declared_arguments = [
        DeclareLaunchArgument('namespace', default_value=namespace),
        DeclareLaunchArgument('xvn_ip', default_value=xvn_ip),
        DeclareLaunchArgument('xvn_port', default_value=xvn_port),
        DeclareLaunchArgument('xvn_rate', default_value=xvn_rate),
        DeclareLaunchArgument('xvn_reconnect_delay', default_value=xvn_reconnect_delay),
        DeclareLaunchArgument('xvn_gnss1_num', default_value=xvn_gnss1_num),
        DeclareLaunchArgument('xvn_gnss2_num', default_value=xvn_gnss2_num),
        DeclareLaunchArgument('xvn_imu_num', default_value=xvn_imu_num),
    ]

    return declared_arguments + [    # noqa: RUF005
        GroupAction(
            actions = [
                PushRosNamespace(namespace_prefix),
                Node(
                    package='fixposition_driver_ros2',
                    executable='fixposition_driver_ros2_exec',
                    name='xvn',
                    output='screen',
                    respawn=True,
                    respawn_delay=10,
                    parameters=[{
                        'fp_output.formats': ["ODOMETRY", "LLH", "ODOMENU", "ODOMSH", "ODOMSTATUS", "RAWIMU",
                                              "CORRIMU", "IMUBIAS", "GNSSANT", "GNSSCORR", "EOE", "TEXT",
                                              "TP", "GPGGA", "GPGLL", "GNGSA", "GPGST", "GPHDT", "GPRMC",
                                              "GPVTG", "GPZDA", "GXGSV"],
                        'fp_output.port': str(xvn_port),
                        'fp_output.ip': xvn_ip,
                        'fp_output.rate': xvn_rate,
                        'fp_output.type': 'tcp',
                        'fp_output.reconnect': xvn_reconnect_delay,
                        'fp_output.qos_type': 'default_long',
                        'customer_input.speed_topic': f'{namespace_prefix}/sensors/ins_0/xvn/input_wheel_speed',
                        'customer_input.rtcm_topic': f'{namespace_prefix}/sensors/ins_0/xvn/input_rtcm_data',
                    }],
                    remappings=[
                        ('/tf', 'tf'),
                        ('/tf_static', 'tf_static'),
                        ('/fixposition/gnss1', [namespace_prefix, '/sensors/ins_0/gps_', xvn_gnss1_num , '/fix']),
                        ('/fixposition/gnss2', [namespace_prefix, '/sensors/ins_0/gps_', xvn_gnss2_num , '/fix']),
                        ('/fixposition/corrimu', [namespace_prefix, '/sensors/ins_0/imu/data']),
                        ('/fixposition/fpa/eoe', [namespace_prefix, '/sensors/ins_0/xvn/fpa/eoe']),
                        ('/fixposition/fpa/gnssant', [namespace_prefix, '/sensors/ins_0/xvn/fpa/gnssant']),
                        ('/fixposition/fpa/gnsscorr', [namespace_prefix, '/sensors/ins_0/xvn/fpa/gnsscorr']),
                        ('/fixposition/fpa/imubias', [namespace_prefix, '/sensors/ins_0/xvn/fpa/imubias']),
                        ('/fixposition/fpa/llh', [namespace_prefix, '/sensors/ins_0/xvn/fpa/llh']),
                        ('/fixposition/fpa/odomenu', [namespace_prefix, '/sensors/ins_0/xvn/fpa/odomenu']),
                        ('/fixposition/fpa/odometry', [namespace_prefix, '/sensors/ins_0/xvn/fpa/odometry']),
                        ('/fixposition/fpa/odomsh', [namespace_prefix, '/sensors/ins_0/xvn/fpa/odomsh']),
                        ('/fixposition/fpa/odomstatus', [namespace_prefix, '/sensors/ins_0/xvn/fpa/odomstatus']),
                        ('/fixposition/fpa/text', [namespace_prefix, '/sensors/ins_0/xvn/fpa/text']),
                        ('/fixposition/fpa/tp', [namespace_prefix, '/sensors/ins_0/xvn/fpa/tp']),
                        ('/fixposition/imu_ypr', [namespace_prefix, '/sensors/ins_0/xvn/imu_ypr']),
                        ('/fixposition/nmea', [namespace_prefix, '/sensors/ins_0/xvn/nmea']),
                        ('/fixposition/nmea/gngsa', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gngsa']),
                        ('/fixposition/nmea/gpgga', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gpgga']),
                        ('/fixposition/nmea/gpgll', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gpgll']),
                        ('/fixposition/nmea/gpgst', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gpgst']),
                        ('/fixposition/nmea/gphdt', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gphdt']),
                        ('/fixposition/nmea/gprmc', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gprmc']),
                        ('/fixposition/nmea/gpvtg', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gpvtg']),
                        ('/fixposition/nmea/gpzda', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gpzda']),
                        ('/fixposition/nmea/gxgsv', [namespace_prefix, '/sensors/ins_0/xvn/nmea/gxgsv']),
                        ('/fixposition/odometry_ecef', [namespace_prefix, '/sensors/ins_0/xvn/odometry_ecef']),
                        ('/fixposition/odometry_enu', [namespace_prefix, '/sensors/ins_0/xvn/odometry_enu']),
                        ('/fixposition/odometry_llh', [namespace_prefix, '/sensors/ins_0/xvn/odometry_llh']),
                        ('/fixposition/odometry_smooth', [namespace_prefix, '/sensors/ins_0/xvn/odometry_smooth']),
                        ('/fixposition/poiimu', [namespace_prefix, '/sensors/ins_0/xvn/poiimu']),
                        ('/fixposition/rawimu', [namespace_prefix, '/sensors/ins_0/xvn/rawimu']),
                        ('/fixposition/ypr', [namespace_prefix, '/sensors/ins_0/xvn/ypr']),
                    ]
                ),
            ]
        )
    ]


def generate_launch_description():

    return LaunchDescription(
        [OpaqueFunction(function=launch_setup)]
    )
