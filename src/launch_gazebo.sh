#!/bin/bash
 
# 1. Source the ROS 2 workspace
source /home/er4-user/ws/install/setup.bash
 
 
# 2. Start the Gazebo Server (Headless/GPU for LiDAR) in the background
echo "[1/3] Starting Gazebo Server (GPU)..."
DISPLAY= ros2 launch togo_gz sim_gz.launch.py &
SERVER_PID=$!
 
 
sleep 4
 
# 3. Start the Gazebo GUI (Software Rendering for ThinLinc) in the background
echo "[2/3] Starting Gazebo GUI (CPU)..."
LIBGL_ALWAYS_SOFTWARE=1 gz sim -g &
GUI_PID=$!
 
 
sleep 2
 
# 4. Start RViz2 in the background
echo "[3/3] Starting RViz2..."
rviz2 -d /home/er4-user/ws/install/togo_deploy/share/togo_deploy/rviz/robot_sensor_checkout.rviz &
RVIZ_PID=$!
 
echo "=========================================="
echo "✅ All systems running! Press Ctrl+C to exit."
echo "=========================================="
 
 
trap "echo -e '\n🛑 Shutting down all processes...'; kill $SERVER_PID $GUI_PID $RVIZ_PID; wait; exit" SIGINT SIGTERM
 
 
wait