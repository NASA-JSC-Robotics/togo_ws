# This ROS node returns a AprilTagDetections... for future use. 
# Pulled from the other branch from bring youth to work day; but all of this is mine.  -AY
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge
import cv2
from apriltag import apriltag
from togo_apriltag.msg import AprilTagDetection 

class AprilTagPublisher(Node):
    def __init__(self):
        super().__init__('apriltag_detector')
        # consts regarding the tag
        self.april_tag_size_cm = 10.0 


        self.img_sub = self.create_subscription(
            Image,
            '/husky/sensors/front_oakd/rgb/image_raw',
            self.image_callback,
            10)

        self.cam_info_sub = self.create_subscription(
            CameraInfo, 
            '/husky/sensors/front_oakd/rgb/camera_info', 
            self.info_callback, 
            10)

        #  publisher
        self.publisher = self.create_publisher(AprilTagDetection, '/apriltag_pos', 10)
        
        # cv bridge stuff
        self.bridge = CvBridge()
        self.detector = apriltag("tag36h11")

        # camera params
        self.camera_matrix = None # fx, fy, cx, cy from  the camera
        self.dist_coeffs = None # distortion coefficients as provided by CameraInfo

    # receive image, publish apriltagdetection object to /apriltag_pos. 
    def image_callback(self, msg):
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        results = self.detector.detect(gray)

        detection_msg = AprilTagDetection()
        detection_msg.header = msg.header
        detection_msg.img_width = float(msg.width)
        detection_msg.img_height = float(msg.height)
        
        if len(results) > 0:
            res = results[0]
            detection_msg.tag_found = True
            detection_msg.tag_id = res["id"]
            detection_msg.center_x = res["center"][0]
            detection_msg.center_y = res["center"][1]

            pose = detector.estimate_tag_pose(res, self.april_tag_size_cm/100., **self.camera_matrix) 
            t = pose['t'].flatten()
            tx, ty, tz = t[0], t[1], t[2]

            # translation in opencv puts Z as the "going out of image frame"
            # ros2/posestamped puts it as X. 
            pose_stamped = PoseStamped()
            pose_stamped.header = msg.header
            pose_msg.header = msg.header
            pose_msg.pose.position.x = float(tz)   # OpenCV Z -> ROS X
            pose_msg.pose.position.y = float(-tx)  # OpenCV X -> ROS Y
            pose_msg.pose.position.z = float(-ty)  # OpenCV Y -> ROS Z

            q = self.rotation_matrix_to_quaternion(pose['R'])
            pose_msg.pose.orientation.x = q[0]
            pose_msg.pose.orientation.y = q[1]
            pose_msg.pose.orientation.z = q[2]
            pose_msg.pose.orientation.w = q[3]
            
            print(f"Tag {det['id']}:")
            print(f"  Position (meters): {pose['t'].T}")
            print(f"  Rotation matrix:\n{pose['R']}")
            print(f"  Reprojection error: {pose['error']}")

            detection_msg.pose = pose_msg
        else:
            detection_msg.tag_found = False

        self.publisher.publish(detection_msg)

    # this one should be pretty straightforward.  
    # But this function was written by ChatGSFC.    
    def info_callback(self, msg):
        # Extract the 4 essential parameters for the AprilTag estimator
        # msg.k is [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        self.intrinsics = [msg.k[0], msg.k[4], msg.k[2], msg.k[5]]

    # https://www.johndcook.com/blog/2025/05/07/quaternions-and-rotation-matrices/
    def rotation_matrix_to_quaternion(self, R):
        r11, r12, r13 = R[0, 0], R[0, 1], R[0, 2]
        r21, r22, r23 = R[1, 0], R[1, 1], R[1, 2]
        r31, r32, r33 = R[2, 0], R[2, 1], R[2, 2]
        
        # Calculate quaternion components
        q0 = 0.5 * np.sqrt(1 + r11 + r22 + r33)
        q1 = 0.5 * np.sqrt(1 + r11 - r22 - r33) * np.sign(r32 - r23)
        q2 = 0.5 * np.sqrt(1 - r11 + r22 - r33) * np.sign(r13 - r31)
        q3 = 0.5 * np.sqrt(1 - r11 - r22 + r33) * np.sign(r21 - r12)
        
        return np.array([q0, q1, q2, q3])


def main(args=None):
    rclpy.init(args=args)
    node = AprilTagPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()