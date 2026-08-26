# Software License Agreement (BSD)
#
# @author    Roni Kreinin <rkreinin@clearpathrobotics.com>
# @copyright (c) 2023, Clearpath Robotics, Inc., All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of Clearpath Robotics nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
import os

from ament_index_python.packages import get_package_share_directory

from clearpath_config.clearpath_config import ClearpathConfig
from clearpath_config.common.utils.yaml import read_yaml

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)

from launch_ros.actions import PushRosNamespace, SetRemap

from nav2_common.launch import RewrittenYaml


ARGUMENTS = [
    DeclareLaunchArgument("use_sim_time", default_value="true", choices=["true", "false"], description="Use sim time"),
    DeclareLaunchArgument(
        "autostart",
        default_value="true",
        choices=["true", "false"],
        description="Automatically startup the slamtoolbox. Ignored when use_lifecycle_manager is true.",
    ),  # noqa: E501
    DeclareLaunchArgument(
        "use_lifecycle_manager",
        default_value="false",
        choices=["true", "false"],
        description="Enable bond connection during node activation",
    ),
    DeclareLaunchArgument("sync", default_value="true", choices=["true", "false"], description="Use synchronous SLAM"),
    DeclareLaunchArgument("scan_topic", default_value="", description="/husky/sensors/seyond/scan"),
]


def launch_setup(context, *args, **kwargs):
    # Packages
    pkg_togo_nav2 = get_package_share_directory("togo_nav2")
    pkg_slam_toolbox = get_package_share_directory("slam_toolbox")

    # Launch Configurations
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")
    use_lifecycle_manager = LaunchConfiguration("use_lifecycle_manager")
    sync = LaunchConfiguration("sync")
    scan_topic = LaunchConfiguration("scan_topic")
    eval_scan_topic = scan_topic.perform(context)

    if len(eval_scan_topic) == 0:
        eval_scan_topic = "/husky/sensors/lidar2d_0/scan"
    #        eval_scan_topic = f'/{namespace}/sensors/lidar2d_0/scan'

    file_parameters = PathJoinSubstitution([pkg_togo_nav2, "config", "slam.yaml"])

    launch_slam_sync = PathJoinSubstitution([pkg_slam_toolbox, "launch", "online_sync_launch.py"])

    launch_slam_async = PathJoinSubstitution([pkg_slam_toolbox, "launch", "online_async_launch.py"])

    slam = GroupAction(
        [
            #        PushRosNamespace(namespace),
            #        SetRemap('/tf', '/' + namespace + '/tf'),
            #        SetRemap('/tf_static', '/' + namespace + '/tf_static'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(launch_slam_sync),
                launch_arguments=[
                    ("use_sim_time", use_sim_time),
                    ("autostart", autostart),
                    ("use_lifecycle_manager", use_lifecycle_manager),
                    ("slam_params_file", file_parameters),
                ],
                condition=IfCondition(sync),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(launch_slam_async),
                launch_arguments=[
                    ("use_sim_time", use_sim_time),
                    ("autostart", autostart),
                    ("use_lifecycle_manager", use_lifecycle_manager),
                    ("slam_params_file", file_parameters),
                ],
                condition=UnlessCondition(sync),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([pkg_togo_nav2, "launch", "pointcloud2laserscan.launch.py"])
                ),
            ),
        ]
    )

    return [slam]


def generate_launch_description():
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(OpaqueFunction(function=launch_setup))
    return ld
