# Copyright (c) 2026, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
#
# All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import PushRosNamespace, SetParameter
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
    ns = LaunchConfiguration("ns")
    use_sim_time = LaunchConfiguration("use_sim_time")

    # include packages
    pkg_deploy = FindPackageShare("togo_deploy")
    pkg_gazebo = FindPackageShare("togo_gz")
    pkg_nav2 = FindPackageShare("togo_nav2")

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_gazebo, "launch", "sim_gz.launch.py"])),
        launch_arguments={"rviz": "false", "world": "b59_localization_world.sdf"}.items(),
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_nav2, "launch", "navigation.launch.py"]))
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_nav2, "launch", "slam.launch.py"])),
    )

    # RViz
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_nav2, "launch", "nav2_rviz.launch.py"])),
    )

    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([pkg_deploy, "launch", "teleop.launch.py"])),
    )

    push_sim_time = SetParameter("use_sim_time", use_sim_time)

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
