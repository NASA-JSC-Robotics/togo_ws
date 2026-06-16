# Clearpath Systemd Services

Togo's configuration described in the [Hardware Run Instructions](../README.md#hardware-run-instructions) replaces the default Clearpath configuration that is installed on the platform out-of-the-box.
While we find Togo's configuration more customizable and user-friendly,
the Clearpath configuration can be enabled as desired.

Note that starting/stopping systemd services requires sudo, which the default `eguser` group on the Togo computer does not have.
Only members of the `egadmin` group have sudo permissions required to run these commands.
If you need to start or stop systemd services, please talk to a member of the `egadmin` group!

## Starting Clearpath Services

Stop the Togo systemd service:

```bash
# stop the Togo robot services
sudo systemctl stop togo-robot.target

# disable the Togo robot services to prevent them from restarting
sudo systemctl disable togo-robot.target

# verify status of Togo robot services
systemctl status togo-robot.target
```

Restart the Clearpath services:

```bash
# re-enable Clearpath robot services
sudo systemctl enable clearpath-robot.service

# re-start Clearpath robot services
sudo systemctl start clearpath-robot.service
```

### Starting Select Systemd Services

Togo nodes launched during the [Hardware Run Instructions](../README.md#hardware-run-instructions) require some services to be running on the robot already,
namely the ROS discovery service and VCAN service.
Both Togo and Clearpath have systemd services for starting these specific services, which are included in the top-level `togo-robot.target` and `clearpath-robot.service` services.
Note that both Togo and Clearpath's implementations of these select services are identical.
We copied Clearpath's services and renamed them to Togo for convenience.

> [!NOTE]
> The easiest way to start these services is to use the top-level `togo-robot.target` service!
> We include the individual services here for anyone interested in Togo's systemd processes!

> [!WARNING]
> Clearpath's top-level `clearpath-robot.service` also starts many other processes besides the necessary ROS discovery and VCAN services.
> When exploring Clearpath's setup, be aware that it may be most convenient to just start these select services!

To start these select services:

- ROS discovery service:

    ```bash
    # Togo's ROS discovery service
    sudo systemctl start togo-discovery.service

    # Clearpath's ROS discovery service
    sudo systemctl start clearpath-discovery.service
    ```

- VCAN service:

    ```bash
    # Togo's VCAN service
    sudo systemctl start togo-vcan.service

    # Clearpath's VCAN service
    sudo systemctl start clearpath-vcan.service
    ```

Check the statuses of these services with:

```bash
systemctl status <service-name>
```

## Stopping Clearpath Services

Stop the Clearpath systemd service:

```bash
# stop the Clearpath robot services
sudo systemctl stop clearpath-robot.service

# disable the Clearpath robot services to prevent them from automatically restarting when they die
sudo systemctl disable clearpath-robot.service
```

Clearpath starts a lot of docker containers by default.
To stop the containers:

```bash
# see running containers
docker container ps

# kill all docker containers (including non-Clearpath containers)
docker stop $(docker ps -q)

# kill only Clearpath containers
docker stop <list-of-container-names>
```

As a sanity check, we can verify that all of the Clearpath processes have stopped:

```bash
# check systemd services
systemctl status clearpath-robot.service

# docker containers
docker ps
```

Restart the Togo services and enable them to restart automatically if they die:

```bash
# re-enable Togo robot services
sudo systemctl enable togo-robot.target

# re-start Togo robot services
sudo systemctl start togo-robot.target
```
