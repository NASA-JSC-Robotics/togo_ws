# Gazebo Troubleshooting

Notes for resolving some commonly encountered Gazebo issues.

## Stuck on `Requesting list of world names.`

If the simulation isn't starting and there are repeated entries in the log:

```bash
[INFO] [1780503451.665904613] [ros_gz_sim]: Requesting list of world names.
```

Gazebo has its own discovery server that is separate from DDS.
In some development environments this can cause problems with the simulation connecting to the backend.
You may need to manually configure the environment to use localhost, set:

```bash
export GZ_IP=127.0.0.1

# Depending you may also need
export GZ_PARTITION=$(hostname)
```

For more information refer to the [Gazebo Transport Docs](https://gazebosim.org/api/transport/14/envvars.html).
