from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace
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

    # initialize arguments
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")
    x = LaunchConfiguration("robot_x")
    y = LaunchConfiguration("robot_y")
    z = LaunchConfiguration("robot_z")

    # include packages
    pkg_deploy = FindPackageShare("togo_deploy")
    pkg_gazebo = FindPackageShare("togo_gz")

    # config files
    gz_bridge_config = PathJoinSubstitution([pkg_gazebo, "config", "bridge.yaml"])
    rgbd_point_fix_config = PathJoinSubstitution([pkg_gazebo, "config", "rgbd_point_fix.yaml"])

    # start world
    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_gazebo, "launch", "start_world.launch.py"]))
    )

    # Gazebo nodes
    gz_sim_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-entity",
            "togo",
            "-name",
            "togo",
            "-topic",
            "robot_description",
            "-x",
            x,
            "-y",
            y,
            "-z",
            z,
            "-controller_manager",
            "controller_manager",
        ],
        output="screen",
    )
    gz_bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="sim_bridge",
        parameters=[
            {
                "config_file": gz_bridge_config,
                "qos_overrides./tf_static.publisher.durability": "transient_local",
            }
        ],
        output="screen",
    )

    # Togo control
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_deploy, "launch", "control.launch.py"])),
        launch_arguments={
            "robot_description_package": "togo_gz",
            "robot_description_file": "togo_gz.urdf.xacro",
            "is_sim": "true",
            "tf_prefix": tf_prefix,
            "ns": ns,
        }.items(),
    )

    # fix the rgbd point clouds
    
    rgbd_point_fix_config = PathJoinSubstitution([pkg_gazebo, "config", "rgbd_point_fix.yaml"])

    gz_rgbd_point_fixer = Node(
        package="togo_gz",
        executable="gz_rgbd_point_fixer",
        name="gz_rgbd_point_fixer",
        parameters=[rgbd_point_fix_config]
    )

    launches_nodes = [
        world_launch,
        gz_sim_node,
        gz_bridge_node,
        control_launch,
        gz_rgbd_point_fixer,
    ]

    ns_action = GroupAction(actions=[PushRosNamespace(ns)] + launches_nodes)

    return LaunchDescription(declared_arguments + [ns_action])
