#!/bin/bash

# set up fixposition
pushd src/external/fixposition_driver || exit
ROS_DISTRO=jazzy ./setup_ros_ws.sh
popd || exit
# remove ROS1 dependency from package.xml
./scripts/remove_ros1_package_dependency.py -p src/external/fixposition_driver/fixposition-sdk/fpsdk_apps

# set up seyond
pushd src/external/seyond_ros_driver/src/seyond_lidar_ros/src/seyond_sdk/build || exit
./build_unix.sh
popd || exit
