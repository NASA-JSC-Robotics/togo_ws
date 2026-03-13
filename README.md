# togo

## Sensors

### OAK-D cameras 
These run from apt packages included from ros-jazzy-depthai-ros.
These end up launching the driver itself for the camera information, as well as a node that converts the RGBD data into point clouds.
Both of these nodes are launched inside a composable node container.
I think the source code should be [here](https://github.com/luxonis/depthai-ros/tree/jazzy).

### Fixposition GNSS
These run on this open source driver package, [fixposition_driver](https://github.com/fixposition/fixposition_driver) package.
The documentation for the driver exists [here](https://docs.fixposition.com/fd/fixposition-ros-driver)

### Seyond 3D lidar
These run on this open source driver package, [seyond_ros_driver](https://github.com/Seyond-Inc/seyond_ros_driver).

### Phidgets spatial

I think this is based on the apt package ros-jazzy-phidgets-spatial.
Clearpath typically launches the generic driver node along with an imu filter node as well. 
These also get launched as a part of a composable node container.
I think the source code should be [here](https://github.com/ros-drivers/phidgets_drivers/tree/jazzy).

## External packages to pull in source code from

fixposition_driver
* The driver is located [here](https://github.com/fixposition/fixposition_driver). 
  * Make sure you are cloning recursively, as there are submodles.
* There is an extra step where you should run the script `setup_ros_ws.sh` from the fixposition_driver directory in your directory. Instructions are [here](<https://docs.fixposition.com/fd/installation-and-usage#Installationandusage-a)SetupdriverforanexistingROSworkspace>). It seems like that might just add some colcon ignores on things you don't need depending on your ros version.

seyond_ros_driver
* The driver is located [here](https://github.com/Seyond-Inc/seyond_ros_driver). 
  * Make sure you are cloning recursively, as there are submodles.
* There are instructions for building the drivers inside the workspace [here](https://github.com/Seyond-Inc/seyond_ros_driver/blob/main/src/seyond_lidar_ros/README.md#compile).