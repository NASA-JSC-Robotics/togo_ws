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



class MovePtzHome(CustomTaskBase):
    def __init__(self):
        super().__init__("move_ptz_home")
        self.move_ptz_client_ = actionlib.SimpleActionClient('/sensors/camera_0/move_ptz/position_abs', PtzAction)


    def run_task(self, goal):
        if len(goal.strings) == 0 and len(goal.floats) == 0:
            rospy.logwarn('Warning')
            self._as.set_aborted()
            return False
        feedback = UITaskFeedback()
        feedback.state = 'Setting camera position to HOME'
        self._as.publish_feedback(feedback)

        self.move_ptz_client_.wait_for_server()
        goal = ptz_action_server_msgs.msg.PtzGoal()
        goal.pan=0.0
        goal.tilt=0.0
        goal.zoom=1.0
        self.move_ptz_client_.send_goal(goal)
        self.move_ptz_client_.wait_for_result()
        print(self.move_ptz_client_.get_result())
        return True
