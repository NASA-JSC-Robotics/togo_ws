The goal of this page is to understand how machines that come with stock Clearpath software are laid out, and the core components that they are built on. The intention is that this captures Clearpath systems in general, and lays out how to add on software in these ecosystems when we want to do something more custom.

# Clearpath software architecture

Clearpath designs their infrastructure so that everything gets generated and configured at boot time :(. This means that it is hard to follow and capture the exact configuration of the robot. The way they like to handle everything is by letting you modify a single file - robot.yaml , and let that their ecosystem parse that to generate the final configuration

This is described in some amount of detail [clearpath's documentation](https://docs.clearpathrobotics.com/docs/ros/config/overview), but I will summarize and add my own context from experience as well.

## Robot.yaml

Clearpath wants you to only interact with the software through the robot.yaml file that they provide. They do their entire system config based on this. Below is an example one provided on clearpaths documentation. You can see that you can modify a large number of components here to get a general setup.

```yaml
serial_number: a200-0000
version: 0
system:
  username: robot
  hosts:
    - hostname: cpr-a200-0000
      ip: 192.168.131.1
  ros2:
    namespace: a200_0000
    domain_id: 0
    middleware:
      implementation: rmw_fastrtps_cpp
    workspaces: []
platform:
  controller: ps4
  battery:
    model: ES20_12C
    configuration: S2P1
  attachments:
    - name: front_bumper
      type: a200.bumper
      model: default
      parent: front_bumper_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      enabled: true
      extension: 0.0
    - name: rear_bumper
      type: a200.bumper
      model: default
      parent: rear_bumper_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      enabled: true
      extension: 0.0
    - name: top_plate
      type: a200.top_plate
      model: pacs
      parent: default_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      enabled: true
    - name: sensor_arch
      type: a200.sensor_arch
      model: sensor_arch_300
      parent: default_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      enabled: true
  extras:
    urdf: {}
links:
  box:
    - name: user_bay_cover
      parent: top_plate_link
      xyz: [0.0, 0.0, 0.00735]
      rpy: [0.0, 0.0, 0.0]
      size: [0.4, 0.4, 0.002]
  cylinder: []
  frame: []
  mesh: []
  sphere: []
mounts:
  bracket:
    - parent: top_plate_mount_d1
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      model: horizontal
  fath_pivot:
    - parent: sensor_arch_mount
      xyz: [0.0, 0.0, -0.021]
      rpy: [3.1415, 0.0, 0.0]
      angle: 0.0
  riser: []
  sick: []
  post: []
  disk: []
sensors:
  camera:
    - model: intel_realsense
      urdf_enabled: true
      launch_enabled: true
      parent: fath_pivot_0_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      ros_parameters:
        intel_realsense:
          camera_name: camera_0
          device_type: d435
          serial_no: '0'
          enable_color: true
          rgb_camera.profile: 640,480,30
          enable_depth: true
          depth_module.profile: 640,480,30
          pointcloud.enable: true
  gps: []
  imu: []
  lidar2d:
    - model: hokuyo_ust
      urdf_enabled: true
      launch_enabled: true
      parent: bracket_0_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      ros_parameters:
        urg_node:
          laser_frame_id: lidar2d_0_laser
          ip_address: 192.168.131.20
          ip_port: 10940
          angle_min: -2.356
          angle_max: 2.356
  lidar3d:
    - model: velodyne_lidar
      urdf_enabled: true
      launch_enabled: true
      parent: sensor_arch_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      ros_parameters:
        velodyne_driver_node:
          frame_id: lidar3d_0_laser
          device_ip: 192.168.131.25
          port: 2368
          model: VLP16
        velodyne_transform_node:
          model: VLP16
          fixed_frame: lidar3d_0_laser
          target_frame: lidar3d_0_laser
```

This is generally pretty nice if you are only using components that clearpath supports, and using them how clearpath wants you to use them. This gets more complex if you are using custom components, although custom components are technically supported to some extent.

It seems like you can do quite a bit in these files, as long as you are doing things that are relatively standard. These include adding clearpath-supported sensors and mounts, and adding primitive or custom meshes with associated links.

The documentation for adding extra components is [here](https://docs.clearpathrobotics.com/docs/ros/config/yaml/platform/extras), and the options are listed below.

* urdf - provide a path to a single extra urdf component to add. Unclear whether this needs to be just a pure urdf, or whether this can be a xacro. It certainly does not seem possible to add any arguments in here
* launch - a list of launch files to run, with each component having the components package , path , and args . I assume this should be paired with a custom ros2 workspace as mentioned in a later section
* parameters - it seems like you can add custom parameters for some nodes. I am not positive if you can do this for any arbitrary node, or if these are only supported for some components

## Customization (Clearpath's way)

Clearpath gives you a couple of options to customize their setup. As mentioned in the robot.yaml config file section, you can add some limited amount of components just using the yaml file. That includes adding links, primitive shapes, and meshes, and associating them to an existing link.

If you want to add components in a more customized manner, you can make a custom ros2 workspace (defined [here](https://docs.clearpathrobotics.com/docs/ros/config/workspaces)) and add in whatever you want there. Then you can run launch files, or incorporate a urdf file as mentioned above. You just have to make sure it first within what they allow you to add - ie. a single urdf file, and launch files that can be run given their setup.

The other thing to note with this is that clearpath prefers this to be hooked in so that it runs at boot time. This means that as soon as the robot turns on, it will immediately start running all of these components together. However, this is challenging to do initial testing and debugging with, especially if your new components are highly custom.

## Services

At boot time, the robot runs several systemd jobs that kick off everything you need to run the robot. They are described in detail [here](https://docs.clearpathrobotics.com/docs/ros/config/services/).

The parent service that runs is [clearpath-robot.service](https://github.com/clearpathrobotics/clearpath_robot/blob/jazzy/clearpath_robot/services/clearpath-robot.service), which first runs a [generator](https://github.com/clearpathrobotics/clearpath_robot/blob/jazzy/clearpath_robot/scripts/generate) which creates a bunch of components you will use for your robot process. You can see all of those below, and a generalized (but simplified) diagram from clearpath is shown as well

```sh
# Generate and source setup.bash
ros2 run clearpath_generator_common generate_bash
source /etc/clearpath/setup.bash

# Generate discovery server start file
ros2 run clearpath_generator_common generate_discovery_server

# Generate Zenoh router start file
ros2 run clearpath_generator_common generate_zenoh_router

# Generate vcan bridge start file
ros2 run clearpath_generator_common generate_vcan

# Generate description
ros2 run clearpath_generator_common generate_description

# Generate semantic description
ros2 run clearpath_generator_common generate_semantic_description

# Generate parameters
ros2 run clearpath_generator_robot generate_param

# Generate launch files
ros2 run clearpath_generator_robot generate_launch
```

![alt text](/images/clearpath_design.png)

Unfortunately to see hows each component is generated, you have to go into two separate repositories and parse through some pretty hard to read code. Everything that is a ros2 run for a clearpath_generator_common package lives [here](https://github.com/clearpathrobotics/clearpath_common/tree/jazzy/clearpath_generator_common/clearpath_generator_common) (go into the subdirectories). And everything that is a ros2 run for a clearpath_generator_robot lives [here](https://github.com/clearpathrobotics/clearpath_robot/tree/jazzy/clearpath_generator_robot/clearpath_generator_robot).

There is a lot involved in what goes into the generation step, and that is what makes it hard to understand and modify the full state of your robot in a standard ROS setup. However, after this is run (at boot time), you can see the result of the generation at etc/clearpath where it creates the structure you can see at [this link](https://docs.clearpathrobotics.com/docs/ros/config/generators#setup-folder-structure) . This will look closer to a standard ROS ecosystem at that point, but it is hard to understand where everything came from without diving into some very hard to digest python generation code.

Alright, so now we have the necessary files that we need. Now, the rest of the systemd services start. There are several children services which are described at [this page](https://docs.clearpathrobotics.com/docs/ros/config/services), and the source for the services live [here](https://github.com/clearpathrobotics/clearpath_robot/tree/jazzy/clearpath_robot/services), but I will give a brief summary of the important ones here anyways.

* [**clearpath-vcan.service**](https://github.com/clearpathrobotics/clearpath_robot/blob/jazzy/clearpath_robot/services/clearpath-vcan.service) - starts up the virtual can network which allows you to read the CAN interface over ethernet
* [**clearpath-sensors.service**](https://github.com/clearpathrobotics/clearpath_robot/blob/jazzy/clearpath_robot/services/clearpath-sensors.service) - starts up all launch files related to the sensors, including things like imus, lidars, cameras. I would link you to what the launch files are, but they don't exist until boot time, so
* [**clearpath-platform.service**](https://github.com/clearpathrobotics/clearpath_robot/blob/jazzy/clearpath_robot/services/clearpath-platform.service) - starts up the launch file related to making the mobile base move. This will typically include a number of things, like
starting and handling the MCU
launch extended kalman filter
handling misc supporting components like batteries, lighting, diagnostics
starting a controller manager and controller to process velocity commands and forward them to the MCU
starting some nodes relating to teleop, which enables you to use the controller to command movement, as well as from several other sources
* [**clearpath-manipulator.service**](https://github.com/clearpathrobotics/clearpath_robot/blob/jazzy/clearpath_robot/services/clearpath-manipulators.service) - starts up the launch file related to any attached manipulators (only relevant if you have a manipulator mounted and managed by clearpath)
* [**clearpath-platform-extras.service**](https://github.com/clearpathrobotics/clearpath_robot/blob/jazzy/clearpath_robot/services/clearpath-platform-extras.service) - starts up the launch file related to extra components that you have added (will be explained soon)

Note that all of these services look something like below (example for platform service). These all just reference a script to run which normally lives in /usr/sbin/ . From what I can tell, each of these bash scripts is actually generating more launch files at runtime, putting them into the /tmp/ directory, and then launching them. But I'm pretty confused by this to be honest.
```systemd
[Unit]
Description="Clearpath robot sub-service, launch all platform nodes"
PartOf=clearpath-robot.service
After=clearpath-robot.service

[Service]
User=robot
Type=simple
ExecStart=/usr/sbin/clearpath-platform-start

[Install]
WantedBy=clearpath-robot.service
```
Because these are all systemd services, you can restart them with systemd commands, like sudo systemctl restart {service_name}, but in practice we have had some issues with doing things like that. Additionally, you should note that these are less convenient to manage compared to being able to cancel a ros launch file in a terminal. These services also tend to start up many different components at the same time, so it is hard to work on a subset of nodes/launch files and really dig into problems if you have them.

# Custom Software Options

I generally see two separate options for working within the clearpath ecosystem, and I will try to explain the general outline, and pros/cons of each of the setups.

## Option 1 - Use the clear path

Clearpath wants you to use their robot.yaml config file, and let their ecosystem build everything when your system boots (or when you tell it to re-run). This is what has been mainly outlined in this document.

### Pros

If you don't go too far away from the stock Clearpath setup (ie adding extra sensors, mounts, etc), things should probably #justwork, and you shouldn't need to do a lot of manual modifications.

The other main benefit of this setup, is that you can probably get support from Clearpath themselves if you have any issues/challenges, and if they update their software/procedures, you can take advantage of that (although we can still easily get software updates in option 2).

### Cons

There are plenty of cons with this setup, and they largely depend on how much customization you want to do with your software stack. If you are adding maybe a sensor or two, but you want to leave the majority of the robot unchanged and running exactly as it was, you shouldn't have too many issues.

As you start to add/modify more components (custom gripper, modifying the structure of the robot, replacing standard clearpath ROS nodes), it becomes increasingly difficult to use the clearpath setup. You might find yourself having to write shell scripts to kill individual processes after they have been started so that they don't conflict with your setup.

This setup also makes it challenging to test small incremental upgrades of setups. Because everything is based on systemd scripts, it is hard to understand how making small changes affects the whole ecosystem. If you are want to update one small component, you will probably have to bring downeverything so that the whole environment can be regenerated.

The fact that everything is generated at boot time means that it is hard to capture the state of the robot in source control like gitlab, and track the changes you are making over time. So if you modify something in robot.yaml, and the system changes significantly, you can't really dive in and see what specific changes were made to launch files and/or system configs. This can be important if you are trying to capture several different robot testing configurations - maybe one with some test lidar, and others with test cameras. You can use source control to manage those configurations in a standard way and capture the state of your testing configuration.

Using Clearpaths way will also make it a bit harder to run the standard setups on any machine other than the robot. For example if you want to do development in gazebo, then push code and test it on the robot, you would have to set up your machine as if it was a clearpath robot machine, and do your development as if it was a clearpath robot machine. This is not a huge deal, but could cause many unnecessary headaches if you want to manage other ROS environments on that machine as well.

This method also only works as long as there is sufficient compute available on the machine to add your extra drivers/algorithms without maxing out resources. If your algorithms use a lot of compute, or would benefit from GPU acceleration, then this isn't a very good option for you.

## Option 2 - Make your own path

The idea of doing this, is you can have clearpath run the boot-time setup one time, and you can grab the intermediate output (all of the packages and launch files that get generated) and use them as your starting point to make your own custom configuration. This gives you the flexibility to leave what you want to leave, but put the code into gitlab and track the changes that your team makes over time.

Should you choose to make your own path, there are some other decisions to make along the way - do you want to use containers, and whether or not you want to put your software on an external computer, or leave it on the main robot computer. See the later sections for information on this.

### Pros

A large benefit of setting up this way is being able to understand the full scope of your system. It is extremely challenging to understand what things are being started and where, as was probably shown by the lengthy explanation above. Having a single gitlab repository with all of the information you need, ie. packages forphoebe_description ,phoebe_deploy ,phoebe_nav2_config, etc makes it easy to search through the repository and find why things are doing what they are doing (see phoebe_bridgeback package for an example).

This gives quite a bit of flexibility for what you want to do. If you want to modify the urdf, or add/remove something from a launch file, it is very straightforward to do, and it is easy to make modifications and see your changes have affect by quickly killing a terminal and restarting just the components that you want.

Going through this process would also mean that you will likely end up with a better understanding of the software stack of the robot, and how information is flowing between components.

### Cons

If you need to troubleshoot something in this setup, you might have to get relatively deep into the software to understand went wrong. For example, we have done plenty of troubleshooting of how the MCU communicates to the rest of the robot. This is mostly because we changed the standard setup in favor of running things the way that we wanted. This can be largely mitigated by leaving the setup relatively standard.

# Other Considerations
## To airgap or to not airgap

For development, we tend to rely a lot on having a network connection so that we can download new software, push our development to gitlab, etc. This is very useful if you have it, but is not always strictly necessary. Here are some considerations to take into account which can help you make that decision

Will most of the custom code development happen on the robot? If yes, then it is very useful to have internet access so that you can directly pull/push code without having to copy code from one machine to another. With any projects that have a decent amount of scale, this could get really challenging really quickly without that. If the custom code development is happening on a separate computer that has internet access, this isn't nearly as important, as the robot computer would likely remain largely static.
Is IT able to support a relatively custom configuration? Our robot computers typically live in a state that doesn't fall into the standard IT framework, and we need to do some relatively custom things. For example, we don't typically run some of the IT checks at the same rate that the rest of the non-robot machines do, and we run a non-FIPS realtime kernel on the robot machine, which IT has to be ok with supporting.

## To container or to not container

You might decide to use some kind of containerization (ie. docker) for your source components for either of the software architecture options. We tend to use docker for a lot of reasons, and it works well in a lot of cases, but does come with additional system complexity that you should be aware of

Some reasons that docker is great:

By default, the docker files which define your docker ends up capturing all of the steps you needed to configure your setup to work properly
If it work on your machine in a docker, it will (probably) work on someone else's machine in the same docker (with a few exceptions)
You are free to try crazy things in your docker without any risk of messing up your host machine
You can use docker to capture specific system config (like network setups) so that you don't need to
You can have many distinct environments for similar but different implementations
You can tag and store a specific image, then reload that exact image later to test in the same exact setup
A docker can be transferred from a dev machine to the robot with a single file transfer (handy if air-gapped)
Dockers work very well for automated testing with CI systems

Some reasons that docker isn't great:

One more thing to learn and maintain (although industry is moving in this direction anyways, so good to learn)
Takes up more space on your machine
Need for more tooling to work in docker environments
If you are working in a container and make a change then exit the container, the change can be lost - but we have ways to handle this in most cases
Docker requires running a daemon process as root, which can be a security concern.

## To add more compute, or to not add more compute

As you are adding more custom sensors and software to your system, you have the option to either put that software on the clearpath CPU, or to move that software to another PC. If you decide to put software on another machine, you can either add an additional PC onboard the robot (likely with some kind of GPU capabilities), or you can push the software to something like an operators console. Typically, we think about any kind of algorithms that integrate directly with sensors, or that get integrated into some kind of a control loop should be run as close to the hardware as possible, and avoid going over a wifi network.The decision to move your compute to a different machine comes down to a couple of important factors.

The first factor is whether or not you want to take advantage of having GPU accelerated computations. The onboard computer does not have a graphics card, so it won't be able to do anything fancy.

The second factor is whether or not the robot computer's interfaces can handle the physical requirements of additional hardware. If you are wanting to add some kind of sensor or additional hardware, you need to understand if there are enough usb/ethernet ports, and make sure that the addition of more components won't push you over bandwidth limitations of your computer. With this in mind, you also need to make sure whatever extra components you want to add can also be handled by your extra compute.

It is worth noting that adding extra compute does add some complexity. You now need to handle how to distribute software to multiple systems - do you duplicate everything and put everything everywhere, or just put the required components on each system? You need to also figure out networking between the devices, and figure out how you are going to handle traffic between devices. It is certainly more expensive to send data over the network, than to use it locally on your machine. This might mean that you need to do some careful configuring to make sure you aren't needlessly sending traffic that could bog down your system.

# Relevant Clearpath Repositories

[clearpath_common](https://github.com/clearpathrobotics/clearpath_common/tree/jazzy)

[clearpath_robot](https://github.com/clearpathrobotics/clearpath_robot)

[robot_upstart](https://github.com/clearpathrobotics/robot_upstart)

[clearpath_config](https://github.com/clearpathrobotics/clearpath_config)