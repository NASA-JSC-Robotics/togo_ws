import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from my_robot_msgs.msg import AprilTagDetection
import tf2_ros
from tf2_geometry_msgs import do_transform_pose
import time

class AprilTagFollower(Node):
    def __init__(self):
        super().__init__('apriltag_nav_follower')
        self.subscription = self.create_subscription(
            AprilTagDetection, '/detected_tag', self.tag_callback, 10)
        
        # Nav2 Action Client
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.get_logger().info("AprilTag Nav Follower Started")

        self.last_time_sent = None 

    def tag_callback(self, msg):
        if not msg.tag_found:
            return

        # make sure we're not calling the tag callback CONSTANTLY
        if self.last_time_sent is not None:
            current_time = self.get_clock().now()
            duration = current_time - self.last_time_sent 
            self.last_time = current_time
            # https://deepwiki.com/ros2/rclpy/7.1-clock-and-time
            if duration / 1e9 < 60. : # 60 seconds
                return 

        # The pose from your detector is relative to the camera frame (e.g., oakd_rgb_optical_frame)
        tag_pose_camera = msg.pose 

        try:
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose.header.frame_id = 'base_link'
            goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
            goal_msg.pose.pose = tag_pose_camera.pose
            
            # 4. Send the Goal to Nav2
            self.get_logger().info("Sending goal to Nav2...")
            self.nav_to_pose_client.wait_for_server()
            self.nav_to_pose_client.send_goal_async(goal_msg)

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            self.get_logger().error(f"TF Transform failed: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = AprilTagFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()