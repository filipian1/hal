#!/usr/bin/env python


import rospy
import cv2
from std_msgs.msg import String
import sys
from cv_bridge import CvBridge, CvBridgeError

from ar_track_alvar_msgs.msg import AlvarMarkers
from sensor_msgs.msg import Image

class DiscoverTags:
    def __init__(self):
        self.sub_ar_pose=rospy.Subscriber("/ar_pose_marker", AlvarMarkers , self.callback)
        self.bridge=CvBridge()
        self.image_sub = rospy.Subscriber("/camera/image_raw", Image , self.callback)

    def callback(self, markers):
        print(markers.x)


        try:
            cv_image = self.bridge.imgmsg_to_cv2(data)
        except CvBridgeError as e:
            print(e)
        

        cv2.imshow("Obrazek", cv_image)
        


def main(args):
    rospy.init_node('listener', anonymous=True)
    dt=DiscoverTags()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down - Keyboard interrupt")
    cv2.destroyAllWindows()

if __name__=='__main__':
    main(sys.argv)
