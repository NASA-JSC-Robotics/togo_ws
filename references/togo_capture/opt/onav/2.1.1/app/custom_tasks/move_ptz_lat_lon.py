#!/usr/bin/python3

from onav_tasks.custom_task_base import *
import actionlib
from clearpath_localization_msgs.srv import *
from clearpath_navigation_msgs.msg import *
from nav_msgs.msg import Odometry
from ptz_action_server_msgs.msg import PtzAction
import ptz_action_server_msgs.msg
import math
from math import remainder, tau
import rospy
from sensor_msgs import *
from tf.transformations import euler_from_quaternion, quaternion_from_euler



class MovePtzLatLon(CustomTaskBase):
    def __init__(self):
        super().__init__("move_ptz_lat_lon")
        self.localization_subscriber_ = rospy.Subscriber("/localization/odom", Odometry, self.localizationCallback)
        self.move_ptz_client_ = actionlib.SimpleActionClient('/sensors/camera_0/move_ptz/position_abs', PtzAction)
        self.service_ = rospy.ServiceProxy('/localization/lat_lon_to_xy', ConvertLatLonToCartesian)
        self.current_pose = Odometry()

    def localizationCallback(self, odom_msg):
        self.current_pose = odom_msg


    def run_task(self, goal):
        if len(goal.strings) == 0 and len(goal.floats) == 0:
            rospy.logwarn('Warning')
            self._as.set_aborted()
            return False
        goal_latitude = goal.floats[0]
        goal_longitude = goal.floats[1]
        goal_zoom = goal.floats[2]
        str2 = 'Received goal latitude: ' + str(goal_latitude) + ', goal longitude: ' + str(goal_longitude) + ', zoom: ' + str(goal_zoom)
        feedback = UITaskFeedback()
        feedback.state = 'Aiming camera at lat-lon (' + str(goal_latitude) + ', ' + str(goal_longitude)+')'
        self._as.publish_feedback(feedback)
        orientation_q = self.current_pose.pose.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, yaw) = euler_from_quaternion (orientation_list)

        gps_msg = sensor_msgs.msg.NavSatFix()
        gps_msg.latitude = goal_latitude
        gps_msg.longitude = goal_longitude
        goal_utm = self.service_(gps_msg)

        goal_x = goal_utm.pose.pose.position.x
        goal_y = goal_utm.pose.pose.position.y

        goal_angle = math.atan2(goal_y - self.current_pose.pose.pose.position.y, goal_x - self.current_pose.pose.pose.position.x)
        pan_angle = math.remainder(goal_angle - yaw, math.tau)
        print(pan_angle)

        self.move_ptz_client_.wait_for_server()
        goal = ptz_action_server_msgs.msg.PtzGoal()
        goal.pan=pan_angle
        goal.tilt=0
        goal.zoom=goal_zoom
        self.move_ptz_client_.send_goal(goal)
        self.move_ptz_client_.wait_for_result()
        print(self.move_ptz_client_.get_result())
        return True

# if __name__ == "__main__":
#     rospy.init_node("move_ptz_lat_lon_node")
#     test = MovePtzLatLon()
#     rospy.spin()