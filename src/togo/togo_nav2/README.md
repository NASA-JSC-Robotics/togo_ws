# togo_nav2

## Table of Contents

- [Summary](#summary)
- [Simulation vs Hardware Topic Differences](#simulation-vs-hardware-topic-differences)
- [togo_nav2](#togo_nav2)
  - [Launch Files (and more)](#launch-files-and-more)
    - [navigation.launch.py](#navigationlaunchpy)
      - [lifecycle_manager_navigation](#lifecycle_manager_navigation)
      - [controller_server](#controller_server)
      - [planner_server](#planner_server)
      - [behavior_server](#behavior_server)
      - [bt_navigator](#bt_navigator)
      - [waypoint_follower](#waypoint_follower)
      - [Cost Maps](#cost-maps)
        - [local_costmap](#local_costmap)
        - [global_costmap](#global_costmap)
      - [smoother_server](#smoother_server)
      - [docking_server](#docking_server)
      - [route_server](#route_server)
      - [velocity_smoother](#velocity_smoother)
      - [collision_monitor](#collision_monitor)
    - [slam.launch.py](#slamlaunchpy)
      - [slam_toolbox](#slam_toolbox)
    - [pointcloud2laserscan.launch.py](#pointcloud2laserscanlaunchpy)
      - [pointcloud_2_laserscan](#pointcloud_2_laserscan)
    - [localization.launch.py](#localizationlaunchpy)
      - [nav2_amcl](#nav2_amcl)
      - [map_server](#map_server)
    - [nav2_rviz.launch.py](#nav2_rvizlaunchpy)
    - [sim_everything.launch.py](#sim_everythinglaunchpy)

## Summary

This is a basic configuration of Nav2 packages for the Togo robot.

## Build

In the docker, this builds alongside the togo package ---

```bash
colcon build
source install/setup.bash
```

## Run

To test the togo_nav2 with the simulation, run the [sim_everything.launch.py](#sim_everythinglaunchpy) file.

```bash
ros2 launch togo_nav2 sim_everything.launch.py
```

## Simulation vs Hardware Topic Differences

As of 17 June 2026, some cases the topics used in the simulation do not match the hardware.
The hardware topic names seemed to be in flux a bit, so differences made in the simulation were made so that a pattern was followed by the sensor data topic names --- /husky/sensors/sensor_name/data_type.

```
| Header Topic | Simulation Topic |
|------------:|:-----------------|
[ /ivpoints    | /husky/sensors/seyond/points |
| /fixposition/gnss1[^1] | /husky/sensors/fixposition/left_gps/fix |
| /fixposition/gnss2[^1] | /husky/sensors/fixposition/right_gps/fix |
| [^2] | /husky/sensors/front_oakd/points |
| [^2] | /husky/sensors/rear_oakd/points |
```

## Launch Files (and more)

### navigation.launch.py

These are the nodes that are launched with the togo_nav2/navigation.launch.py launch file.
This launch file replaces nav2_bringup/navigation_launch.py.
It uses our configuration configuration and only brings up the nodes we are currently using.

#### lifecycle_manager_navigation

This is the core orchestrator for the Navigation 2 stack.
It controls the startup, shutdown, reset, pause, and resume states of your navigation nodes.
We use the default configuration.
The current configuration launches the **bold** nodes.
Descriptions of all the lifecycle nodes are included.

- [**controller_server**](#controller_server)
- [**planner_server**](#planner_server)
- [**behavior_server**](#behavior_server)
- [**bt_navigator**](#bt_navigator)
- [**waypoint_follower**](#waypoint_follower)
- [smoother_server](#smoother_server)
- [docking_server](#docking_server)
- [route_server](#route_server)
- [velocity_smoother](#velcity_smoother)
- [collision_monitor](#collision_monitor)

#### **controller_server**

Server for handling the controller requests for the stack and host map of plugins.
Currently using the default configuration which launches the following plugins:

- Progress Checker
- Goal Checker
- Path Handler
- Follow Path

We use the default parameters from clearpath_nav2/demos/a300, except setting the
AckermannConstraints:min_turning_r to 0.0, since we are using skid steer instead of ackerman steering.

This node brings up the [local_costmap](#local_costmap).

#### **planner_server**

Server for handling planner requests.
We are using the default planner "GridBased".
Manages and brings up the [global_costmap](#global_costmap).

We use the default parameters from clearpath_nav2/demos/a300.

#### **behavior_server**

Implements the server for handling various behaviors, such as recoveries and docking. Required by the [bt_navigator](#bt_navigator)

We use the default parameters from clearpath_nav2/demos/a300.

#### **bt_navigator**

The brain of the navigator stack --- implements the NavigateToPose, NavigateThroughPoses, and other task interfaces.
It is a Behavior Tree-based implementation of navigation that is intended to allow for flexibility in the navigation task and provide a way to easily specify complex robot behaviors, including recovery.

We use the default parameters from clearpath_nav2/demos/a300.

#### **waypoint_follower**

Implements a way of doing waypoint following using the NavigateToPose action server.
It will take in a set of ordered waypoints to follow and then try to navigate to them in order.
We've only tested this with a single waypoint sent from rviz2.

We use the default parameters from clearpath_nav2/demos/a300.

#### **Cost Maps**

The costmaps are currently configured as 2D costmaps with an obstacle layer and a costmap layer.
The costmap includes the obstacle inflation, ensuring that the robot gives space around the obstacles.
They can also be configured to include a 'static_layer' that is an a priori map.
These nodes are brought up by other nodes and not explicitly launched.

##### **local_costmap**

The local costmap is a rolling window that is always centered on the robot.
It is used by the controller to compute robot trajectories.
Launched with the [controller_server](#controller_server).

##### **global_costmap**

Like the local_costmap, the global costmap has and obstacle layer and a costmap layer. The local costmap does NOT feed the global costmap --- they are computed independently.
The global_costmap is used by the planner.
The global costmap requires a link between the /odom and the /map frame.
The /odom frame represents the cumulative position of the robot starting at 0,0 with 0 heading.
The /map frame represents a  true global frame.
This link is not provided by any module launched by nav2.launch.py, so don't worry if this launch file doesn't work on it's own.

The global costmap is launched with the [planner_server](*planner_server)

#### smoother_server

Implements the server for handling smooth path requests and hosting a vector of plugins implementing various C++ smoothers.
The server exposes an action interface for smoothing with multiple smoothers that share resources such as costmaps and TF buffers.

#### docking_server

Docking Server is a general framework which can be used with arbitrary types of robots and docks in order to auto-dock them.

#### route_server

Implements the server for computing routes through a predefined navigation graph rather than using freespace planning like the Planner Server.
It may be used to fully replace freespace planning when following a particular route closely or to augment the global planner with long-distance routing to a goal.
In this case, the planner will generate feasible paths with localized environmental information for only the future part of the route necessary.

#### velocity_smoother

This node is for smoothing velocities sent by Nav2 to robot controllers.

#### collision_monitor

Works independenty of the costmaps and provides a level of robot safety.
It uses the robot sensors to detect imminent collisions at the emergency stop level.

### slam.launch.py

Launches the slam_toolbox launch file  'online_async_launch.py' or 'online_sync_launch.py' depending on the 'sync' argument.
This brings up the /slam_toolbox node.
Slam_toolbox makes maps of an area while tracking position.

#### slam_toolbox

Slam_toolbox only does 2D maps and localization.
It uses laserscan messages rather than pointclouds, so we need to use the pointclould_2_laserscan node to convert our pointclouds.
It is launched using the [pointcloud2laserscan.launch.py](#pointcloud2laserscanlaunchpy).

### pointcloud2laserscan.launch.py

Launches a pointcloud_2_laserscan node to convert the seyond/points PointCloud message to the seyond/scan LaserScan message.
We can add additional nodes here to convert the oakd point clouds.

#### pointcloud_2_laserscan

Converts PointCloud2 messages to LaserScan messages by projecting a portion of the pointcloud onto a plane and finding the nearest points.
It expect the poincloud to be in a frame with x pointing into the cloud, and z being the height of the cloud.
If it isn't in a frame like this, a *target_frame* parameter is available.
If *target_frame* is specified, the cloud will be transformed to that frame before the conversion is performed.
This can also be helpful if the original frame is oriented in such a way that the laser scan, which will be parallel to the x, y plane of the frame, would not be useful (e.g. the LiDar is mounted high and pointed toward the ground).

### localization.launch.py

This is currently just a copy of the clearpath nav2 demos localization.launch.py file, which in turn, launches the nav2_bringup localization.launch.py file.
Consider everything in this file currently unconfigured.

#### nav2_amcl

Uses an  Adaptive Monte-Carlo Localizer (amcl) to find the robot location in a known map.

#### map_server

Implements various components for handling grid maps, including loading, saving, and publishing maps and their metadata.
It takes a yaml file, which includes the name of the map image (greyscale .pgm --- not sure if jpg will work) and information about placement and resolution.
This is the map the localization will find it's position in.

### nav2_rviz.launch.py

Launches rviz2 configured for good visualization of these processes.

### sim_everything.launch.py

Meant for testing and familiarization.
Launches:

- sim_gz.launch.py from togo_gz
- teleop.launch.py from togo_deploy
- navigation.launch.py from togo_nav2
- slam.launch.py from togo_nav2 which also launches
  - pointcloud2laserscan.launch.py from togo_nav2
- nav2_rviz.launch.py from togo_nav2

When you launch sim_everything.launch.py, assuming you have joystick on /dev/input/ps2 (configurable in togo_deploy/config/husky/teleop_joy.yaml) you should be able to drive the robot in simulation using the joystick.
You should also be able to use the *2D Goal Pose* on the menu bar to set a goal.
The robot will plan a path and move to the goal.

[^1]: This is my best guess for what the gps fix message is from the hardware.

[^2]: These may not be enabled in the realsense camera drivers on hardware.
