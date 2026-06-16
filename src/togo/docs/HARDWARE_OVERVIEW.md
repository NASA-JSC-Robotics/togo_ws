# Togo Hardware Overview

Brief overview of the Togo hardware components.

## Husky A300 AMP

The Clearpath Husky A300 Autonomous Mobile Platform (AMP) known as Togo as outdoor/rugged differential drive wheels.
This means the robot can be commanded in the linear x-direction (forward/backward) and the angular z-direction (rotating left/right around the vertical z-axis).

### Lights

The Husky includes 4 status lights, two in front and two in rear.
The most commonly seen status light indicators are described in the [Hardware Run Instructions](../README.md#hardware-run-instructions).
For more information about the status lights, please refer to the [Husky User Manual](https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a300/user_manual_husky/#status-lights).

## Sensors

Togo uses the following sensors:

- Front and rear OAK-D (RGB-D) cameras
- Seyond 3D LIDAR
- Phidgets Spatial IMU
- Fixposition GPS

These sensors are included automatically in the Togo workspace.
Please refer to our [sensor source code documentation](./SENSOR_SOURCE_CODE.md) for more information about the sensor packages used in this workspace.
