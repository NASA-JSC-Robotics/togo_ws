# `togo_deploy` Documentation

Notes on bringing up the `togo_deploy` package.

## Running List of Misc TODOs

- [ ] Testing deploy functionality
  - [ ] in `controllers_a300.yaml`, does changing `tf_frame_prefix_enable` to `True` cause problems given that I also manually included the `tf_prefix`?
  - [ ] double check tf_prefixing for lynx motor controller too; joint names have been changed in `motor_driver.yaml` config file
  - [ ] double check that IMU filter container is set up properly, especially with topic remappings
- [ ] Docs
  - [x] include link to Clearpath Hardware notes when that gets merged in
  - [ ] tidy up, especially under `husky_comm`; right now it's very stream-of-consciousness
  - [ ] remove scratch work; put that somewhere internal
- [ ] Repo
  - [ ] Verify all dependencies are used
  - [ ] Verify all exec dependencies (especially in husky_comm) are in package.xml!

## `togo_sensors.launch.py`

Responsible for launching all sensors on Togo, using information from the respective sensor drivers/packages.
- **Seyond LIDAR**: see `seyond_ros_driver/src/seyond_lidar_ros/launch/start_with_config.py` for inspiration example
- **OAK-D Camera**: two cameras, mounted on front and rear of Togo
- **FixPosition GPS/IMU**: called the Inertial Navigation System (INS) sensor provides GPS/IMU data;
see `fixposition_driver/fixposition_driver_ros2/launch/node.launch` for inspiration example
  - See `fixposition_driver/fixposition_driver_ros2/launch/config.yaml` for additional explanation on the node parameters
- **Phidgets Spatial IMU**: additional IMU used by base Clearpath Husky robot;
see `togo_capture/etc/clearpath/sensors/launch/imu_0.launch.py` for inspiration example and more information

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
We also separate into multiple configs to separate basic ROS2 robot configs (`controllers_common`) from platform-specific configs (`controllers_a300`).
As more components are added to Togo, their controller configs can be similarly separated.
- `controllers_common.yaml` is pretty generic, just joint state publisher (which we expect to exist for any ROS2 robot)
- `controllers_a300.yaml` includes controllers specific to the Clearpath Husky.
A few default parameters were changed from `togo_capture`:
  - `tf_frame_prefix_enable` is set to `True`

## `husky_comm.launch.py`

Togo will eventually have an option to run in simulation or on hardware.
To anticipate this separation, we have separated some hardware-specific launch files and configs to give us more control over what nodes get started.
For more information about what all of the nodes launched in this file do and why, see [Clearpath Hardware Architecture notes](./Clearpath_Hardware_Architecture.md).
The `husky_comm` launch file is adapted from `togo_capture/etc/clearpath/platform/launch/platform-service.launch.py`.

### Husky Configs

Any config files that were copied directly from `togo_capture/etc/clearpath/platform/config/` are placed in the sub-directory `togo_deploy/config/husky/`. The only changes made are to change the node namespace to the more generic `/**:`

### Ignore `clearpath_common` Platform Launch

Clearpath generated launch files will launch this `clearpath_common platform.launch.py`.  We do not launch this, since we separate these out for manual bringup.  Platform brings up the description, control, localization, teleop base, and teleop joy, all of which are turned into separate launch files.

### Ignore `foxglove_bridge`

The [Foxglove bridge](https://docs.foxglove.dev/docs/visualization/ros-foxglove-bridge) is used for data visualization purposes. Phoebe seems to ignore this, so Togo will too.

### Motor Driver

The Husky uses the `lynx_motor_driver`.
The controller config is in `togo_deploy/config/motor_driver.yaml`, adapted from `togo_capture/etc/clearpath/platform/config/control.yaml`.
The `lynx_motor_driver` needs information about [its VCAN device](https://github.com/clearpathrobotics/clearpath_robot/tree/jazzy/clearpath_motor_drivers/lynx_motor_driver) for communication to the MCU.

## teleop

Ignore BlueTooth cutoff (BT cutoff node); Phoebe does something similar, its params are removed from `teleop_joy.yaml`

## sensors

IMU launches related nodes, specifically EKF localization and IMU filter
- `config/sensors/phidgets_imu_config.yaml` includes params for 2 nodes: `phidgets_spatial` and the `imu_filter_madgwick`
- `config/husky/imu_filter.yaml` contains params for *just* the `imu_filter` node; this is merely for convenience, but you will notice the params are exactly the same between these two files
- Clearpath seems to actually *only* use the equivalent of the `phidgets_imu_config.yaml` and pass this same set of params to both the IMU and filter node

## SCRATCH WORK

### clearpath capture

Summarizing from [here](./Software%20Infrastructure.md):
- `togo_capture/etc/clearpath/` contains all of the launch/config files generated by Clearpath
- `togo_capture/lib/systemd/system/` contains all of the systemd services that generate the launch files
- `togo_capture/usr/sbin/` contains the scripts that are run by the systemd services to generate the launch files

Verify that all generated files (in `etc/clearpath`) are understood and something comparable is replicated in the resulting `togo_deploy` package:
- [x] `├── discovery-server-start` (starts ROS discovery service)
  - [x] called by `lib/systemd/system/clearpath-discovery.service`
- [x] `├── manipulators` (no manipulators, and we'd generate the necessary files from the MoveIt Setup Assistant)
- [x] `│   ├── config`
- [x] `│   │   ├── control.yaml`
- [x] `│   │   └── moveit.yaml`
- [x] `│   └── launch`
- [x] `│       └── manipulators-service.launch.py`
- [x] `├── platform`
- [x] `│   ├── config`
- [x] `│   │   ├── control.yaml`
- [x] `│   │   ├── diagnostic_aggregator.yaml`
- [x] `│   │   ├── diagnostic_updater.yaml`
- [x] `│   │   ├── foxglove_bridge.yaml`
- [x] `│   │   ├── imu_filter.yaml`
- [x] `│   │   ├── localization.yaml`
- [x] `│   │   ├── teleop_interactive_markers.yaml`
- [x] `│   │   ├── teleop_joy.yaml`
- [x] `│   │   └── twist_mux.yaml`
- [x] `│   └── launch`
- [x] `│       └── platform-service.launch.py`
  - [x] `clearpath_common platform.launch.py`
    - [x] robot description: `clearpath_platform_description description.launch.py`
      - [x] Includes some remappings for the `robot_state_publisher`; Phoebe ignores them, so Togo will too
    - [x] controller manager/spawner: `clearpath_control control.launch.py`
    - [x] togo sensors: `clearpath_control localization.launch.py`
    - [x] togo teleop: `clearpath_control teleop_base.launch.py`
    - [x] togo teleop: `clearpath_control teleop_joy.launch.py`
  - [x] diagnostics, called directly from togo: `clearpath_diagnostics diagnostics.launch.py`
  - [x] ignored in togo: `clearpath_diagnostics foxglove_bridge.launch.py`
  - [x] VCAN0, called directly from togo: `clearpath_ros2_socketcan_interface receiver.launch.py`
  - [x] VCAN0, called directly from togo: `clearpath_ros2_socketcan_interface sender.launch.py`
  - [x] VCAN1, called directly from togo: `canopen_inventus bringup inventus.launch.py`
- [x] `├── platform-extras`
- [x] `│   └── launch`
- [x] `│       └── platform-extras-service.launch.py`
- [x] `├── robot.srdf` (just disables a bunch of collisions)
- [x] `├── robot.srdf.xacro` (empty)
- [x] `├── robot.urdf.xacro` (copied into togo description)
- [x] `├── robot.yaml`
- [x] `├── sensors`
- [x] `│   ├── config`
- [x] `│   │   └── imu_0.yaml` (phidgets config)
- [x] `│   └── launch`
- [x] `│       ├── imu_0.launch.py`
  - [x] `clearpath_sensors phidgets_spatial.launch.py`
  - [x] `clearpath_sensors imu_filter.launch.py`
- [x] `│       └── sensors-service.launch.py`
- [x] `├── setup.bash`
  - [x] Sets ROS configuration variables, `ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, ROS discovery server, ROS super client
- [x] `├── vcan-start`
  - [x] called by `lib/systemd/system/clearpath-vcan.service`
  - [x] Starts the VCAN bridges for devices VCAN0 and VCAN1
- [x] `└── zenoh-router-start`
  - [x] called by `lib/systemd/system/clearpath-zenoh-router.service`
  - [x] Starts [Zenoh ROS Middleware](https://docs.clearpathrobotics.com/docs/ros/networking/ros2_networking/zenoh/)
  - [x] But this script seems mostly empty and just complains that Zenoh is not the right RMW implementation?
  - [x] Plus `robot.yaml` seems to use [Fast RTPS](https://github.com/clearpathrobotics/Fast-RTPS) as the middleware implementation, not Zenoh anyway...
  - [x] BUT since we aren't using the `robot.yaml`, I don't think that's actually the middleware we're using...


### package outlines

`phoebe_deploy` files (mark complete when file has been reviewed):
- [x] `├── CMakeLists.txt`
- [x] `├── config`
- [x] `│   ├── controllers_common.yaml`
- [x] `│   ├── controllers_ewellix.yaml`
- [x] `│   ├── controllers_hande.yaml`
- [x] `│   ├── controllers_moveit_pro.yaml`
- [x] `│   ├── controllers_r100.yaml`
- [x] `│   ├── controllers_ur.yaml`
- [x] `│   ├── pb_left.yaml`
- [x] `│   ├── pb_right.yaml`
- [x] `│   ├── ridgeback`
- [x] `│   │   ├── can_config.yaml`
- [x] `│   │   ├── imu_filter.yaml`
- [x] `│   │   ├── lidar2d_0.yaml`
- [x] `│   │   ├── localization.yaml`
- [x] `│   │   ├── robot.yaml`
- [x] `│   │   ├── teleop_interactive_markers.yaml`
- [x] `│   │   ├── teleop_joy.yaml`
- [x] `│   │   └── twist_mux.yaml`
- [x] `│   └── teleop_interactive_markers.yaml`
- [x] `├── launch`
- [x] `│   ├── control_hardware.launch.py`
- [x] `│   ├── control.launch.py`
- [x] `│   ├── control_mock_hardware.launch.py`
- [x] `│   ├── pb_ur_gui.launch.py`
- [x] `│   ├── phoebe_rspc_camera.launch.py`
- [x] `│   ├── realsense_cameras.launch.py`
- [x] `│   ├── ridgeback_comm.launch.py`
- [x] `│   ├── ridgeback_sensors.launch.py`
- [x] `│   ├── spawn_controllers`
- [x] `│   │   ├── spawn_controllers_admittance.launch.py`
- [x] `│   │   ├── spawn_controllers_ewellix.launch.py`
- [x] `│   │   ├── spawn_controllers_hande.launch.py`
- [x] `│   │   ├── spawn_controllers_r100.launch.py`
- [x] `│   │   └── spawn_controllers_ur.launch.py`
- [x] `│   ├── spawn_controllers.launch.py`
- [x] `│   ├── teleop.launch.py`
- [x] `│   ├── transport`
- [x] `│   │   ├── transport_control.launch.py`
- [x] `│   │   ├── transport.launch.py`
- [x] `│   │   └── transport_robot_state_publisher.launch.py`
- [x] `│   └── ur_tools.launch.py`
- [x] `├── package.xml`
- [x] `└── scripts`
- [x] `│   ├── keyboard_joy.py`
- [x] `│   ├── odometry_joint_state_publisher.py`
- [x] `│   ├── prioritize_threads.sh`
- [x] `│   ├── world_publisher.py`


`togo_deploy` files:
- [x] `├── CMakeLists.txt`
- [x] `├── config`
- [x] `│   ├── controllers_a300.yaml`
- [x] `│   ├── husky`
- [x] `│   │   ├── diagnostic_aggregator.yaml`
- [x] `│   │   ├── diagnostic_updater.yaml`
- [x] `│   │   ├── imu_filter.yaml`
- [x] `│   │   ├── localization.yaml`
- [x] `│   │   ├── robot.yaml`
- [x] `│   │   ├── teleop_interactive_markers.yaml`
- [x] `│   │   ├── teleop_joy.yaml`
- [x] `│   │   └── twist_mux.yaml`
- [x] `│   ├── motor_driver.yaml`
- [x] `│   └── sensors`
- [x] `│       ├── front_oakd_config.yaml`
- [x] `│       ├── ins_config.yaml`
- [x] `│       ├── phidgets_imu_config.yaml`
- [x] `│       ├── rear_oakd_config.yaml`
- [x] `│       └── seyond_config.yaml`
- [x] `├── launch`
- [x] `│   ├── control_hardware.launch.py`
- [x] `│   ├── control.launch.py`
- [x] `│   ├── husky_comm.launch.py`
- [x] `│   ├── teleop.launch.py`
- [x] `│   └── togo_sensors.launch.py`
- [x] `└── package.xml`
