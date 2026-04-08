# Clearpath Hardware Notes

If we do our job right with the `togo_deploy` package, none of this information is really important for how to get the robot up and running.
Ideally, all of this gets started up and runs in the background, enabling us to do our cool robotics things on top.
However, a lot of nodes get started to facilitate communication with the hardware due to how Clearpath sets up their platforms.
This page documents (to the best of our understanding based on Clearpath's documentation) some of the Clearpath hardware and what nodes get started up to facilitate basic operations.

Some useful starting points in the Clearpath documentation:
- [Husky A300 Overview](https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a300/)
- [Husky A300 User Manual](https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a300/user_manual_husky/)

Alright, so let's get into it...

> ![WARNING]
> *whew* This is complicated.

## TODO FOR THIS PAGE
- [ ] citations to back up what Mark said?
- [ ] general cleanup

## CAN

Several Clearpath platforms (like Ridgeback R100 and Husky A300) use [CAN bus for communication](https://docs.clearpathrobotics.com/docs/ros/config/yaml/platform/can/).
CAN bus is often used for automotive applications (TODO citation?).
In the sense that this is a protocol for communicating data to hardware, we can think of CAN as comparable to ethercat. (TODO ethercat citation?)
The difference between CAN and ethercat is that ethercat supports direct communication, while CAN does not.

The CAN is plugged directly into the onboard Microcontroller Unit (MCU), so anything that needs to communicate needs to be bridged between the MCU and the robot computer.
To facilitate this, the Clearpath platform will have some default [Virtual CAN (VCAN) adapters](https://docs.clearpathrobotics.com/docs/ros/config/yaml/platform/can/#virtual-can-adapters).
The VCAN is what facilitates communication between the robot/controls computer and the CAN on the MCU.
This indirect communication through the VCAN is the biggest difference between CAN and ethercat.

VCAN communications are facilitated by sender and receiver nodes, which we see launched in `togo_capture/etc/clearpath/platform/launch/platform-service.launch.py`.
These sender and receiver nodes live on the robot computer. (TODO citation?)
So the sender translates ROS packates into CAN packets and sends them along the bus to the MCU,
while the receiver translates CAN packets received from the MCU into ROS packets.
These sender and receiver nodes specifically handle controller commands; they are high-frequency and sent in the native language of the micro controller for the MCU to carry out.

For more information about the Husky's CAN network, please refer to [Clearpath's Husky documentation](https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a300/integration_husky/#canbus-connection).

## micro-ROS

The CAN bus facilitates communications with the control motors specifically.
All other ROS messages are communicated between the MCU and the robot computer using [micro-ROS](https://micro.ros.org/).
While both CAN and micro-ROS enable communication between the MCU and control computer, they run parallel and completely independently, transporting different types of information to the MCU.

Critically, micro-ROS *is not ROS*.
ROS uses [DDS](https://docs.ros.org/en/jazzy/Installation/RMW-Implementations.html), which expects high-frequency updates that a node is still alive.
But the MCU does not need information that fast (at least, for anything that isn't the motor controller commands being sent over the CAN bus).
Instead, micro-ROS is used for communication of ROS messages (such as status of batteries and lights) between the MCU and controls computer.
The MCU drives all of this, creating requests for data from the controls computer and sending information to the controls computer when it has it.
There's an agent that lives on the controls computer to carry out the ROS message translations and respond to the MCU's commands.
(TODO citations for all of this)

Basically micro-ROS simulates ROS for communication of ROS messages, but it *is not ROS* because it doesn't deal with DDS.

## (Coming Soon?) Proton

Clearpath has starting migrating its MCU communication protocol from micro-ROS to [Proton](https://docs.clearpathrobotics.com/docs/ros/config/yaml/platform/mcu/).
This change is required on platforms using newer firmware versions.
Based on the services started in the Clearpath generated launch files, this Husky A300 is still using micro-ROS.
