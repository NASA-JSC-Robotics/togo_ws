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

## Deploy

To deploy Togo hardware:

1. Start Husky hardware communications:
    ```bash
    ros2 launch togo_deploy husky_comm.launch.py
    ```

2. Start Togo's controllers:
    ```bash
    ros2 launch togo_deploy control.launch.py
    ```

3. Start Togo's sensors:
    ```bash
    ros2 launch togo_deploy togo_sensors.launcy.py
    ```

### Deploy Testing

This info will eventually be wrapped up in the `systemd` processes on the Togo controls computer.
For now, a few helpful notes on manually starting/stopping Clearpath services:
- Stopping Clearpath:
  - `sudo systemctl stop clearpath-robot.service` to stop all of the Clearpath processes
  - `sudo systemctl disable clearpath-robot.service` to disable all of the Clearpath processes and prevent them from automatically restarting when they die
  - Clearpath starts a lot of docker containers by default. We can view all of the running containers:
    ```bash
    docker container ps
    ```
    To stop all running Clearpath dockers:
    ```bash
    docker stop $(docker ps -q)
    ```
  - As a sanity check, you can confirm everything has stopped using `systemctl status clearpath-robot.service` and `docker container ps`
- Starting the background Clearpath services that we do actually need:
  - ROS discovery service: copy the commands from `/etc/clearpath/discovery-server-start`:
    - `source /opt/ros/jazzy/setup.bash`
    - `fastdds discovery -i 0 -p 11811`
    - This server will hang in the terminal
  - VCAN
    - `sudo systmctl start clearpath-vcan.service`
    - Check the status of this process using `systemctl status clearpath-vcan.service`
- Restarting Clearpath:
  - `sudo systemctl enable clearpath-robot.service`
  - `sudo systemctl start clearpath-robot.service`
