#!/bin/bash

# set up fixposition
cd src/external/fixposition_driver || exit
./setup_ros_ws.sh
cd - || exit
# remove ROS1 dependency from package.xml
./scripts/remove_ros1_package_dependency.py -p src/external/fixposition_driver/fixposition-sdk/fpsdk_apps

# set up seyond
cd src/external/seyond_ros_driver/src/seyond_lidar_ros/src/seyond_sdk/build || exit
./build_unix.sh
cd - || exit
