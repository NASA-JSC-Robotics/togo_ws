# OutdoorNav - CPR Platform

A package containing the startup launch files and parameters for the Clearpath Robotics OutdoorNav autonomy product.

## Starting the Navigation

To start OutdoorNav, you can can either launch the following files in seperate terminals,

```bash
roslaunch husky_gps_navigation sensors.launch.xml
roslaunch husky_gps_navigation localization.launch.xml
roslaunch husky_gps_navigation navigation.launch.xml
```

or, you can use `tmux` to run all the launch files with one command.

```bash
bash runOutdoorNav.sh
```

## OutdoorNav Features

The following features are currenlty available in the OutdoorNav software:

| Feature | Description |
|---|---|
| **Collision Avoidance** | Collision avoidance is the robots ability to detect obstacles and stop/maneuver around the obstacle without any collisions. If `true`, the robot will detect obstacles and if `false` no obstacles will be detected. Setting to `false` is not recommended and may cause harm to property or to other individuals.<br><br>Environment Variable: `ENABLE_COLLISION_AVOIDANCE` (Default: `true`) |
| **Obstacle Avoidance Mode** | When collision avoidance is enabled, the robot will behave in one of two way according to the obstacle avoidance mode. If set to `true`, the robot will perform obstacle avoidance maneuvers, replanning around detected obstacles. If set to `false`, the robot will slow down to a stop in front of detected obstacles and wait for the obstacle to clear before proceeding.<br><br>Environment Variable: `OBSTACLE_AVOIDANCE_MODE` (Default: `true`) |
| **Continuous Planning** | The continuous planning feature allows the robot to continuously monitor whether an obstacle on the robots path and replan around said obstacle smoothly without the need for stopping in front of the obstacle. If disabled, the robot will come to a full stop in front of obstacles and then replan around said obstacle. <br><br>Environment Variable: `ENABLE_CONTINUOUS_PLANNER` (Default: `true`) |
| **Path Smoothing** | The path smoothing feature allow paths to be generated according to a specified turning radius. The default behaviour will generate point-to-point straight line paths. <br><br>Environment Variable: `ENABLE_PATH_SMOOTHER` (Default: `false`) |
| **Path Shifting** | The path shifting feature is designed to reduce the oscillation around the initial reference path if the robot begins to deviate of said reference path. It is particularly useful for our Warthog platform whose tires are incredibly pliable and results in unmodeled effects on the navigation.<br><br>Environment Variable: `ENABLE_PATH_SHIFTING` (Default: `false`) |
| **Constrained Replanning** | The constrained replanning feature restricts the area in which replanning paths can be generated. For example, if a `REPLANNING_CONSTRAINT` of 3.0 m is used, the robot will not be allowed to replan a path that drives it more than 3.0 m from the initial path.<br><br>Environment Variable: `ENABLE_CONSTRAINED_REPLANNING` (Default: `false`)<br><br>Use the `REPLANNING_CONSTRAINT` environment variable to modify the replanning constraint (in meters). |
| **Stop Distance** | The stop distance feature allows the robot to stop a predefined distance away from obstacles. This is useful if a robot cannot drive in reverse and needs the required room in front of it to replan around an obstacle.<br><br>Environment Variable: `ENABLE_STOP_DISTANCE` (Default: `false`)<br><br>Use the `STOP_DISTANCE` environment variable to modify the stop distance (in meters). The maximum allowable stop distance for Husky is 4.5m. Anything larger in the environment variable will be decreased to this maximum value. |
| **Delay Compensation** | The delay compensation feature is able to compensate for mechanical delay on robots where either accelerator introduces delay into the linear velocity or the steering introduces delay in the angular velocity. This feature is not required for Clearpath UGVs as negligible delay is present in our system. <br><br>Environment Variable: `ENABLE_DELAY_COMPENSATION` (Default: `false`)<br><br>Use the `CONTROLLER_DELAY` environment variable to modify the amount of delay to be compensated (in milliseconds). |


## Build Docker Image

```bash
docker build -t husky-gps-navigation:latest .
```

## Run Docker Image:

```bash
  docker run --mount source=onav-config,destination=/opt/onav  --mount source=onav-log,destination=/onav_log -it --rm husky-gps-navigation:latest
```
