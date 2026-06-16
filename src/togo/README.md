# Togo

Instructions for running Togo, the Clearpath A300 Husky Autonomous Mobile Platform (AMP).
Please refer to the [Husky User Manual](https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a300/user_manual_husky/) for more in-depth information.

The Togo platform includes several systemd services that run whenever the robot is booted up.
These services take the place of the default Clearpath configuration that comes on the robot out-of-the-box.
For more information about enabling/disabling Clearpath's baseline configuration, please refer to our [Clearpath systemd docs](./docs/CLEARPATH_SYSTEMD_SERVICES.md).

![Togo Robot](./docs/images/togo.jpg)

## Table of Contents

- [Togo](#togo)
  - [Table of Contents](#table-of-contents)
  - [Hardware Run Instructions](#hardware-run-instructions)
    - [Transport Mode](#transport-mode)
    - [Non-Transport Mode](#non-transport-mode)
    - [Joystick Control](#joystick-control)
    - [Launch Sensors](#launch-sensors)
    - [Shutting Down the Robot](#shutting-down-the-robot)
  - [Gazebo Run Instructions](#gazebo-run-instructions)

## Hardware Run Instructions

See our [hardware overview docs](./docs/HARDWARE_OVERVIEW.md) for more information about Togo's hardware components.

Hardware instructions are taken directly from the [Husky Quick Start](https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a300/user_manual_husky/#quick-start) guide.
However, we provide additional details specific to Togo's setup.

1. Verify the robot is in a ready state.
   1. Unplug the charger and any ethernet cables.
   2. Close the port hatch door.
    The robot will not run if this hatch is open.

    ![Port Hatch](./docs/images/togo-back-labeled.png)

2. Press and hold the Power Button for one second and then release it.

    ![Power Button](./docs/images/power-and-reset-buttons-labeled.jpg)

3. Wait one minute for the robot's computer and MCU to boot up.
4. Ensure all e-stops (front and rear) are unplunged.
  If one of the e-stops is pressed, all 4 status lights will be blinking red in unison.
  Once the e-stops are released, the status lights will blinking red, alternating left/right, indicating the safety restart button needs to be pressed.
5. Press and release the Safety Restart button.
6. When the robot is up and ready to go, the front lights should be solid white and the rear lights (by the mast) should be solid red.
7. All remaining hardware instructions will be run on the robot's control computer.
   1. SSH into the robot from the console computer:

      ```bash
      ssh robot
      ```

   2. Connect to the [hardware development docker container](../../README.md#hardware-development-image).
   By default, this container will already be running:

      ```bash
      # connect to the already running container
      docker compose exec hw-dev terminator # TODO is this right? or would it be transport?
      ```

> [!NOTE]
> Unless otherwise noted, all remaining hardware instructions should be run on the robot's control computer in the hardware development docker container.

### Transport Mode

By default, Togo starts in `transport_mode`.
This means the basic platform comm nodes, control nodes, and joystick control nodes are brought up in the Togo docker container when the robot starts.
For more in-depth information about what transport mode does, please refer to [transport mode docs](../../references/documentation/Transport_Mode.md).

To check whether Togo is in transport mode:

```bash
systemctl status togo-transport.service
```

We expect to see the service as started, enabled, and active (all green).

If the previous steps were completed in transport mode, then Togo is ready to go!
See [joystick control](#joystick-control) below for more information on driving Togo.

### Non-Transport Mode

To stop transport mode, run the following alias on Togo (*not* in the docker container):

```bash
stop_transport_mode
```

This kills the docker container running transport mode.
This means all of the basic platform comm and control nodes are no longer running.

To bring up the robot manually in non-transport mode:

1. Start Husky hardware communications:

    ```bash
    ros2 launch togo_deploy husky_comm.launch.py
    ```

2. To bring up Togo's controllers and teleop control (enabling control through the PS4 controller),
we include a few convenient launch file for Togo's hardware operation mode.

    ```bash
    ros2 launch togo_deploy control_hardware.launch.py
    ```

    This launch file is equivalent to launching controls and teleop separately:

    ```bash
    # controllers
    ros2 launch togo_deploy control.launch.py
    # teleop
    ros2 launch togo_deploy teleop.launch.py
    ```

To restart transport mode, restart the robot.

### Joystick Control

At this point after following the instructions above (for either transport or non-transport mode), joystick control should be active on the robot.
To use the PS4 controller to run the robot:

1. Ensure the controller is charged.
2. Press the middle button to power the controller on and connect it to the robot.
3. L1 is the fast mode deadman switch, R1 is the slow mode deadman switch.
 Press and hold either deadman for whichever drive mode is desired.
 By default, fast mode velocity and acceleration limits are twice as fast as the slow mode limits.
4. Use the left joystick to send linear (x-direction) commands to Togo. Use the right joystick to send angular (z-direction) commands to Togo.

![PS4 Controller](./docs/images/ps4-controller-labeled.png)

### Launch Sensors

Start Togo's sensors (and related nodes, including the IMU filter and localization) and view the robot and sensor data in RViz:

```bash
ros2 launch togo_deploy togo_sensors.launch.py
```

For more information about the sensors available on Togo, please see [hardware overview of sensors](./docs/HARDWARE_OVERVIEW.md#sensors).

### Shutting Down the Robot

When you're done with Togo for the day:

1. Stop any nodes you started.
2. Exit the docker container.
3. Turn off the robot by pressing the power button.
4. Plug the robot in to charge.
    ![Charger](./docs/images/charger.jpg)
5. Say "Good boy, Togo!" and give him a lil pat of appreciation.


## Gazebo Run Instructions

To bring up Togo in Gazebo, run:

```bash
ros2 launch togo_gz sim_gz.launch.py
```

This launch file will launch the controls appropriately from the `togo_deploy` package using the Gazebo URDF in the `togo_gz` package.
The Gazebo URDF instantiates the Togo macro in `togo_description` and adds the appropriate `ros2_control` plugins for Gazebo.
This launch file will also automatically launch RViz to view the simulated robot and sensor information.

Once Gazebo is running, you can publish velocity commands from the command line:

```bash
ros2 topic pub --once /platform_velocity_controller/cmd_vel geometry_msgs/msg/TwistStamped 'header:
  stamp: now
  frame_id: ''
twist:
  linear:
    x: 0.0
    y: 0.0
    z: 0.0
  angular:
    x: 0.0
    y: 0.0
    z: 0.5
'
```

Publish a zero command to stop the robot:

```bash
ros2 topic pub --once /platform_velocity_controller/cmd_vel geometry_msgs/msg/TwistStamped 'header:
  stamp: now
  frame_id: ''
twist:
  linear:
    x: 0.0
    y: 0.0
    z: 0.0
  angular:
    x: 0.0
    y: 0.0
    z: 0.0
'
```

If you have any problems running Gazebo, please refer to our [Gazebo troubleshooting docs](./docs/GAZEBO_TROUBLESHOOTING.md).
