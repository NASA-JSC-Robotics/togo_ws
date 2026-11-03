# Software Development on Togo

## Best Practices for Development on Robots

> [!WARNING]
> Please review these best practices carefully.

1. When in doubt, ***ask for help and ask questions***.
2. Develop new applications in ***separate packages*** from the key robot functionality packages (`togo_description` and `togo_deploy`).
   1. If you are thinking of making any changes to the Togo core packages, talk through these changes with experienced operators and developers.
3. Develop on ***separate branches*** so this git repository maintains the latest stable, working robot configuration packages.
4. Test all changes thorough ***in simulation*** before testing on the robot.
5. Debugging code on the robot during an ops session is expected.
  However, completing development on the robot is typically unwise (since it often skips testing in simulation first) and is a waste of hardware time.
6. Use your teammates as rubber ducks!
  Even experienced operators benefit from talking through their changes before running on the robot.
7. Always test your code on the robot!
  Code does not work unless it survives a robot ops session!
8. Freeze code before a demo.
  Last minute changes, no matter how small, can break a functioning demo in ways you may not anticipate.

## Running Your Code on Togo

1. ***Before starting up the robot*** pull your changes onto Togo's robot computer.
2. If your changes added new package dependencies, the [hardware development docker images](../../../README.md#hardware-development-image) will need to be rebuilt:

    ```bash
    docker compose build hw-dev
    ```

3. Continue with the [Interactive Mode hardware instructions](../README.md#switching-to-interactive-mode).
   1. After you connect to the hardware development container, remember to [build the workspace](../../../README.md#building-the-togo-workspace) so your changes take effect.

      ```bash
      # build the whole workspace; best practice is to do this before launching anything
      colcon build

      # source the workspace changes in all open terminals
      source install/setup.bash
      ```

4. At the end of your ops session, ***commit and push all of your code!***
