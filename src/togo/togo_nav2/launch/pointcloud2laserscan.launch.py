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
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="pointcloud_to_laserscan",
                executable="pointcloud_to_laserscan_node",
                name="pointcloud_to_laserscan_node",
                remappings=[("cloud_in", "/husky/sensors/seyond/points"), ("scan", "/husky/sensors/seyond/scan")],
                parameters=[
                    {
                        #                'target_frame': 'camera_0_rgb_camera_frame',              # Center of your camera frame
                        "use_sim_time": True,
                        "transform_tolerance": 0.01,
                        "min_height": 0.0,  # Min Z point to consider (meters)
                        "max_height": 20.5,  # Max Z point to consider (meters)
                        "angle_min": -1.5708,  # -90 degrees
                        "angle_max": 1.5708,  # 90 degrees
                        "angle_increment": 0.0087,  # Resolution of scan
                        "range_min": 0.5,  # Min range (meters)
                        "range_max": 30.0,  # Max range (meters)
                        "use_inf": True,
                    }
                ],
            )
        ]
    )
