#!/usr/bin/python3

import dynamic_reconfigure.client
import rospy
from clearpath_navigation_msgs.msg import *
from onav_tasks.custom_task_base import *


def globalConfigCallback(config):
    rospy.loginfo(
        "Global costmap config: {enabled}, {footprint_clearing_enabled}, {max_obstacle_height}, {combination_method}".format(
            **config))


def localConfigCallback(config):
    rospy.loginfo(
        "Local costmap config: {enabled}, {footprint_clearing_enabled}, {max_obstacle_height}, {combination_method}".format(
            **config))


class SetObstacleDetection(CustomTaskBase):
    def __init__(self):
        super().__init__("set_obstacle_detection")
        self.global_costmap_client_ = None
        self.local_costmap_client_ = None

    def run_task(self, goal):
        if len(goal.strings) == 0 and len(goal.floats) == 0:
            rospy.logwarn('No arguments set in task')
            self._as.set_aborted()
            return False

        self.global_costmap_client_ = dynamic_reconfigure.client.Client("/navigation/global_costmap/obstacles",
                                                                        timeout=30,
                                                                        config_callback=globalConfigCallback)
        self.local_costmap_client_ = dynamic_reconfigure.client.Client("/navigation/local_costmap/obstacles",
                                                                       timeout=30, config_callback=localConfigCallback)

        feedback = UITaskFeedback()
        feedback.state = 'Setting obstacle detection as:' + goal.strings[0]
        self._as.publish_feedback(feedback)
        rospy.sleep(5.0)

        if (goal.strings[0].lower() == 'enabled'):
            self.global_costmap_client_.update_configuration({"enabled": True})
            self.local_costmap_client_.update_configuration({"enabled": True})
        elif (goal.strings[0].lower() == 'disabled'):
            self.global_costmap_client_.update_configuration({"enabled": False})
            self.local_costmap_client_.update_configuration({"enabled": False})
        else:
            rospy.logerr("Invalid argument. Must be either 'enabled' or 'disabled'")
            return False

        rospy.sleep(1.0)
        return True
