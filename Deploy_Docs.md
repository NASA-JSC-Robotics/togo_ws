# `togo_deploy` Documentation

Notes on bringing up the `togo_deploy` package.

## `togo_sensors.launch.py`

Responsible for launching all sensors on Togo, using information from the respective sensor drivers/packages.
- **Seyond LIDAR**: see `seyond_ros_driver/src/seyond_lidar_ros/launch/start_with_config.py` for inspiration example
- **OAK-D Camera**: two cameras, mounted on front and rear of Togo
- **FixPosition GPS/IMU**: called the Intertial Navigation System (INS) sensor provides GPS/IMU data; see `fixposition_driver/fixposition_driver_ros2/launch/node.launch` for inspiration example
  - See `fixposition_driver/fixposition_driver_ros2/launch/config.yaml` for additional explanation on the node parameters

