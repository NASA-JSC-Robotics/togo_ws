#!/bin/bash

# set up fixposition
pushd src/external/fixposition_driver || exit
ROS_DISTRO=jazzy ./setup_ros_ws.sh
popd || exit
# remove ROS1 dependency from package.xml
sed -i "s|<depend>fpsdk_ros1</depend>|<!-- <depend>fpsdk_ros1</depend> -->|g" src/external/fixposition_driver/fixposition-sdk/fpsdk_apps/package.xml

# set up seyond
pushd src/external/seyond_ros_driver/src/seyond_lidar_ros/src/seyond_sdk/build || exit
./build_unix.sh
popd || exit
