#!/usr/bin/python3

from onav_tasks.custom_task_base import *
from clearpath_localization_msgs.srv import *
from clearpath_navigation_msgs.msg import *
import rospy

class ResetLocalizationTask(CustomTaskBase):
    def __init__(self):
        super().__init__("reset_localization")
        self.service_ = rospy.ServiceProxy('/localization/reset', ResetLocalization)


    def run_task(self, goal):
        feedback = UITaskFeedback()
        feedback.state = 'Resetting localization'
        self._as.publish_feedback(feedback)
        rospy.sleep(5.0)
        
        reset_msg = ResetLocalizationRequest()
        reset_msg.gnss_samples = 100
        reset_msg.require_gnss = True
        self.service_.call(gnss_samples=100, require_gnss=True)
        rospy.logwarn("Finished calling reloc service")
        return True
    

# if __name__ == "__main__":
#     rospy.init_node("reset_localization_node")
#     test = ResetLocalizationTask()
#     rospy.spin()