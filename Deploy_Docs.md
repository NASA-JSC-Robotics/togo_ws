# `togo_deploy` Documentation

Notes on bringing up the `togo_deploy` package.



## Table of Contents

- [`togo_deploy` Documentation](#togo_deploy-documentation)
  - [Table of Contents](#table-of-contents)
  - [`husky_comm.launch.py`](#husky_commlaunchpy)
    - [Husky Configs](#husky-configs)
    - [Clearpath Common Platform Launch](#clearpath-common-platform-launch)
    - [Motor Driver](#motor-driver)
    - [Motor Driver Remappings](#motor-driver-remappings)
  - [`control.launch.py`](#controllaunchpy)
    - [Launch Args](#launch-args)
    - [Controller Configs](#controller-configs)
  - [`togo_sensors.launch.py`](#togo_sensorslaunchpy)
    - [IMU Related Nodes](#imu-related-nodes)
    - [IMU Config Files](#imu-config-files)



## `husky_comm.launch.py`

Togo will eventually have an option to run in simulation or on hardware.
To anticipate this separation, we have separated some hardware-specific launch files and configs to give us more control over what nodes get started.
For more information about what all of the nodes launched in this file do and why, see [Clearpath Hardware Architecture notes](./Clearpath_Hardware_Architecture.md).
The `husky_comm` launch file is adapted from `togo_capture/etc/clearpath/platform/launch/platform-service.launch.py`.

### Husky Configs

Any config files that were copied directly from `togo_capture/etc/clearpath/platform/config/` are placed in the sub-directory `togo_deploy/config/husky/`. The only changes made are to change the node namespace to the more generic `/**:`

### Clearpath Common Platform Launch

The Clearpath generated `platform-service.launch.py` launches many other files, including `clearpath_common platform.launch.py`.
We do not launch this, since we separate everything in that launch file for manual bringup.
Clearpath's platform launch brings up the description, control, localization, teleop base, and teleop joy, all of which are turned into separate launch files for the togo-specific bringup (description, control, sensors, and teleop, respectively).

### Motor Driver

The Husky uses the `lynx_motor_driver`.
The controller config is in `togo_deploy/config/motor_driver.yaml`, adapted from `togo_capture/etc/clearpath/platform/config/control.yaml`.
The `lynx_motor_driver` needs information about [its VCAN device](https://github.com/clearpathrobotics/clearpath_robot/tree/jazzy/clearpath_motor_drivers/lynx_motor_driver) for communication to the MCU.

### Motor Driver Remappings

The `lynx_motor_driver` node includes topic remapping to ensure the appropriate velocity commands get communicated via the `lynx_hardware_interface`.
The `lynx_hardware_interface` gets brought up by the controller manager based on the URDF; the node inside there isn't easily accessible to remap topics, so we won't change the topics expected by the `lynx_hardware_interface`.
Once this remapping is completed, these two nodes will communicate properly and we can send velocity commands to Togo!




## `control.launch.py`

### Launch Args

Inspired by the ER4 Dexterous Robotics Team's approach, there are a few launch arguments that may not be super relevant for the single-robot use case for Togo.
However, we include them just in case, especially since an LTV testbed may be tested in multi-robot applications.
All of these default to empty strings for the single-robot use case.
- `tf_prefix` adds a prefix to each robot link and joint.
For example, `togo_1/base_link` and `togo_2/base_link` are prefixed to differentiate the base links in multiple instances of the same robot.
- `namespace` similarly adds a prefix to ROS nodes, so all node names and topics/services are prefixed.
For example, `togo_1/controller_manager` and `togo_2/controller_manager` differentiate the controller manager nodes for multiple instances of the same robot.

### Controller Configs

Controller configs are adapted from `togo_capture/etc/clearpath/platform/config/control.yaml` to be a little more readable.
In particular, we separate this file into:
- `controllers_a300.yaml` includes the joint state publisher and platform velocity controller.
A few default parameters were changed from `togo_capture`:
  - `tf_frame_prefix_enable` is set to `True`
- `motor_driver.yaml` includes the [`lynx_motor_driver` parameters](#motor-driver), used in [`husky_comm.launch.py`](#husky_commlaunchpy).



## `togo_sensors.launch.py`

Responsible for launching all sensors on Togo, using information from the respective sensor drivers/packages.
- **Seyond LIDAR**: see `seyond_ros_driver/src/seyond_lidar_ros/launch/start_with_config.py` for inspiration example
- **OAK-D Camera**: two cameras, mounted on front and rear of Togo
- **FixPosition GPS/IMU**: called the Inertial Navigation System (INS) sensor provides GPS/IMU data;
see `fixposition_driver/fixposition_driver_ros2/launch/node.launch` for inspiration example
  - See `fixposition_driver/fixposition_driver_ros2/launch/config.yaml` for additional explanation on the node parameters
- **Phidgets Spatial IMU**: additional IMU used by base Clearpath Husky robot;
see `togo_capture/etc/clearpath/sensors/launch/imu_0.launch.py` for inspiration example and more information

This launch file includes flags for launching each sensor.
Config files for each sensor are included within `togo_deploy/config/sensors/`.

### IMU Related Nodes

When the IMU flag is true (`launch_phidgets:=true`), related nodes (IMU filter and EKF localization) are also launched.

### IMU Config Files

There are two config files related to the IMU data:
- `config/sensors/phidgets_imu_config.yaml` includes parameters for 2 nodes: `phidgets_spatial` and the `imu_filter_madgwick`
- `config/husky/imu_filter.yaml` contains parameters for *just* the `imu_filter` node.
This is merely for convenience, but the parameters are nearly identical.

Clearpath actually *only* uses the equivalent of the `phidgets_imu_config.yaml` file and passes this same set of parameters to both the IMU and IMU filter nodes.
For convenience in separation, Togo uses both config files to launch the IMU and IMU filter nodes, respectively.
