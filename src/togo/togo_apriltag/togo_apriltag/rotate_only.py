# This demo for bring youth to work day. Logic written by Tim Burns. I pulled this file from the other branch and cleaned it up -AY
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped, Vector3, Twist
from std_msgs.msg import Header
from my_robot_msgs.msg import AprilTagDetection
import numpy as np
from time import time

class TagFollower(Node):
    def __init__(self):
        super().__init__('tag_follower')
        self.subscription = self.create_subscription(
            AprilTagDetection,
            '/detected_tag',
            self.tag_callback,
            10)
        self.publisher = self.create_publisher(TwistStamped, "/platform_velocity_controller/cmd_vel", 10)
        
        # Logic Parameters
        self.decelleration = 0.05
        self.target_rot_speed = 0.2
        self.current_rot_speed = 0.0
        self.last_execution_time = time()
        self.dt = 0.0

    def tag_callback(self, msg):
        self.dt = time() - self.last_execution_time
        self.last_execution_time = time()
        
        img_w = msg.img_width

        if msg.tag_found:
            tag_x = msg.center_x
            x_buffer = img_w / 12
            x_error = tag_x - img_w / 2
            
            if abs(x_error) < x_buffer:
                if abs(self.current_rot_speed) < self.decelleration * self.dt:
                    self.current_rot_speed = 0.0
                else:
                    self.current_rot_speed += -np.sign(self.current_rot_speed) * self.decelleration
            else:
                self.current_rot_speed = -np.sign(x_error) * self.target_rot_speed
        else:
            # Slow down if tag lost
            if abs(self.current_rot_speed) < 2 * self.decelleration * self.dt:
                self.current_rot_speed = 0.0
            else:
                self.current_rot_speed += -np.sign(self.current_rot_speed) * (self.decelleration * self.dt)

        self.current_rot_speed = np.clip(self.current_rot_speed, -self.target_rot_speed, self.target_rot_speed)

        # Publish Twist
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.angular.z = float(self.current_rot_speed)
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = TagFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()