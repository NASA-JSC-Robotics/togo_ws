from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace, SetParameter
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # declare launch arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "tf_prefix",
            default_value="",
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation time",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_x",
            default_value="0.0",
            description="Initial X-position of the robot when spawned into Gazebo",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_y",
            default_value="0.0",
            description="Initial Y-position of the robot when spawned into Gazebo",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_z",
            default_value="0.2",
            description="Initial Z-position of the robot when spawned into Gazebo",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "rviz", default_value="true", description="Flag to start RViz for robot and sensor checkout."
        )
    )

    # initialize arguments
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")
    x = LaunchConfiguration("robot_x")
    y = LaunchConfiguration("robot_y")
    z = LaunchConfiguration("robot_z")
    rviz = LaunchConfiguration("rviz")
    use_sim_time = LaunchConfiguration("use_sim_time")

    # include packages
    pkg_deploy = FindPackageShare("togo_deploy")
    pkg_gazebo = FindPackageShare("togo_gz")
    pkg_nav2 = FindPackageShare("togo_nav2")

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_gazebo, "launch", "sim_gz.launch.py"])),
            launch_arguments={
                'rviz': 'false',
                'world': 'b59_localization_world.sdf'
            }.items()  
    )


    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_nav2, "launch", "navigation.launch.py"])),
            launch_arguments={
                'rviz': 'false',
            }.items()  
    )


    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_nav2, "launch", "slam.launch.py"])
        ),
    )

    # RViz
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_nav2, "launch", "nav2_rviz.launch.py"])
        ),
    )

    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_deploy, "launch", "teleop.launch.py"])
        ),
    )

    push_sim_time = SetParameter('use_sim_time', use_sim_time)

    launches_nodes = [
        push_sim_time,
        sim_launch,
        nav2_launch,
        slam_launch,
        rviz_launch,
        teleop_launch,
    ]

    ns_action = GroupAction(actions=[PushRosNamespace(ns)] + launches_nodes)

    return LaunchDescription(declared_arguments + [ns_action])
